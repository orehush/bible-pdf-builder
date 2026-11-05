"""Focused regression tests for carrying notes across book boundaries."""
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from kulish.builder import renderer


class CarryFootnotesTests(unittest.TestCase):
    def test_carry_multiple_notes_preserves_source_references_and_order(self):
        books = BeautifulSoup(
            '<section class="book" id="book-ISA"></section>'
            '<section class="book" id="book-JER"></section>',
            "html.parser",
        ).select(".book")
        html = {
            "ISA": (
                '<section class="print-book" id="print-book-ISA">'
                '<div class="verse-line"><span class="verse-text">'
                'A<span class="footnote">First</span> B'
                '<span class="footnote">Second</span></span></div></section>'
            ),
            "JER": (
                '<section class="print-book" id="print-book-JER">'
                '<div class="verse-line"><span class="verse-text">C</span></div>'
                '</section>'
            ),
        }
        with patch.object(renderer, "FOOTNOTE_CARRY_TO_NEXT_BOOK", {
            "ISA": {"target": "JER", "count": 2}
        }), patch.object(renderer, "render_book", side_effect=lambda b, **kw: html[renderer.book_code(b)]):
            result = renderer.render_testament_books(books)
            # A carry configured for ISA must not break rendering of the NT.
            nt = BeautifulSoup('<section class="book" id="book-ROM"></section>', "html.parser").select(".book")
            self.assertIn("ROM", renderer.render_testament_books(nt))

        soup = BeautifulSoup(result, "html.parser")
        source = soup.select_one("#print-book-ISA")
        target = soup.select_one("#print-book-JER")
        refs = source.select(".carried-footnote-reference")
        notes = target.select(".carried-footnote")
        self.assertEqual(len(refs), 2)
        self.assertEqual([n.get_text() for n in notes], ["First", "Second"])
        self.assertEqual(
            [r["data-note-target"] for r in refs],
            ["#carried-footnote-ISA-1", "#carried-footnote-ISA-2"],
        )
        self.assertEqual([n["id"] for n in notes],
                         ["carried-footnote-ISA-1", "carried-footnote-ISA-2"])

    def test_legacy_shorthand(self):
        books = BeautifulSoup(
            '<section class="book" id="book-ISA"></section>'
            '<section class="book" id="book-JER"></section>', "html.parser"
        ).select(".book")
        html = {
            "ISA": '<section><span class="footnote">Note</span></section>',
            "JER": '<section><div class="verse-line"><span class="verse-text">Text</span></div></section>',
        }
        with patch.object(renderer, "FOOTNOTE_CARRY_TO_NEXT_BOOK", {"ISA": "JER"}), patch.object(
            renderer, "render_book", side_effect=lambda b, **kw: html[renderer.book_code(b)]
        ):
            result = renderer.render_testament_books(books)
        self.assertEqual(result.count('class="carried-footnote-reference"'), 1)


if __name__ == "__main__":
    unittest.main()
