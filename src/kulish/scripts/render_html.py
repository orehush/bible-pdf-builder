#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ..builder.renderer import build_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Kulish Bible source HTML into PrinceXML-ready HTML.")
    parser.add_argument("source", type=Path, help="Source Bible HTML file")
    parser.add_argument("-o", "--output", type=Path, default=Path("kulish_bible_print.html"))
    parser.add_argument(
        "--styles",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "styles" / "styles.css",
        help="CSS file used for print layout",
    )
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"Source file not found: {args.source}")
    if not args.styles.exists():
        raise SystemExit(f"Styles file not found: {args.styles}")

    build_html(args.source, args.output, args.styles)


if __name__ == "__main__":
    main()
