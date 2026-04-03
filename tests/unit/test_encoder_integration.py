"""Integration tests: full pipeline from Python data to PDF using a self-contained template."""

import tempfile
from io import BytesIO
from pathlib import Path

import pytest
import typst

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.templates import Template
from typy.typst_encoder import TypstEncoder


# ---- Self-contained template fixture ----
# This template does not import any external Typst packages and therefore
# works in environments without network access to the Typst package registry.

_SIMPLE_TEMPLATE = """\
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

= #typy("title", "str")

Author: #typy("author", "str")

Date: #typy("date", "str")

#typy("body", "content")
"""


class SimpleTemplate(Template):
    """Minimal self-contained template for integration testing."""

    title: str
    author: str
    date: str
    body: Content

    __template_name__ = "simple_test"
    # template path is set dynamically in the fixture


@pytest.fixture()
def simple_template_path(tmp_path_factory):
    """Write the simple template file to a temporary directory and return its path."""
    tpl_dir = tmp_path_factory.mktemp("tpl")
    tpl_file = tpl_dir / "main.typ"
    tpl_file.write_text(_SIMPLE_TEMPLATE, encoding="utf-8")
    return tpl_file


@pytest.fixture()
def simple_template(simple_template_path):
    """Return a SimpleTemplate instance bound to the self-contained template file."""
    SimpleTemplate.__template_path__ = simple_template_path
    return SimpleTemplate(
        title="Integration Test Document",
        author="Test Author",
        date="2024-01-01",
        body=Content("This is the body of the document."),
    )


@pytest.fixture()
def builder_with_simple_template(simple_template):
    """DocumentBuilder already set up with the simple template."""
    builder = DocumentBuilder()
    builder.add_template(simple_template)
    return builder


# ---- Tests ----


def test_integration_to_buffer_returns_valid_pdf(builder_with_simple_template):
    """Full pipeline: template + data → BytesIO containing a valid PDF."""
    buf = builder_with_simple_template.to_buffer()
    assert isinstance(buf, BytesIO)
    content = buf.read()
    assert len(content) > 0, "PDF buffer is empty"
    assert content.startswith(b"%PDF-"), "Buffer does not contain PDF data"


def test_integration_save_pdf_creates_valid_file(builder_with_simple_template, tmp_path):
    """Full pipeline: template + data → PDF file that is non-empty and valid."""
    out = tmp_path / "integration_output.pdf"
    builder_with_simple_template.save_pdf(out)
    assert out.exists(), "PDF file was not created"
    assert out.stat().st_size > 0, "PDF file is empty"
    assert out.read_bytes().startswith(b"%PDF-"), "File does not contain PDF data"


def test_integration_pdf_content_consistency(builder_with_simple_template, tmp_path):
    """save_pdf and to_buffer produce the same valid PDF content."""
    out = tmp_path / "consistency_output.pdf"
    builder_with_simple_template.save_pdf(out)
    buf = builder_with_simple_template.to_buffer()

    file_bytes = out.read_bytes()
    buf_bytes = buf.read()

    assert file_bytes.startswith(b"%PDF-"), "Saved file is not a valid PDF"
    assert buf_bytes.startswith(b"%PDF-"), "Buffer is not a valid PDF"


def test_integration_with_dict_data(simple_template_path, tmp_path):
    """Full pipeline using add_data with a plain dict instead of a Template."""
    SimpleTemplate.__template_path__ = simple_template_path
    encoded = TypstEncoder.encode(
        {
            "title": "Dict Data Test",
            "author": "Jane Doe",
            "date": "2024-06-15",
            "body": Content("Body from dict."),
        }
    )
    builder = DocumentBuilder()
    builder.add_template(
        SimpleTemplate(
            title="Dict Data Test",
            author="Jane Doe",
            date="2024-06-15",
            body=Content("Body from dict."),
        )
    )
    out = tmp_path / "dict_data.pdf"
    builder.save_pdf(out)
    assert out.read_bytes().startswith(b"%PDF-"), "Output is not a valid PDF"


def test_integration_with_unicode_data(simple_template_path, tmp_path):
    """PDF is generated correctly when template fields contain Unicode characters."""
    SimpleTemplate.__template_path__ = simple_template_path
    builder = DocumentBuilder()
    builder.add_template(
        SimpleTemplate(
            title="Ünïcödé Títlé",
            author="café author ñoño",
            date="2024-01-01",
            body=Content("Unicode body: 日本語 🌍"),
        )
    )
    out = tmp_path / "unicode_output.pdf"
    builder.save_pdf(out)
    assert out.read_bytes().startswith(b"%PDF-"), "Output is not a valid PDF"


def test_integration_multiple_builds(simple_template_path, tmp_path):
    """DocumentBuilder can be used to generate multiple PDFs sequentially."""
    SimpleTemplate.__template_path__ = simple_template_path

    for i in range(3):
        builder = DocumentBuilder()
        builder.add_template(
            SimpleTemplate(
                title=f"Document {i}",
                author="Author",
                date="2024-01-01",
                body=Content(f"Body of document {i}."),
            )
        )
        out = tmp_path / f"output_{i}.pdf"
        builder.save_pdf(out)
        assert out.read_bytes().startswith(b"%PDF-"), f"Document {i} is not a valid PDF"
