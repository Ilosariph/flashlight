"""Project footprints → flashlight.pretty (+ fp-lib-table in each board dir).

USB_C_TE_2495702-1  TE customer drawing 2495702 rev A, sheet 2 "Recommend PCB
                    layout (component side)". Origin = midpoint of the Ø0.95
                    peg holes, +Y = towards the mating face ("product edge").
SpineJoint_*        90° solder joint driver ↔ spine: 5 signal pads (1.5 mm
                    pitch) along the spine's top face + 2 anchor pads (BODY)
                    along its bottom face. Origin = spine top-face line /
                    spine end edge, row centred on X. Check pin order at layout:
                    if the spine sits on the driver's B side, X mirrors.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "flashlight.pretty")


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


class Fp:
    def __init__(self, name, descr, smd=True):
        self.name, self.items = name, []
        self.head = (f'(footprint "{name}"\n  (version 20240108)\n  (generator "gen_footprints")\n'
                     f'  (layer "F.Cu")\n  (descr "{descr}")\n'
                     f'  (attr {"smd" if smd else "through_hole"})\n')

    def text(self, kind, txt, x, y, layer):
        self.items.append(f'  (fp_text {kind} "{txt}" (at {f(x)} {f(y)}) (layer "{layer}")\n'
                          f'    (effects (font (size 0.8 0.8) (thickness 0.12))))')

    def rect(self, x1, y1, x2, y2, layer, w=0.1):
        self.items.append(f'  (fp_rect (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                          f'(stroke (width {w}) (type solid)) (fill none) (layer "{layer}"))')

    def line(self, x1, y1, x2, y2, layer, w=0.1):
        self.items.append(f'  (fp_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                          f'(stroke (width {w}) (type solid)) (layer "{layer}"))')

    def smd(self, num, x, y, w, h, side="F", shape="rect"):
        L = f'"{side}.Cu" "{side}.Paste" "{side}.Mask"'
        self.items.append(f'  (pad "{num}" smd {shape} (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) (layers {L}))')

    def slot(self, num, x, y, dw, dh, pw, ph):
        self.items.append(f'  (pad "{num}" thru_hole oval (at {f(x)} {f(y)}) (size {f(pw)} {f(ph)}) '
                          f'(drill oval {f(dw)} {f(dh)}) (layers "*.Cu" "*.Mask"))')

    def npth(self, x, y, d):
        self.items.append(f'  (pad "" np_thru_hole circle (at {f(x)} {f(y)}) (size {f(d)} {f(d)}) '
                          f'(drill {f(d)}) (layers "*.Cu" "*.Mask"))')

    def save(self):
        os.makedirs(LIB, exist_ok=True)
        with open(os.path.join(LIB, self.name + ".kicad_mod"), "w") as fh:
            fh.write(self.head + "\n".join(self.items) + "\n)\n")


def usb_c_te_2495702():
    p = Fp("USB_C_TE_2495702-1",
           "TE 2495702-1 USB-C 6P power-only, IPX7, offset/overhang SMT, PCB 1.0-1.2 mm. "
           "Layout per TE drawing 2495702 sheet 2", smd=False)
    # signal pads: drawing order B12 B9 A5 B5 A9 A12 (= C1..C6), top edge 2.70
    # behind the peg-hole line, length 1.65 (scaled from drawing, ±0.05)
    y_top, plen = -2.70, 1.65
    yc = y_top + plen / 2
    for num, x, w in (("B12", -2.75, 0.80), ("B9", -1.52, 0.76), ("A5", -0.50, 0.70),
                      ("B5", 0.50, 0.70), ("A9", 1.52, 0.76), ("A12", 2.75, 0.80)):
        p.smd(num, x, yc, w, plen)
    for x in (-3.25, 3.25):
        p.npth(x, 0, 0.95)
    # shell legs: 4 plated slots 0.50 x 1.10 at x ±9.79/2, 6.10 and 3.10
    # behind the product edge (edge = +6.00 from peg line)
    for x in (-4.895, 4.895):
        for y in (-0.10, 2.90):
            p.slot("SH", x, y, 0.50, 1.10, 0.90, 1.50)
    edge = 6.00
    p.line(-4.97, edge, 4.97, edge, "F.Fab")          # mating face
    p.rect(-4.97, edge - 8.60, 4.97, edge, "F.Fab")   # shell 9.94 x 8.60
    p.rect(-5.32, edge - 1.50, 5.32, edge, "F.Fab")   # O-ring 10.64, 1.5 thick
    # PCB edge: TE wants 0.10-0.15 between PCB and the O-ring → 1.65 behind face
    p.line(-6, edge - 1.65, 6, edge - 1.65, "Dwgs.User", 0.05)
    p.text("user", "PCB edge", 0, edge - 1.65 - 0.6, "Dwgs.User")
    p.rect(-5.6, -3.0, 5.6, edge + 0.3, "F.CrtYd", 0.05)
    p.line(-5.2, -2.95, 5.2, -2.95, "F.SilkS", 0.12)
    p.text("reference", "REF**", 0, -3.8, "F.SilkS")
    p.text("value", "USB_C_TE_2495702-1", 0, 1.4, "F.Fab")
    p.save()


PITCH, PW, PL = 1.5, 0.9, 1.6          # signal pads
ANCHOR_X, AW, AL = 5.0, 2.0, 1.2       # BODY anchor pads
SPINE_T = 1.0


def spine_joint_driver():
    """On the driver face. Spine top face at y=0, spine body in y 0..+1."""
    p = Fp("SpineJoint_1x05_P1.5_Driver",
           "Driver side of the 90 deg spine joint: 5 pads above the spine top face, "
           "2 BODY anchors below its bottom face (spine 1.0 mm)")
    for i in range(5):
        p.smd(str(i + 1), (i - 2) * PITCH, -PL / 2, PW, PL)
    for x in (-ANCHOR_X, ANCHOR_X):
        p.smd("5", x, SPINE_T + AL / 2, AW, AL)
    hw = ANCHOR_X + AW / 2
    p.rect(-hw - 0.5, 0, hw + 0.5, SPINE_T, "F.Fab")   # spine cross-section
    p.text("user", "spine", 0, SPINE_T / 2, "F.Fab")
    p.rect(-hw - 0.3, -PL - 0.3, hw + 0.3, SPINE_T + AL + 0.3, "F.CrtYd", 0.05)
    p.text("reference", "REF**", 0, -PL - 0.9, "F.SilkS")
    p.text("value", "SpineJoint_Driver", 0, SPINE_T + AL + 1, "F.Fab")
    p.save()


def spine_joint_spine():
    """At the spine's end edge (y=0 = board edge, board towards +y).
    Signal pads on F (top face, towards driver pads), anchors on B."""
    p = Fp("SpineJoint_1x05_P1.5_SpineEdge",
           "Spine side of the 90 deg joint: 5 edge pads on top, 2 BODY anchors on bottom; "
           "pads run to the board edge for the solder fillet")
    for i in range(5):
        p.smd(str(i + 1), (i - 2) * PITCH, PL / 2, PW, PL)
    for x in (-ANCHOR_X, ANCHOR_X):
        p.smd("5", x, AL / 2, AW, AL, side="B")
    hw = ANCHOR_X + AW / 2
    p.line(-hw - 0.5, 0, hw + 0.5, 0, "Dwgs.User", 0.05)
    p.text("user", "board edge", 0, -0.6, "Dwgs.User")
    p.rect(-hw - 0.3, 0, hw + 0.3, max(PL, AL) + 0.3, "F.CrtYd", 0.05)
    p.text("reference", "REF**", 0, PL + 1.0, "F.SilkS")
    p.text("value", "SpineJoint_SpineEdge", 0, PL + 2.0, "F.Fab")
    p.save()


def lib_tables():
    for b in ("driver", "spine", "tail"):
        with open(os.path.join(HERE, b, "fp-lib-table"), "w") as fh:
            fh.write('(fp_lib_table\n  (version 7)\n  (lib (name "flashlight")(type "KiCad")'
                     '(uri "${KIPRJMOD}/../flashlight.pretty")(options "")(descr "project footprints"))\n)\n')


if __name__ == "__main__":
    usb_c_te_2495702()
    spine_joint_driver()
    spine_joint_spine()
    lib_tables()
