# Vertical design systems

A **vertical design system** is a named family of templates that share:

- A **Typst theme file** — fonts, colours, page geometry, and reusable Typst components imported by every member template.
- A **Python base class** — shared Pydantic fields (e.g. `court`, `case_number`) that all templates in the family inherit, so data flows consistently across document types.
- **Shared assets** — optional fonts, images, or other resources bundled alongside the theme.

The architecture is intentionally lightweight: a family is just a naming convention plus a `TemplateFamily` descriptor object.
Existing standalone templates (report, invoice, letter, …) do not need to be refactored — they remain standalone while the pattern is proven on the **legal vertical**.

---

## Architecture overview

```
TemplateFamily          ← descriptor: name, description, theme_path
      │
      ├── LegalBase(Template)          ← shared Python fields
      │       ├── LegalBriefTemplate   ← legal-brief.typ
      │       └── LegalMemoTemplate    ← legal-memo.typ
      │
      └── legal-theme.typ              ← shared Typst components
              imported by legal-brief.typ & legal-memo.typ
```

### `TemplateFamily` descriptor

```python
from pathlib import Path
from typy.templates import TemplateFamily

legal = TemplateFamily(
    name="legal",
    description="Legal document vertical — court filings and memos.",
    theme_path=Path("path/to/legal-theme.typ"),
)
```

The descriptor is a plain Python object.
It carries the theme path so tooling can discover it, but it does not change rendering behaviour.

### Python base class

```python
from typy.templates import Template, TemplateFamily
from pydantic import BaseModel
from typing import ClassVar, Optional

class MyVerticalBase(Template):
    """Shared fields for all My Vertical templates."""

    # Declare family membership
    __template_family__: ClassVar[Optional[str]] = "my-vertical"

    # Shared fields
    organisation: str
    department: str
```

Every template in the family inherits from `MyVerticalBase` instead of `Template` directly, gaining all shared fields automatically.

### Typst theme file

Create a `my-theme.typ` file that defines:

- Colour palette variables
- Page setup function
- Typography rules
- Reusable component functions

```typst
// my-theme.typ

#let accent = rgb("#0055a4")

#let my-page-setup() = {
  set page(paper: "a4", margin: 2.5cm)
}

#let my-typography() = {
  set text(font: "New Computer Modern", size: 11pt)
  set par(justify: true)
}

#let my-header(title: "") = {
  align(center, text(weight: "bold", size: 14pt)[#title])
  line(length: 100%, stroke: 1pt + accent)
  v(0.5em)
}
```

Each template `.typ` file in the family imports the theme:

```typst
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data
#import "my-theme.typ": *

#let t = init_typy(typy_data)
#my-page-setup()
#my-typography()

#my-header(title: t("title", "str"))
#t("body", "content")
```

> **Note:** The typy document builder automatically copies sibling `.typ` files from the same directory as your template, so `my-theme.typ` will be available at compile time without any extra configuration.

### `.typy` package metadata

A `.typy` package can declare its family in `manifest.json` using the optional `family` field:

```json
{
  "manifest_version": 1,
  "name": "my-report",
  "version": "1.0.0",
  "description": "My vertical report template.",
  "author": "Jane Doe",
  "typy_compatibility": ">=0.8.0",
  "family": "my-vertical"
}
```

---

## The legal vertical (built-in)

The first built-in vertical is the **legal** family, shipping two templates:

| Template | Purpose |
|---|---|
| [`legal-brief`](templates.md#legal-brief) | Court filing with case caption, line numbering, signature block, certificate of service |
| [`legal-memo`](templates.md#legal-memo) | Internal legal memorandum — IRAC structure (Issue / Analysis / Conclusion) |

Both templates share:

- **`LegalBase`** — common fields: `court`, `case_number`, `jurisdiction`, `parties` (list of `LegalParty`), `attorney_info` (`LegalAttorneyInfo`)
- **`legal-theme.typ`** — shared Typst components: `case-caption`, `signature-block`, `certificate-of-service`, `with-line-numbers`

### Importing the legal family descriptor

```python
from typy.templates import legal_family

print(legal_family.name)        # "legal"
print(legal_family.theme_path)  # Path to legal-theme.typ
```

---

## Building a custom vertical (stub example)

The following shows how a third party could create a `clinical` vertical with its own base class and theme.

### Python models

```python
# clinical/templates.py
from pathlib import Path
from typing import ClassVar, Optional
from pydantic import BaseModel
from typy.templates import Template, TemplateFamily

clinical_family = TemplateFamily(
    name="clinical",
    description="Clinical document vertical for medical reports and consults.",
    theme_path=Path(__file__).parent / "clinical-theme.typ",
)


class ClinicalBase(Template):
    """Shared fields for all clinical templates."""

    __template_family__: ClassVar[Optional[str]] = "clinical"

    patient_name: str
    patient_id: str
    provider: str
    institution: str


class ClinicalReportTemplate(ClinicalBase):
    """A clinical report document."""

    from typy.content import Content

    document_title: str
    date: str
    findings: Content
    recommendations: Content

    __template_name__ = "clinical-report"
    __template_path__ = Path(__file__).parent / "clinical-report.typ"
```

### Typst theme

```typst
// clinical-theme.typ
#let clinical-accent = rgb("#00695c")  // teal

#let clinical-page-setup() = {
  set page(paper: "a4", margin: (top: 2cm, bottom: 2cm, left: 2.5cm, right: 2.5cm))
}

#let patient-header(name: "", id: "", provider: "", institution: "") = {
  grid(
    columns: (1fr, 1fr),
    [*Patient:* #name \ *ID:* #id],
    [*Provider:* #provider \ *Institution:* #institution],
  )
  line(length: 100%, stroke: 0.5pt + clinical-accent)
  v(0.5em)
}
```

### Template `.typ` file

```typst
// clinical-report.typ
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data
#import "clinical-theme.typ": *

#let t = init_typy(typy_data)
#clinical-page-setup()

#patient-header(
  name: t("patient_name", "str"),
  id: t("patient_id", "str"),
  provider: t("provider", "str"),
  institution: t("institution", "str"),
)

= #t("document_title", "str")

== Findings
#t("findings", "content")

== Recommendations
#t("recommendations", "content")
```

---

## See also

- [Template reference](templates.md) — field schemas for all built-in templates including the legal vertical
- [Package format](package-format.md) — how to bundle templates as `.typy` packages
- [Cookbook — legal document workflow](cookbook.md#12-generate-a-legal-brief-from-python) — end-to-end recipe
