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
- `orders/digikey_backorder.csv` — Carclo 10139 (0 stock, ~16 wk lead). Order separately or skip.
- Upload via DigiKey *BOM Manager → Upload* or *Cart → Bulk add*, map column "Digi-Key Part Number" + "Quantity".
- ⚠️ NTC B57540G1103F000: bead diameter not confirmed (pocket in head is Ø1.8, param `ntc_hole`) → check datasheet, enlarge pocket if needed.

## Detent hardware (not at DigiKey)

Per ring: 1 ball Ø1.5, 1 spring (OD ≤1.4, wire ~0.15–0.2, free length ~3 mm), 1 set screw M2×2.
M2 tap drill = Ø1.6 = ball/spring bore → everything goes in through the threaded hole.

| What | Where | Notes |
|---|---|---|
| All three, one shop | **Misumi Europe** (ships to CH) | balls, configurable mini compression springs, set screws |
| Set screws M2×2 A2/A4 stainless | **Bossard** (CH), Distrelec, Conrad | A2/A4 ≈ non-magnetic |
| Springs | **Gutekunst Federn** (DE, catalogue, small qty) | stainless 1.4310 is slightly magnetic once cold-worked — OK, sits opposite the magnet |
| Balls | bearing shops (e.g. kugellager-shop), Misumi | **ceramic (Si3N4/ZrO2) balls** = non-magnetic, hard; 316 steel soft; 440C magnetic |
| Cheap prototyping | AliExpress assortments (ball 1–3 mm, mini springs, M2 set screws) | good enough for the FDM test rings |
| Alternative all-in-one | ball spring plungers (Kipp K0314 / Ganter GN 615, M3) | check length vs tab (~4.4 mm radial wall at tab) |

Magnets: supermagnete.ch, N52 disc Ø3 × 1.5 mm, axial magnetisation.
Optics: Kaidomain sells only its own generic TIRs, not Carclo → Carclo from DigiKey.
