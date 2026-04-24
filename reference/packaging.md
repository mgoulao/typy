# Packaging — `.typy` Template Bundles

> **Status:** The `.typy` packaging CLI (`typy package`) is **planned** and
> tracked in issue #38. It is not yet available in the current release.
>
> This document describes the *intended* workflow so agents can document,
> plan, and implement around it once it lands. Do not attempt to use
> `typy package` commands until the feature is released.

---

## Intended workflow (post-#38)

A `.typy` package is a distributable archive that bundles a Typst template
(`.typ` file or directory), its Python `Template` subclass, and a manifest.

### Export

```bash
typy package export <template_name_or_py_path> --output my_template.typy
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

### Import

```bash
typy package import my_template.typy
```

Installs the template into the local typy template store. After import, the
template appears in `typy list` and can be consumed via Flow A.

### Roundtrip script

See [`../examples/package-export.sh`](../examples/package-export.sh) for a
full export → validate → import → render roundtrip.

---

## Confirming availability

To check whether packaging is available in the installed version:

```bash
typy --help | grep package
```

If `package` does not appear, the feature is not yet available. Install from
the `main` branch or wait for the next release.

---

## Versioning

- Package manifests include a `manifest_version` field.
- Do not hand-edit manifests; always use `typy package validate` to diagnose
  structural issues.
- Pin the `.typy` package to the typy version it was exported from.
