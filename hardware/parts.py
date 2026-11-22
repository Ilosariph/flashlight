"""Common footprints and helpers for the generators."""
R0402 = "Resistor_SMD:R_0402_1005Metric"
R0603 = "Resistor_SMD:R_0603_1608Metric"
R1206 = "Resistor_SMD:R_1206_3216Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
SOT236 = "Package_TO_SOT_SMD:SOT-23-6"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
PAD = "TestPoint:TestPoint_Pad_D1.5mm"


def R(s, ref, val, a, b, fp=R0402, **f):
    s.part("Device:R", ref, val, {"1": a, "2": b}, fp, f)


def C(s, ref, val, a, b, fp=C0402, **f):
    s.part("Device:C", ref, val, {"1": a, "2": b}, fp, f)


def TP(s, ref, net, label, fp=PAD):
    s.part("Connector:TestPoint", ref, label, {"1": net}, fp)
