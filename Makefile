.DEFAULT_GOAL := help

# Kulish input and output paths (override on the command line as needed).
KULISH_SOURCE ?= sources/bible/kulish_pulyuj_1905_corrected.html
KULISH_HTML_OUTPUT ?= html/kulish_bible_print.html
KULISH_PDF_OUTPUT ?= pdf/kulish_bible.pdf

.PHONY: help kulish-render-html kulish-render-pdf

help:
	@printf '%s\n' \
	  'Available commands:' \
	  '  make / make help         Show this command list' \
	  '  make kulish-render-html  Generate print-ready HTML' \
	  '  make kulish-render-pdf   Generate HTML and PDF (requires PrinceXML)' \
	  '' \
	  'Override paths with KULISH_SOURCE, KULISH_HTML_OUTPUT, and KULISH_PDF_OUTPUT.'

kulish-render-html:
	poetry run kulish-render-html "$(KULISH_SOURCE)" --output "$(KULISH_HTML_OUTPUT)"

kulish-render-pdf: kulish-render-html
	poetry run kulish-render-pdf "$(KULISH_HTML_OUTPUT)" --output "$(KULISH_PDF_OUTPUT)"
