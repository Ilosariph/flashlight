"""Regenerate project footprints + all schematics, run ERC, export PDFs."""
import subprocess
import sys

subprocess.run([sys.executable, "gen_footprints.py"], check=True)
ok = True
for b in ("driver", "spine", "tail"):
    subprocess.run([sys.executable, f"gen_{b}.py"], check=True)
    sch = f"{b}/{b}.kicad_sch"
    r = subprocess.run(["kicad-cli", "sch", "erc", "--severity-error", "--exit-code-violations",
                        "-o", f"{b}/erc.rpt", sch], capture_output=True, text=True)
    print(b, r.stdout.strip().splitlines()[0] if r.stdout else r.stderr)
    ok &= r.returncode == 0
    subprocess.run(["kicad-cli", "sch", "export", "pdf", "-o", f"{b}/{b}.pdf", sch],
                   check=True, capture_output=True)
sys.exit(0 if ok else 1)
