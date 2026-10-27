"""Regression checks for the generated Kulish Bible HTML and PDF."""
import os
import re
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from kulish.builder.config import OLD_TESTAMENT_CODES
from kulish.builder.renderer import book_code, clean_spaces, split_paragraph_into_verses

SOURCE = Path(os.getenv("KULISH_SOURCE", "sources/bible/kulish_pulyuj_1905_corrected.html"))
HTML = Path(os.getenv("KULISH_HTML_OUTPUT", "html/kulish_bible_print.html"))
PDF = Path(os.getenv("KULISH_PDF_OUTPUT", "pdf/kulish_bible.pdf"))

def chapters(book):
    return book.select(":scope > .book-content > .chapter") or book.select(".chapter")

class GeneratedHTMLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert SOURCE.is_file() and HTML.is_file(), "Run make kulish-render-html first"
        cls.source = BeautifulSoup(SOURCE.read_text(encoding="utf-8"), "html.parser")
        cls.html = BeautifulSoup(HTML.read_text(encoding="utf-8"), "html.parser")

    def test_book_count_and_order(self):
        source = [book_code(b) for b in self.source.select("section.book")]
        output = [b["id"].removeprefix("print-book-") for b in self.html.select("section.print-book")]
        self.assertEqual(len(source), 66)
        self.assertEqual(len(set(source)), 66)
        self.assertEqual(source[:39], OLD_TESTAMENT_CODES)
        self.assertEqual(output, source)

    def test_chapters_and_verses(self):
        count = 0
        for book in self.source.select("section.book"):
            code = book_code(book)
            output = self.html.select_one(f"#print-book-{code}")
            self.assertIsNotNone(output)
            expected = {}
            for chapter in chapters(book):
                label = chapter.select_one(":scope > .chapterlabel")
                if label is None:
                    continue
                number = clean_spaces(label.get_text(" ", strip=True))
                verses = []
                for paragraph in chapter.select(".p"):
                    verses.extend(str(n) for n, _ in split_paragraph_into_verses(paragraph))
                self.assertNotIn(number, expected)
                expected[number] = verses
            count += len(expected)
            labels = [n["id"].removeprefix(f"{code}-chapter-") for n in output.select(".chapter-start")]
            self.assertEqual(labels, list(expected), code)
            for number, verses in expected.items():
                actual = [v["id"].removeprefix(f"{code}-{number}-") for v in output.select(f'.verse-line[id^="{code}-{number}-"]')]
                self.assertEqual(actual, verses, f"{code} {number}")
        self.assertEqual(count, 1189)

    def test_unique_verse_ids_and_first_verses(self):
        lines = self.html.select(".verse-line")
        ids = [v.get("id") for v in lines]
        self.assertEqual(len(ids), len(set(ids)))
        for chapter in self.html.select(".chapter-start"):
            code, number = chapter["id"].split("-chapter-", 1)
            first = self.html.select_one(f'[id="{code}-{number}-1"]')
            if first:
                self.assertIn("first-verse", first.get("class", []))
                self.assertIsNone(first.select_one(".verse-no"))
                self.assertIsNotNone(first.select_one(".dropcap"))

    def test_books_share_column_flow_and_have_separators(self):
        testaments = self.html.select(".print-testament")
        self.assertEqual([len(t.select(":scope > .print-book")) for t in testaments], [39, 27])
        for testament in testaments:
            books = testament.select(":scope > .print-book")
            self.assertIsNone(books[0].select_one(".book-separator"))
            for book in books[1:]:
                separator = book.select_one(".book-separator")
                self.assertIsNotNone(separator, book.get("id"))
                self.assertIsNotNone(separator.find_next_sibling("h1", class_="book-opening"))
        css = self.html.select_one("style").get_text()
        self.assertIn(".print-testament", css)
        self.assertIn("column-fill: auto", css)
        self.assertIn("float: footnote", css)

    def test_toc_and_headings(self):
        books = self.html.select("section.print-book")
        self.assertEqual(len(self.html.select(".book-opening")), 66)
        self.assertEqual(len(self.html.select(".running-book-title")), 66)
        pages = self.html.select(".front-toc-page")
        self.assertEqual([len(p.select(".toc-row:not(.toc-header)")) for p in pages], [39, 27])
        for page in pages:
            for row in page.select(".toc-row:not(.toc-header)"):
                link = row.select_one(".toc-name a")
                self.assertIsNotNone(link)
                target = self.html.select_one(link["href"])
                self.assertIsNotNone(target)
                code = link["href"].removeprefix("#print-book-")
                source_book = self.source.select_one(f"#book-{code}")
                self.assertIsNotNone(source_book)
                self.assertEqual(int(row.select_one(".toc-chapters").get_text(strip=True)), len([c for c in chapters(source_book) if c.select_one(":scope > .chapterlabel")]))
        self.assertEqual(len(books), 66)

    def test_footnotes(self):
        for book in self.source.select("section.book"):
            code = book_code(book)
            rendered = self.html.select_one(f"#print-book-{code}")
            self.assertEqual(len(rendered.select(".footnote")), len(book.select(".fn")), code)
            self.assertEqual(len(rendered.select(".title-footnote")), len(book.select(".mt .fn")), code)
            for note in rendered.select(".footnote"):
                self.assertTrue(note.get_text(" ", strip=True), code)
        self.assertEqual(len(self.html.select(".footnote")), len(self.source.select(".fn")))

    def test_template_resolved(self):
        text = HTML.read_text(encoding="utf-8")
        self.assertNotIn("{toc}", text)
        self.assertIn("Prince.addScriptFunc", text)
        self.assertIn("@page", text)

class GeneratedPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert PDF.is_file(), "Run make kulish-render-pdf first"
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("Install PyMuPDF: poetry install --with dev") from exc
        cls.doc = fitz.open(PDF)
        cls.pages = [p.get_text("text") for p in cls.doc]
        cls.text = "\n".join(cls.pages)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "doc"):
            cls.doc.close()

    def test_readable_pdf(self):
        self.assertGreater(len(self.doc), 100)
        self.assertGreater(sum(map(len, self.pages)), 100000)

    def test_front_matter(self):
        self.assertFalse(self.pages[0].strip())
        self.assertFalse(self.pages[1].strip())
        for title in ("СЬВЯТЕ ПИСЬМО", "ЗМІСТ СТАРОГО ЗАВІТУ", "ЗМІСТ НОВОГО ЗАВІТУ"):
            self.assertIn(title, self.text)

    def test_trim_size(self):
        for page in self.doc:
            self.assertAlmostEqual(page.rect.width, 125 * 72 / 25.4, delta=1)
            self.assertAlmostEqual(page.rect.height, 176 * 72 / 25.4, delta=1)

if __name__ == "__main__":
    unittest.main()
