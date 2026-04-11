# typy

typy is a Python library to generate reports, presentations, and other documents (for now, only PDFs) using Typst. The library offers an easy-to-use API to create documents from predefined templates, templates that you can create, or from scratch.

> [!WARNING]
> This library is still very experimental and for now my main goal is to test the idea as a whole.

typy is composed of two main components:
* the Python library, which is the interface to create documents
* the Typst library, which acts as glue code between the Python library and the Typst markup language.

## Installation

To install typy, you can use pip:

```bash
pip install git+https://github.com/mgoulao/typy
```

## Basic usage

The following code snippet shows how to create a simple PDF document using typy:

```python
from pathlib import Path

import pandas as pd

from typy.builder import (
    DocumentBuilder,
)
from typy.content import Content
from typy.functions import Block, Figure, Image, Table
from typy.markup import Text
from typy.templates import BasicTemplate

builder = DocumentBuilder()
# Files must be explicitly added to the document builder
img_path = builder.add_file(Path(__file__).parent / "example.png")

table_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

# Build like you would using Typst
body = Block(
    Content(
        [
            Text("This is a text"),
            Figure(Image(img_path), caption="This is a caption"),
            Figure(Table(table_df.to_dict()), caption="This is a caption"),
        ]
    )
)

template = BasicTemplate(
    title="Basic Template",
    date="2023-01-01",
    author="John Doe",
    body=body,
)

builder.add_template(template).save_pdf("basic.pdf")
```

### Result

![Basic PDF](./assets//example.png)


## Templates

### Typst

Templates in Typst must:
* import the `typy` Typst library which exposes the `init_typy` function, which initializes the data for the placeholder functions
* import the `typy_data.typ` file, which will be created by the Python library during build time and which will contain the data to be used in the template
* initialize typy using the `init_typy` function

```typst
#import "@preview/diatypst:0.4.0": *
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#show: slides.with(
  title: typy("title", "str"), // Required
  subtitle: "easy slides in typst",
  date: typy("date", "str"),
  authors: (typy("author", "str")),
  // Optional Styling (for more / explanation see in the typst universe)
  ratio: 16/9,
  layout: "medium",
  title-color: blue.darken(60%),
  toc: true,
)

= First Section

#typy("content1", "content")

== First Slide

#lorem(20)

/ *Term*: Definition
```

### Python

To declare a template in Python, you must:
1. Create a class that inherits from the `Template`
2. Define the default fields of the template (i.e. `__template_name__` and `__template_path__`)
3. Define the data model of the template by adding fields to the class

```python
from typy.templates import Template


@dataclass
class CustomTemplate(Template):
    title: str
    body: Content

    __template_name__ = "custom"
    __template_path__ = Path(__file__).parent / "custom.typ"
```


## Markdown support

You can use `Markdown` content anywhere a body or content is accepted. Markdown is rendered via the [`cmarker`](https://typst.app/universe/package/cmarker) Typst package — no Typst knowledge required.

```python
from typy.builder import DocumentBuilder
from typy.markup import Markdown
from typy.templates import BasicTemplate

body = Markdown("""
## Results

The analysis shows a **significant improvement** in performance.

| Metric     | Before | After |
| ---------- | ------ | ----- |
| Latency    | 120ms  | 45ms  |
| Throughput | 1000   | 3200  |
""")

builder = DocumentBuilder()
builder.add_template(BasicTemplate(
    title="Performance Report",
    date="2024-01-01",
    author="Jane Doe",
    body=body,
)).save_pdf("report.pdf")
```

`Markdown` supports standard CommonMark: headings, bold, italic, code blocks, links, images, lists, tables, and blockquotes. It also works inside a `Content` block alongside other elements:

```python
from typy.content import Content
from typy.markup import Markdown, Text

body = Content([
    Text("Summary: "),
    Markdown("## Details\n\nSee the **table** below."),
])
```

### Auto-conversion of raw strings in `Content` fields

Template fields typed as `Content` automatically convert a raw Python string to a `Markdown` object, so AI-generated or otherwise markdown-formatted text can be passed directly without any wrapper:

```python
from typy.templates import BasicTemplate

# Passing a raw string — auto-converted to Markdown
template = BasicTemplate(
    title="Report",       # str field: stays a plain string, NOT converted
    date="2024-01-01",
    author="Jane Doe",
    body="## Summary\n\nThis text is **automatically** rendered as markdown.",
    # ^^^ Content field: raw string is wrapped in Markdown(...)
)
```

**Rules:**

| Field type | Input           | Result                                                     |
| ---------- | --------------- | ---------------------------------------------------------- |
| `Content`  | `str`           | auto-converted to `Markdown(str)` and rendered via cmarker |
| `Content`  | `Content(...)`  | passed through unchanged                                   |
| `Content`  | `Markdown(...)` | passed through as a `Content` wrapping the `Markdown`      |
| `str`      | `str`           | stays a plain string — never converted                     |

An explicit `Markdown(...)` wrapper always works as an override and is passed through unchanged:

```python
from typy.markup import Markdown
from typy.templates import BasicTemplate

template = BasicTemplate(
    title="Report",
    date="2024-01-01",
    author="Jane Doe",
    body=Markdown("## Override\n\nExplicit wrapper still works."),
)
```

## CLI

typy ships a command-line interface for common document tasks without writing any Python.

```
typy [command] [options]
```

### `typy list`

List all available built-in templates.

```bash
typy list
```

**Output:**

| Name           | Description                                  |
| -------------- | -------------------------------------------- |
| `report`       | General-purpose report with TOC and sections |
| `invoice`      | Business invoice with line items             |
| `letter`       | Formal business letter                       |
| `cv`           | CV / resume                                  |
| `academic`     | Academic paper with citations                |
| `presentation` | Slide deck (16:9)                            |
| `basic`        | Basic single-section document                |

---

### `typy info <template>`

Print the field schema for a template.

```bash
typy info report
typy info report --json          # output as JSON
typy info ./my_template.py       # custom template from a .py file
```

| Option   | Description                             |
| -------- | --------------------------------------- |
| `--json` | Print schema as JSON instead of a table |

---

### `typy scaffold <template>`

Generate a sample `data.json` pre-filled with placeholder values for every field.

```bash
typy scaffold report                        # print to stdout
typy scaffold report --output data.json     # write to a file
typy scaffold ./my_template.py --output data.json
```

| Option            | Description                               |
| ----------------- | ----------------------------------------- |
| `--output <file>` | Write JSON to this file instead of stdout |

**Typical workflow:**

```bash
typy scaffold report --output data.json
# edit data.json …
typy render --template report --data data.json
```

---

### `typy render`

Render a PDF from a template and/or a Markdown file.

```bash
typy render --template report --data data.json
typy render --template report --data data.json --output report.pdf
typy render --markdown README.md                         # Markdown-only, no template required
typy render --template report --markdown body.md         # injects markdown into the body field
typy render --template report                            # renders with auto-generated sample data
typy render --template ./custom.typ --data data.json     # raw .typ file
```

| Option                    | Default      | Description                                                                                                                                                                          |
| ------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--template <name\|path>` | —            | Built-in template name (e.g. `report`), path to a `.py` file with a `Template` subclass, or path to a raw `.typ` file                                                                |
| `--data <file>`           | —            | Path to a JSON file with template field values                                                                                                                                       |
| `--markdown <file>`       | —            | Path to a Markdown file. When used without `--template`, renders standalone via `BasicTemplate`. When combined with `--template`, the file content is injected into the `body` field |
| `--output <file>`         | `output.pdf` | Destination PDF path                                                                                                                                                                 |

At least one of `--template` or `--markdown` must be provided.

When `--data` is omitted and no `--markdown` is given, sample data is auto-generated — useful for a quick preview. Run `typy scaffold` to get an editable JSON file.

---

The current code to encode the data into Typst markup is still very basic and only supports a few types, functions, and markup elements. **Most importantly, it is very buggy.**
