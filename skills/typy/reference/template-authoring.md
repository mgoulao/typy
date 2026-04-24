# Template Authoring — Python ↔ Typst Contract

This document explains how to author a new template that works with typy's
Python layer.

---

## Overview

Every typy template consists of two parts:

1. **A Python class** (`Template` subclass) — declares the data fields and
   points to the `.typ` file.
2. **A Typst `.typ` file** — the layout that renders those fields.

The Python library compiles the field data into a `typy_data.typ` file at
build time. The `.typ` file imports that generated file and accesses the
values using the `typy("field_name", "type")` accessor.

---

## Python class contract

```python
from pathlib import Path
from typing import Optional
from typy.content import Content
from typy.templates import Template

class MyReportTemplate(Template):
    # --- Required class-level attributes ---
    __template_name__ = "my_report"        # logical name; used in error messages
    __template_path__ = Path(__file__).parent / "my_report.typ"

    # --- Data fields (Pydantic model fields) ---
    title: str
    author: str
    date: str
    summary: Optional[str] = None          # optional with default
    body: Content                          # rich content block
```

### Rules

- **Inherit from `Template`** (which extends `pydantic.BaseModel`).
- **Set `__template_name__`** to a unique string identifier.
- **Set `__template_path__`** to the absolute path of the matching `.typ`
  file (use `Path(__file__).parent / ...` to stay portable).
- **Field types** must be encodable (see `reference/api-cheatsheet.md` for
  supported types). `Content` fields accept `str`, `Markdown`, `Content`,
  or any `Encodable`.
- The class does *not* need `@dataclass` — Pydantic handles validation and
  serialisation.

### Nested models

Nested `BaseModel` subclasses are supported:

```python
from pydantic import BaseModel

class Author(BaseModel):
    name: str
    email: str

class PaperTemplate(Template):
    __template_name__ = "paper"
    __template_path__ = Path(__file__).parent / "paper.typ"

    title: str
    authors: list[Author]
    body: Content
```

---

## Typst file contract

### Minimum required boilerplate

```typst
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)
```

**All three lines are mandatory.** Omitting any of them causes the template
to render with empty fields or raise a Typst compilation error.

### Accessing fields

```typst
#typy("field_name", "type_hint")
```

`type_hint` tells typy how to interpret the value. Common type hints:

| Python field type | Typst type hint |
|---|---|
| `str` | `"str"` |
| `int` / `float` | `"str"` (safe) or `"int"` |
| `Content` | `"content"` |
| `bool` | `"bool"` |
| `list[str]` | `"list"` |

### Full template example

```typst
// my_report.typ
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#set page(margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)

// Title block
#align(center)[
  #text(size: 18pt, weight: "bold")[#typy("title", "str")]
  \
  #text(size: 12pt)[#typy("author", "str") — #typy("date", "str")]
]

#v(1em)

// Optional summary
#if typy("summary", "str") != "" [
  #block(fill: luma(230), inset: 8pt, radius: 4pt)[
    #typy("summary", "str")
  ]
  #v(0.5em)
]

// Body content
#typy("body", "content")
```

---

## Directory-based templates

When `__template_path__` points to a **directory** (instead of a single
`.typ` file), the entire directory is copied into the build environment.
The entry point must be named `main.typ` inside that directory.

```
my_template/
├── main.typ          ← entry point
├── components.typ    ← imported by main.typ
└── logo.png          ← asset referenced in main.typ
```

```python
class MyTemplate(Template):
    __template_name__ = "my_template"
    __template_path__ = Path(__file__).parent / "my_template"   # directory
    title: str
    body: Content
```

This is the recommended structure for complex templates that use multiple
`.typ` files or bundled assets.

---

## Asset handling

Assets (images, logos, etc.) referenced inside the `.typ` file itself (not
passed as Python field values) must be co-located with the template. If the
template is a single `.typ` file, use a directory-based template and place
assets in that directory.

Assets passed as *field values* from Python must be registered with
`builder.add_file(path)` and the returned relative path used in content:

```python
builder = DocumentBuilder()
img_path = builder.add_file(Path("chart.png"))   # returns relative path

template = MyTemplate(
    title="Report",
    body=Content([Figure(Image(img_path))]),      # use relative path here
)
builder.add_template(template).save_pdf("out.pdf")
```

---

## Encoding notes

The `TypstEncoder` converts Python values to Typst source. The following
patterns are known-safe:

- `str`, `int`, `float`, `bool`, `None` — fully supported
- `list[str]`, `list[int]` — fully supported
- `dict` with string keys and primitive values — supported
- Pydantic `BaseModel` subclasses — supported (encoded as Typst dict)
- `Content`, `Function`, `Markup` subclasses — supported via `.encode()`

**Known-fragile paths:**
- Very deeply nested dicts/models may produce unexpected Typst output.
- `Path` fields are encoded as strings — ensure the paths are registered
  via `add_file` first.

When encoding fails, the fallback is to pre-render the value into a
`Content(...)` block or a plain string before passing it to the template.
See [`troubleshooting.md`](troubleshooting.md) for the full error table.
