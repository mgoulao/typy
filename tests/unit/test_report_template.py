import pytest

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Lorem
from typy.markup import Heading, Text
from typy.templates import ReportTemplate


@pytest.fixture
def report_template():
    """Create a report template with all fields set."""
    return ReportTemplate(
        title="Test Report",
        subtitle="A Test Subtitle",
        author="Test Author",
        date="January 1, 2025",
        body=Content([Heading(1, "Introduction"), Lorem(30)]),
        abstract=Content(Text("This is a test abstract.")),
        toc=True,
    )


@pytest.fixture
def minimal_report_template():
    """Create a report template with only required fields."""
    return ReportTemplate(
        title="Minimal Report",
        author="Test Author",
        date="2025-01-01",
        body=Content(Lorem(20)),
    )


# ---- ReportTemplate model tests ----


def test_report_template_required_fields():
    """Test that ReportTemplate requires title, author, date, and body."""
    with pytest.raises(Exception):
        ReportTemplate(title="T", author="A", date="D")


def test_report_template_optional_fields_default_to_none():
    """Test that optional fields subtitle and abstract default to None."""
    t = ReportTemplate(
        title="T", author="A", date="D", body=Content(Lorem(10))
    )
    assert t.subtitle is None
    assert t.abstract is None


def test_report_template_toc_defaults_to_true():
    """Test that toc defaults to True."""
    t = ReportTemplate(
        title="T", author="A", date="D", body=Content(Lorem(10))
    )
    assert t.toc is True


def test_report_template_accepts_subtitle():
    """Test that subtitle can be set."""
    t = ReportTemplate(
        title="T", subtitle="Sub", author="A", date="D", body=Content(Lorem(10))
    )
    assert t.subtitle == "Sub"


def test_report_template_accepts_abstract():
    """Test that abstract can be set as Content."""
    abstract = Content(Text("Abstract text."))
    t = ReportTemplate(
        title="T", author="A", date="D", body=Content(Lorem(10)), abstract=abstract
    )
    assert t.abstract is not None


def test_report_template_toc_can_be_false():
    """Test that toc can be set to False."""
    t = ReportTemplate(
        title="T", author="A", date="D", body=Content(Lorem(10)), toc=False
    )
    assert t.toc is False


# ---- ReportTemplate compilation tests ----


def test_report_template_compiles_to_pdf(report_template, tmp_path):
    """Test that a full report template compiles to a valid PDF."""
    output_path = tmp_path / "report.pdf"
    builder = DocumentBuilder()
    builder.add_template(report_template).save_pdf(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    with open(output_path, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_minimal_report_template_compiles(minimal_report_template, tmp_path):
    """Test that a minimal report (no optional fields) compiles successfully."""
    output_path = tmp_path / "minimal_report.pdf"
    builder = DocumentBuilder()
    builder.add_template(minimal_report_template).save_pdf(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_report_template_toc_false_compiles(tmp_path):
    """Test that a report with toc=False compiles successfully."""
    output_path = tmp_path / "report_notoc.pdf"
    template = ReportTemplate(
        title="No TOC Report",
        author="Author",
        date="2025-01-01",
        body=Content(Lorem(20)),
        toc=False,
    )
    builder = DocumentBuilder()
    builder.add_template(template).save_pdf(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
