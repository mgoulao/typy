# Troubleshooting

Error table for the most common typy failures. Match the symptom, apply the
fix, then re-run `typy verify <pdf>` to confirm.

---

## Error table

| Symptom | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError` during render — asset not found | Asset path passed directly instead of via `builder.add_file(...)` | Route every file through `builder.add_file(path)` and use the returned relative path in `Image(...)` or template fields |
| Template renders with empty / `none` fields | `init_typy` not called, or `typy_data.typ` import missing in `.typ` | Add all three required imports; see [Typst file contract](template-authoring.md#typst-file-contract) |
| `FileNotFoundError: Template file not found` | `__template_path__` points to a non-existent file | Check the path; use `Path(__file__).parent / "..."` to stay relative to the Python file |
| "Template not found" at runtime from CLI | `__template_name__` not in the built-in registry and no `.py` file path given | For custom templates pass the `.py` file path: `typy render --template ./my_template.py` |
| `TypeError: Failed to encode field '...'` | Field value contains a type not supported by `TypstEncoder` | Fall back to primitive types (`str`, `int`, `float`, `bool`) or pre-render the value into a `Content(...)` block |
| Encoding error on non-primitive field | Known limitation of the current encoder | Pre-render the value as `Content(Text(str(value)))` and pass that to the field; see [Encoding fallback](#encoding-fallback) |
| `typst.TypstError: Typst compilation failed` | Typst syntax error in the `.typ` file | Read the error context printed by typy (includes line numbers); check the `.typ` file and `typy_data.typ` |
| `.typy` package rejected on import | Manifest version mismatch or structural issue | Run `typy package validate <file>.typy` and read the specific error; do not hand-edit the manifest |
| PDF exists but is 0 bytes | `save_pdf` called before `add_template` | Ensure the call chain is `builder.add_template(tmpl).save_pdf(path)` |
| `pydantic.ValidationError` when constructing template | Required field missing or wrong type | Run `typy info <template> --json` to see the required schema; check all required fields are provided |
| Markdown not rendered — shows raw text | Raw string passed to a `str` field instead of a `Content` field | Ensure the field type is `Content`; raw strings in `Content` fields auto-convert to `Markdown` |
| Image not found during Typst compilation | `add_file` called after `add_template` | Call `add_file` *before* `add_template` |

---

## Encoding fallback

When `TypstEncoder.encode(value)` raises `TypeError` for a complex value,
use one of these fallback patterns:

**Pattern 1 — Stringify**

```python
from typy.content import Content
from typy.markup import Text

# Instead of passing the complex value directly, convert to string first
field_value = Content(Text(str(complex_value)))
```

**Pattern 2 — Pre-render to Markdown**

```python
from typy.markup import Markdown

field_value = Markdown(f"**{complex_value}**")  # or any markdown string
```

**Pattern 3 — Use primitive fields**

Decompose the complex object into primitive fields on the `Template` subclass
and pass each part as `str`/`int`/`float`.

---

## Missing `typy_data.typ` import

If the rendered PDF shows placeholder text like `typy(...)` literally or
renders blank fields, check the `.typ` file for all three required lines:

```typst
#import "typy.typ": init_typy        // ← line 1
#import "typy_data.typ": typy_data   // ← line 2

#let typy = init_typy(typy_data)     // ← line 3
```

None of these three lines may be omitted or reordered.

---

## Template not found via CLI

Custom templates must be referenced by their `.py` file path, not by name:

```bash
# WRONG — will fail unless registered as a built-in
typy render --template my_template

# CORRECT — load from Python file
typy render --template ./my_template.py --data data.json
```

---

## Verbose mode for debugging

Enable verbose output to see the generated `typy_data.typ` source and
Typst compilation details:

```python
builder = DocumentBuilder(verbose=True)
```

---

## Known-fragile encoding paths

The following are known to be fragile in the current encoder; use the
fallback patterns above rather than debugging the encoder directly:

- Deeply nested `dict`-of-`dict` with non-string keys
- `Path` fields that are not registered via `add_file`
- `datetime.datetime` objects (use `.isoformat()` and pass as `str`)
- Recursive or circular Pydantic models

These are *not* permanently broken — they can be retried with pre-processing,
but agents should not spend time debugging the encoder on first failure.
