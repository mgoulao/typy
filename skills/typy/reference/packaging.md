# Packaging — `.typy` Template Bundles

The `.typy` packaging CLI is available via `typy package`.

---

## Workflow

A `.typy` package is a distributable archive that bundles a Typst template
(`.typ` file or directory), its Python `Template` subclass, and a manifest.

### Export

```bash
typy package export path/to/template.py --manifest path/to/manifest.json --output my_template.typy
```

Creates `my_template.typy` containing:
- The `.typ` file(s)
- The Python class definition
- A `manifest.json` with name, version, and field schema

### Validate

```bash
typy package validate my_template.typy
```

Must pass before sharing. Checks manifest version, structural integrity,
and that the `.typ` entry point exists.

### Install

```bash
typy package install my_template.typy
```

Installs the template into the local typy template store. After install, the
template appears in `typy list` and can be consumed via Flow A.

### Roundtrip script

See [`../../../examples/package-export.sh`](../../../examples/package-export.sh) for a
full export → validate → install → render roundtrip.

---

## Notes

You can render directly from a package file without installing first:

```bash
typy render --template my_template.typy --data data.json --output out.pdf
```

---

## Versioning

- Package manifests include a `manifest_version` field.
- Do not hand-edit manifests; always use `typy package validate` to diagnose
  structural issues.
- Pin the `.typy` package to the typy version it was exported from.
