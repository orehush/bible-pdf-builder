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
Prince.addScriptFunc("page_header", function(firstMarker, lastMarker) {
    function unpack(value) {
        var parts = String(value || "").split("|");
        return {book: (parts[0] || "").trim(), chapter: (parts[1] || "").trim()};
    }
    var first = unpack(firstMarker);
    var last = unpack(lastMarker);
    if (!last.book) last = first;
    if (!last.book) return "";
    // Never mix chapter numbers belonging to different books.
    if (!first.book || first.book !== last.book) {
        return last.book + (last.chapter ? " " + last.chapter : "");
    }
    if (!first.chapter || !last.chapter || first.chapter === last.chapter) {
        return last.book + (last.chapter ? " " + last.chapter : "");
    }
    var from = Number(first.chapter), to = Number(last.chapter);
    if (Number.isInteger(from) && Number.isInteger(to) && to >= from) {
        var chapters = [];
        for (var n = from; n <= to; n++) chapters.push(String(n));
        return last.book + " " + chapters.join(", ");
    }
    return last.book + " " + first.chapter + ", " + last.chapter;
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
