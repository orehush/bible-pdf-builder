#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup


def normalize(value: str) -> str:
    return re.sub(r"\\s+", " ", value).strip().casefold()


def page_start_books(pdf: Path, headings: dict[str, str]) -> set[str]:
    """Find headings that are the first body text on their physical page."""
    try:
        import pymupdf as fitz
    except ImportError as exc:
        raise SystemExit(
            "Two-pass separator detection needs PyMuPDF: poetry add --group dev pymupdf"
        ) from exc

    result: set[str] = set()
    with fitz.open(pdf) as document:
        for page in document:
            # Ignore running headers (above the 13 mm body margin).
            body_top = 13 * 72 / 25.4
            body_bottom = page.rect.height - 8 * 72 / 25.4
            lines = []
            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    value = normalize("".join(span["text"] for span in line["spans"]))
                    if value and body_top - 3 <= line["bbox"][1] < body_bottom:
                        lines.append((line["bbox"][1], line["bbox"][0], value))
            lines.sort()
            if not lines:
                continue
            # A wrapped heading can span multiple lines. Compare its beginning
            # with the first visible body line, rather than relying on search_for.
            first_line = lines[0][2]
            for code, title in headings.items():
                if first_line.startswith(normalize(title)[:min(18, len(normalize(title)))]):
                    result.add(code)
    return result


def suppress_separators(html_text: str, codes: set[str]) -> str:
    """Hide separator ink in the requested books without changing layout."""
    for code in codes:
        # Match only the opening portion of this book. Never cross into the
        # following book when looking for its separator.
        opening = re.compile(
            r'(<section\\b[^>]*\\bid="print-book-' + re.escape(code) +
            r'"[^>]*>[\\s\\S]*?<div class="book-separator")'
            r'(?=[\\s\\S]*?</section>)'
        )
        match = opening.search(html_text)
        if match is None:
            raise RuntimeError(f"Could not locate separator for {code}")
        # Ensure the separator occurs before the first chapter in this book.
        start = match.start()
        end = html_text.find("</section>", start)
        chapter = html_text.find('class="chapter-start"', start, end)
        if chapter >= 0 and match.end() > chapter:
            raise RuntimeError(f"Separator occurs after chapter text for {code}")
        html_text = (
            html_text[:match.end()]
            + ' style="border-top-color: transparent"'
            + html_text[match.end():]
        )
    return html_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PrinceXML-ready HTML into PDF.")
    parser.add_argument("source", type=Path, help="Rendered HTML file")
    parser.add_argument("-o", "--output", type=Path, default=Path("kulish.pdf"))
    parser.add_argument("--prince", default="prince", help="PrinceXML executable")
    parser.add_argument(
        "--keep-page-start-separators",
        action="store_true",
        help="Disable automatic hiding of separators at the beginning of a page",
    )
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"HTML file not found: {args.source}")
    prince = shutil.which(args.prince)
    if prince is None:
        raise SystemExit("PrinceXML was not found in PATH.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    def run(source: Path, destination: Path) -> None:
        command = [prince, "--javascript", str(source), "-o", str(destination)]
        print("Running:", " ".join(command), flush=True)
        subprocess.run(command, check=True)

    if args.keep_page_start_separators:
        run(args.source, args.output)
    else:
        soup = BeautifulSoup(args.source.read_text(encoding="utf-8"), "html.parser")
        headings = {}
        for section in soup.select("section.print-book"):
            if section.select_one(".book-separator"):
                heading = section.select_one(".book-opening")
                if heading:
                    headings[section["id"].removeprefix("print-book-")] = heading.get_text(" ", strip=True).rstrip(".")
        del soup
        with tempfile.TemporaryDirectory(prefix="kulish-prince-") as directory:
            draft = Path(directory) / "draft.pdf"
            run(args.source, draft)
            suppressed = page_start_books(draft, headings)
            if suppressed:
                print("Hiding page-start separators:", ", ".join(sorted(suppressed)))
                modified = Path(directory) / "final.html"
                modified.write_text(
                    suppress_separators(args.source.read_text(encoding="utf-8"), suppressed),
                    encoding="utf-8",
                )
                run(modified, args.output)
                # The separator's border remains allocated; verify that no new
                # page-start headings appear after the second pagination.
                after = page_start_books(args.output, headings)
                if after != suppressed:
                    print("Warning: heading positions changed after second pass:",
                          sorted(after.symmetric_difference(suppressed)))
            else:
                shutil.copyfile(draft, args.output)
    print(f"Created: {args.output}")


if __name__ == "__main__":
    main()
