from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, NavigableString, Tag

from .config import FOOTNOTE_SYMBOL_RE, OLD_TESTAMENT_CODES, TITLE_OVERRIDES
from .templates import (
    DOCUMENT_TEMPLATE,
    FRONT_MATTER_TEMPLATE,
    NEW_TESTAMENT_FRONT_MATTER_TEMPLATE,
    PAGE_HEADER_SCRIPT,
)


def clean_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_footnote(raw: str) -> tuple[str, str]:
    raw = clean_spaces(raw)
    match = FOOTNOTE_SYMBOL_RE.match(raw)
    if match:
        symbol, note = match.group(1), match.group(2).strip()
        if note.startswith("[") and note.endswith("]"):
            note = note[1:-1].strip()
        return symbol, note
    return "*", raw.strip("[] ")


def render_inline(node) -> str:
    if isinstance(node, NavigableString):
        return html.escape(str(node))
    if not isinstance(node, Tag):
        return ""

    classes = set(node.get("class", []))
    if "verse" in classes:
        return ""
    if "fn" in classes:
        symbol, note = parse_footnote(node.get_text(" ", strip=True))
        return (
            f'<span class="footnote" data-symbol="{html.escape(symbol, quote=True)}">'
            f"{html.escape(note)}</span>"
        )

    inner = "".join(render_inline(child) for child in node.children)
    if "wj" in classes:
        return f'<span class="wj">{inner}</span>'
    if node.name in {"em", "i"}:
        return f"<em>{inner}</em>"
    if node.name in {"strong", "b"}:
        return f"<strong>{inner}</strong>"
    return inner


def normalize_inline(value: str) -> str:
    value = re.sub(r"[ \t\r\n]+", " ", value)
    value = re.sub(r"\s+([,.;:!?…])", r"\1", value)
    return value.strip()


def split_paragraph_into_verses(paragraph: Tag):
    verses = []
    current_no = None
    current_parts = []

    def flush():
        nonlocal current_parts
        if current_no is not None:
            verses.append((current_no, normalize_inline("".join(current_parts))))
        current_parts = []

    for node in paragraph.children:
        if isinstance(node, Tag) and "verse" in node.get("class", []):
            flush()
            current_no = clean_spaces(node.get_text(" ", strip=True))
        elif current_no is not None:
            current_parts.append(render_inline(node))
    flush()
    return verses


def wrap_first_letter(text_html: str) -> str:
    in_tag = False
    chars = list(text_html)
    for index, char in enumerate(chars):
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag and char.isalpha():
            chars[index] = f'<span class="dropcap">{char}</span>'
            return "".join(chars)
    return text_html


def book_code(book: Tag) -> str:
    return book.get("id", "book-UNK").removeprefix("book-")


def book_title(book: Tag) -> str:
    code = book_code(book)
    if code in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[code]

    node = book.select_one(".mt")
    if not node:
        return code

    clone = BeautifulSoup(str(node), "html.parser").select_one(".mt")
    for footnote in clone.select(".fn"):
        footnote.decompose()
    return clean_spaces(clone.get_text(" ", strip=True)).rstrip(".")


def title_footnote(book: Tag) -> tuple[str, str] | None:
    node = book.select_one(".mt")
    if not node:
        return None
    footnote = node.select_one(".fn")
    if not footnote:
        return None
    return parse_footnote(footnote.get_text(" ", strip=True))


def render_verse(code: str, title: str, chapter_no: str, verse_no: str, text_html: str) -> str:
    marker = (
        f'<span class="chapter-page-marker" '
        f'data-book="{html.escape(title, quote=True)}" '
        f'data-chapter="{html.escape(chapter_no, quote=True)}" '
        f'data-header="{html.escape(title + "|" + chapter_no, quote=True)}">'
        f"{html.escape(chapter_no)}</span>"
    )

    if verse_no == "1":
        text_html = wrap_first_letter(text_html)
        return (
            f'<div class="verse-line first-verse" id="{code}-{chapter_no}-{verse_no}" '
            f'data-book-title="{html.escape(title, quote=True)}" data-chapter="{chapter_no}">'
            f'{marker}<span class="verse-text">{text_html}</span></div>'
        )

    return (
        f'<div class="verse-line" id="{code}-{chapter_no}-{verse_no}" '
        f'data-book-title="{html.escape(title, quote=True)}" data-chapter="{chapter_no}">'
        f'{marker}<span class="verse-no">{html.escape(verse_no)}</span>'
        f'<span class="verse-text">{text_html}</span></div>'
    )


def render_book(book: Tag, *, first_in_testament: bool = False) -> str:
    code = book_code(book)
    title = book_title(book)
    note = title_footnote(book)

    opening = html.escape(title)
    if note:
        opening += (
            f'<sup class="book-title-note-mark" '
            f'data-note-target="#title-footnote-{html.escape(code, quote=True)}"></sup>'
        )

    output = [
        f'<section class="print-book" id="print-book-{html.escape(code)}">',
        f'<div class="running-book-title">{html.escape(title)}</div>',
        '<div class="book-heading-band">',
        *([] if first_in_testament else ['<div class="book-separator" aria-hidden="true"></div>']),
        f'<h1 class="book-opening">{opening}.</h1>',
        '</div>',
    ]

    if note:
        symbol, note_text = note
        output.append(
            f'<span id="title-footnote-{html.escape(code, quote=True)}" '
            f'class="footnote title-footnote title-footnote-anchor" ' 
            f'data-symbol="{html.escape(symbol, quote=True)}">'
            f"{html.escape(note_text)}</span>"
        )

    chapters = book.select(":scope > .book-content > .chapter") or book.select(".chapter")
    for chapter in chapters:
        label = chapter.select_one(":scope > .chapterlabel")
        if label is None:
            continue

        chapter_no = clean_spaces(label.get_text(" ", strip=True))
        heading_word = "Псальма" if code == "PSA" else "Голова"
        output.append(
            f'<div class="chapter-start" id="{code}-chapter-{chapter_no}">'
            f'<span class="chapter-visible">{heading_word} {html.escape(chapter_no)}.</span>'
            "</div>"
        )

        for child in chapter.children:
            if not isinstance(child, Tag):
                continue
            classes = set(child.get("class", []))
            if "chapterlabel" in classes:
                continue
            if "p" in classes:
                for verse_no, text_html in split_paragraph_into_verses(child):
                    output.append(render_verse(code, title, chapter_no, verse_no, text_html))
            elif "s" in classes:
                source_heading = clean_spaces(child.get_text(" ", strip=True))
                if source_heading:
                    output.append(
                        f'<div class="source-heading">{html.escape(source_heading)}</div>'
                    )

    output.append("</section>")
    return "".join(output)


def source_toc_name(soup: BeautifulSoup, code: str, book: Tag) -> str:
    link = soup.select_one(f'a[href="#book-{code}"]')
    if link:
        return clean_spaces(link.get_text(" ", strip=True))
    return book_title(book)


def render_toc_columns(soup: BeautifulSoup, books: list[Tag], codes: list[str]) -> str:
    by_code = {book_code(book): book for book in books}
    entries = []

    for code in codes:
        book = by_code.get(code)
        if not book:
            continue

        name = source_toc_name(soup, code, book)
        chapters = len(
            book.select(":scope > .book-content > .chapter") or book.select(".chapter")
        )
        entries.append(
            '<div class="toc-row">'
            f'<div class="toc-name"><a href="#print-book-{html.escape(code)}">'
            f"{html.escape(name)}</a></div>"
            f'<div class="toc-chapters">{chapters}</div>'
            '<div class="toc-page-number">'
            f'<a href="#print-book-{html.escape(code)}"></a>'
            "</div></div>"
        )

    split = (len(entries) + 1) // 2
    columns = []
    for rows in (entries[:split], entries[split:]):
        columns.append(
            '<div class="toc-column">'
            '<div class="toc-row toc-header">'
            '<div class="toc-name">КНИГА</div>'
            '<div class="toc-chapters">ГОЛ.</div>'
            '<div class="toc-page-number">СТР.</div>'
            "</div>"
            + "".join(rows)
            + "</div>"
        )
    return '<div class="toc-columns">' + "".join(columns) + "</div>"


def render_frontmatter(soup: BeautifulSoup, books: list[Tag]) -> str:
    toc = render_toc_columns(soup, books, OLD_TESTAMENT_CODES)
    return FRONT_MATTER_TEMPLATE.format(toc=toc)


def render_new_testament_frontmatter(soup: BeautifulSoup, books: list[Tag]) -> str:
    new_codes = [
        book_code(book)
        for book in books
        if book_code(book) not in OLD_TESTAMENT_CODES
    ]
    toc = render_toc_columns(soup, books, new_codes)
    return NEW_TESTAMENT_FRONT_MATTER_TEMPLATE.format(toc=toc)


def css_with_absolute_resources(css_path: Path) -> str:
    """Resolve relative CSS url() resources against the stylesheet location."""
    css = css_path.read_text(encoding="utf-8")
    base_url = css_path.resolve().as_uri()

    def resolve_url(match: re.Match[str]) -> str:
        raw_url = match.group("url").strip().strip("\\\"'")
        if not raw_url or raw_url.startswith(("#", "data:")):
            return match.group(0)
        parsed = urlparse(raw_url)
        if parsed.scheme or raw_url.startswith("//"):
            return match.group(0)
        return f'url("{urljoin(base_url, raw_url)}")'

    return re.sub(
        r"url\(\s*(?P<url>[^)]*?)\s*\)",
        resolve_url,
        css,
        flags=re.IGNORECASE,
    )


def build_html(source: Path, output: Path, css_path: Path) -> None:
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    books = soup.select("section.book")

    old_books = [book for book in books if book_code(book) in OLD_TESTAMENT_CODES]
    new_books = [book for book in books if book_code(book) not in OLD_TESTAMENT_CODES]

    body = (
        render_frontmatter(soup, books)
        + '<div class="print-testament old-testament">'
        + "\n".join(render_book(book, first_in_testament=(i == 0)) for i, book in enumerate(old_books))
        + "</div>"
        + render_new_testament_frontmatter(soup, books)
        + '<div class="print-testament new-testament">'
        + "\n".join(render_book(book, first_in_testament=(i == 0)) for i, book in enumerate(new_books))
        + "</div>"
    )

    document = DOCUMENT_TEMPLATE.format(
        css=css_with_absolute_resources(css_path),
        javascript=PAGE_HEADER_SCRIPT,
        body=body,
    )
    output.write_text(document, encoding="utf-8")

    print(f"Created: {output}")
    print(f"Books: {len(books)}")
    print(f'Chapters: {len(soup.select(".chapter"))}')
    print(f'Verses: {len(soup.select(".verse"))}')
    print(f'Footnotes: {len(soup.select(".fn"))}')
