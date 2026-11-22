"""Tiny KiCad schematic generator: symbols from the stock libraries, every pin
connected by a net label placed on its end point (no wires).

Used by gen_*.py; run `python hardware/gen_all.py`, then check with
`kicad-cli sch erc`.
"""
import glob
import os
import re
import uuid as _uuid

# ------------------------------------------------------------ s-expressions
TOK = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+)')


def parse(text):
    stack, cur = [], []
    for m in TOK.finditer(text):
        t = m.group(1)
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t)
    return cur


def dump(e, ind=0):
    if not isinstance(e, list):
        return e
    if all(not isinstance(x, list) for x in e):
        return "(" + " ".join(e) + ")"
    pad = "\t" * (ind + 1)
    parts = [x if not isinstance(x, list) else dump(x, ind + 1) for x in e]
    head = []
    while parts and not isinstance(e[len(head)], list):
        head.append(parts.pop(0))
    return "(" + " ".join(head) + "".join("\n" + pad + p for p in parts) + ")"


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def uq(s):
    return s[1:-1] if s.startswith('"') else s


def find(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


def uid():
    return str(_uuid.uuid4())


# ------------------------------------------------------------ libraries
def libdir():
    d = os.environ.get("KICAD_SYMBOL_DIR")
    if d:
        return d
    c = sorted(glob.glob("/nix/store/*kicad-symbols*/share/kicad/symbols"))
    if not c:
        raise SystemExit("set KICAD_SYMBOL_DIR")
    return c[-1]


_libs = {}


def lib(name):
    if name not in _libs:
        path = os.path.join(libdir(), name + ".kicad_sym")
        tree = parse(open(path).read())[0]
        _libs[name] = {uq(s[1]): s for s in find(tree, "symbol")}
    return _libs[name]


def symdef(lib_id):
    """Flattened symbol definition, renamed to lib_id (as in lib_symbols)."""
    lname, sname = lib_id.split(":")
    syms = lib(lname)
    s = syms[sname]
    ext = find(s, "extends")
    if ext:
        parent = symdef(f"{lname}:{uq(ext[0][1])}")
        pname = uq(ext[0][1])
        body = [x for x in parent[2:] if not (isinstance(x, list) and x[0] == "property")]
        props = find(s, "property")
        body = [_rename_units(x, pname, sname) for x in body]
        s = ["symbol", q(sname)] + props + body
    s = [x for x in s if not (isinstance(x, list) and x[0] == "extends")]
    return ["symbol", q(lib_id)] + s[2:]


def _rename_units(x, old, new):
    if isinstance(x, list) and x[0] == "symbol":
        n = uq(x[1])
        if n.startswith(old + "_"):
            return [x[0], q(new + n[len(old):])] + x[2:]
    return x


def pins(sd):
    """[(unit, number, name, x, y, angle, etype)] from a flattened symbol."""
    out = []
    for sub in find(sd, "symbol"):
        m = re.match(r".*_(\d+)_(\d+)$", uq(sub[1]))
        unit, style = int(m.group(1)), int(m.group(2))
        if style > 1:
            continue
        for p in find(sub, "pin"):
            at = find(p, "at")[0]
            name = uq(find(p, "name")[0][1])
            num = uq(find(p, "number")[0][1])
            hidden = "hide" in p
            out.append((unit, num, name, float(at[1]), float(at[2]),
                        float(at[3]) if len(at) > 3 else 0.0, p[1], hidden))
    return out


# ------------------------------------------------------------ schematic
G = 2.54


def snap(v):
    return round(v / 1.27) * 1.27


class Sheet:
    def __init__(self, project, title, paper="A3"):
        self.project, self.title, self.paper = project, title, paper
        self.uuid = uid()
        self.libsyms = {}
        self.items = []
        self.x, self.y, self.rowh = 25.4, 30.48, 0
        self.width = 400 if paper == "A3" else 280
        self.pwr = 0

    # placement cursor
    def group(self, text):
        self.newrow()
        self.items.append(["text", q(text), ["exclude_from_sim", "no"],
                           ["at", f"{self.x:.2f}", f"{self.y:.2f}", "0"],
                           ["effects", ["font", ["size", "2", "2"], "bold"],
                            ["justify", "left", "bottom"]], ["uuid", uid()]])
        self.y += 7.62

    def newrow(self):
        if self.rowh:
            self.y += self.rowh + 12.7
        self.x, self.rowh = 25.4, 0

    def note(self, text):
        self.items.append(["text", q(text), ["exclude_from_sim", "no"],
                           ["at", f"{self.x:.2f}", f"{self.y:.2f}", "0"],
                           ["effects", ["font", ["size", "1.27", "1.27"]],
                            ["justify", "left", "top"]], ["uuid", uid()]])
        self.y += 5.08 * (text.count("\n") + 1)

    def part(self, lib_id, ref, value, nets, footprint="", fields=None,
             unit=1, dnp=False):
        """nets: {pin number or name: net}; None → no-connect flag."""
        if lib_id not in self.libsyms:
            self.libsyms[lib_id] = symdef(lib_id)
        sd = self.libsyms[lib_id]
        ps = [p for p in pins(sd) if p[0] in (0, unit)]
        xs = [p[3] for p in ps] or [0]
        ys = [p[4] for p in ps] or [0]
        lab = lambda side: max([len(nets.get(p[1], nets.get(p[2], "")) or "")
                                for p in ps if side(p)] or [0]) * 1.1 + 2.54
        left = lab(lambda p: p[5] == 0)
        right = lab(lambda p: p[5] == 180)
        w = (max(xs) - min(xs)) + left + right + 10
        h = (max(ys) - min(ys)) + 10
        if self.x + w > self.width:
            self.newrow()
        X = snap(self.x + left - min(xs) + 2.54)
        Y = snap(self.y - min(-y for y in ys) + 5.08)
        self.x += w + 7.62
        self.rowh = max(self.rowh, h + 5)

        if not footprint:
            fp = [x for x in find(sd, "property") if uq(x[1]) == "Footprint"]
            footprint = uq(fp[0][2]) if fp else ""
        props = {"Reference": ref, "Value": value, "Footprint": footprint,
                 "Datasheet": "", **(fields or {})}
        top = Y - max(ys) - 2.54
        bot = Y - min(ys) + 3.81
        sym = ["symbol", ["lib_id", q(lib_id)],
               ["at", f"{X:.2f}", f"{Y:.2f}", "0"], ["unit", str(unit)],
               ["exclude_from_sim", "no"], ["in_bom", "yes"],
               ["on_board", "yes"], ["dnp", "yes" if dnp else "no"],
               ["uuid", uid()]]
        for i, (k, v) in enumerate(props.items()):
            hide = k not in ("Reference", "Value")
            py = top if k == "Reference" else bot + (0 if k == "Value" else 2.54 * i)
            eff = ["effects", ["font", ["size", "1.27", "1.27"]]]
            if hide:
                eff.append(["hide", "yes"])
            sym.append(["property", q(k), q(v),
                        ["at", f"{X:.2f}", f"{py:.2f}", "0"], eff])
        for p in pins(sd):
            if p[0] in (0, unit):
                sym.append(["pin", q(p[1]), ["uuid", uid()]])
        sym.append(["instances", ["project", q(self.project),
                                  ["path", q("/" + self.uuid),
                                   ["reference", q(ref)], ["unit", str(unit)]]]])
        self.items.append(sym)

        used = set()
        for (u, num, name, px, py, ang, etype, hidden) in ps:
            key = num if num in nets else name if name in nets else None
            if key is None:
                if etype in ("no_connect",) or hidden:
                    continue
                raise SystemExit(f"{ref} pin {num} ({name}) not assigned")
            used.add(key)
            net = nets[key]
            x, y = X + px, Y - py
            if net is None:
                self.items.append(["no_connect", ["at", f"{x:.2f}", f"{y:.2f}"],
                                   ["uuid", uid()]])
                continue
            a = (int(ang) + 180) % 360
            just = "left" if a in (0, 90) else "right"
            self.items.append(["label", q(net), ["at", f"{x:.2f}", f"{y:.2f}", str(a)],
                               ["fields_autoplaced", "yes"],
                               ["effects", ["font", ["size", "1.27", "1.27"]],
                                ["justify", just, "bottom"]], ["uuid", uid()]])
        bad = set(nets) - used
        if bad:
            raise SystemExit(f"{ref}: unknown pins {bad}")

    def pwr_flag(self, net):
        self.pwr += 1
        self.part("power:PWR_FLAG", f"#FLG0{self.pwr}", "PWR_FLAG", {"1": net})

    def save(self, path):
        doc = ["kicad_sch", ["version", "20231120"],
               ["generator", q("flashlight_kisch")],
               ["generator_version", q("1.0")], ["uuid", self.uuid],
               ["paper", q(self.paper)],
               ["title_block", ["title", q(self.title)],
                ["comment", "1", q("generated by hardware/gen_*.py — edit the script, not this file")]],
               ["lib_symbols"] + list(self.libsyms.values())]
        doc += self.items
        doc.append(["sheet_instances", ["path", q("/"), ["page", q("1")]]])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write(dump(doc) + "\n")


def show(lib_id):
    for p in pins(symdef(lib_id)):
        print(lib_id, p[:3], p[6], "hidden" if p[7] else "")
