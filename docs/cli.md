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
