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
| SP3T slide SMD (SW1) | ✓ C&K PCM13SMTR, E-Switch EG1312AR / EG1315AA, Nidec CUS-13TB | pick by actuator height (needs ~3.4 mm reach, see mech) |
| SPDT slide SMD (SW2) | ✓ C&K JS102011SAQN, PCM12SMTR | |
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
