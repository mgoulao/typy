# Cookbook

Each entry is designed so an LLM can copy, adapt, and run it directly.
Every recipe includes a clear goal and complete code or commands.

## 1. Generate a report from a pandas DataFrame

Goal: render a report PDF containing a real table from analytics data.

**Prerequisites:** `pandas` must be installed. Run `pip install "typy[pandas]"` or `pip install pandas`.

```python
from datetime import date

import pandas as pd

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Figure, Table
from typy.markup import Heading, Text
from typy.templates import ReportTemplate

df = pd.DataFrame(
    {
        "Region": ["EMEA", "AMER", "APAC"],
        "Revenue": [1_200_000, 980_000, 1_450_000],
        "GrowthPct": [8.1, 5.4, 11.3],
    }
)

body = Content(
    [
        Heading(1, "Quarterly performance"),
        Text("This report summarizes regional revenue and growth."),
        Figure(Table(df.to_dict()), caption="Revenue by region"),
    ]
)

template = ReportTemplate(
    title="Q1 revenue report",
    subtitle="Regional breakdown",
    author="Finance Analytics",
    date=date.today().isoformat(),
    body=body,
    toc=True,
)

DocumentBuilder().add_template(template).save_pdf("q1-report.pdf")
```

## 2. Create an invoice from JSON data

Goal: render an invoice with line items loaded from a JSON payload.

```python
import json

from typy.builder import DocumentBuilder
from typy.templates import InvoiceTemplate

payload = {
    "company_name": "Northwind Design LLC",
    "company_address": "101 River St, Porto",
    "client_name": "Contoso Retail",
    "client_address": "25 Market Ave, Lisbon",
    "invoice_number": "INV-2026-0411",
    "date": "2026-04-11",
    "due_date": "2026-05-11",
    "tax_rate": 23.0,
    "notes": "Thank you for your business.",
    "items": [
        {"description": "UI redesign", "quantity": 32, "unit_price": 75.0},
        {"description": "Design system audit", "quantity": 12, "unit_price": 90.0},
    ],
}

with open("invoice.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

data = json.loads(open("invoice.json", encoding="utf-8").read())
template = InvoiceTemplate(**data)
DocumentBuilder().add_template(template).save_pdf("invoice.pdf")
```

## 3. Convert a Markdown file to a styled PDF

Goal: convert existing Markdown notes into a PDF without writing Python.

```bash
typy render --markdown README.md --output readme.pdf
```

## 4. Batch-generate certificates from a CSV

Goal: produce one PDF per person in a CSV list.

```python
import csv
from pathlib import Path

from typy.builder import DocumentBuilder
from typy.templates import BasicTemplate

Path("out").mkdir(exist_ok=True)

rows = [
    {"name": "Alice Martins", "course": "Data Visualization"},
    {"name": "Bruno Costa", "course": "Prompt Engineering"},
]

with open("certificates.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "course"])
    writer.writeheader()
    writer.writerows(rows)

with open("certificates.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        body = (
            "# Certificate of Completion\n\n"
            f"This certifies that **{row['name']}** completed "
            f"**{row['course']}**."
        )
        template = BasicTemplate(
            title="Certificate",
            date="2026-04-11",
            author="Training Team",
            body=body,
        )
        filename = f"out/{row['name'].lower().replace(' ', '-')}.pdf"
        DocumentBuilder().add_template(template).save_pdf(filename)
```

## 5. Build and render a custom template from scratch

Goal: use your own Typst template file with JSON data.

```bash
cat > custom.typ <<'TYP'
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let t = init_typy(typy_data)

= #t("title", "str")

#t("body", "content")
TYP

cat > custom-data.json <<'JSON'
{
  "title": "Custom template demo",
  "body": "## Hello\n\nRendered with a raw Typst template."
}
JSON

typy render --template custom.typ --data custom-data.json --output custom.pdf
```

## 6. Use typy only from the CLI

Goal: full CLI workflow from discovery to render.

```bash
typy list
typy info report --json
typy scaffold report --output data.json
typy render --template report --data data.json --output report.pdf
```

## 7. Use typy with an AI agent code-execution pattern

Goal: reliable command sequence for tools that can execute shell commands.

```bash
# Step 1: discover and inspect schema
typy list
typy info letter --json > schema-letter.json

# Step 2: produce data.json that matches required fields
cat > data-letter.json <<'JSON'
{
  "sender_name": "Northwind Legal",
  "sender_address": "101 River St, Porto",
  "recipient_name": "Maria Silva",
  "recipient_address": "12 Elm Road, Braga",
  "date": "2026-04-11",
  "subject": "Contract renewal",
  "body": "Dear Maria,\n\nPlease find the updated renewal terms attached.",
  "signature_name": "Pedro Azevedo"
}
JSON

# Step 3: render
typy render --template letter --data data-letter.json --output letter.pdf
```

## 8. Combine markdown with programmatic figures and tables

Goal: mix human-written markdown and generated visual content in one document.

```python
from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Figure, Table
from typy.markup import Markdown
from typy.templates import ReportTemplate

table_data = {
    "Metric": {0: "Latency", 1: "Throughput"},
    "Before": {0: "120ms", 1: "1000 req/s"},
    "After": {0: "45ms", 1: "3200 req/s"},
}

body = Content(
    [
        Markdown("## Benchmark summary\n\nPerformance improved after optimization."),
        Figure(Table(table_data), caption="Before vs after"),
    ]
)

template = ReportTemplate(
    title="Performance benchmark",
    author="Platform Team",
    date="2026-04-11",
    body=body,
)

DocumentBuilder().add_template(template).save_pdf("benchmark.pdf")
```

## 9. Generate a business letter from Python

Goal: create a formal letter programmatically.

```python
from typy.builder import DocumentBuilder
from typy.templates import LetterTemplate

template = LetterTemplate(
    sender_name="Acme Procurement",
    sender_address="44 Harbor Road, Porto",
    recipient_name="Nova Supplies",
    recipient_address="9 Cedar St, Faro",
    date="2026-04-11",
    subject="Request for quotation",
    body="Dear team,\n\nPlease send a quote for 500 units of Model X by next Friday.",
    closing="Best regards",
    signature_name="Joana Pereira",
)

DocumentBuilder().add_template(template).save_pdf("rfq-letter.pdf")
```

## 10. Build a presentation with multiple slides

Goal: generate a slide deck PDF from structured slide content.

```python
from typy.builder import DocumentBuilder
from typy.templates import PresentationTemplate, Slide

slides = [
    Slide(title="Context", body="## Current state\n\nUsage has grown 40% year over year."),
    Slide(title="Plan", body="## Next steps\n\n- Stabilize API\n- Improve docs\n- Expand templates"),
]

template = PresentationTemplate(
    title="Product update",
    subtitle="Q2 planning",
    author="Product Team",
    date="2026-04-11",
    slides=slides,
)

DocumentBuilder().add_template(template).save_pdf("product-update.pdf")
```

## 11. Render markdown into a report template body

Goal: keep metadata in JSON and body content in a separate Markdown file.

```bash
cat > report-data.json <<'JSON'
{
  "title": "Research summary",
  "author": "R&D Team",
  "date": "2026-04-11",
  "toc": true
}
JSON

cat > body.md <<'MD'
## Findings

The experiments show statistically significant improvements.

## Next actions

- Expand sample size
- Validate in production conditions
MD

typy render --template report --data report-data.json --markdown body.md --output research-summary.pdf
```
