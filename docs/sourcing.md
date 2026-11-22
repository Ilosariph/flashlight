# Sourcing — one-distributor check (2026-11-22)

Goal: as few shipments as possible (CH import: 8.1 % VAT + carrier fee per parcel).
PCB parts are assembled by JLC from LCSC anyway → this list is for the **bench
rig / hand-built prototype + off-PCB parts**.

**Winner: DigiKey** — only distributor found carrying the Chinese protection/charger
parts (DW01A, FS8205A, TP4057) *and* the Carclo optics and an ATtiny1616 board.
Mouser: has Carclo 10139, no DW01A/TP4057/FS8205A/Adafruit 1616 found.
RS / Farnell: Carclo yes; Chinese parts not checked (unlikely).

| Item | DigiKey | Notes |
|---|---|---|
| Carclo 10138 optic (20 mm, frosted narrow) | ✓ 10138 | lead time ~16 wk listed, check stock |
| Carclo 10139 optic (20 mm, frosted medium) | ✓ 1066-1007-ND | also Mouser |
| ATtiny1616 (bare) | ✓ (Microchip) | |
| ATtiny1616 dev board | ✓ Adafruit 5690 (1528-5690-ND) | for firmware v0 before own PCB |
| TLV9001IDBVR | ✓ (TI) | |
| DW01A | ✓ SLKor DW01A | |
| FS8205A | ✓ EVVO FS8205A — **SOT-23-6**, 20 V 6 A, 27 mΩ | ⚠️ plan says TSSOP-8 → check LCSC C16052 package before layout |
| TP4057 | ✓ UMW / EVVO, SOT-23-6 | |
| USB-C 6P power-only | ✓ **TE 2495702-1** (IPX7, CHF 1.32, 6k stock) / GCT USB4125-GF-A (not sealed) | 2495702-1 now in model |
| TMAG5273 (ring sensors) | ✓ TMAG5273C1QDBVR CHF 1.00, 17k stock; B2 variant CHF 0.95 | slide switches dropped |
| TMAG5273 breakout (bench) | ✓ Adafruit 6489 CHF 4.93, SparkFun 23880 CHF 6.21 | no fine soldering needed |
| Q1, Q4, R1, D1, F1, NTC, passives, AO3401A | ✓ standard parts | still to pick (plan §9) |
| UPDI adapter | ✓ any CP2102/FTDI USB-serial + 4.7 kΩ | |
| Kapton tape, thermal paste | ✓ | |

**Not at DigiKey/Mouser → Kaidomain (1 parcel):**
Nichia 519A 5000K R9080 on 10 mm DTP copper, 12 mm forward clicky + boot,
springs (head/tail), O-rings (or RS). 14500 cell → battery shop.

Option: let JLC also make the LED board (copper-core DTP MCPCB) and only buy
bare 519A LEDs — but bare 519A also not found at DigiKey/Mouser.

Sources: digikey.com product pages for 10138, 10139, 5690, DW01A, FS8205A,
TP4057, USB4125-GF-A, PCM13SMTR, EG1312AR; mouser.com 10139.

## Order files (checked on digikey.ch 2026-11-22)

- `orders/digikey_instock.csv` — bench/prototype parts, all in stock, ≈ CHF 44 excl. shipping/VAT
- `orders/digikey_backorder.csv` — Carclo 10139 (0 stock, ~16 wk). Not needed: 10138 alone is the chosen optic.
- `orders/digikey_extras.csv` — ≈ CHF 28 of useful later/bench parts to reach the CHF 100 free-shipping threshold.
- Upload via DigiKey *BOM Manager → Upload* or *Cart → Bulk add*, map column "Digi-Key Part Number" + "Quantity".
- ⚠️ NTC B57540G1103F000: bead diameter not confirmed (pocket in head is Ø1.8, param `ntc_hole`) → check datasheet, enlarge pocket if needed.

## Detent hardware

Misumi Europe **BPK3** ball plunger (short body, M3, L 5, ball Ø2, stroke 0.5,
load 1.0–2.0 N, hex socket B 1.5), 1 per ring → order 4 (spares). Replaces
ball + spring + set screw. Ball is EN 1.4125 (440C, magnetic) — sits at the tab,
opposite the magnet/sensors; check field offset on the bench.
Loctite 243 on the thread. Set screws no longer needed.

Misumi doesn't sell to private customers. **Chosen: AliExpress "Federkugelstößel" listing (4.9★, 800+ sold), M3×5 in 304 stainless (main) + M3×4 in 12.9 steel (only length offered; to compare), 10 pcs each ≈ CHF 1.9**; seller table: ball Ø1.5, protrusion 0.5, hex 1.5, load 6–10 N. 12.9: magnetic (moves with the ring and is far from the sensors → calibrated out, minor) and rusts (black oxide; exposed hex end only). Same short M3 hex-socket hex-socket stainless
ball plunger (BPK clone) on eBay/AliExpress ("Kugeldruckstück M3x5 Innensechskant
A2"), e.g. https://www.ebay.de/itm/388668408143 (~EUR 2). Ball Ø, protrusion
and stroke are not specified → measure, then set `ball_d`, `ball_out`,
`plunger_l`, `plunger_r` in flashlight.py. Branded M3 parts (Ganter GN 615.3,
Kipp K0316, Essentra) are 8–9 mm long → tab would be ~6.5 mm tall, no.
Loctite 243: Galaxus 5 ml CHF 8.30.

Magnets: supermagnete.ch, N48 disc Ø3 × 1 mm (S-03-01-N), axial magnetisation.
Optics: Kaidomain sells only its own generic TIRs, not Carclo → Carclo from DigiKey.
