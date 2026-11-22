# Hardware

Three boards, schematics generated from Python (`kisch.py` = tiny generator
using the stock KiCad libraries, nets connected by labels on the pins):

| Board | Script | Ø / size | Ground |
|---|---|---|---|
| driver (head, behind shelf) | `gen_driver.py` | Ø19 | BODY |
| spine (under the rings) | `gen_spine.py` | strip | BODY |
| tail | `gen_tail.py` | Ø16 | CELL− |

```
python hardware/gen_all.py   # regenerate, ERC (errors fail), export PDFs
```

Edit the scripts, not the `.kicad_sch` files. Design notes: `docs/electronics.md`.
