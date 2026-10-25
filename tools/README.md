# Build pipeline

Everything that turns the AutoCAD master into the font.

## Requirements

- Python 3.10+
  `pip install fonttools shapely uharfbuzz brotli ttfautohint-py ezdxf pillow numpy scipy`
- Node 18+ — only to read a DWG you edited:
  `cd dwgtool && npm install @mlightcad/libredwg-web`

## After editing the master in AutoCAD

Run from this folder (`tools/`).

```bash
# 1. read the DWG into JSON (skip if you use the pre-read sources/master/kufic_master.json)
node dwgtool/conv.mjs ../sources/master/kufic_master.dwg ../sources/master/kufic_master.json

# 2. build the font
KUFI_DWG=../sources/master/kufic_master.json python3 kufi/build_font.py ../out/KairouanKufic.ttf

# 3. release: version, hinting, WOFF2 / WOFF
python3 release.py ../out/KairouanKufic.ttf 2.100 ../out

# 4. tester page
python3 kufi/make_tester.py ../out/KairouanKufic.ttf ../docs/index.html
```

Windows PowerShell, step 2: `$env:KUFI_DWG="../sources/master/kufic_master.json"; python kufi/build_font.py ../out/KairouanKufic.ttf`

## Checks

| Script | Checks |
|---|---|
| `python3 pairs.py FONT.ttf` | every joining pair: no gap in the join band, no letters running into each other |
| `python3 pairs2.py FONT.ttf` | body collisions vs. dots touching the next letter |
| `python3 wordcoll2.py FONT.ttf "text\|text"` | letters / words touching in real text |
| `python3 markcoll.py FONT.ttf "text" [ss03]` | harakat touching letters or each other |
| `python3 need2.py FONT.ttf` | how much a join must grow for 0.1 nuqta clearance |

## Master conventions (AutoCAD)

- One cell per letter form, label `name_form` on layer **LABELS** (`ba_init`, `ya_fina`, `lam-alif_isol` …). Cells: 13 × 11 nuqta, baseline 5 nuqta above the bottom; 1 nuqta = 196 drawing units.
- Outlines: closed polylines on **GLYPHS**. A polyline whose ends meet counts as closed; exploded lines and arcs are joined automatically.
- Identical copies in one cell are one glyph (one copy per dot pattern: ب ت ث).
- A different shape left of the main one is an alternate (`.alt1`), e.g. the short ya / nun / qaf / seen / sad. It may be drawn raised to fit the cell; it is dropped back to the line.
- Dots: circles on layer **later**. Eyes (counters): circles on layer **EYES**.
- The cell without a label is the Allah ligature (alif + لله + eye).
- Digits and punctuation: cells labelled `<label>_isol` (see `../sources/master/kufic_symbols.dxf`) replace the generated shapes.

## Modules (`kufi/`)

| File | Role |
|---|---|
| `build_font.py` | main builder: forms, features, metrics, TTF |
| `dwg_glyphs.py`, `dwg_marks.py` | read outlines, alternates, dots and eyes from the master |
| `shorts.py` | short tails and the automatic long/short choice (`calt`) |
| `kern.py` | pair spacing measured on the outlines |
| `dotshift.py` | dots moved away from a following tall letter (`calt`) |
| `symbols.py` | digits and punctuation on the grid |
| `harakat.py` | harakat, superscript alef, wasla, Du'ali dots |
| `spec.py` | the nuqta system (W, V, H, G, cut) |
| `make_tester.py`, `tester_template.html` | the tester page |

Settings (environment variables): `KUFI_TAIL_KERN` (1.0 — next word after a long tail, nuqta), `KUFI_SHORT_KERN` (2.0 — after a short form), `KUFI_KERN` (letters with pair kerning), `KUFI_TAILS` (`auto` / `off`).

The letter folders (`ain/`, `ba/`, `heh/` …) hold the first, strict geometric construction of each letter; the master drawing overrides them.
