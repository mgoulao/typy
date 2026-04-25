"""Academic example — demonstrates AcademicTemplate with abstract, two-column body, and bibliography."""

from pathlib import Path

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Lorem
from typy.markup import Heading
from typy.templates import AcademicAuthor, AcademicTemplate

builder = DocumentBuilder()

bib_path = builder.add_file(Path(__file__).parent / "references.bib")

body = Content(
    [
        Heading(2, "Introduction"),
        Lorem(200),
        Heading(2, "Related Work"),
        Lorem(150),
        Heading(2, "Methodology"),
        Heading(3, "Data Collection"),
        Lorem(120),
        Heading(3, "Analysis"),
        Lorem(100),
        Heading(2, "Results"),
        Lorem(180),
        Heading(2, "Conclusion"),
        Lorem(100),
    ]
)

template = AcademicTemplate(
    title="Typy: Programmatic Document Generation with Typst",
    authors=[
        AcademicAuthor(name="Jane Smith", affiliation="University of Example"),
        AcademicAuthor(name="John Doe", affiliation="Institute of Technology"),
    ],
    abstract=(
        "We present Typy, a Python library for generating PDF documents "
        "using the Typst typesetting system. Typy provides a high-level "
        "API for composing documents from structured data and rich content, "
        "making it straightforward to produce publication-quality PDFs "
        "programmatically. We describe the design, implementation, and "
        "use cases of the library."
    ),
    keywords=["document generation", "Typst", "Python", "PDF", "typesetting"],
    body=body,
    two_column=True,
    bibliography_path=bib_path,
)

builder.add_template(template).save_pdf("academic.pdf")
