from __future__ import annotations

import re

FOOTNOTE_SYMBOL_RE = re.compile(r"^([*†‡§¶]+)\s*(.*)$", re.S)

TITLE_OVERRIDES = {
    "ROM": "ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО РИМЛЯН",
    "1CO": "ПЕРВЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО КОРИНТЯН",
    "2CO": "ДРУГЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО КОРИНТЯН",
    "PHP": "ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО ФИЛИПЯН",
    "1TH": "ПЕРВЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО СОЛУНЯН",
    "2TH": "ДРУГЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО СОЛУНЯН",
    "1TI": "ПЕРВЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО ТИМОТЕЯ",
    "2TI": "ДРУГЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО ТИМОТЕЯ",
    "PHM": "ПОСЛАННЄ СЬВ. АПОСТОЛА ПАВЛА ДО ФИЛИМОНА",
    "1PE": "ПЕРВЕ СОБОРНЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПЕТРА",
    "2PE": "ДРУГЕ СОБОРНЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ПЕТРА",
    "1JN": "ПЕРВЕ СОБОРНЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ЙОАНА",
    "2JN": "ДРУГЕ СОБОРНЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ЙОАНА",
    "3JN": "ТРЕТЄ СОБОРНЕ ПОСЛАННЄ СЬВ. АПОСТОЛА ЙОАНА",
}

OLD_TESTAMENT_CODES = [
    "GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT","1SA","2SA","1KI","2KI",
    "1CH","2CH","EZR","NEH","EST","JOB","PSA","PRO","ECC","SNG","ISA","JER",
    "LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP",
    "HAG","ZEC","MAL",
]

# Optional manual footnote placement across book boundaries.
# Key: source book code. Value: destination book code.
# Moves the final note of the source book to the beginning of the destination
# book, with a hidden call marker. Leave empty unless PDF inspection confirms
# the source and destination begin/end on the same physical page.
FOOTNOTE_CARRY_TO_NEXT_BOOK: dict[str, str] = {}

# Manual per-book pagination adjustments (book codes such as "MRK", "ROM").
# heading_spacing_mm changes the space BEFORE the separator + title band.
# Negative values tighten the gap and may keep the next book on this page;
# positive values add space and may push the band to the next page.
# break_before_page forces a new page regardless of available space.
# separator_previous_page splits the separator from the heading and forces
# the heading onto a new page. Use with negative heading_spacing_mm to
# help the separator fit at the end of the preceding page.
# Example:
# BOOK_HEADING_LAYOUT = {
#     "MRK": {"heading_spacing_mm": -2},
#     "ROM": {"heading_spacing_mm": 3},
#     "HEB": {"break_before_page": True},
# }
BOOK_HEADING_LAYOUT: dict[str, dict[str, float | bool]] = {
    "JOS": {"separator_previous_page": True},
}
