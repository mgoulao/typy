# Template reference

typy ships seven built-in templates, all sharing a consistent colour palette
(blue-600 `#2563eb` accent, slate body text) and typographic family.

## Templates at a glance

| Template | Best for | Key fields |
|---|---|---|
| `report` | Multi-section reports with TOC | `title`, `author`, `body`, `abstract`, `toc` |
| `invoice` | Business invoices with line items | `company_name`, `client_name`, `items`, `tax_rate` |
| `letter` | Formal letters with letterhead | `sender_name`, `recipient_name`, `subject`, `body` |
| `cv` | CV / résumé | `name`, `contact`, `experience`, `education`, `skills` |
| `academic` | Academic papers with bibliography | `title`, `authors`, `abstract`, `body`, `two_column` |
| `presentation` | 16:9 slide decks | `title`, `author`, `slides` (each with `layout_variant`) |
| `basic` | Minimal single-section documents | `title`, `author`, `body` |

Use `typy info <template>` to inspect fields in table form.

Use `typy info <template> --json` for machine-readable schema output.

## report

A multi-page report with optional abstract, table of contents, running header, and page numbers.

```bash
typy info report
```

**Key fields**: `title`, `subtitle`, `author`, `date`, `body`, `abstract`, `toc`

## invoice

A one-page business invoice with a line-item table, subtotal/tax/total block, and optional notes.

```bash
typy info invoice
```

**Key fields**: `company_name`, `company_address`, `client_name`, `client_address`,
`invoice_number`, `date`, `due_date`, `items` (list of `description`/`quantity`/`unit_price`),
`tax_rate`, `notes`, `logo`

## letter

A formal business letter with optional letterhead logo.

```bash
typy info letter
```

**Key fields**: `sender_name`, `sender_address`, `recipient_name`, `recipient_address`,
`date`, `subject`, `body`, `closing`, `signature_name`, `logo`

## cv

A single-page CV / résumé with experience, education, skills, languages, and certifications.

```bash
typy info cv
```

**Key fields**: `name`, `contact` (email/phone/location/links), `summary`, `experience`,
`education`, `skills`, `languages`, `certifications`

## academic

An academic paper template with abstract box, optional two-column body, and bibliography support.

```bash
typy info academic
```

**Key fields**: `title`, `authors` (list of `name`/`affiliation`), `abstract`, `keywords`,
`body`, `two_column`, `bibliography_path`

## presentation

A 16:9 slide deck with an auto-generated title slide and per-slide layout variants.

```bash
typy info presentation
```

**Key fields**: `title`, `subtitle`, `author`, `date`, `slides`, `theme`

### Slide layout variants

Each `Slide` accepts a `layout_variant` field that controls the page layout:

| `layout_variant` | Description |
|---|---|
| `None` / `"default"` | Accent header bar at the top, body below |
| `"hero"` | Full accent background, large centred title and body |
| `"two-column"` | Accent header, body split into two equal columns |
| `"blank"` | No header, body fills the whole slide |

```python
from typy.templates import PresentationTemplate, Slide
from typy.content import Content

slides = [
    Slide(title="Section Break", body=Content(["Big idea here"]), layout_variant="hero"),
    Slide(title="Comparison", body=Content(["Left #colbreak() Right"]), layout_variant="two-column"),
]
```

## basic

A minimal document for quick notes and one-off outputs.

```bash
typy info basic
```

**Key fields**: `title`, `author`, `date`, `body`

## Example: report fields

```bash
typy info report
```

## Example: invoice fields as JSON

```bash
typy info invoice --json
```
