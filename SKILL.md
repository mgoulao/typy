---
name: typy
description: Use when the user wants to generate a PDF report, slide deck, or
  document from Python using Typst — including discovering built-in templates,
  filling a template with data (tables, figures, images, prose), authoring a
  new Typst or Python template, or exporting/importing a .typy template
  package. Covers the DocumentBuilder API, the init_typy + typy_data.typ
  convention, and the .typy packaging workflow. Do NOT use for raw Typst-only
  projects without the typy Python layer, or for generating non-PDF formats.
---

# typy Skill — Agent Workflow Guide

typy is a Python library that generates PDFs from Typst templates. It exposes
three distinct surfaces an agent must not confuse:

| Surface | What it is |
|---|---|
| **Typst template** | A `.typ` file using `init_typy` + `typy_data.typ` |
| **Python `Template` subclass** | A Pydantic model that binds to a `.typ` file via `__template_path__` |
| **`.typy` package** | A distributable bundle (export/import via CLI — *planned*) |

---

## Flow router — pick one

```
User intent
├── "render / generate / produce / build a PDF from <data>"  ──► Flow A: Consume
├── "create / design / author / scaffold a new template"     ──► Flow B: Author
└── "share / export / install / distribute a template"       ──► Flow C: Package
```

---

## Flow A — Consume an existing template

### Quick path (copy-paste)

```python
from typy.builder import DocumentBuilder
from typy.templates import BasicTemplate

builder = DocumentBuilder()
template = BasicTemplate(
    title="My Report",
    date="2024-01-01",
    author="Jane Doe",
    body="## Summary\n\nResults look **great**.",  # str auto-converts to Markdown
)
builder.add_template(template).save_pdf("output.pdf")
```

### Standard path (assets + table + image)

See [`examples/consume-basic.py`](examples/consume-basic.py) for a complete
example that adds an image and a data table.

Key rules:
1. **Always register assets via `builder.add_file(path)`** — do not pass raw
   filesystem paths to `Image(...)` or template fields; they won't be found
   during compilation.
2. Use the returned relative path from `add_file` as the argument to `Image(...)`.
3. Chain: `builder.add_template(tmpl).save_pdf("out.pdf")`.

```python
from pathlib import Path
from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Block, Figure, Image, Table
from typy.templates import BasicTemplate

builder = DocumentBuilder()

# Register assets BEFORE constructing Content that references them
img_path = builder.add_file(Path("chart.png"))

body = Block(Content([
    Figure(Image(img_path), caption="Sales chart"),
    Figure(Table({"Month": {0:"Jan",1:"Feb"}, "Sales": {0:100,1:120}}), caption="Data"),
]))

builder.add_template(BasicTemplate(
    title="Sales Report",
    date="2024-01-01",
    author="Alice",
    body=body,
)).save_pdf("sales.pdf")
```

### Discover available templates

```bash
typy list                         # table of built-in templates
typy info report                  # human-readable field schema
typy info report --json           # machine-readable JSON schema (prefer for automation)
typy scaffold report              # print sample data.json to stdout
typy scaffold report --output data.json
```

Built-in template names: `basic`, `report`, `letter`, `invoice`, `cv`,
`academic`, `presentation`.

### Render via CLI (no Python required)

```bash
typy scaffold report --output data.json
# edit data.json ...
typy render --template report --data data.json --output report.pdf

# Markdown-only (uses BasicTemplate automatically)
typy render --markdown README.md --output readme.pdf

# Inject markdown into template body field
typy render --template report --markdown body.md --output report.pdf
```

### Verify the output

```bash
python scripts/verify_pdf.py output.pdf
```

On error, consult [`reference/troubleshooting.md`](reference/troubleshooting.md).

### Advanced path

→ [`reference/api-cheatsheet.md`](reference/api-cheatsheet.md) — full API surface  
→ [`reference/template-authoring.md`](reference/template-authoring.md) — encoding details

---

## Flow B — Author a new template

### Choose a surface

| Surface | When to use |
|---|---|
| **Python subclass only** | Layout is expressible via existing blocks; no custom Typst styling needed |
| **Typst-backed template** | Custom page layout, fonts, colours, or Typst-specific packages required |

### Quick path — Python subclass

```python
from pathlib import Path
from typy.content import Content
from typy.templates import Template

class MyTemplate(Template):
    title: str
    subtitle: str = ""
    body: Content

    __template_name__ = "my_template"
    __template_path__ = Path(__file__).parent / "my_template.typ"
```

Pair it with a matching `.typ` file — see Quick path below.

### Quick path — Typst file

```typst
// my_template.typ
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

= #typy("title", "str")
#typy("subtitle", "str")

#typy("body", "content")
```

**Required boilerplate** (all three lines are mandatory):
1. `#import "typy.typ": init_typy`
2. `#import "typy_data.typ": typy_data`
3. `#let typy = init_typy(typy_data)`

### Standard path

See [`examples/author-python-template.py`](examples/author-python-template.py)
and [`examples/author-typst-template.typ`](examples/author-typst-template.typ).

### Roundtrip test

After authoring, always render twice:

```python
# Minimal instance — catches missing-field bugs
builder = DocumentBuilder()
builder.add_template(MyTemplate(title="Test", body="Hello.")).save_pdf("/tmp/minimal.pdf")

# Realistic instance
builder2 = DocumentBuilder()
builder2.add_template(MyTemplate(title="Real", subtitle="Sub", body="Content.")).save_pdf("/tmp/realistic.pdf")

# Verify both
import subprocess
subprocess.run(["python", "scripts/verify_pdf.py", "/tmp/minimal.pdf"], check=True)
subprocess.run(["python", "scripts/verify_pdf.py", "/tmp/realistic.pdf"], check=True)
```

### Advanced path

→ [`reference/template-authoring.md`](reference/template-authoring.md) — deep dive on the Python↔Typst contract  
→ [`reference/typst-primer.md`](reference/typst-primer.md) — Typst syntax agents need  
→ [`reference/troubleshooting.md`](reference/troubleshooting.md) — encoding errors and fixes

---

## Flow C — Package / distribute

> **Status:** `.typy` packaging is planned (see issue #38). The `typy package`
> CLI subcommand is not yet available. Use this flow when it lands.

See [`reference/packaging.md`](reference/packaging.md) for the planned workflow
and how to track when it is available.

---

## Installation into agent runtimes

| Runtime | How to install |
|---|---|
| **Claude Code / Claude.ai** | Copy or symlink this `SKILL.md` (and the `reference/` folder) into your Claude skills directory, or reference the file path in your project configuration. |
| **Codex** | Place `SKILL.md` under `.agents/skills/typy/` in the consuming repo; Codex picks it up automatically. |
| **Generic / MCP** | Reference `SKILL.md` via the runtime's skill-loading or context-injection mechanism. |

**Versioning:** The skill version tracks typy releases. Pin the skill
commit/tag to the typy version you are using. Bump the skill whenever any
public-API surface documented here changes.
