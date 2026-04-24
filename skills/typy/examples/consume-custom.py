"""
consume-custom.py — Flow A: Consume a user-authored template

Demonstrates how to use a custom Template subclass (defined in a separate
.py file) to render a PDF.

The matching Typst file is examples/author-typst-template.typ.

Run from the repo root:
    python skills/typy/examples/consume-custom.py
Then verify:
    python scripts/verify_pdf.py /tmp/consume-custom.pdf
"""

from pathlib import Path

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.markup import Text
from typy.templates import Template


# ── 1. Define (or import) the custom Template subclass ────────────────────
#       In real usage you would import this from your template module.
class SimpleReportTemplate(Template):
    __template_name__ = "simple_report"
    __template_path__ = Path(__file__).parent / "author-typst-template.typ"

    title: str
    author: str
    body: Content


# ── 2. Create the builder ──────────────────────────────────────────────────
builder = DocumentBuilder()

# ── 3. Construct the template instance ────────────────────────────────────
template = SimpleReportTemplate(
    title="Custom Template Demo",
    author="Bob Smith",
    body=Content([
        Text("Overview: This PDF was generated from a custom template."),
        Text("- Item one"),
        Text("- Item two"),
        Text("- Item three"),
    ]),
)

# ── 4. Render ──────────────────────────────────────────────────────────────
output_path = Path("/tmp/consume-custom.pdf")
builder.add_template(template).save_pdf(output_path)
print(f"PDF saved to {output_path}")
