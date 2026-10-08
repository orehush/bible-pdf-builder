from __future__ import annotations

DOCUMENT_TEMPLATE = """<!doctype html>
<html lang="uk">
<head>
<meta charset="utf-8">
<title>Біблія Куліша — друкована версія</title>
<style>
{css}
</style>
<script>
{javascript}
</script>
</head>
<body>{body}</body>
</html>
"""

PAGE_HEADER_SCRIPT = r"""
Prince.addScriptFunc("page_header", function(book, firstChapter, lastChapter) {
    book = String(book || "").trim();
    firstChapter = String(firstChapter || "").trim();
    lastChapter = String(lastChapter || "").trim();

    if (!firstChapter && !lastChapter) return book;
    if (!firstChapter) return book + " " + lastChapter;
    if (!lastChapter || firstChapter === lastChapter) {
        return book + " " + firstChapter;
    }

    var first = parseInt(firstChapter, 10);
    var last = parseInt(lastChapter, 10);

    if (!isNaN(first) && !isNaN(last) && last >= first) {
        var chapters = [];
        for (var chapter = first; chapter <= last; chapter++) {
            chapters.push(String(chapter));
        }
        return book + " " + chapters.join(", ");
    }

    return book + " " + firstChapter + ", " + lastChapter;
});
"""

FRONT_MATTER_TEMPLATE = """
<section class="front-page front-blank"></section>
<section class="front-page front-blank"></section>
<section class="front-page front-title-page">
    <div>СЬВЯТЕ ПИСЬМО</div>
    <div>СТАРОГО І НОВОГО ЗАВІТУ.</div>
</section>
<section class="front-page front-blank"></section>
<section class="front-page front-toc-page">
    <h1 class="front-toc-title">ЗМІСТ СТАРОГО ЗАВІТУ.</h1>
    {toc}
</section>
<section class="front-page front-blank"></section>
"""

NEW_TESTAMENT_FRONT_MATTER_TEMPLATE = """
<section class="front-page front-blank nt-front-start"></section>
<section class="front-page front-title-page">
    <div>СЬВЯТЕ ПИСЬМО НОВОГО ЗАВІТУ.</div>
</section>
<section class="front-page front-blank"></section>
<section class="front-page front-toc-page">
    <h1 class="front-toc-title">ЗМІСТ НОВОГО ЗАВІТУ.</h1>
    {toc}
</section>
<section class="front-page front-blank"></section>
"""
