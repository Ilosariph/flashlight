"""Render PNG previews of the model via openscad (STL import + colors).

python mech/render.py → mech/out/render/{exterior,section,head_section,top}.png
"""

import subprocess
from pathlib import Path

import cadquery as cq

import flashlight as fl

OUT = Path(__file__).parent / "out"
R = OUT / "render"


def export(parts, tag):
    d = R / tag
    d.mkdir(parents=True, exist_ok=True)
    for name, s in parts.items():
        cq.exporters.export(s, str(d / f"{name}.stl"), tolerance=0.02,
                            angularTolerance=0.1)
    return d


def scad(d, names, file):
    lines = ["rotate([0,90,0]) {"]  # lay the light along +X (front to the right)
    for n in names:
        r, g, b, a = fl.COLORS[n]
        lines.append(f'  color([{r},{g},{b},{a}]) import("{d}/{n}.stl");')
    lines.append("}")
    file.write_text("\n".join(lines))


def png(scadfile, png, camera, size=(1600, 700)):
    subprocess.run(["openscad", "-o", str(png), f"--imgsize={size[0]},{size[1]}",
                    f"--camera={camera}", "--projection=o",
                    "--colorscheme=Tomorrow", str(scadfile)],
                   check=True, capture_output=True)


def main():
    parts = fl.all_parts()
    names = list(parts)
    d = export(parts, "full")
    # section: keep model x >= cut (through SW1 knob); after rotate([0,90,0])
    # model x → -global z, so the cut face looks up (+Z) in openscad
    x1, *_ = fl.switch_layout()
    xcut = (x1[0] + x1[1]) / 2
    half = fl.box(-50, xcut, -50, 50, -200, 100)
    cut = {}
    for n, s in parts.items():
        try:
            c = s.cut(half)
            if c.val().isValid() and c.val().Volume() > 1e-6:
                cut[n] = c
        except Exception:
            pass
    ds = export(cut, "section")

    scad(d, names, R / "full.scad")
    scad(ds, list(cut), R / "section.scad")
    # rotate([0,90,0]): model z → global +x (front right), model y stays up
    zc = (fl.Z.front + fl.Z.tail) / 2
    zh = (fl.Z.front + fl.Z.head_rear) / 2
    png(R / "full.scad", R / "exterior.png", f"{zc},0,0,240,0,340,230")
    png(R / "section.scad", R / "section.png", f"{zc},0,0,0,0,0,250")
    png(R / "section.scad", R / "head_section.png", f"{zh},0,0,0,0,0,110",
        (1400, 900))
    png(R / "full.scad", R / "top.png", f"{zc},0,0,270,0,0,250")
    print("\n".join(str(p) for p in sorted(R.glob("*.png"))))


if __name__ == "__main__":
    main()
