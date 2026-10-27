# Kulish HTML/PDF integrity tests

The suite compares the generated HTML with the source Bible, including book order (66 books), chapter count (1189), verse IDs, first-verse drop caps, contents links, headings and footnotes. PDF checks cover readability, initial blank pages, title pages and the expected trim size.

## Run

Install Poetry dependencies and the PDF test dependency:

```sh
poetry lock
poetry install --with dev
make kulish-test-html
make kulish-test-pdf
# or:
make kulish-test
```

The PDF target requires PrinceXML installed and available as `prince`. `make kulish-test-html` does not require PrinceXML or PyMuPDF.

Output locations can be overridden using `KULISH_SOURCE`, `KULISH_HTML_OUTPUT`, and `KULISH_PDF_OUTPUT`.

**Note:** The generated PDF has not been validated in this GitHub commit environment; run the full suite locally or in CI. Refresh `poetry.lock` after adding the development dependency.
