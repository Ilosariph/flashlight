"""DIY 14500 EDC flashlight: parametric concept model (v0).

Coordinates: light points +Z, axis = Z. z = 0 is the LED shelf front face
(MCPCB seating plane). +Y = top of the light (slide switches), -Y = USB-C side.

Housing parts (CNC): head, bezel, body, tailcap.
Reference parts (bought / PCBs): everything in `components()`.

Threads are cosmetic (plain diameters); the thread spec lives in P and goes
on the JLCCNC drawing. Run `python mech/flashlight.py` → mech/out/.
"""

from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

E = 0.01  # overlap for clean boolean cuts


@dataclass(frozen=True)
class Params:
    # --- optic / LED (Carclo 20 mm, 519A on 10 mm DTP)
    optic_d: float = 20.0
    optic_h: float = 9.9
    optic_clear: float = 0.3  # bore clearance on diameter
    mcpcb_d: float = 10.0
    mcpcb_t: float = 1.5
    # --- head
    head_od: float = 23.5
    bezel_od: float = 21.5  # bezel ring thread major (M22x0.5 class)
    bezel_id: float = 17.6  # lip over optic rim
    bezel_t: float = 2.0
    shelf_t: float = 3.0
    cavity_d: float = 18.0  # spine PCB cavity, also driver stop shoulder
    cavity_len: float = 14.0
    driver_d: float = 19.0
    driver_t: float = 1.2
    driver_pocket_d: float = 19.2  # = head thread minor, driver goes in from rear
    flat_y: float = 10.5  # milled switch deck on head top
    # --- head <-> body joint: M20x0.75, body collar OD 20
    hb_thread: str = "M20x0.75"
    hb_major: float = 20.0
    hb_thread_len: float = 7.0
    hb_relief_len: float = 3.0  # plain bore behind thread, O-ring seals here
    hb_relief_d: float = 20.1
    # --- body / cell
    body_od: float = 18.0
    bore_d: float = 15.2  # 14500 (14.5) + anodize / kapton sleeve
    cell_d: float = 14.5
    cell_len: float = 51.5  # button top, worst case long (flat top ~50)
    head_spring_c: float = 3.0  # compressed length
    tail_spring_c: float = 3.0
    # --- body <-> tailcap: M18x0.75 external on body
    bt_thread: str = "M18x0.75"
    bt_thread_len: float = 7.0
    tc_seal_len: float = 2.7  # plain section in front of thread, internal O-ring
    # --- tailcap
    tc_od: float = 21.0
    tailpcb_d: float = 17.3
    tailpcb_t: float = 1.2
    usb_chamber_d: float = 16.0
    usb_chamber_len: float = 10.1
    clicky_d: float = 12.0
    clicky_len: float = 10.0
    boot_hole_d: float = 11.0
    tc_end_t: float = 2.0
    # --- slide switches (placeholders until parts are picked)
    sw1: tuple = (4.0, 13.0, 3.0)  # w(x), len(z), h(y)  SP3T
    sw2: tuple = (3.5, 8.5, 3.0)  # SPDT
    sw_gap: float = 1.0
    sw_pitch: float = 2.0  # actuator travel per position
    knob: float = 1.5
    knob_proud: float = 0.5  # above the flat
    spine_t: float = 1.0


P = Params()


# ---------------------------------------------------------------- stack (z)
class Z:
    optic0 = P.mcpcb_t
    optic1 = optic0 + P.optic_h
    front = optic1 + P.bezel_t  # head front face
    shelf1 = -P.shelf_t
    driver_front = shelf1 - P.cavity_len
    driver_rear = driver_front - P.driver_t  # = body front face
    hb_thread_end = driver_rear - P.hb_thread_len
    head_rear = hb_thread_end - P.hb_relief_len
    cell_top = driver_rear - P.head_spring_c
    cell_bot = cell_top - P.cell_len
    tailpcb_front = cell_bot - P.tail_spring_c  # = body rear face
    tailpcb_rear = tailpcb_front - P.tailpcb_t
    bt_thread_front = tailpcb_front + P.bt_thread_len
    tc_front = bt_thread_front + P.tc_seal_len
    chamber_rear = tailpcb_rear - P.usb_chamber_len
    clicky_rear = chamber_rear - P.clicky_len
    tail = clicky_rear - P.tc_end_t


def cyl(d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).circle(d / 2).extrude(z1 - z0)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(
        x1 - x0, y1 - y0, z1 - z0, centered=False
    ).translate((x0, y0, z0))


# ------------------------------------------------------- switch placement
def switch_layout():
    """x-ranges of SW1/SW2 bodies, y of PCB top, z centre."""
    w1, w2 = P.sw1[0], P.sw2[0]
    total = w1 + P.sw_gap + w2
    x1 = (-total / 2, -total / 2 + w1)
    x2 = (x1[1] + P.sw_gap, total / 2)
    # switch top must fit inside the cavity at its outer corners
    r = P.cavity_d / 2
    y_top = (r**2 - (total / 2) ** 2) ** 0.5 - 0.3
    y_base = y_top - P.sw1[2]
    zc = (Z.shelf1 + Z.driver_front) / 2
    return x1, x2, y_base, y_top, zc


def knob_slot(xr, length, travel, zc):
    xc = (xr[0] + xr[1]) / 2
    w = P.knob + 0.3
    L = P.knob + travel + 0.3
    return box(xc - w / 2, xc + w / 2, 0, P.head_od, zc - L / 2, zc + L / 2)


# ------------------------------------------------------------- housings
def head():
    h = cyl(P.head_od, Z.head_rear, Z.front)
    h = h.cut(cyl(P.bezel_od, Z.optic1, Z.front + E))
    h = h.cut(cyl(P.optic_d + P.optic_clear, 0, Z.optic1 + E))
    h = h.cut(cyl(P.cavity_d, Z.driver_front, Z.shelf1))
    h = h.cut(cyl(P.driver_pocket_d, Z.hb_thread_end, Z.driver_front + E))
    h = h.cut(cyl(P.hb_relief_d, Z.head_rear - E, Z.hb_thread_end + E))
    # switch deck: milled flat over the cavity
    h = h.cut(box(-P.head_od, P.head_od, P.flat_y, P.head_od,
                  Z.driver_front + 0.5, Z.shelf1 - 0.5))
    x1, x2, _, _, zc = switch_layout()
    h = h.cut(knob_slot(x1, P.sw1[1], 2 * P.sw_pitch, zc))
    h = h.cut(knob_slot(x2, P.sw2[1], P.sw_pitch, zc))
    # LED wire holes through shelf, just outside the MCPCB
    for x in (-5.8, 5.8):
        h = h.cut(cq.Workplane("XY").workplane(offset=Z.shelf1 - E)
                  .center(x, -2.0).circle(0.6).extrude(P.shelf_t + 2 * E))
    return h


def bezel():
    return cyl(P.bezel_od, Z.optic1, Z.front).cut(
        cyl(P.bezel_id, Z.optic1 - E, Z.front + E))


def body():
    collar = cyl(P.hb_major, Z.head_rear, Z.driver_rear)
    # O-ring groove (ID ~17.6 x 1.0 CS) in the relief section of the collar
    g0 = Z.head_rear + 0.8
    collar = collar.cut(cyl(P.hb_major + 1, g0, g0 + 1.2)
                        .cut(cyl(P.hb_major - 1.6, g0 - E, g0 + 1.2 + E)))
    tube = cyl(P.body_od, Z.tailpcb_front, Z.head_rear + E)
    return collar.union(tube).cut(
        cyl(P.bore_d, Z.tailpcb_front - E, Z.driver_rear + E))


def tailcap():
    t = cyl(P.tc_od, Z.tail, Z.tc_front)
    t = t.cut(cyl(P.body_od + 0.05, Z.tailpcb_front, Z.tc_front + E))
    # internal O-ring groove in the plain seal section
    g0 = Z.bt_thread_front + 0.6
    t = t.cut(cyl(P.body_od + 1.6, g0, g0 + 1.2))
    t = t.cut(cyl(P.tailpcb_d + 0.1, Z.tailpcb_rear, Z.tailpcb_front + E))
    t = t.cut(cyl(P.usb_chamber_d, Z.chamber_rear, Z.tailpcb_rear + E))
    t = t.cut(cyl(P.clicky_d + 0.3, Z.clicky_rear, Z.chamber_rear + E))
    t = t.cut(cyl(P.boot_hole_d, Z.tail - E, Z.clicky_rear + E))
    # USB-C opening on -Y side, connector long side along Z
    zc = (Z.chamber_rear + Z.tailpcb_rear) / 2
    slot = (cq.Workplane("XZ").workplane(offset=0)
            .center(0, zc).slot2D(9.2, 3.6, angle=90).extrude(P.tc_od))
    return t.cut(slot)


# ----------------------------------------------------------- components
def components():
    c = {}
    c["mcpcb"] = cyl(P.mcpcb_d, 0, P.mcpcb_t)
    c["led"] = box(-1.75, 1.75, -1.75, 1.75, P.mcpcb_t, P.mcpcb_t + 0.7).union(
        cyl(2.8, P.mcpcb_t + 0.7, P.mcpcb_t + 1.4))
    c["optic"] = (cq.Workplane("XY").workplane(offset=Z.optic0).circle(3.5)
                  .workplane(offset=P.optic_h - 2.5).circle(P.optic_d / 2).loft()
                  .union(cyl(P.optic_d, Z.optic1 - 2.5, Z.optic1))
                  .cut(cyl(6.0, Z.optic0 - E, Z.optic0 + 4.0)))
    c["driver"] = cyl(P.driver_d, Z.driver_rear, Z.driver_front)
    x1, x2, yb, yt, zc = switch_layout()
    pw = 2 * ((P.cavity_d / 2) ** 2 - yb**2) ** 0.5 - 1.0
    c["spine"] = box(-pw / 2, pw / 2, yb - P.spine_t, yb,
                     Z.driver_front, Z.shelf1 - 0.5)
    knob_top = P.flat_y + P.knob_proud
    for name, xr, (w, L, hh), pos in (("sw1", x1, P.sw1, -P.sw_pitch),
                                      ("sw2", x2, P.sw2, -P.sw_pitch / 2)):
        c[name] = box(xr[0], xr[1], yb, yt, zc - L / 2, zc + L / 2)
        xc = (xr[0] + xr[1]) / 2
        kz = zc + pos
        c[name + "_knob"] = box(xc - P.knob / 2, xc + P.knob / 2, yt, knob_top,
                                kz - P.knob / 2, kz + P.knob / 2)
    c["head_spring"] = cyl(6.0, Z.cell_top, Z.driver_rear).cut(
        cyl(4.8, Z.cell_top - E, Z.driver_rear + E))
    c["cell"] = cyl(P.cell_d, Z.cell_bot, Z.cell_top - 1.0).union(
        cyl(5.0, Z.cell_top - 1.0, Z.cell_top))
    c["tail_spring"] = cyl(8.0, Z.tailpcb_front, Z.cell_bot).cut(
        cyl(6.8, Z.tailpcb_front - E, Z.cell_bot + E))
    c["tail_pcb"] = cyl(P.tailpcb_d, Z.tailpcb_rear, Z.tailpcb_front)
    zc_usb = (Z.chamber_rear + Z.tailpcb_rear) / 2
    r_out = P.tc_od / 2 - 0.3
    c["usb_c"] = box(-1.63, 1.63, -r_out, -r_out + 7.35,
                     zc_usb - 4.47, zc_usb + 4.47)
    c["clicky"] = cyl(P.clicky_d, Z.clicky_rear, Z.chamber_rear)
    c["boot"] = cyl(P.boot_hole_d - 0.2, Z.tail - 1.5, Z.clicky_rear)
    return c


HOUSING = {"head": head, "bezel": bezel, "body": body, "tailcap": tailcap}

COLORS = {  # rgba, used for STEP assembly and renders
    "head": (0.55, 0.58, 0.62, 1), "bezel": (0.45, 0.47, 0.5, 1),
    "body": (0.62, 0.65, 0.68, 1), "tailcap": (0.55, 0.58, 0.62, 1),
    "mcpcb": (0.85, 0.5, 0.25, 1), "led": (1.0, 0.9, 0.4, 1),
    "optic": (0.8, 0.9, 1.0, 0.45), "driver": (0.1, 0.45, 0.2, 1),
    "spine": (0.1, 0.45, 0.2, 1), "sw1": (0.15, 0.15, 0.15, 1),
    "sw2": (0.15, 0.15, 0.15, 1), "sw1_knob": (0.85, 0.35, 0.2, 1),
    "sw2_knob": (0.85, 0.35, 0.2, 1), "head_spring": (0.8, 0.7, 0.3, 1),
    "cell": (0.2, 0.35, 0.75, 1), "tail_spring": (0.8, 0.7, 0.3, 1),
    "tail_pcb": (0.1, 0.45, 0.2, 1), "usb_c": (0.75, 0.75, 0.78, 1),
    "clicky": (0.1, 0.1, 0.1, 1), "boot": (0.2, 0.2, 0.2, 1),
}


def all_parts():
    parts = {k: f() for k, f in HOUSING.items()}
    parts.update(components())
    return parts


def summary():
    x1, x2, yb, yt, _ = switch_layout()
    return "\n".join([
        f"overall length   {Z.front - (Z.tail - 1.5):6.1f} mm  (incl. boot)",
        f"head  OD {P.head_od}  length {Z.front - Z.head_rear:5.1f} mm",
        f"body  OD {P.body_od}  exposed {Z.head_rear - Z.tc_front:5.1f} mm",
        f"tail  OD {P.tc_od}  length {Z.tc_front - Z.tail:5.1f} mm",
        f"cell space {Z.cell_top - Z.cell_bot:.1f} mm + springs "
        f"(button {P.cell_len}, flat top needs ~1.5 mm extra spring travel)",
        f"switch bodies y {yb:.2f}..{yt:.2f}, knob protrudes to {P.flat_y + P.knob_proud}",
        f"threads: head-body {P.hb_thread}, body-tail {P.bt_thread}, "
        f"body wall at tail thread root ~{(17.2 - P.bore_d) / 2:.2f} mm",
    ])


if __name__ == "__main__":
    out = Path(__file__).parent / "out"
    (out / "stl").mkdir(parents=True, exist_ok=True)
    parts = all_parts()
    asm = cq.Assembly(name="flashlight")
    for name, shape in parts.items():
        cq.exporters.export(shape, str(out / "stl" / f"{name}.stl"),
                            tolerance=0.02, angularTolerance=0.1)
        asm.add(shape, name=name, color=cq.Color(*COLORS[name]))
        if name in HOUSING:
            cq.exporters.export(shape, str(out / f"{name}.step"))
    asm.export(str(out / "flashlight_assembly.step"))
    print(summary())
