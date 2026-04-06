from datetime import datetime

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Lorem
from typy.markup import Heading, Text
from typy.templates import ReportTemplate

builder = DocumentBuilder()

abstract = Content(
    Text(
        "This report demonstrates the typy report template. "
        "It covers professional document generation with sections, "
        "subsections, figures, tables, and code blocks using the "
        "Typst typesetting system."
    )
)

body = Content(
    [
        Heading(1, "Introduction"),
        Lorem(80),
        Heading(2, "Background"),
        Lorem(60),
        Heading(2, "Motivation"),
        Lorem(60),
        Heading(1, "Methodology"),
        Lorem(100),
        Heading(2, "Data Collection"),
        Lorem(60),
        Heading(2, "Analysis"),
        Lorem(60),
        Heading(1, "Results"),
        Lorem(80),
        Heading(1, "Conclusion"),
        Lorem(60),
    ]
)

template = ReportTemplate(
    title="Annual Research Report",
    subtitle="A Comprehensive Overview",
    author="Jane Doe",
    date=datetime(2025, 1, 1).strftime("%B %d, %Y"),
    body=body,
    abstract=abstract,
    toc=True,
)

builder.add_template(template).save_pdf("report.pdf")
