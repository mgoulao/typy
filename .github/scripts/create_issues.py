import json, os, subprocess, sys

token = os.environ["GH_TOKEN"]
repo = os.environ["REPO"]

def api(endpoint, method="GET", data=None):
    args = ["gh", "api", f"repos/{repo}/{endpoint}", "--method", method]
    if data:
        args += ["--input", "-"]
    r = subprocess.run(
        args,
        input=json.dumps(data) if data else None,
        capture_output=True, text=True,
        env={**os.environ, "GH_TOKEN": token}
    )
    if r.returncode != 0:
        print(f"WARN: {method} {endpoint} => {r.stderr.strip()}", file=sys.stderr)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}

# Labels
labels = [
    ("bug",               "d73a4a", "Something isn't working"),
    ("enhancement",       "a2eeef", "New feature or request"),
    ("core",              "0075ca", "Core library functionality"),
    ("testing",           "e4e669", "Related to tests and coverage"),
    ("feature",           "84b6eb", "Brand-new capability"),
    ("template",          "c5def5", "Document template"),
    ("priority: critical","b60205", "Must fix before release"),
    ("priority: high",    "e99695", "High priority"),
    ("priority: medium",  "f9d0c4", "Medium priority"),
]
for name, color, desc in labels:
    r = api(f"labels/{name}", "PATCH", {"color": color, "description": desc})
    if not r.get("name"):
        api("labels", "POST", {"name": name, "color": color, "description": desc})
print("Labels done.")

# Milestones
for v in ["v0.2.0", "v0.3.0", "v0.4.0", "v0.5.0"]:
    api("milestones", "POST", {"title": v})
ms_list = api("milestones?state=all&per_page=100")
if not isinstance(ms_list, list):
    ms_list = []
ms = {m["title"]: m["number"] for m in ms_list}
print("Milestones:", ms)

issues = [
    {
        "title": "Stabilize the Typst encoder for core Python types",
        "labels": ["bug", "core", "priority: critical"],
        "milestone": ms.get("v0.2.0"),
        "body": (
            "## Description\n\n"
            "The current Typst encoding layer is acknowledged as buggy and incomplete. "
            "Before any new features, the encoder needs to reliably handle the most common "
            "Python types that users will pass into templates and content blocks.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] `str` \u2014 correctly escaped for Typst (handles quotes, special characters, Unicode)\n"
            "- [ ] `int`, `float` \u2014 numeric literals\n"
            "- [ ] `bool` \u2014 mapped to Typst `true`/`false`\n"
            "- [ ] `None` \u2014 mapped to Typst `none`\n"
            "- [ ] `list` / `tuple` \u2014 mapped to Typst arrays\n"
            "- [ ] `dict` \u2014 mapped to Typst dictionaries\n"
            "- [ ] `datetime` / `date` \u2014 formatted as Typst datetime or string\n"
            "- [ ] `pandas.DataFrame` \u2014 mapped to Typst table data "
            "(already partially working via `.to_dict()`, but should be first-class)\n"
            "- [ ] Nested combinations of the above\n\n"
            "## Additional context\n\n"
            "Each type conversion should have corresponding unit tests with edge cases "
            "(empty strings, special characters, deeply nested structures, DataFrames with mixed dtypes). "
            "Consider creating a `typy.encode` module with a clear `encode(value) -> str` interface "
            "that the rest of the codebase uses consistently."
        ),
    },
    {
        "title": "Improve error messages and validation in the encoder",
        "labels": ["enhancement", "core", "priority: high"],
        "milestone": ms.get("v0.2.0"),
        "body": (
            "## Description\n\n"
            "When encoding fails or produces invalid Typst, the user currently gets opaque errors "
            "(or worse, silent corruption). The encoder should validate inputs and provide clear, "
            "actionable error messages.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Unsupported types raise `TypeError` with a message like: "
            "`\"Cannot encode type 'set' to Typst. Supported types: str, int, float, bool, list, dict, ...\"`\n"
            "- [ ] Typst compilation errors are caught and surfaced with the relevant Typst source "
            "context (line number + snippet)\n"
            "- [ ] Template data validation: if a template expects `str` but receives `int`, raise "
            "early with a clear message rather than failing at Typst compile time\n"
            "- [ ] Add a `--verbose` / debug mode that prints the generated Typst source before "
            "compilation, for debugging template issues"
        ),
    },
    {
        "title": "Add comprehensive test suite for the encoder",
        "labels": ["testing", "core", "priority: high"],
        "milestone": ms.get("v0.2.0"),
        "body": (
            "## Description\n\n"
            "The encoder is the foundation of the entire library. It needs thorough test coverage "
            "before building anything on top of it.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Unit tests for every supported type (see Issue #1)\n"
            "- [ ] Round-trip tests: Python value \u2192 Typst source \u2192 verify it compiles without error\n"
            "- [ ] Edge case tests: empty strings, very long strings, strings with Typst-reserved "
            "characters (`#`, `$`, `//`, etc.), Unicode, emoji\n"
            "- [ ] DataFrame tests: empty DataFrame, single row, mixed dtypes, NaN handling, multi-index\n"
            "- [ ] Integration tests: full template render from Python data to PDF output "
            "(verify PDF is valid and non-empty)\n"
            "- [ ] CI setup: tests run on push via GitHub Actions"
        ),
    },
    {
        "title": "Add markdown input support",
        "labels": ["enhancement", "feature", "priority: high"],
        "milestone": ms.get("v0.3.0"),
        "body": (
            "## Description\n\n"
            "Markdown is the lingua franca for both humans and LLMs. Adding markdown as an input "
            "format dramatically lowers the barrier to entry \u2014 users don't need to learn Typst or "
            "typy's content API to generate beautiful documents.\n\n"
            "Typst has community packages that convert markdown to Typst markup (e.g., `cmarker`), "
            "making the implementation on the Typst side straightforward.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] New `Markdown` content type: `Markdown(\"## Hello\\n\\nSome **bold** text\")`\n"
            "- [ ] Works as a first-class content element anywhere `Content` is accepted "
            "(template body, figures, sections)\n"
            "- [ ] Supports standard CommonMark: headings, bold, italic, code blocks, links, "
            "images, lists, tables, blockquotes\n"
            "- [ ] Integrates a Typst markdown package (e.g., `cmarker`) transparently \u2014 "
            "the user never sees it\n"
            "- [ ] Example in README showing markdown usage\n\n"
            "## Example API\n\n"
            "```python\n"
            "from typy.content import Markdown\n\n"
            "body = Markdown(\"\"\"\n"
            "## Results\n\n"
            "The analysis shows a **significant improvement** in performance.\n\n"
            "| Metric | Before | After |\n"
            "|--------|--------|-------|\n"
            "| Latency | 120ms | 45ms |\n"
            "| Throughput | 1000 | 3200 |\n"
            "\"\"\")\n\n"
            "builder.add_template(BasicTemplate(\n"
            "    title=\"Performance Report\",\n"
            "    body=body,\n"
            ")).save_pdf(\"report.pdf\")\n"
            "```"
        ),
    },
    {
        "title": "Support markdown strings in template data fields",
        "labels": ["enhancement", "feature", "priority: medium"],
        "milestone": ms.get("v0.3.0"),
        "body": (
            "## Description\n\n"
            "Beyond a standalone `Markdown` content block, template data fields that accept `str` "
            "should optionally accept markdown and convert it to rich Typst content. This is "
            "especially important for AI agent usage, where the agent will naturally produce "
            "markdown text.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields typed as `Content` accept raw markdown strings and auto-convert\n"
            "- [ ] Template fields typed as `str` remain plain strings (no conversion)\n"
            "- [ ] Explicit `Markdown(...)` wrapper always works as an override\n"
            "- [ ] Document the behavior clearly: when does auto-conversion happen vs. not\n\n"
            "## Dependencies\n\n"
            "Depends on #4 (Add markdown input support)"
        ),
    },
    {
        "title": "Build template: Report",
        "labels": ["template", "enhancement"],
        "milestone": ms.get("v0.4.0"),
        "body": (
            "## Description\n\n"
            "Create a polished, general-purpose report template. This is the most common document "
            "type for both human users and AI agents.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields: `title`, `subtitle` (optional), `author`, `date`, `body` (Content), "
            "`abstract` (optional), `toc` (bool, default True)\n"
            "- [ ] Professional styling: clean typography, page numbers, headers/footers\n"
            "- [ ] Supports sections, subsections, figures, tables, and code blocks in body\n"
            "- [ ] Includes example in `examples/` directory\n"
            "- [ ] Template file in `templates/report.typ`"
        ),
    },
    {
        "title": "Build template: Invoice",
        "labels": ["template", "enhancement"],
        "milestone": ms.get("v0.4.0"),
        "body": (
            "## Description\n\n"
            "Create an invoice template \u2014 one of the most requested document automation use cases.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields: `company_name`, `company_address`, `client_name`, `client_address`, "
            "`invoice_number`, `date`, `due_date`, `items` (list of dicts with description/quantity/unit_price), "
            "`tax_rate` (optional), `notes` (optional)\n"
            "- [ ] Auto-calculated subtotal, tax, and total\n"
            "- [ ] Clean, professional layout with logo support (optional image field)\n"
            "- [ ] Includes example in `examples/` directory"
        ),
    },
    {
        "title": "Build template: Letter",
        "labels": ["template", "enhancement"],
        "milestone": ms.get("v0.4.0"),
        "body": (
            "## Description\n\n"
            "Create a formal letter template.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields: `sender_name`, `sender_address`, `recipient_name`, "
            "`recipient_address`, `date`, `subject`, `body`, `closing` (default \"Sincerely\"), "
            "`signature_name`\n"
            "- [ ] Standard business letter layout\n"
            "- [ ] Optional letterhead/logo support\n"
            "- [ ] Includes example in `examples/` directory"
        ),
    },
    {
        "title": "Build template: CV / Resume",
        "labels": ["template", "enhancement"],
        "milestone": ms.get("v0.4.0"),
        "body": (
            "## Description\n\n"
            "Create a CV/resume template. High demand from both individuals and AI-assisted "
            "resume builders.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields: `name`, `contact` (email, phone, location, links), "
            "`summary` (optional), `experience` (list), `education` (list), `skills` (list), "
            "`languages` (optional), `certifications` (optional)\n"
            "- [ ] Modern, clean single-column or two-column layout\n"
            "- [ ] Includes example in `examples/` directory"
        ),
    },
    {
        "title": "Build template: Academic paper",
        "labels": ["template", "enhancement"],
        "milestone": ms.get("v0.4.0"),
        "body": (
            "## Description\n\n"
            "Create an academic paper template targeting researchers who want to replace LaTeX "
            "with Typst.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields: `title`, `authors` (list with name/affiliation), `abstract`, "
            "`keywords`, `body`, `bibliography` (optional path to .bib file)\n"
            "- [ ] Standard academic formatting: two-column option, numbered sections, "
            "figure/table numbering\n"
            "- [ ] Citation support via Typst's built-in bibliography system\n"
            "- [ ] Includes example in `examples/` directory"
        ),
    },
    {
        "title": "Build template: Presentation (slides)",
        "labels": ["template", "enhancement"],
        "milestone": ms.get("v0.4.0"),
        "body": (
            "## Description\n\n"
            "Create a presentation/slide deck template, building on the existing `diatypst` "
            "integration shown in the README.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] Template fields: `title`, `subtitle` (optional), `author`, `date`, "
            "`slides` (list of slide content)\n"
            "- [ ] Each slide supports: title, body content (text, images, lists, code), "
            "speaker notes\n"
            "- [ ] 16:9 aspect ratio by default\n"
            "- [ ] Clean, minimal styling\n"
            "- [ ] Includes example in `examples/` directory"
        ),
    },
    {
        "title": "CLI \u2014 `typy render` command",
        "labels": ["enhancement", "feature", "priority: high"],
        "milestone": ms.get("v0.5.0"),
        "body": (
            "## Description\n\n"
            "Add a CLI interface for rendering documents. This is essential for scriptability, "
            "CI/CD pipelines, and AI agents that execute shell commands.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] `typy render --template <name-or-path> --data <data.json> --output <out.pdf>` "
            "\u2014 render a template with JSON data\n"
            "- [ ] `--template` accepts either a built-in template name (`report`, `invoice`, etc.) "
            "or a path to a custom `.typ` template file\n"
            "- [ ] `typy render --markdown <input.md> --output <out.pdf>` \u2014 render a markdown "
            "file to PDF with default styling\n"
            "- [ ] `typy render --markdown <input.md> --template <name>` \u2014 render markdown using "
            "a specific template (markdown goes into the template's body field)\n"
            "- [ ] `--output` supports `.pdf` (default), and later `.png`, `.svg`\n"
            "- [ ] Sensible defaults: if `--output` is omitted, default to `output.pdf`\n"
            "- [ ] Exit codes: 0 on success, 1 on error with stderr message\n\n"
            "## Dependencies\n\n"
            "Depends on #4 (markdown), #6\u2013#11 (templates)\n\n"
            "## Example usage\n\n"
            "```bash\n"
            "typy render --template report --data report_data.json --output report.pdf\n"
            "typy render --markdown notes.md --output notes.pdf\n"
            "typy render --markdown notes.md --template report --output notes.pdf\n"
            "```"
        ),
    },
    {
        "title": "CLI \u2014 `typy list` and `typy info` commands",
        "labels": ["enhancement", "feature"],
        "milestone": ms.get("v0.5.0"),
        "body": (
            "## Description\n\n"
            "Discovery commands for the CLI so users (and AI agents) can explore available "
            "templates and their schemas.\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] `typy list` \u2014 list all available built-in templates with a one-line description\n"
            "- [ ] `typy info <template-name>` \u2014 show the full schema for a template "
            "(fields, types, required/optional)\n"
            "- [ ] Machine-readable output: `--json` flag for both commands\n"
            "- [ ] Help text is clear and includes examples\n\n"
            "## Dependencies\n\n"
            "Depends on #6\u2013#11 (templates)"
        ),
    },
]

created = []
for issue in issues:
    payload = {
        "title": issue["title"],
        "body": issue["body"],
        "labels": issue["labels"],
    }
    if issue.get("milestone"):
        payload["milestone"] = issue["milestone"]
    data = api("issues", "POST", payload)
    if "number" in data:
        print(f"Created #{data['number']}: {issue['title']}")
        created.append(data["number"])
    else:
        print(f"FAILED: {issue['title']} => {data}", file=sys.stderr)

print(f"\nDone. Created {len(created)} issues: {created}")
