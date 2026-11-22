"""DIY 14500 EDC flashlight: parametric concept model (v0).

Coordinates: light points +Z, axis = Z. z = 0 is the LED shelf front face
(MCPCB seating plane). +Y = top of the light (ring tabs), -Y = USB-C side,
ring magnets and Hall sensors.

Housing parts (CNC): head, bezel (cup, holds optic, retains rings), ring1
(output level L/H/T, rear), ring2 (mode N/S, front), spacer (keyed sheet-metal
washer between the rings), body, tailcap.
Reference parts (bought / PCBs): everything in `components()`.

Threads are cosmetic (plain diameters); the thread spec lives in P and goes
on the JLCCNC drawing. Run `python mech/flashlight.py` → mech/out/.
"""

import math
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
    # bezel cup: screws onto the head stub (M21x0.75), clamps optic, retains rings
    bezel_od: float = 24.0
    bezel_id: float = 17.6  # lip over optic rim
    bezel_t: float = 2.0
    optic_gasket: float = 0.5  # thin O-ring / gasket between optic and lip
    stub_thread: str = "M21x0.75"
    stub_len: float = 4.0  # thread engagement, also = bezel rear skirt
    seat_d: float = 21.0  # ring seat on head, = stub thread major
    shelf_t: float = 6.0  # solid LED shelf; grows into cavity space not needed by spine
    ntc_hole: tuple = (1.8, 4.0)  # Ø, depth: leaded bead NTC glued in, behind LED
    # --- position marks, CNC-engraved (0.5 mm cutter: DejaVu Bold 3.2 → stem 0.6)
    # order follows ring*_pos; +angle offset = left seen from top, beam away
    mark_h: float = 3.2
    mark_depth: float = 0.25
    ring1_marks: tuple = ("T", "H", "L")  # level, on head shoulder behind ring1
    ring2_marks: tuple = ("S", "N")  # mode, on bezel cup in front of ring2
    # --- selector rings (magnet + ball detent in the tab)
    ring_od: float = 26.0
    ring_id: float = 21.2
    ring_w: float = 6.5
    ring_gap: float = 0.2  # to bezel / head shoulder
    # spacer washer between the rings, keyed to a flat on the seat → rings
    # only rub on a stationary part, never drag each other
    spacer_t: float = 0.5
    spacer_od: float = 24.6
    spacer_gap: float = 0.15
    key_depth: float = 0.4  # seat flat at +X, only under the spacer
    ring_chamfer: float = 0.4
    tab_h: float = 2.0  # tab above ring OD (holds the 4 mm ball plunger)
    tab_w: float = 5.5  # ring 2: -1.0
    # detent: generic M3x4 hex-socket ball plunger (AliExpress, 304 stainless,
    # ball Ø1.5 protrudes 0.5, hex 1.5, 6-10 N) screwed in from outside, bottoms
    # on a shoulder at plunger_r
    plunger_m: float = 3.0
    plunger_tap: float = 2.5
    plunger_l: float = 4.0
    ball_d: float = 1.5
    ball_out: float = 0.5
    plunger_r: float = 10.75  # plunger inner end; detent preload 0.05, land 0.35
    dimple_d: float = 1.2  # ball sits on the edge → sinks ~0.30
    magnet_d: float = 3.0  # disc, radial: supermagnete S-03-01-N (N48 Ø3×1)
    magnet_t: float = 1.0
    magnet_angle: float = 270.0  # bottom, over the sensors
    tab_angle: float = 90.0  # top, under the thumb
    ring1_pos: tuple = (-40.0, 0.0, 40.0)  # level detents (turbo / high / low)
    ring2_pos: tuple = (-25.0, 25.0)  # mode detents (strobe / normal)
    cavity_d: float = 18.0  # spine PCB cavity, also driver stop shoulder
    cavity_len: float = 11.0
    driver_d: float = 19.0
    driver_t: float = 1.2
    driver_pocket_d: float = 19.2  # = head thread minor, driver goes in from rear
    # --- head <-> body joint: M20x0.75, body collar OD 20
    hb_thread: str = "M20x1"
    hb_major: float = 20.0
    hb_thread_len: float = 6.0
    hb_relief_len: float = 3.0  # plain bore behind thread, O-ring 17x1.5 seals here
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
    bt_thread_len: float = 5.0
    tc_seal_len: float = 2.4  # plain section in front of thread, internal O-ring 18x1
    # --- tailcap
    tc_od: float = 21.5
    tring_d: float = 17.0  # brass tail retaining ring M17x0.5, BODY contact
    tring_id: float = 13.0
    tring_t: float = 1.5
    tailpcb_d: float = 16.0
    tailpcb_t: float = 1.0
    # USB-C (TE 2495702-1, IPX7, power only) SMD on the tail PCB rear side,
    # lying flat, port facing -Y, overhangs PCB edge. Dims placeholder until
    # TE drawing is read.
    usb_w: float = 9.0
    usb_h: float = 3.4
    usb_depth: float = 7.6
    usb_flat_y: float = -9.9  # milled flat for the plug overmold
    usb_chamber_d: float = 14.0
    usb_chamber_len: float = 3.8  # behind PCB, holds connector + charger parts
    clicky_d: float = 12.0
    clicky_len: float = 10.0
    boot_hole_d: float = 11.0
    tc_end_t: float = 2.0
    # --- spine PCB with 2x TMAG5273 (SOT-23-6) on its underside
    spine_t: float = 1.0
    spine_y: float = -4.0  # top face of spine (chord), sensors hang below
    sensor: tuple = (2.9, 1.6, 1.1)  # SOT-23-6 l(x), w(z), h(y)


P = Params()


# ---------------------------------------------------------------- stack (z)
class Z:
    optic0 = P.mcpcb_t
    optic1 = optic0 + P.optic_h
    front = optic1 + P.optic_gasket + P.bezel_t  # bezel front face
    stub_rear = -P.stub_len  # bezel rear face
    ring2_front = stub_rear - P.ring_gap  # mode ring, front
    ring2_rear = ring2_front - P.ring_w
    spacer_front = ring2_rear - P.spacer_gap
    spacer_rear = spacer_front - P.spacer_t
    ring1_front = spacer_rear - P.spacer_gap  # level ring, rear
    ring1_rear = ring1_front - P.ring_w
    shoulder = ring1_rear - P.ring_gap  # head full OD from here back
    shelf1 = -P.shelf_t
    driver_front = shelf1 - P.cavity_len
    driver_rear = driver_front - P.driver_t  # = body front face
    hb_thread_end = driver_rear - P.hb_thread_len
    head_rear = hb_thread_end - P.hb_relief_len
    cell_top = driver_rear - P.head_spring_c
    cell_bot = cell_top - P.cell_len
    tailpcb_front = cell_bot - P.tail_spring_c
    body_rear = tailpcb_front + P.tring_t  # body end face presses the ring
    tailpcb_rear = tailpcb_front - P.tailpcb_t
    bt_thread_front = body_rear + P.bt_thread_len
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


# ------------------------------------------------------------- helpers
def radial_cyl(d, r0, r1, angle, z):
    """Cylinder of diameter d along the radius at `angle` (deg from +X)."""
    a = math.radians(angle)
    u = cq.Vector(math.cos(a), math.sin(a), 0)
    return cq.Workplane("XY").add(
        cq.Solid.makeCylinder(d / 2, r1 - r0, u * r0 + cq.Vector(0, 0, z), u))


def engrave(shape, text, r, angle, z):
    """Cut `text` into a cylinder surface of radius r; reads with +Z up."""
    a = math.radians(angle)
    n = cq.Vector(math.cos(a), math.sin(a), 0)
    plane = cq.Plane(origin=n * (r + 0.5) + cq.Vector(0, 0, z),
                     xDir=cq.Vector(-n.y, n.x, 0), normal=n)
    t = cq.Workplane(plane).text(text, P.mark_h, -(0.5 + P.mark_depth),
                                 font="DejaVu Sans", kind="bold",
                                 halign="center", valign="center", combine=False)
    return shape.cut(t)


def ring_z(n):
    return ((Z.ring1_rear, Z.ring1_front) if n == 1
            else (Z.ring2_rear, Z.ring2_front))


# ------------------------------------------------------------- housings
def head():
    h = cyl(P.head_od, Z.head_rear, Z.shoulder).union(
        cyl(P.seat_d, Z.shoulder - E, 0))  # ring seat + bezel stub (thread)
    # O-ring 19x1 groove on the stub, seals against the bezel bore
    h = h.cut(cyl(P.seat_d + 1, -1.4, -0.3).cut(cyl(19.4, -1.5, -0.2)))
    h = h.cut(cyl(P.cavity_d, Z.driver_front, Z.shelf1))
    h = h.cut(cyl(P.driver_pocket_d, Z.hb_thread_end, Z.driver_front + E))
    h = h.cut(cyl(P.hb_relief_d, Z.head_rear - E, Z.hb_thread_end + E))
    # detent dimples in the seat, one per ring position, under the tab ball
    for n, pos in ((1, P.ring1_pos), (2, P.ring2_pos)):
        zc = sum(ring_z(n)) / 2
        for a in pos:
            h = h.cut(radial_cyl(P.dimple_d, P.seat_d / 2 - 0.6, P.seat_d / 2 + E,
                                 P.tab_angle + a, zc))
    # level ring (ring1) marks on the shoulder behind it
    for a, txt in zip(P.ring1_pos, P.ring1_marks):
        h = engrave(h, txt, P.head_od / 2, P.tab_angle - a, Z.shoulder - 1.8)
    # key flat for the spacer washer
    h = h.cut(box(P.seat_d / 2 - P.key_depth, P.seat_d, -P.seat_d, P.seat_d,
                  Z.spacer_rear - 0.3, Z.spacer_front + 0.3))
    # NTC pocket in the shelf rear face, straight behind the LED
    d, depth = P.ntc_hole
    h = h.cut(cyl(d, Z.shelf1 - E, Z.shelf1 + depth))
    # LED wire holes through shelf, just outside the MCPCB
    for x in (-5.8, 5.8):
        h = h.cut(cq.Workplane("XY").workplane(offset=Z.shelf1 - E)
                  .center(x, -2.0).circle(0.6).extrude(P.shelf_t + 2 * E))
    return h


def bezel():
    b = cyl(P.bezel_od, Z.stub_rear, Z.front)
    b = b.cut(cyl(P.bezel_id, Z.optic1, Z.front + E))  # lip
    b = b.cut(cyl(P.optic_d + P.optic_clear, 0, Z.optic1 + P.optic_gasket))
    # internal thread section, bottoms on the stub front face at z = 0
    b = b.cut(cyl(P.seat_d, Z.stub_rear - E, 0 + E))
    # mode ring (ring2) marks, just in front of it
    for a, txt in zip(P.ring2_pos, P.ring2_marks):
        b = engrave(b, txt, P.bezel_od / 2, P.tab_angle - a, Z.stub_rear + 1.8)
    return b


def spacer():
    s = cyl(P.spacer_od, Z.spacer_rear, Z.spacer_front).cut(
        cyl(P.seat_d + 0.1, Z.spacer_rear - E, Z.spacer_front + E))
    # D-flat matching the seat key (0.1 clearance)
    return s.union(box(P.seat_d / 2 - P.key_depth + 0.1, P.seat_d / 2 + 0.2,
                       -4, 4, Z.spacer_rear, Z.spacer_front)
                   .intersect(cyl(P.seat_d + 0.2, Z.spacer_rear, Z.spacer_front)))


def ring(n):
    z0, z1 = ring_z(n)
    zc = (z0 + z1) / 2
    r = cyl(P.ring_od, z0, z1).edges("%CIRCLE").chamfer(P.ring_chamfer)
    # grip flutes around the circumference, skipped near the tab
    for i in range(16):
        a = i * 360 / 16
        if abs((a - P.tab_angle + 180) % 360 - 180) < 30:
            continue
        ar = math.radians(a)
        r = r.cut(cq.Workplane("XY").workplane(offset=z0 - E)
                  .center((P.ring_od / 2 + 1.0) * math.cos(ar),
                          (P.ring_od / 2 + 1.0) * math.sin(ar))
                  .circle(1.5).extrude(P.ring_w + 2 * E))
    # tab: glove lug, ring 2 narrower so they're told apart by feel
    tw = P.tab_w if n == 1 else P.tab_w - 1.0
    tab = (box(-tw / 2, tw / 2, P.ring_od / 2 - 1.0,
               P.ring_od / 2 + P.tab_h, z0, z1)
           .edges("|Z").fillet(0.8)
           .rotate((0, 0, 0), (0, 0, 1), P.tab_angle - 90))
    r = r.union(tab)
    r = r.cut(cyl(P.ring_id, z0 - E, z1 + E))
    # detent: Ø ball+0.2 through to the shoulder, M3 tapped above it
    r = r.cut(radial_cyl(P.ball_d + 0.2, P.ring_id / 2 - E,
                         P.plunger_r + E, P.tab_angle, zc))
    r = r.cut(radial_cyl(P.plunger_tap, P.plunger_r,
                         P.ring_od / 2 + P.tab_h + E, P.tab_angle, zc))
    # magnet pocket from the inside
    return r.cut(radial_cyl(P.magnet_d + 0.05, P.ring_id / 2 - E,
                            P.ring_id / 2 + P.magnet_t + 0.1, P.magnet_angle, zc))


def body():
    collar = cyl(P.hb_major, Z.head_rear, Z.driver_rear)
    # O-ring groove (ID ~17.6 x 1.0 CS) in the relief section of the collar
    # O-ring 17x1.5 groove: Ø17.8 x 2.0 wide, seals against head relief bore
    g0 = Z.head_rear + 0.5
    collar = collar.cut(cyl(P.hb_major + 1, g0, g0 + 2.0)
                        .cut(cyl(17.8, g0 - E, g0 + 2.0 + E)))
    tube = cyl(P.body_od, Z.body_rear, Z.head_rear + E)
    return collar.union(tube).cut(
        cyl(P.bore_d, Z.body_rear - E, Z.driver_rear + E))


def tailcap():
    t = cyl(P.tc_od, Z.tail, Z.tc_front)
    t = t.cut(cyl(P.body_od + 0.05, Z.body_rear, Z.tc_front + E))
    # internal O-ring groove (18x1) in the plain seal section, Ø19.5 x 1.4
    g0 = Z.bt_thread_front + 0.5
    t = t.cut(cyl(19.5, g0, g0 + 1.4))
    t = t.cut(cyl(P.tring_d, Z.tailpcb_front, Z.body_rear + E))  # M17x0.5 ring
    t = t.cut(cyl(P.tailpcb_d + 0.1, Z.tailpcb_rear, Z.tailpcb_front + E))
    t = t.cut(cyl(P.usb_chamber_d, Z.chamber_rear, Z.tailpcb_rear + E))
    t = t.cut(cyl(P.clicky_d + 0.3, Z.clicky_rear, Z.chamber_rear + E))
    t = t.cut(cyl(P.boot_hole_d, Z.tail - E, Z.clicky_rear + E))
    # USB-C: pocket for the connector body + port opening + flat for the plug
    z0, z1 = usb_z()
    t = t.cut(box(-P.usb_w / 2 - 0.2, P.usb_w / 2 + 0.2, -P.tc_od, 0,
                  z0 - 0.2, z1 + 0.2))
    t = t.cut(box(-P.tc_od, P.tc_od, -P.tc_od, P.usb_flat_y, z0 - 2.5, z1 + 2.5))
    return t


def usb_z():
    """Connector on the PCB rear face (mid-mount would hit ring/spring)."""
    return Z.tailpcb_rear - P.usb_h, Z.tailpcb_rear


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
    yb = P.spine_y - P.spine_t
    pw = 2 * ((P.cavity_d / 2) ** 2 - yb**2) ** 0.5 - 1.0
    c["spine"] = box(-pw / 2, pw / 2, yb, P.spine_y,
                     Z.driver_front, Z.shelf1 - 0.5)
    sl, sw, sh = P.sensor
    mags = None
    balls = None
    for n in (1, 2):
        zc = sum(ring_z(n)) / 2
        c[f"hall{n}"] = box(-sl / 2, sl / 2, yb - sh, yb, zc - sw / 2, zc + sw / 2)
        m = radial_cyl(P.magnet_d, P.ring_id / 2 + 0.05,
                       P.ring_id / 2 + 0.05 + P.magnet_t, P.magnet_angle, zc)
        mags = m if mags is None else mags.union(m)
        a = math.radians(P.tab_angle)
        sink = P.ball_d / 2 - ((P.ball_d / 2) ** 2 - (P.dimple_d / 2) ** 2) ** 0.5
        rb = P.seat_d / 2 - sink + P.ball_d / 2
        pl = radial_cyl(P.plunger_m, P.plunger_r, P.plunger_r + P.plunger_l,
                        P.tab_angle, zc)
        plungers = pl if n == 1 else plungers.union(pl)
        b = (cq.Workplane("XY").sphere(P.ball_d / 2)
             .translate((rb * math.cos(a), rb * math.sin(a), zc)))
        balls = b if balls is None else balls.union(b)
    c["ntc"] = cyl(1.5, Z.shelf1 + P.ntc_hole[1] - 1.6, Z.shelf1 + P.ntc_hole[1] - 0.1)
    c["magnets"] = mags
    c["balls"] = balls
    c["plungers"] = plungers
    c["head_spring"] = cyl(6.0, Z.cell_top, Z.driver_rear).cut(
        cyl(4.8, Z.cell_top - E, Z.driver_rear + E))
    c["cell"] = cyl(P.cell_d, Z.cell_bot, Z.cell_top - 1.0).union(
        cyl(5.0, Z.cell_top - 1.0, Z.cell_top))
    c["tail_spring"] = cyl(8.0, Z.tailpcb_front, Z.cell_bot).cut(
        cyl(6.8, Z.tailpcb_front - E, Z.cell_bot + E))
    c["tail_ring"] = cyl(P.tring_d, Z.tailpcb_front, Z.body_rear).cut(
        cyl(P.tring_id, Z.tailpcb_front - E, Z.body_rear + E))
    z0, z1 = usb_z()
    c["tail_pcb"] = cyl(P.tailpcb_d, Z.tailpcb_rear, Z.tailpcb_front)
    c["usb_c"] = box(-P.usb_w / 2, P.usb_w / 2, P.usb_flat_y - 0.1,
                     P.usb_flat_y - 0.1 + P.usb_depth, z0, z1)
    c["clicky"] = cyl(P.clicky_d, Z.clicky_rear, Z.chamber_rear)
    c["boot"] = cyl(P.boot_hole_d - 0.2, Z.tail - 1.5, Z.clicky_rear)
    return c


HOUSING = {"head": head, "bezel": bezel, "ring1": lambda: ring(1),
           "ring2": lambda: ring(2), "spacer": spacer, "body": body,
           "tailcap": tailcap}

COLORS = {  # rgba, used for STEP assembly and renders
    "head": (0.55, 0.58, 0.62, 1), "bezel": (0.45, 0.47, 0.5, 1),
    "body": (0.62, 0.65, 0.68, 1), "tailcap": (0.55, 0.58, 0.62, 1),
    "mcpcb": (0.85, 0.5, 0.25, 1), "led": (1.0, 0.9, 0.4, 1),
    "optic": (0.8, 0.9, 1.0, 0.45), "driver": (0.1, 0.45, 0.2, 1),
    "spine": (0.1, 0.45, 0.2, 1), "ring1": (0.75, 0.38, 0.22, 1),
    "ring2": (0.4, 0.42, 0.46, 1), "spacer": (0.8, 0.8, 0.82, 1), "hall1": (0.1, 0.1, 0.1, 1),
    "hall2": (0.1, 0.1, 0.1, 1), "magnets": (0.7, 0.7, 0.75, 1),
    "balls": (0.9, 0.9, 0.9, 1), "plungers": (0.6, 0.6, 0.65, 1), "ntc": (0.2, 0.2, 0.6, 1), "head_spring": (0.8, 0.7, 0.3, 1),
    "cell": (0.2, 0.35, 0.75, 1), "tail_spring": (0.8, 0.7, 0.3, 1),
    "tail_pcb": (0.1, 0.45, 0.2, 1), "tail_ring": (0.8, 0.65, 0.3, 1), "usb_c": (0.75, 0.75, 0.78, 1),
    "clicky": (0.1, 0.1, 0.1, 1), "boot": (0.2, 0.2, 0.2, 1),
}


def all_parts():
    parts = {k: f() for k, f in HOUSING.items()}
    parts.update(components())
    return parts


def summary():
    yb = P.spine_y - P.spine_t - P.sensor[2]
    gap = (P.ring_id / 2 + 0.05) - abs(yb)
    return "\n".join([
        f"overall length   {Z.front - (Z.tail - 1.5):6.1f} mm  (incl. boot)",
        f"head  OD {P.head_od} / rings {P.ring_od} (+tab {P.tab_h})  "
        f"length incl. bezel {Z.front - Z.head_rear:5.1f} mm",
        f"body  OD {P.body_od}  exposed {Z.head_rear - Z.tc_front:5.1f} mm",
        f"tail  OD {P.tc_od}  length {Z.tc_front - Z.tail:5.1f} mm",
        f"cell space {Z.cell_top - Z.cell_bot:.1f} mm + springs "
        f"(button {P.cell_len}, flat top needs ~1.5 mm extra spring travel)",
        f"sensor face to magnet face {gap:.1f} mm (seat wall "
        f"{(P.seat_d - P.cavity_d) / 2:.1f} mm), rings z "
        f"{Z.ring1_rear:.1f}..{Z.ring2_front:.1f}",
        f"threads: head-body {P.hb_thread} x{P.hb_thread_len}, body-tail "
        f"{P.bt_thread} x{P.bt_thread_len}, bezel {P.stub_thread} x{P.stub_len}, tail ring M17x0.5",
        f"body wall at tail thread root ~{(17.08 - P.bore_d) / 2:.2f} mm, "
        f"tailcap wall at O-ring groove {(P.tc_od - 19.5) / 2:.2f} mm",
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
