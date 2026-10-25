# Changelog

## 2.1
- Harakat redrawn on the pen (thicker, flat cuts; sukun = hollow rhombic nuqta).
- Mark stacking (`mkmk`): vowels over shadda, hamza, madda and small alif; per-letter harakat on the Allah ligature.
- Alef wasla ٱ (with ٱللَّه ligature) and superscript alef ٰ.
- `ss03`: Du'ali red vowel dots (colour font, COLR/CPAL).
- Arabic presentation forms U+FE70–FEFC; zero-width controls (ZWJ, ZWNJ, LRM, RLM, ALM).
- TrueType hinting (ttfautohint, Arabic) and `gasp`.
- Full naming: designer, description, Arabic family name; SIL Open Font License 1.1.

## 2.0
- Allah ligature from the master drawing (الله, لله, U+FDF2).
- Digits ٠–٩ / 0–9 and Arabic + Latin punctuation, editable as master cells.
- Kashida: `ss02` (every join +1 nuqta) and `jalt` (+1/+2/+3).
- Dots of ت ث ق move away from a following tall letter.
- Web package: WOFF2, WOFF, CSS.

## 1.x
- Long tails reach under the next word; automatic short forms where they would touch (`calt`), all short with `ss01`.
- Pair kerning for ر ز و ا د ذ ة لا and after short forms.
- Joins reworked in the master: no gaps, no collisions (checked on every joining pair).

## 0.x
- Strict construction of every letter on the nuqta grid from the book; AutoCAD master; reading the master (outlines, alternates, dots, eyes) into the font.
