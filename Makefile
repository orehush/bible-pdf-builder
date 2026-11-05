.DEFAULT_GOAL := help

# Kulish input and output paths (override on the command line as needed).
KULISH_SOURCE ?= sources/bible/kulish_pulyuj_1905_corrected.html
KULISH_HTML_OUTPUT ?= html/kulish_bible_print.html
KULISH_PDF_OUTPUT ?= pdf/kulish_bible.pdf
KULISH_PROFILE ?= standard

.PHONY: help kulish-render-html kulish-render-pdf kulish-test-html kulish-test-pdf kulish-test kulish-render-large-html kulish-render-large-pdf kulish-render-pocket-html kulish-render-pocket-pdf

help:
	@printf '%s\n' \
	  'Available commands:' \
	  '  make / make help         Show this command list' \
	  '  make kulish-render-html  Generate print-ready HTML' \
	  '  make kulish-render-pdf   Generate HTML and PDF (requires PrinceXML)' \
	  '  make kulish-render-large-pdf   Generate 165x235 mm Bible' \
	  '  make kulish-render-pocket-pdf  Generate 80x130 mm Bible' \
	  '' \
	  'Override source with KULISH_SOURCE; select preset with KULISH_PROFILE.'

kulish-render-html:
	poetry run kulish-render-html "$(KULISH_SOURCE)" --output "$(KULISH_HTML_OUTPUT)" --profile "$(KULISH_PROFILE)"

kulish-render-pdf: kulish-render-html
	poetry run kulish-render-pdf "$(KULISH_HTML_OUTPUT)" --output "$(KULISH_PDF_OUTPUT)"

# Validate rendered output. PDF checks require PrinceXML and PyMuPDF.
.PHONY: kulish-test-html kulish-test-pdf kulish-test

kulish-test-html: kulish-render-html
	KULISH_SOURCE="$(KULISH_SOURCE)" KULISH_HTML_OUTPUT="$(KULISH_HTML_OUTPUT)" poetry run python -m unittest discover -s tests -p 'test_generated.py' -k GeneratedHTMLTests -v

kulish-test-pdf: kulish-render-pdf
	KULISH_SOURCE="$(KULISH_SOURCE)" KULISH_HTML_OUTPUT="$(KULISH_HTML_OUTPUT)" KULISH_PDF_OUTPUT="$(KULISH_PDF_OUTPUT)" poetry run python -m unittest discover -s tests -p 'test_generated.py' -v

kulish-test: kulish-test-pdf

# Dedicated outputs avoid overwriting the standard edition.
kulish-render-large-html:
	$(MAKE) kulish-render-html KULISH_PROFILE=large KULISH_HTML_OUTPUT=html/kulish_bible_large.html

kulish-render-large-pdf:
	$(MAKE) kulish-render-pdf KULISH_PROFILE=large KULISH_HTML_OUTPUT=html/kulish_bible_large.html KULISH_PDF_OUTPUT=pdf/kulish_bible_large.pdf

kulish-render-pocket-html:
	$(MAKE) kulish-render-html KULISH_PROFILE=pocket-size KULISH_HTML_OUTPUT=html/kulish_bible_pocket.html

kulish-render-pocket-pdf:
	$(MAKE) kulish-render-pdf KULISH_PROFILE=pocket-size KULISH_HTML_OUTPUT=html/kulish_bible_pocket.html KULISH_PDF_OUTPUT=pdf/kulish_bible_pocket.pdf
