"""Head driver board (Ø19 mm): MCU, 2-range linear LED current regulator,
reverse-polarity FET, charge-path diode. GND of this board = BODY."""
import kisch
from parts import *

s = kisch.Sheet("driver", "Flashlight head driver")

s.group("Power entry (head spring = CELL+ raw, outer ring = BODY)")
TP(s, "TP1", "CELLP_RAW", "head spring")
TP(s, "TP2", "BODY", "body ring")
s.part("Transistor_FET:SiS415DNT", "Q4", "SiS415DNT", {"D": "CELLP_RAW", "S": "VDD", "G": "Q4_G"},
       "Package_SO:Vishay_PowerPAK_1212-8_Single", {"Note": "reverse-polarity block, P-ch -20 V, ~8 mOhm @ -4.5 V"})
R(s, "R1", "10k", "Q4_G", "BODY")
s.part("Device:Polyfuse", "F1", "0.75A hold", {"1": "BODY", "2": "F1_D1"}, "Fuse:Fuse_1206_3216Metric",
       {"MPN": "SMD1206P075TF", "Note": "trips on reversed cell + clicky on"})
s.part("Device:D_Schottky", "D1", "PMEG3020EH", {"A": "F1_D1", "K": "CELLP_RAW"}, "Diode_SMD:D_SOD-123F",
       {"Note": "charge path BODY->CELL+, Vf < 0.45 V @ 0.5 A"})
C(s, "C1", "10u", "VDD", "BODY", C0603)
C(s, "C2", "100n", "VDD", "BODY")
s.pwr_flag("CELLP_RAW")
s.pwr_flag("BODY")
s.pwr_flag("VDD")

s.group("MCU")
s.part("MCU_Microchip_ATtiny:ATtiny1616-M", "U1", "ATtiny1616-MNR", {
    "VCC": "VDD", "GND": "BODY",
    "~{RESET}/PA0": "UPDI",
    "PA1": None, "PA2": None,
    "PA3": "NTC_PWR", "PA4": "KILL_A", "PA5": "KILL_B", "PA6": "DAC",
    "PA7": "NTC_SIG",
    "PB0": "SCL", "PB1": "SDA", "PB2": "TXD", "PB3": "RXD",
    "PB4": "OPA_PWR", "PB5": "SENS_PWR",
    "PC0": None, "PC1": None, "PC2": None, "PC3": None,
}, "", {"LCSC": "C507118"})
C(s, "C3", "100n", "VDD", "BODY")
TP(s, "TP3", "UPDI", "UPDI")
TP(s, "TP4", "VDD", "VDD")
TP(s, "TP5", "BODY", "GND")
TP(s, "TP6", "TXD", "TX")
TP(s, "TP7", "RXD", "RX")

s.group("LED current regulator: DAC0 → channel A (Q1, 0.05 R, up to 2.8 A) or channel B (Q5, 4.7 R, up to 117 mA)")
s.note("DAC VREF 1.1 V for A (47k/6.8k → 0-139 mV → 0-2.8 A, 10.8 mA/LSB), VREF 0.55 V for B (0-117 mA, 0.46 mA/LSB).\n"
       "Unused channel: its KILL pin driven high → FB ≈ VDD/2 → op-amp output low → FET off. Both KILL pins hi-Z = both channels live.\n"
       "Op-amp powered from PB4 → zero drain after LVP. Gates pulled down when MCU/op-amp are off.")
TP(s, "TP8", "VDD", "LED+")
TP(s, "TP9", "LED_K", "LED-")
R(s, "R2", "47k", "DAC", "REF_A")
R(s, "R3", "6.8k", "REF_A", "BODY")
s.part("Amplifier_Operational:OPA2333xxDGK", "U2", "TLV9002IDGKR", {"1": "OUT_A", "-": "FB_A", "+": "REF_A"},
       "Package_SO:VSSOP-8_3x3mm_P0.65mm", {"Note": "RRIO, Vos 0.4 mV typ"}, unit=1)
s.part("Amplifier_Operational:OPA2333xxDGK", "U2", "TLV9002IDGKR", {"7": "OUT_B", "-": "FB_B", "+": "DAC"},
       "Package_SO:VSSOP-8_3x3mm_P0.65mm", unit=2)
s.part("Amplifier_Operational:OPA2333xxDGK", "U2", "TLV9002IDGKR", {"V+": "OPA_PWR", "V-": "BODY"},
       "Package_SO:VSSOP-8_3x3mm_P0.65mm", unit=3)
C(s, "C4", "100n", "OPA_PWR", "BODY")
s.pwr_flag("OPA_PWR")

s.newrow()
s.note("Channel A (High / Turbo)")
R(s, "R4", "1k", "OUT_A", "GATE_A")
R(s, "R5", "100k", "GATE_A", "BODY")
s.part("Transistor_FET:DMN3008SFG", "Q1", "DMN3008SFG", {"D": "LED_K", "G": "GATE_A", "S": "SENSE_A"},
       "", {"Note": "linear pass FET, up to ~1.8 W, needs copper + thermal path to shelf"})
R(s, "R6", "0.05", "SENSE_A", "BODY", R1206, Note="1 %, ≥0.5 W")
R(s, "R7", "10k", "SENSE_A", "FB_A")
C(s, "C5", "10n", "FB_A", "OUT_A")
R(s, "R8", "10k", "KILL_A", "FB_A")

s.newrow()
s.note("Channel B (Low)")
R(s, "R9", "1k", "OUT_B", "GATE_B")
R(s, "R10", "100k", "GATE_B", "BODY")
s.part("Transistor_FET:AO3400A", "Q5", "AO3400A", {"D": "LED_K", "G": "GATE_B", "S": "SENSE_B"},
       SOT23, {"LCSC": "C20917"})
R(s, "R11", "4.7", "SENSE_B", "BODY", R0603, Note="1 %")
R(s, "R12", "10k", "SENSE_B", "FB_B")
C(s, "C6", "10n", "FB_B", "OUT_B")
R(s, "R13", "10k", "KILL_B", "FB_B")

s.group("Temperature + spine joint")
R(s, "R14", "10k", "NTC_PWR", "NTC_SIG", Note="1 %")
C(s, "C7", "100n", "NTC_SIG", "BODY")
s.part("Connector_Generic:Conn_01x05", "J1", "spine joint", {
    "1": "SENS_PWR", "2": "SDA", "3": "SCL", "4": "NTC_SIG", "5": "BODY"},
    "Connector_PinHeader_1.27mm:PinHeader_1x05_P1.27mm_Vertical",
    {"Note": "right-angle solder joint to spine PCB (pads, footprint TBD)"})

s.save("driver/driver.kicad_sch")
