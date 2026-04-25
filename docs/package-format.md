# RFC: .typy template package format and manifest v1

This document defines the portable template package format used by typy.
A `.typy` file is a self-contained, distributable unit that bundles a Python `Template` class, the Typst files it references, and any associated assets.

## Overview

A `.typy` package is a **ZIP archive** with the `.typy` file extension.
The archive contains a mandatory `manifest.json` (the package descriptor) and a `template.py` file that defines the template data model as a subclass of `typy.templates.Template`.
Because it is plain ZIP, consumers can inspect and unpack it with any standard ZIP tool.

---

## Container structure

```
my-template.typy          ← ZIP archive with .typy extension
├── manifest.json         ← REQUIRED: package descriptor (manifest v1)
├── template.py           ← REQUIRED: Python file defining the Template subclass
├── templates/            ← REQUIRED: Typst files referenced by __template_path__ in template.py
│   └── template.typ
├── assets/               ← optional: images, fonts, or other static resources
│   ├── logo.png
│   └── font.ttf
└── README.md             ← optional: human-readable notes for the package
```

### Required files

| File | Description |
|---|---|
| `manifest.json` | Package descriptor in JSON format conforming to manifest schema v1 (see below). |
| `template.py` | Python module containing exactly one `typy.templates.Template` subclass. The class defines the data model and sets `__template_name__` and `__template_path__`. `__template_path__` must be a path relative to the archive root pointing to the entry `.typ` file inside `templates/`. |
| `templates/` | Directory containing the Typst file(s) referenced by `__template_path__` in `template.py`. At least one `.typ` file must be present. |

### Optional files

| File/directory | Description |
|---|---|
| `assets/` | Static resources (images, fonts, etc.) referenced by the template. Paths must be relative and must stay inside the archive root. |
| `README.md` | Package documentation for human readers. Shown by tools that display package info. |

### Path rules

- All paths inside the archive must be **relative** (no leading `/` or `..` traversal).
- `__template_path__` in `template.py` and any files it references **must not** escape the archive root via path traversal (`../`).
- File names are case-sensitive.

---

## Manifest schema v1

The `manifest.json` file is UTF-8-encoded JSON.
The `"manifest_version"` field determines which schema applies.
This document specifies manifest version **1**.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `manifest_version` | integer | **yes** | Schema version. Must be `1` for this spec. |
| `name` | string | **yes** | Package identifier. Lowercase alphanumeric, hyphens allowed. Pattern: `^[a-z0-9][a-z0-9-]*[a-z0-9]$` (min length 2). |
| `version` | string | **yes** | [Semantic version](https://semver.org/) of this package, e.g. `"1.0.0"`. |
| `description` | string | **yes** | One-line human-readable summary of the template's purpose. |
| `author` | string | **yes** | Author name, optionally with email in angle brackets, e.g. `"Jane Doe <jane@example.com>"`. |
| `typy_compatibility` | string | **yes** | PEP 440 version specifier for the typy version this package requires, e.g. `">=0.1.0"`. |
| `dependencies` | array of strings | no | List of other `.typy` package identifiers that must be installed before this package. Format for each entry: `"<name>@<version-specifier>"`. Defaults to `[]`. |
| `family` | string | no | Name of the [vertical design system](design-systems.md) this template belongs to (e.g. `"legal"`). Informational — readers that do not recognise the value must ignore it. |
| `license` | string | no | SPDX license identifier, e.g. `"MIT"`. |
| `homepage` | string | no | URL for the package's home page or repository. |
| `keywords` | array of strings | no | Tags for discovery. Each keyword: max 32 characters. |

### Example: minimal valid manifest

```json
{
  "manifest_version": 1,
  "name": "my-report",
  "version": "1.0.0",
  "description": "A general-purpose report template with cover page and TOC.",
  "author": "Jane Doe <jane@example.com>",
  "typy_compatibility": ">=0.1.0"
}
```

### Example: full valid manifest

```json
{
  "manifest_version": 1,
  "name": "corporate-invoice",
  "version": "2.1.0",
  "description": "Professional invoice template with logo, line items, and tax calculation.",
  "author": "Acme Corp <templates@acme.example.com>",
  "typy_compatibility": ">=0.2.0,<1.0.0",
  "dependencies": [
    "acme-base@>=1.0.0"
  ],
  "license": "MIT",
  "homepage": "https://github.com/acme/typy-templates",
  "keywords": ["invoice", "billing", "business"]
}
```

---

## Compatibility and versioning policy

### Manifest version

The `"manifest_version"` integer is the **primary compatibility signal** for readers.

| manifest_version | Status | Supported by |
|---|---|---|
| 1 | **Current** | This specification |

Future schemas increment `manifest_version`. A reader that does not recognise a `manifest_version` value **must** reject the package with a clear diagnostic (see [error model](#error-model-for-invalid-packages)) rather than silently ignoring unknown fields.

### Forward compatibility within v1

- **New optional fields** may be added to manifest v1 in minor typy releases.
  Readers encountering unknown fields **must** ignore them (be liberal in what they accept).
- **Removing or renaming** required fields, or changing the type of any existing field, requires a new `manifest_version`.

### Package versioning

Package authors use [Semantic Versioning](https://semver.org/) for `"version"`:
- **MAJOR** – incompatible API or field changes in the template.
- **MINOR** – new optional fields or backwards-compatible feature additions.
- **PATCH** – bug fixes or asset updates that do not alter the template interface.

### typy_compatibility

The `"typy_compatibility"` field uses [PEP 440](https://peps.python.org/pep-0440/#version-specifiers) version specifiers so that the installed typy version can be checked before importing a package.
Using a compatible-release specifier (`~=`) or an upper bound (`<`) is recommended when a package relies on behaviour introduced in a specific release.

---

## Error model for invalid packages

Errors are reported as structured diagnostics.
Each diagnostic has a **code**, a human-readable **message**, and an optional **hint** with a corrective action.

### Diagnostic structure

```json
{
  "code": "PKG_E003",
  "message": "manifest.json is missing required field: 'name'",
  "hint": "Add a 'name' field using only lowercase letters, digits, and hyphens (e.g. 'my-template')."
}
```

### Error codes

| Code | Trigger condition | Example message |
|---|---|---|
| `PKG_E001` | File is not a valid ZIP archive | `"Not a valid .typy package: file is not a ZIP archive."` |
| `PKG_E002` | `manifest.json` is absent from the archive root | `"manifest.json not found in package root."` |
| `PKG_E003` | `manifest.json` is not valid JSON | `"manifest.json contains invalid JSON: <detail>."` |
| `PKG_E004` | `manifest_version` is missing | `"manifest.json is missing required field: 'manifest_version'."` |
| `PKG_E005` | `manifest_version` is not a recognised integer | `"Unsupported manifest_version: 99. This version of typy supports manifest_version 1."` |
| `PKG_E006` | A required field is absent | `"manifest.json is missing required field: '<field>'."` |
| `PKG_E007` | A field has the wrong type | `"manifest.json field '<field>' must be <expected-type>, got <actual-type>."` |
| `PKG_E008` | `name` does not match the naming pattern | `"'name' must match ^[a-z0-9][a-z0-9-]*[a-z0-9]$, got '<value>'."` |
| `PKG_E009` | `version` is not a valid semver string | `"'version' must be a valid semantic version (e.g. '1.0.0'), got '<value>'."` |
| `PKG_E010` | `template.py` is absent from the archive root | `"template.py not found in package root. The Template subclass must be defined in template.py."` |
| `PKG_E011` | A path inside the archive escapes the root (`../`) | `"Unsafe path detected in archive: '<path>'. Paths must not traverse outside the package root."` |
| `PKG_E012` | `typy_compatibility` is not a valid PEP 440 specifier | `"'typy_compatibility' is not a valid version specifier: '<value>'."` |
| `PKG_E013` | Installed typy version does not satisfy `typy_compatibility` | `"Package requires typy <specifier> but typy <installed-version> is installed."` |

Validators **must** collect all applicable errors before reporting, so that a user can fix all problems in one pass.

### Example: invalid manifest — multiple errors

```json
{
  "manifest_version": 1,
  "name": "My Template",
  "version": "not-a-version",
  "description": "A report template.",
  "author": "Jane Doe",
  "typy_compatibility": ">=0.1.0"
}
```

Expected diagnostics:

```
PKG_E008  'name' must match ^[a-z0-9][a-z0-9-]*[a-z0-9]$, got 'My Template'.
          Hint: Use only lowercase letters, digits, and hyphens (e.g. 'my-template').

PKG_E009  'version' must be a valid semantic version (e.g. '1.0.0'), got 'not-a-version'.
          Hint: Use MAJOR.MINOR.PATCH format as defined at https://semver.org.

PKG_E010  template.py not found in package root. The Template subclass must be defined in template.py.
          Hint: Add a template.py file to the archive root that defines a subclass of typy.templates.Template.
```

---

## Non-goals (MVP)

- Implementing `typy package export/import` commands — tracked in a separate issue.
- A remote registry or marketplace for packages.
- Package signing or tamper-detection.
- Dependency resolution or a lock-file mechanism.

---

## See also

- [Template reference](templates.md) — built-in templates and field schemas
- [CLI reference](cli.md) — available commands
- [Getting started](getting-started.md) — first-run walkthrough
