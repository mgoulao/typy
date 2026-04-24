# CLI reference

The CLI is workflow-oriented and supports direct discovery through `--help`.

## Commands

### list
List built-in templates.

```bash
typy list
```

### info
Inspect template schema.

```bash
typy info report
typy info report --json
```

### scaffold
Generate sample JSON input for a template.

```bash
typy scaffold report --output data.json
```

### render
Render PDF from template data, Markdown, or both.

```bash
typy render --template report --data data.json --output report.pdf
typy render --markdown notes.md --output notes.pdf
typy render --template report --markdown body.md --output report.pdf
```

Constraints:
- At least one of `--template` or `--markdown` is required.
- If `--template` is provided without `--data` and without `--markdown`, typy auto-generates sample data for preview rendering.

### package
Manage `.typy` template packages. Run `typy package --help` for details.

#### package validate
Validate the structure and manifest of a `.typy` package.

```bash
typy package validate my-template.typy
```

Reports all errors in a single pass so they can be fixed together.

#### package export
Export a template as a self-contained `.typy` package archive.

```bash
typy package export template.py \
    --manifest manifest.json \
    --output my-template.typy
```

Optional flags:

| Flag | Description |
|---|---|
| `--assets <dir>` | Bundle a directory of static assets (images, fonts, …) under `assets/`. |
| `--readme <file>` | Bundle a README file as `README.md`. |

Minimal `manifest.json`:

```json
{
  "manifest_version": 1,
  "name": "my-report",
  "version": "1.0.0",
  "description": "A general-purpose report template.",
  "author": "Jane Doe <jane@example.com>",
  "typy_compatibility": ">=0.1.0"
}
```

See [package-format.md](package-format.md) for the full manifest schema.

#### package install
Validate and install a `.typy` package into the local template store
(`~/.typy/packages/` by default).

```bash
typy package install my-template.typy
typy package install my-template.typy --store /path/to/store
typy package install my-template.typy --force   # overwrite existing
```

After installation the package is unpacked to
`<store>/<name>/<version>/` and the `template.py` inside can be passed
directly to `typy render`:

```bash
typy render --template ~/.typy/packages/my-report/1.0.0/template.py \
    --data data.json --output report.pdf
```

## Typical package workflow

```bash
# 1. Author creates a template and writes a manifest
typy scaffold report --output data.json      # optional: inspect field schema
cat manifest.json                            # verify manifest fields

# 2. Export as a distributable package
typy package export template.py \
    --manifest manifest.json \
    --output my-report.typy

# 3. Validate before distribution
typy package validate my-report.typy

# 4. End-user installs the package
typy package install my-report.typy

# 5. Render a document using the installed template
typy render \
    --template ~/.typy/packages/my-report/1.0.0/template.py \
    --data data.json \
    --output report.pdf
```

