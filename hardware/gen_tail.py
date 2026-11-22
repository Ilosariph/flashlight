"""Tail PCB (Ø16 mm): USB-C, TP4057 charger, clicky. GND of this board = CELL-
(tail spring); the rim pad touches the brass tail ring = BODY."""
import kisch
from parts import *

s = kisch.Sheet("tail", "Flashlight tail (charger + clicky)", paper="A4")
s.group("Contacts + clicky (LED current path, ≤3 A)")
TP(s, "TP1", "CELLN", "tail spring")
TP(s, "TP2", "BODY", "rim / tail ring")
s.part("Switch:SW_Push", "SW1", "forward clicky", {"1": "CELLN", "2": "BODY"},
       "Button_Switch_THT:SW_PUSH_6mm", {"Note": "switch from KDLITKER 16 mm module, footprint after measuring"})
s.pwr_flag("CELLN")

s.group("USB-C (power only) + charger. Click OFF to charge: BAT → BODY → head D1 → CELL+")
s.part("Connector:USB_C_Receptacle_PowerOnly_6P", "J1", "TE 2495702-1", {
    "VBUS": "VBUS", "GND": "CELLN", "CC1": "CC1", "CC2": "CC2", "SHIELD": "CELLN"},
    "Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal",
    {"Note": "IPX7 TE 2495702-1, footprint TBD (placeholder)"})
s.pwr_flag("VBUS")
R(s, "R1", "5.1k", "CC1", "CELLN")
R(s, "R2", "5.1k", "CC2", "CELLN")
C(s, "C1", "10u", "VBUS", "CELLN", C0603)
s.part("Battery_Management:TP4057", "U1", "TP4057", {
    "V_{CC}": "VBUS", "GND": "CELLN", "BAT": "BODY", "PROG": "PROG",
    "~{CHRG}": "CHRG", "STDBY": "STDBY"}, SOT236, {"LCSC": "C12044"})
R(s, "R3", "2.7k", "PROG", "CELLN", Note="Ibat ≈ 1000/R(kΩ)·… → ~400 mA, check TP4057 datasheet")
C(s, "C2", "10u", "BODY", "CELLN", C0603)

s.group("Charge indicator (optional, may glow through the port opening)")
R(s, "R4", "1k", "VBUS", "LED_R")
s.part("Device:LED", "D1", "red", {"A": "LED_R", "K": "CHRG"}, "LED_SMD:LED_0603_1608Metric", dnp=True)
R(s, "R5", "1k", "VBUS", "LED_G")
s.part("Device:LED", "D2", "green", {"A": "LED_G", "K": "STDBY"}, "LED_SMD:LED_0603_1608Metric", dnp=True)
s.save("tail/tail.kicad_sch")
