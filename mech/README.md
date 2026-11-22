# mech

CadQuery concept model (v0). All dimensions in `Params` at the top of `flashlight.py`.

    python mech/flashlight.py   # → mech/out/*.step, stl/, assembly STEP
    python mech/render.py       # → mech/out/render/*.png (exterior, top, section, head_section)

Threads are cosmetic (plain cylinders); the spec (M20x0.75 head-body,
M18x0.75 body-tail) goes on the JLCCNC drawing. Switch / USB / clicky
geometry are placeholders until parts are picked.
