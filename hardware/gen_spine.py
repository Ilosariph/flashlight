"""Spine PCB under the rings: 2x TMAG5273 (different I2C addresses) + NTC pads."""
import kisch
from parts import *

s = kisch.Sheet("spine", "Flashlight spine (ring sensors)", paper="A4")
s.group("Joint to driver")
s.part("Connector_Generic:Conn_01x05", "J1", "driver joint", {
    "1": "SENS_PWR", "2": "SDA", "3": "SCL", "4": "NTC_SIG", "5": "BODY"},
    "Connector_PinHeader_1.27mm:PinHeader_1x05_P1.27mm_Vertical")
s.pwr_flag("SENS_PWR")
s.pwr_flag("BODY")
C(s, "C1", "1u", "SENS_PWR", "BODY")
R(s, "R1", "4.7k", "SDA", "SENS_PWR")
R(s, "R2", "4.7k", "SCL", "SENS_PWR")

s.group("Ring sensors: U1 under rear ring (level), U2 under front ring (mode)")
for ref, var, addr, c, lcsc in (("U1", "TMAG5273A1QDBVR", "0x35", "C2", "C3716049"), ("U2", "TMAG5273C1QDBVR", "0x78", "C3", "C32969674")):
    s.part("Sensor_Magnetic:TMAG5273x1QDBV", ref, var, {
        "VCC": "SENS_PWR", "GND": "BODY", "TEST": "BODY", "SDA": "SDA", "SCL": "SCL",
        "~{INT}": None}, SOT236, {"LCSC": lcsc, "Note": f"I2C {addr}, ±40/80 mT"})
    C(s, c, "100n", "SENS_PWR", "BODY")

s.group("NTC (leaded bead, hand-soldered, in shelf pocket behind LED)")
s.part("Device:Thermistor_NTC", "TH1", "10k B3478", {"1": "NTC_SIG", "2": "BODY"},
       "Connector_Wire:SolderWire-0.1sqmm_1x02_P3.6mm_D0.4mm_OD1mm",
       {"MPN": "TDK B57540G1103F000"})
s.save("spine/spine.kicad_sch")
