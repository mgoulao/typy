"""
author-python-template.py — Flow B: Author a new Python Template subclass

Shows the complete pattern for creating a new Template class with:
- Required class attributes (__template_name__, __template_path__)
- Typed Pydantic fields including nested models
- A minimal roundtrip render test

Run from the repo root:
    python skills/typy/examples/author-python-template.py
Then verify:
    python scripts/verify_pdf.py /tmp/author-minimal.pdf
    python scripts/verify_pdf.py /tmp/author-realistic.pdf
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.markup import Text
from typy.templates import Template


# ── 1. (Optional) Define nested models ────────────────────────────────────
class Section(BaseModel):
    heading: str
    body: str


# ── 2. Define the Template subclass ───────────────────────────────────────
class TechnicalReportTemplate(Template):
    """A technical report with a title, author, executive summary, and sections."""

    # Required class-level attributes
    __template_name__ = "technical_report"
    __template_path__ = Path(__file__).parent / "author-typst-template.typ"

    # Data fields — all must be encodable by TypstEncoder
    title: str
    author: str
    date: str
    executive_summary: Optional[str] = None  # optional with default None
    body: Content                            # rich content block


# ── 3. Minimal roundtrip test ─────────────────────────────────────────────
def render_minimal():
    """Render with the fewest possible fields to catch missing-field bugs."""
    builder = DocumentBuilder()
    template = TechnicalReportTemplate(
        title="Minimal Test",
        author="Test Author",
        date="2024-01-01",
        body=Content([Text("Minimal body content.")]),
    )
    out = Path("/tmp/author-minimal.pdf")
    builder.add_template(template).save_pdf(out)
    print(f"Minimal render saved to {out}")


def render_realistic():
    """Render with realistic data to catch encoding and layout issues."""
    builder = DocumentBuilder()
    template = TechnicalReportTemplate(
        title="System Architecture Report",
        author="Alice Engineer",
        date="2024-06-15",
        executive_summary="This report describes the revised architecture.",
        body=Content([
            Text("Background: The legacy system was replaced in Q2."),
            Text("Findings: Latency reduced by 40 percent. Uptime improved. Cost down 15 percent."),
            Text("Recommendations: Proceed with full rollout in Q3."),
        ]),
    )
    out = Path("/tmp/author-realistic.pdf")
    builder.add_template(template).save_pdf(out)
    print(f"Realistic render saved to {out}")


if __name__ == "__main__":
    render_minimal()
    render_realistic()
