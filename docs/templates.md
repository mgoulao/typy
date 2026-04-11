# Template reference

Built-in templates:
- `report`: General-purpose report with TOC and sections
- `invoice`: Business invoice with line items
- `letter`: Formal business letter
- `cv`: CV or resume
- `academic`: Academic paper with citations
- `presentation`: Slide deck (16:9)
- `basic`: Basic single-section document

Use `typy info <template>` to inspect fields in table form.

Use `typy info <template> --json` for machine-readable schema output.

## Example: report fields

```bash
typy info report
```

## Example: invoice fields as JSON

```bash
typy info invoice --json
```
