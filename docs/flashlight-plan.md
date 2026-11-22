# DIY 14500 EDC Flashlight — Project Plan

Status: concept done, ready for schematic. Last update: 2026-11-22.

## 1. Requirements (what I want)

| # | Requirement | Decision |
|---|---|---|
| R1 | AA size | 14500 Li-ion (3.7 V). AA NiMH/alkaline not supported |
| R2 | 3-position selector, glove-usable | **Magnetic ring** (ring1): Low / High / Turbo, absolute position, ball detents |
| R3 | 2-position selector, glove-usable | **Magnetic ring** (ring2, narrower tab): Normal / Strobe |
| R4 | Tail switch | Mechanical **forward clicky**, true power cutoff, momentary on half-press |
| R5 | Physical lockout | Unscrew tailcap ~¼–½ turn → body end face lifts off brass tail ring |
| R6 | USB-C charging, onboard | Port location irrelevant → **in tailcap** (side) |
| R7 | Splash resistance | Nice to have (IPX4-ish): O-rings + TPU plug over USB-C |
| R8 | Adjustable brightness | Firmware constants, reflash via UPDI; optional EEPROM config gesture later |
| R9 | Testable without housing | Yes — bench rig before any CNC order |

Manufacturing: FDM printing (fit prototypes only), JLCPCB (PCB + assembly), JLCCNC (aluminum housing).

## 2. Architecture

Split design: **driver/MCU/LED in head, charger in tail, Schottky diode in head as charge path.**

```
HEAD (has CELL+ and BODY only)
  CELL+ spring (raw) ──┬── Q4 P-FET (reverse-polarity block, gate = BODY) ── CELL+_P
                       └── D1 cathode ◄── D1 anode ── F1 PTC ── BODY   (charge branch only)
  CELL+_P ──┬── MCU VDD, op-amp VDD, DW01A VCC
            └── LED anode ── LED cathode ── Q1 ── Rsense ── Q2 FS8205A ── BODY (= head GND)
                                                              ▲ driven by U4 DW01A

TAIL (has CELL− and BODY only)
  CELL− spring ─┬── clicky ─────────────────────── rim ring → BODY   (LED current path, ≤3 A)
                └── charger GND
  USB-C VBUS → TP4057 → BAT ── (opt. Q3) ── rim ring → BODY          (charge path, ~0.5 A)
```

How it works:
- **Clicky ON:** BODY = CELL−. Head sees full cell voltage, runs normally. D1 reverse-biased.
- **Clicky OFF + USB in:** charger drives BODY up; current flows BODY → D1 → CELL+ → cell → CELL− → charger GND. Head sees −Vf(D1) ≈ −0.3 V → stays off.
- **Rule: click OFF to charge.** Clicky ON while plugged → charger BAT shorted to GND via clicky; TP4057 drops to trickle (BAT < 2.9 V). Optional Q3 P-FET disconnects charger in that case.
- **Lockout** (tailcap twisted) also breaks charge path → unlock to charge.

### Known consequences / design rules
- Cell charges to **~4.0–4.05 V** (4.2 V CV minus D1 drop) ≈ 90 % capacity. **Cannot overcharge** — diode drop only ever lowers cell voltage. Accepted tradeoff (also better cycle life).
- D1 Vf must stay **< ~0.45 V** at charge current, so head ICs (reverse-biased by Vf during charge) don't conduct through internal ESD/substrate diodes. Pick low-Vf Schottky, check datasheet at 0.5 A.
- **No ideal-diode IC possible in head** (e.g. LM66100): needs a GND reference, head only has CELL+ and BODY.
- **Cell: unprotected 14500, button top planned, flat top must also fit.** No protected cell. All protection onboard, in head:
  - DW01 can't go in tail (needs CELL+). In head it works: with clicky ON, BODY = CELL−, so head sees both poles exactly when discharge protection matters.
  - Overcharge: D1 + 4.2 V CV → cell ≤ ~4.05 V by physics. DW01A unpowered during charge, not needed.
  - Overdischarge: firmware LVP (primary) + DW01A/FS8205A at 2.5 V (hardware backup). After LVP cutoff MCU in deepest sleep (< 1 µA).
  - Overcurrent / LED-path short: DW01A overcurrent trip + Q1 regulation.
  - **Reversed cell** (electrical only): Q4 P-FET blocks CELL+ feed to all head circuits. D1 branch must stay on raw spring side (charge current flows into cell+ directly), so with reversed cell + clicky ON D1 would short the cell → **F1 PTC in series with D1** trips (hold ≥ 0.75 A > 0.5 A charge). D1 must survive surge until trip (check IFSM). TP4057 has battery polarity reversal protection for reversed cell + USB.
  - Not covered electrically: head spring shorting directly to body or cell can → mechanical: insulated spring pad (§4).
  - Cost: FS8205A + Q4 add ~65 mΩ in LED path → ~0.15 V loss in turbo.
- Future option (not v1): small MCU in tail pauses charge, measures BODY (floats ≈ CELL+ when clicky open) → full 4.2 V charge. Puts overcharge safety on firmware → not for v1.

## 3. Firmware spec (head MCU, ATtiny1616)

- Power: MCU only powered while clicky closed. Boot → read slides → light immediately (<50 ms target).
- Inputs: 2× TMAG5273 3D Hall (I2C, one per ring, different address variants). Poll ~20 Hz → ring angle → position (per-unit calibration table, handles crosstalk between rings + cell can). Sensors powered from a GPIO → 0 drain after LVP. **Live mode change** while on.
- Output levels (start values, tune on bench):
  - Low ≈ 20–30 mA
  - High ≈ 500 mA
  - Turbo ≈ 2.5 A → thermal stepdown to High at ~55 °C, and/or timed (~45 s) stepdown
- Strobe (SW2): ~10 Hz, at brightness of SW1 position (tunable).
- Current control: MCU DAC0 → op-amp (+) ; op-amp (−) ← Rsense top ; op-amp out → Q1 gate.
  - **Open item:** 8-bit DAC resolution too coarse for Low with 0.05 Ω (30 mA = 1.5 mV). Options: PWM-gate the DAC/op-amp reference for Low, or second sense range. Decide during schematic.
- Thermal: **leaded bead NTC 10k** glued (thermal epoxy) into Ø1.8×4 mm pocket in shelf rear face, straight behind LED, leads hand-soldered to spine. Backups: TMAG5273 die temp, MCU internal sensor.
- LVP: measure VDD (internal ref): step down at ~3.3 V, warning blinks, shutdown ~3.0 V.
- Brightness values as constants in one header; optional later: EEPROM config gesture.
- Reference code: Anduril 2 (ToyKeeper) — ATtiny1616 hwdefs, thermal regulation, DAC/PWM ramp handling. Own UI is far simpler (slides are absolute state).
- Toolchain: avr-gcc + avr-libc (ATtiny 1-series may need Microchip ATtiny DFP pack), flash via **SerialUPDI** (USB-serial adapter + resistor) with avrdude ≥7 or pymcuprog.

## 4. Mechanical

```
[bezel cup: optic][stub|shelf][rings 1+2 over spine PCB w/ 2× TMAG5273][driver]   HEAD 23.5 / rings 26 OD
[ body tube: 14500 unprotected, button or flat top (49–52 mm)   ]   BODY  ~17–18 mm OD
[ ring | tail PCB (USB-C flat on rear, IPX7) | clicky ] tailcap      TAIL  OD 21.5, ~26 mm
```
- Overall length estimate ~95–105 mm. Optic = Carclo 20 mm (Ø20, 9.9 mm tall) → head OD ~23.5 mm. Get STEP from carclo-optics.com for CAD.
- Spine PCB soldered 90° to head driver (large pads or 1.27 mm pin header — hand-solderable). No wall penetrations: rings act through the 1.5 mm seat wall.
- Bezel cup (M21×0.75 on head stub, bottoms on stub face, O-ring 19×1) clamps optic and retains both rings on the Ø21 seat; ~0.3 mm axial play per ring.
- Ring: 6061, OD 26, 16 flutes, tab +2 mm (ring2 tab narrower → tell apart by feel). Detent ball in tab → dimples in seat. Magnet opposite tab.
- LED shelf 6 mm solid (grew into unused cavity, no length cost, +~2.8 g). Heat path shelf → 1.5 mm seat wall ≈ 0.9 K/W (≈ +2.5 K vs full-wall head at ~5.4 W turbo heat) + stub thread → bezel cup. Acceptable.
- Position marks laser-engraved after anodize: L/H/T on bezel cup in front of ring1, N/S on head shoulder behind ring2 (1.8 mm DejaVu Bold).
- Body = conductor (BODY net). Contact faces (body thread ends, tailcap rim, head contact) **unanodized** — mask or face after anodize. **Bore stays anodized** (insulates cell can from tube). First CNC batch: skip anodize, bead blast only → use kapton sleeve in bore for test.
- **Cell compatibility:** plan for **button top** (~51–52 mm), flat top (~49–50 mm) must still contact → head spring ≥ 3 mm working travel; tail spring adds margin. Test both on FDM prototype.
- **Insulated spring pad (head driver):**
  - Spring ≤ 6–7 mm Ø, centered, soldered to center pad.
  - Copper keepout ≥ 1.5 mm around spring pad; no GND/BODY copper on top layer near it.
  - Kapton / fish-paper washer glued around spring → flat-top cell can (cell−) shoulder cannot touch spring or + pad.
  - Keep factory fish-paper ring on cells.
  - Spring must not be able to deflect sideways into driver retaining ring / head wall.
- Thermal: LED MCPCB on aluminum shelf in head, Q1 thermally coupled to head (runs linear, up to ~3 W at full cell in turbo).
- Splash: O-rings at head–body and body–tail, TPU-printed plug for USB-C, slide slots tight.
- FDM: fit/ergonomics prototypes only. Use coarse thread pitch (≥1.5 mm) or press-fit on prints; real threads (e.g. M18×1 / M20×1) on CNC parts.
- CAD: **CadQuery** (in `.venv` via devShell), sources in `mech/`, exports to `mech/out/`.

## 5. BOM (v1)

LCSC numbers marked ✓ were found on LCSC; others to verify/pick. Full table also in the Claude Sheet "Flashlight BOM – 14500 tail-charger build".

### Head driver + spine PCB
| Ref | Part | LCSC | Package | Notes |
|---|---|---|---|---|
| U1 | ATTINY1616-MNR | C507118 ✓ | QFN-20 3×3 | MCU |
| U2 | TLV9001IDBVR | C398363 ✓ | SOT-23-5 | CC loop op-amp, RRIO |
| Q1 | N-MOSFET logic-level, Rds(on) < 10 mΩ @ 4.5 V | TBD | DFN3×3 / PDFN | linear LED FET, thermal path required |
| R1 | 0.05 Ω 1 % ≥ 0.5 W | TBD | 1206 | sense, 125 mV @ 2.5 A |
| D1 | Schottky, low Vf, ≥ 1 A (e.g. B5819W) | TBD | SOD-123 | charge path, anode BODY → cathode raw CELL+ spring, in series with F1 |
| F1 | PTC polyfuse, hold ≥ 0.75 A, trip ~1.5 A | TBD | 1206 | reversed-cell short protection in D1 branch |
| Q4 | P-MOSFET logic-level, Rds(on) ≤ 15 mΩ | TBD | DFN3×3 / PDFN | reverse-polarity block in CELL+ feed |
| U4 | DW01A | C351410 ✓ | SOT-23-6 | HW backup: overdischarge 2.5 V, overcurrent; VCC = CELL+_P, GND = BODY |
| Q2 | FS8205A | C16052 ✓ | TSSOP-8 | in LED return path between Rsense and BODY; check rating vs 2.5 A |
| R7–R8, C5 | 100 Ω, 1 kΩ, 100 nF | TBD | 0402 | DW01A reference circuit |
| U5, U6 | TMAG5273 3D Hall, I2C (A1 + B1 or other address pair) | TBD (check LCSC) | SOT-23-6 | on spine underside, ~5 mm from ring magnets (~12 mT est.) |
| R11–R12 | I2C pull-ups 4.7 kΩ | TBD | 0402 | |
| RT1 | NTC 10 k, leaded glass/epoxy bead ≤1.6 mm | TBD (DigiKey) | leaded | in shelf pocket behind LED, hand-soldered |
| C1–C3 | 100 nF | C1525 (verify) | 0402 | decoupling |
| C4 | 10 µF | C19702 (verify) | 0603 | bulk |
| R2–R3 | 10 kΩ | C25744 (verify) | 0402 | gate pulldown, op-amp net |
| — | UPDI + GND + VDD test pads | — | pads | programming |

### Tail PCB
| Ref | Part | LCSC | Package | Notes |
|---|---|---|---|---|
| U3 | TP4057-42-SOT26-R | C12044 ✓ | SOT-23-6 | 500 mA, 4.2 V CV |
| J1 | USB-C 6P TYPE-C-31-M-17 | C283540 ✓ | SMD R/A | power only |
| R4–R5 | 5.1 kΩ | C25905 (verify) | 0402 | CC1/CC2 pulldowns — required for C-to-C chargers |
| R6 | PROG resistor | per datasheet | 0402 | ~400–500 mA |
| D2–D3, R9–R10 | charge LEDs red/green + 1 kΩ | TBD | 0603/0402 | optional CHRG/STDBY |
| Q3 | P-MOSFET AO3401A | C15127 | SOT-23 | optional: disconnect charger while clicky on |

### Off-LCSC
| Part | Source | Notes |
|---|---|---|
| Nichia 519A **domed, R9080, 5000K (sm503)** on 10 mm DTP copper MCPCB | Kaidomain / Convoy store | 519A-V1 also OK (~+50 mV Vf). Fallback: Samsung LH351D |
| TIR optic **Carclo 10138** (20 mm, frosted narrow, ~15°) | LEDSupply / Mouser / DigiKey | alt **10139** (frosted medium, ~24°), same outline → order both, pick on bench. 9.9 mm tall. Head OD ~23.5 mm |
| Forward clicky 12 mm, ≥ 3 A | Kaidomain (Omten style) | |
| Springs, brass contact ring | Kaidomain | head spring CELL+, tail spring CELL− |
| 14500 Li-ion **unprotected, button top** (flat top also fits), ≥ 3 A | battery shop | candidates: Vapcell K10 1000 mAh 8 A, Efest 1200 mAh 6 A. ⚠️ Vapcell H10 from ~mid-2025: bad batches (fast self-discharge) → don't use |
| Insulating washer, kapton / fish paper | generic | around head spring |
| 2× N52 disc magnet 3×1.5 mm, axial | supermagnete.ch / DigiKey | epoxy into ring pocket, radial |
| 2× steel ball 1.5 mm + spring + M2 set screw (stainless, low-magnetic) | Misumi / generic | detent in each ring tab |
| O-rings, TPU USB plug | printed / generic | |
| Head / body / tailcap, 6061 | JLCCNC | after FDM fit test |
| UPDI adapter | USB-serial (CH340/CP2102) + 4.7 kΩ | |

## 5b. Hand assembly (user solders ≥0805 only)
JLC places every SMD part (incl. TMAG5273, USB-C). By hand: LED wires, head/tail springs, spine↔driver joint, clicky leads, magnets (epoxy), detent balls/set screws.

## 6. Plan / order of work

1. ~~Pick optic + LED~~ ✓ Carclo 20 mm + 519A 5000K. Concept CAD v0 in `mech/` (~114 mm long). Sourcing: `docs/sourcing.md` (DigiKey + Kaidomain).
2. **Schematic** (KiCad): head driver + spine, tail board. Resolve Low-mode current resolution (PWM vs 2nd range). Pick Q1, R1, D1 (check Vf @ 0.5 A < 0.45 V).
3. **PCB layout**: 4-layer, 0402, panelize head + spine + tail in one JLC order (pay extended-part fees once). Add generous test pads + bench-rig wire pads (CELL+, BODY, CELL−).
4. **Firmware v0** on dev board / first PCBs: slides, levels, strobe, LVP, thermal.
5. **Bench test, no housing** (see §7).
6. **FDM fit prototype**: head/body/tail, slide slots, USB plug, clicky fit.
7. **JLCCNC** first batch, no anodize.
8. Iterate: PCB rev 2 likely.

## 7. Bench test plan (before CNC)

- Rig: 14500 holder or bench PSU (current limit), two wires as BODY, meter in series for LED current.
- LED MCPCB clamped to aluminum block with paste — **never run turbo without heatsink**.
- Check: each slide position, live switching, strobe, currents vs targets, thermal stepdown (thermocouple on block), LVP thresholds (PSU sweep).
- Protection (PSU with current limit, not a real cell first): reversed polarity with clicky closed → Q4 blocks, F1 trips; DW01A cutoff at ~2.5 V; overcurrent trip.
- Charging: USB in, clicky lead open → charge current, final cell voltage (~4.0–4.05 V), head stays dark, termination. Then clicky closed while plugged → confirm charger trickles/doesn't overheat (or Q3 works).

## 8. Cost estimate (rough, USD, no fresh quotes)

- First working light: **~200–350** (PCB+PCBA 60–100, LED/optic/clicky/springs 15–25, cell 6–10, CNC set 80–200, shipping 30–50).
- Per unit at 5 pcs: **~40–70**. Swiss import: 8.1 % VAT + carrier fees per shipment.

## 9. Open decisions

- [x] Optic → Carclo 20 mm (10138 primary, 10139 alt), LED → 519A domed 5000K R9080. Head OD ~23.5 mm
- [ ] Low-mode current method (PWM-gated reference vs dual sense range)
- [ ] Q1, Q4, R1, D1, F1, NTC part picks (D1: Vf @ 0.5 A < 0.45 V, IFSM survives F1 trip time)
- [ ] Strobe frequency / level, turbo stepdown thresholds
- [ ] Q3 needed? (test TP4057 behaviour with BAT shorted first)
- [x] Threads: head-body **M20×1**, 6 mm; body-tail **M18×0.75**, 5 mm (lockout ¼ turn = 0.19 mm gap, ½ turn for margin); bezel ring **M21×0.5** internal (lathe-cut, non-ISO); tail retaining ring **M17×0.5** brass (= BODY contact). O-rings: head-body 17×1.5 on body collar, body-tail 18×1 internal in tailcap. All single-point on lathe, 6H/6g
- [x] Glove-friendly mode selection → 2 magnetic rings + TMAG5273 (modelled)
- [ ] Bench-test ring sensing: Adafruit 6489 TMAG5273 breakout + magnet + cell can nearby
- [ ] Detent force: ball/spring/set screw sizes, dimple depth
- [x] CAD tool → **CadQuery** (STEP export for JLCCNC; preview via STL → openscad PNG)

## 10. Suggested repo layout

```
flashlight/
  flake.nix          # devShell: avr-gcc/avr-libc, avrdude, pymcuprog, uv + CadQuery venv (kicad, openscad from system)
  hardware/          # KiCad project: head, spine, tail (one panel)
  firmware/          # ATtiny1616, Makefile, config.h with brightness levels
  mech/              # CadQuery sources; STL/STEP exports in mech/out/ (gitignored)
  docs/              # this file, bench results, datasheets list
```
