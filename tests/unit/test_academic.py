from pathlib import Path

import pytest

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Lorem
from typy.markup import Heading
from typy.templates import AcademicAuthor, AcademicTemplate


@pytest.fixture
def minimal_template():
    """Create a minimal academic template for testing."""
    return AcademicTemplate(
        title="Test Paper",
        authors=[AcademicAuthor(name="Alice", affiliation="Test University")],
        abstract="This is a test abstract.",
        keywords=["testing", "typy"],
        body=Content("Body content."),
    )


@pytest.fixture
def two_column_template():
    """Create a two-column academic template."""
    return AcademicTemplate(
        title="Two-Column Paper",
        authors=[
            AcademicAuthor(name="Alice", affiliation="University A"),
            AcademicAuthor(name="Bob", affiliation=""),
        ],
        abstract="Abstract for two-column test.",
        keywords=["columns"],
        body=Content(
            [
                Heading(2, "Introduction"),
                Lorem(100),
                Heading(2, "Conclusion"),
                Lorem(50),
            ]
        ),
        two_column=True,
    )


def test_academic_author_defaults():
    """AcademicAuthor should default affiliation to empty string."""
    author = AcademicAuthor(name="Alice")
    assert author.name == "Alice"
    assert author.affiliation == ""


def test_academic_author_with_affiliation():
    """AcademicAuthor should store provided affiliation."""
    author = AcademicAuthor(name="Bob", affiliation="MIT")
    assert author.name == "Bob"
    assert author.affiliation == "MIT"


def test_academic_template_defaults(minimal_template):
    """AcademicTemplate should default two_column=False and bibliography_path=None."""
    assert minimal_template.two_column is False
    assert minimal_template.bibliography_path is None


def test_academic_template_two_column_flag(two_column_template):
    """AcademicTemplate should store the two_column flag."""
    assert two_column_template.two_column is True


def test_academic_template_bibliography_path():
    """AcademicTemplate should accept an optional bibliography path."""
    template = AcademicTemplate(
        title="Cited Paper",
        authors=[AcademicAuthor(name="Alice")],
        abstract="Abstract.",
        keywords=[],
        body=Content("Body."),
        bibliography_path=Path("references.bib"),
    )
    assert template.bibliography_path == Path("references.bib")


def test_academic_template_saves_pdf(minimal_template, tmp_path):
    """AcademicTemplate should compile to a valid PDF."""
    output = tmp_path / "academic.pdf"
    DocumentBuilder().add_template(minimal_template).save_pdf(output)
    assert output.exists()
    assert output.stat().st_size > 0
    with open(output, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_academic_template_two_column_saves_pdf(two_column_template, tmp_path):
    """Two-column AcademicTemplate should compile to a valid PDF."""
    output = tmp_path / "two_col.pdf"
    DocumentBuilder().add_template(two_column_template).save_pdf(output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_academic_template_with_bibliography(tmp_path):
    """AcademicTemplate with a bibliography should compile successfully."""
    bib_content = (
        "@article{test2024,\n"
        "  author = {Test, Author},\n"
        "  title  = {A Test Article},\n"
        "  year   = {2024},\n"
        "  journal = {Journal of Tests},\n"
        "}\n"
    )
    bib_file = tmp_path / "refs.bib"
    bib_file.write_text(bib_content, encoding="utf-8")

    builder = DocumentBuilder()
    bib_path = builder.add_file(bib_file)

    template = AcademicTemplate(
        title="Paper with Refs",
        authors=[AcademicAuthor(name="Alice", affiliation="Uni")],
        abstract="Abstract.",
        keywords=["test"],
        body=Content("Body text."),
        bibliography_path=bib_path,
    )

    output = tmp_path / "with_bib.pdf"
    builder.add_template(template).save_pdf(output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_academic_template_no_keywords(tmp_path):
    """AcademicTemplate with an empty keywords list should compile."""
    template = AcademicTemplate(
        title="No Keywords",
        authors=[AcademicAuthor(name="Alice")],
        abstract="Abstract.",
        keywords=[],
        body=Content("Body."),
    )
    output = tmp_path / "no_kw.pdf"
    DocumentBuilder().add_template(template).save_pdf(output)
    assert output.exists()
