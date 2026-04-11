# Getting started

This page gets you from zero to your first PDF with both CLI and Python API.

## 1. Install typy

```bash
pip install git+https://github.com/mgoulao/typy
```

## 2. Render your first PDF with the CLI

```bash
typy scaffold report --output data.json
typy render --template report --data data.json --output first-report.pdf
```

## 3. Render Markdown directly

```bash
typy render --markdown README.md --output readme.pdf
```

## 4. Minimal Python example

```python
from typy.builder import DocumentBuilder
from typy.templates import BasicTemplate

template = BasicTemplate(
    title="Hello typy",
    date="2026-04-11",
    author="Your Name",
    body="## Welcome\n\nThis PDF was generated from Python.",
)

DocumentBuilder().add_template(template).save_pdf("hello-typy.pdf")
```

## 5. Understand what fields are required

```bash
typy info report --json
```

Use this JSON output as the source of truth before creating or validating `data.json`.

## Next

- Continue with complete examples in [cookbook](cookbook.md)
- Check built-in schemas in [template reference](templates.md)
- Explore modules in [API reference](api/index.md)
