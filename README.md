# Bible PDF Builder

Інструменти для створення друкованих HTML і PDF видань Біблії. Кожен переклад матиме власну реалізацію, конфігурацію та стилі; наразі доданий переклад Куліша. Спільну логіку між перекладами можна винести окремо, коли це стане потрібним.

## Структура проєкту

```text
.
├── pyproject.toml
├── .python-version              # Python 3.13
├── poetry.lock                 # створюється командою poetry lock
├── Makefile                    # команди kulish-render-html / kulish-render-pdf
├── README.md
├── sources/
│   ├── bible/                  # вихідний HTML тексту Куліша
│   └── cross-references/       # дані перехресних посилань
├── src/kulish/
│   ├── builder/
│   │   ├── config.py           # конфігурація перекладу
│   │   ├── renderer.py         # перетворення вихідного HTML
│   │   └── templates.py        # HTML-шаблони
│   ├── scripts/
│   │   ├── render_html.py      # створення HTML для друку
│   │   └── render_pdf.py       # запуск PrinceXML
│   └── styles/styles.css       # стилі верстки Куліша
├── html/                       # згенерований HTML
└── pdf/                        # згенерований PDF
```

## Вимоги

- Python 3.13 (версія вказана у `.python-version` і обмежена в `pyproject.toml`).
- [Poetry](https://python-poetry.org/docs/#installation) для керування Python-залежностями.
- GNU Make для коротких команд з Makefile.
- PrinceXML для створення PDF. Це окрема програма; Poetry її не встановлює. Команда `prince` має бути доступна в `PATH`.
- Для найкращого відтворення верстки бажано встановити Gentium Book Plus; CSS має запасні шрифти.

## Встановлення

Переконайтеся, що Python 3.13 встановлений. Якщо Poetry не вибрала його автоматично, вкажіть інтерпретатор із `.python-version`, а тоді встановіть залежності та пакет:

```bash
poetry env use "$(cat .python-version)"
poetry install
```

Для повторюваного встановлення зберігайте `poetry.lock` у системі контролю версій. Створити чи оновити lock-файл можна командою `poetry lock`.

Перевірте наявність інструментів:

```bash
poetry run python --version
make --version
prince --version
```

## Створення HTML та PDF

Команди Make запускаються з кореня проєкту. Виклик `make` без аргументів і `make help` показують довідку:

```bash
make
make help
make kulish-render-html
make kulish-render-pdf
```

`kulish-render-html` створює `html/kulish_bible_print.html` із `sources/bible/kulish_pulyuj_1905_corrected.html`. `kulish-render-pdf` спочатку виконує HTML-етап, а потім створює `pdf/kulish_bible.pdf` за допомогою PrinceXML із JavaScript для динамічних колонтитулів.

Шляхи джерела та результатів для перекладу Куліша можна перевизначити при виклику Make:

```bash
make kulish-render-html KULISH_SOURCE=path/to/source.html KULISH_HTML_OUTPUT=html/edition.html
make kulish-render-pdf KULISH_SOURCE=path/to/source.html KULISH_HTML_OUTPUT=html/edition.html KULISH_PDF_OUTPUT=pdf/edition.pdf
```

CLI-довідка:

```bash
poetry run kulish-render-html --help
poetry run kulish-render-pdf --help
```

За замовчуванням для HTML використовується `src/kulish/styles/styles.css`. Інший CSS-файл можна вказати напряму:

```bash
poetry run kulish-render-html path/to/source.html --styles path/to/styles.css -o html/output.html
```

## Що налаштовувати

- `src/kulish/styles/styles.css` — формат сторінок, колонки, колонтитули, зноски та інші стилі верстки Куліша.
- `src/kulish/builder/config.py` — параметри розбору книг, назви та символи зносок.
- `src/kulish/builder/templates.py` — HTML-шаблони й JavaScript колонтитулів.
- `src/kulish/builder/renderer.py` — розбір вихідного HTML і побудова друкованої версії.
- `src/kulish/scripts/` — CLI-команди.
- `Makefile` — команди та шляхи джерела й результатів для Куліша.
