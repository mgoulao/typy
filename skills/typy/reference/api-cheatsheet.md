# typy API Cheatsheet

Quick reference for the Python library surface. All symbols are importable
from the modules shown.

---

## DocumentBuilder

```python
from typy.builder import DocumentBuilder
```

| Method | Signature | Returns | Notes |
|---|---|---|---|
| `__init__` | `(verbose=False)` | `DocumentBuilder` | `verbose=True` prints generated Typst source |
| `add_template` | `(template: Template)` | `self` | Copies `.typ` file + encodes data → `typy_data.typ` |
| `add_typ_template` | `(typ_path: Path, data: dict \| None)` | `self` | Raw `.typ` file without a Python Template class |
| `add_file` | `(filepath: Path)` | `Path` | Registers a file asset; returns the relative path to use in content |
| `copy_assets_from` | `(source_dir: Path)` | `self` | Bulk-copy assets from a directory (best-effort) |
| `save_pdf` | `(filepath: Path)` | `None` | Compiles and writes the PDF |
| `to_buffer` | `()` | `BytesIO` | Compiles and returns PDF bytes in memory |
| `add_data` | `(data: dict \| Template)` | `self` | Low-level: write `typy_data.typ` directly |

### Typical call chain

```python
builder = DocumentBuilder()
img_path = builder.add_file(Path("logo.png"))   # must happen before add_template
builder.add_template(my_template).save_pdf("out.pdf")
```

> **Critical:** call `add_file` *before* constructing any `Content`/`Image`
> that references the asset path, and before calling `add_template`.

---

## Template base class

```python
from typy.templates import Template
```

Subclass Pydantic `BaseModel`. Required class attributes:

| Attribute | Type | Purpose |
|---|---|---|
| `__template_name__` | `str` | Logical name (used in error messages) |
| `__template_path__` | `Path` | Path to the `.typ` file on disk |

Fields must be Pydantic-compatible types. `Content` fields auto-convert raw
strings to `Markdown`.

---

## Built-in templates

```python
from typy.templates import (
    BasicTemplate,
    ReportTemplate,
    LetterTemplate,
    InvoiceTemplate,
    CVTemplate,
    AcademicTemplate,
    PresentationTemplate,
)
```

| Class | `__template_name__` | Key fields |
|---|---|---|
| `BasicTemplate` | `basic` | `title`, `date`, `author`, `body: Content` |
| `ReportTemplate` | `report` | `title`, `author`, `date`, `body: Content`, `subtitle?`, `abstract?`, `toc: bool` |
| `LetterTemplate` | `letter` | `sender_name`, `recipient_name`, `date`, `subject`, `body: Content`, `closing`, `signature_name` |
| `InvoiceTemplate` | `invoice` | `company_name`, `client_name`, `invoice_number`, `date`, `due_date`, `items: list[InvoiceItem]` |
| `CVTemplate` | `cv` | `name`, `contact: CVContact`, `experience`, `education`, `skills` |
| `AcademicTemplate` | `academic` | `title`, `authors: list[AcademicAuthor]`, `abstract`, `keywords`, `body: Content` |
| `PresentationTemplate` | `presentation` | `title`, `author`, `date`, `slides: list[Slide]` |

Run `typy info <name> --json` for machine-readable field schema.

---

## Content

```python
from typy.content import Content
```

Wraps a list of encodable items (markup, functions, strings) into a Typst
content block `[...]`.

```python
Content(item)           # single item
Content([item1, item2]) # list of items
```

A raw `str` passed to a `Content`-typed field is **automatically** wrapped in
`Markdown(str)`.

---

## Markup

```python
from typy.markup import Text, Raw, Heading, Markdown
```

| Class | Purpose | Example |
|---|---|---|
| `Text(text)` | Plain text string | `Text("Hello")` |
| `Raw(text)` | Unescaped Typst source | `Raw("auto")` |
| `Heading(level, text)` | Heading `= `, `== `, … | `Heading(2, "Section")` |
| `Markdown(text)` | CommonMark rendered via `cmarker` | `Markdown("**bold**")` |

---

## Functions

```python
from typy.functions import Block, Figure, Image, Table, Function, Datetime, Lorem
```

| Class | Typst equivalent | Key args |
|---|---|---|
| `Block(content, **kwargs)` | `#block(...)` | Any Typst block parameters |
| `Figure(content, **kwargs)` | `#figure(...)` | `caption=` |
| `Image(src: Path, **kwargs)` | `#image(...)` | `src` must be a path returned by `add_file` |
| `Table(data: dict, **kwargs)` | `#table(...)` | `data` keys → column headers; values are `{row_index: cell_value}` dicts |
| `Function(name, content, **kwargs)` | `#name(...)` | Generic Typst function call |
| `Datetime(date=None, **kwargs)` | `#datetime(...)` | `year/month/day` from a Python `datetime` |
| `Lorem(words=100)` | `#lorem(...)` | Placeholder text |

### Table data format

`Table` expects a `dict` where each key is a column header and each value is
a dict mapping row-index to cell value. A `pandas.DataFrame.to_dict()` call
produces exactly this format:

```python
import pandas as pd
from typy.functions import Table

df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
tbl = Table(df.to_dict())
```

---

## TypstEncoder (low-level)

```python
from typy.typst_encoder import TypstEncoder

TypstEncoder.encode(value)  # returns Typst source string
```

Supported Python → Typst mappings:

| Python type | Typst output | Notes |
|---|---|---|
| `str` | `"..."` | Escaped |
| `int`, `float` | literal | |
| `bool` | `true` / `false` | |
| `None` | `none` | |
| `list` | `(item, ...)` | |
| `dict` | `(key: value, ...)` | |
| `Path` | `"path/string"` | |
| `Encodable` subclasses | `.encode()` | `Content`, `Function`, `Markup` |
| `BaseModel` | dict of fields | Pydantic model |

**Known-fragile types:** complex nested structures and some edge cases in
`dict`-of-`dict` may raise `TypeError`. Fall back to pre-rendering the value
into a `Content(...)` block or a primitive string when this happens.
See [`troubleshooting.md`](troubleshooting.md) for details.
