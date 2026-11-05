"""Print profiles and tunable typography/spacing for Kulish editions.

All CSS dimensions are resolved before handing HTML to PrinceXML, including
@page rules (where CSS custom properties are not reliably supported).
"""
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class PrintProfile:
    width_mm: float
    height_mm: float
    inner_mm: float
    outer_mm: float
    top_mm: float
    bottom_mm: float
    font_pt: float
    line_height: float
    overrides: Mapping[str, str]


# All editable style values are declared here; defaults preserve the original
# 110 x 180 mm edition. Override individual keys in each profile as needed.
BASE_STYLES: dict[str, str] = {
    "front_top": "13mm", "front_right": "10mm", "front_bottom": "8mm", "front_left": "10mm",
    "header_font": "6.8pt", "header_padding": "6mm",
    "footnote_rule": ".35pt", "footnote_margin_top": "2.2mm",
    "footnote_padding_top": "1.6mm", "footnote_side_margin": "3mm",
    "column_gap": "4mm", "column_rule": ".35pt",
    "front_title_font": "18pt", "front_title_line": "1.35",
    "toc_title_font": "11pt", "toc_font": "5.9pt",
    "toc_gap": "4mm", "toc_number_width": "8mm",
    "toc_column_gap": "1.2mm", "toc_row_gap": ".65mm",
    "separator_width": "76mm", "separator_height": "6mm",
    "book_title_font": "12pt", "book_title_bottom": "4mm",
    "chapter_font": "8.5pt", "chapter_top": "2mm", "chapter_bottom": "1.2mm",
    "verse_font": "8pt", "verse_indent": "1.5mm",
    "verse_number_gap": ".8mm", "verse_bottom": ".2mm",
    "dropcap_font": "20.5pt", "dropcap_line": "15pt",
    "dropcap_gap": ".65mm", "source_heading_font": "7pt",
    "footnote_font": "6.6pt", "footnote_line": "1.08",
    "footnote_call_font": "5.5pt",
    "front_toc_top": "1mm", "toc_title_bottom": "3mm",
}

PROFILES: dict[str, PrintProfile] = {
    "standard": PrintProfile(
        110, 180, 10, 8, 13, 8, 7.5, 1.10,
        {"front_top": "13mm", "front_right": "10mm", "front_bottom": "8mm", "front_left": "10mm"},
    ),
    "large": PrintProfile(
        165, 235, 13, 12, 14, 14, 10.5, 1.14,
        {"front_title_font": "23pt", "toc_title_font": "15pt", "toc_font": "8.5pt",
         "toc_number_width": "12mm", "toc_gap": "6mm", "column_gap": "5mm",
         "book_title_font": "16pt", "chapter_font": "12pt",
         "verse_font": "10.5pt", "verse_indent": "2mm", "verse_number_gap": "1mm",
         "dropcap_font": "29pt", "dropcap_line": "21pt", "source_heading_font": "10pt",
         "footnote_font": "9pt", "footnote_call_font": "7.5pt",
         "header_font": "9pt", "separator_width": "115mm", "separator_height": "9mm"},
    ),
    "pocket-size": PrintProfile(
        80, 130, 8, 7, 9, 7, 6.1, 1.07,
        {"front_title_font": "13pt", "toc_title_font": "8pt", "toc_font": "4.5pt",
         "toc_number_width": "6mm", "toc_gap": "2mm", "toc_column_gap": ".6mm",
         "toc_row_gap": ".35mm", "column_gap": "2.5mm",
         "book_title_font": "9pt", "book_title_bottom": "2mm",
         "chapter_font": "7pt", "chapter_top": "1mm", "chapter_bottom": ".6mm",
         "verse_font": "6.3pt", "verse_indent": "1mm", "verse_number_gap": ".4mm",
         "dropcap_font": "16pt", "dropcap_line": "11pt", "source_heading_font": "5.5pt",
         "footnote_font": "5.3pt", "footnote_call_font": "4.5pt",
         "header_font": "5.5pt", "header_padding": "4mm",
         "footnote_margin_top": "1mm", "footnote_padding_top": ".8mm",
         "footnote_side_margin": "1mm", "separator_width": "54mm",
         "separator_height": "4mm", "front_toc_top": ".5mm", "toc_title_bottom": "2mm"},
    ),
}


def css_values(profile_name: str) -> dict[str, str]:
    if profile_name not in PROFILES:
        raise ValueError(f"Unknown print profile: {profile_name}. Choose from: {', '.join(PROFILES)}")
    p = PROFILES[profile_name]
    values = dict(BASE_STYLES)
    values.update(p.overrides)
    values.update({
        "page_width": f"{p.width_mm:g}mm",
        "page_height": f"{p.height_mm:g}mm",
        "page_top": f"{p.top_mm:g}mm",
        "page_bottom": f"{p.bottom_mm:g}mm",
        "page_inner": f"{p.inner_mm:g}mm",
        "page_outer": f"{p.outer_mm:g}mm",
        "body_font": f"{p.font_pt:g}pt",
        "body_line": f"{p.line_height:g}",
        "front_height": f"{p.height_mm - p.top_mm - p.bottom_mm:g}mm",
    })
    # Front matter uses symmetric margins, independent of page parity.
    if profile_name != "standard":
        values.update({
            "front_top": f"{p.top_mm:g}mm",
            "front_bottom": f"{p.bottom_mm:g}mm",
            "front_left": f"{p.inner_mm:g}mm",
            "front_right": f"{p.outer_mm:g}mm",
        })
    return values
