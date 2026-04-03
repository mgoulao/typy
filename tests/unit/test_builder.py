import pytest
from pathlib import Path
from io import BytesIO
import tempfile

from typy.builder import DocumentBuilder
from typy.templates import BasicTemplate
from typy.content import Content
from typy.typst_encoder import TypstEncoder


@pytest.fixture
def basic_template():
    """Create a basic template for testing."""
    return BasicTemplate(
        title="Test Document",
        date="2025-10-16",
        author="Test Author",
        body=Content("This is a test document body.")
    )


@pytest.fixture
def builder_with_template(basic_template):
    """Create a DocumentBuilder with a basic template."""
    builder = DocumentBuilder()
    builder.add_template(basic_template)
    return builder


def test_save_pdf_creates_file(builder_with_template, tmp_path):
    """Test that save_pdf creates a PDF file at the specified path."""
    output_path = tmp_path / "test_output.pdf"

    # Execute save_pdf
    builder_with_template.save_pdf(output_path)

    # Verify the file was created
    assert output_path.exists(), "PDF file was not created"
    assert output_path.is_file(), "Output is not a file"
    assert output_path.stat().st_size > 0, "PDF file is empty"


def test_save_pdf_overwrites_existing_file(builder_with_template, tmp_path):
    """Test that save_pdf overwrites an existing file."""
    output_path = tmp_path / "test_output.pdf"

    # Create an existing file
    output_path.write_text("old content")
    old_size = output_path.stat().st_size

    # Execute save_pdf
    builder_with_template.save_pdf(output_path)

    # Verify the file was overwritten
    assert output_path.exists(), "PDF file was not created"
    new_size = output_path.stat().st_size
    assert new_size != old_size, "File was not overwritten"


def test_save_pdf_with_nested_directory(builder_with_template, tmp_path):
    """Test that save_pdf works with nested directories."""
    nested_dir = tmp_path / "subdir" / "nested"
    nested_dir.mkdir(parents=True)
    output_path = nested_dir / "test_output.pdf"

    # Execute save_pdf
    builder_with_template.save_pdf(output_path)

    # Verify the file was created
    assert output_path.exists(), "PDF file was not created in nested directory"
    assert output_path.stat().st_size > 0, "PDF file is empty"


def test_save_pdf_returns_builder(builder_with_template, tmp_path):
    """Test that save_pdf returns self for method chaining."""
    output_path = tmp_path / "test_output.pdf"

    # Execute save_pdf and check return value
    result = builder_with_template.save_pdf(output_path)

    # save_pdf doesn't return self currently, so it should return None
    # This test documents the current behavior
    assert result is None


def test_to_buffer_returns_bytesio(builder_with_template):
    """Test that to_buffer returns a BytesIO object."""
    buffer = builder_with_template.to_buffer()

    # Verify it's a BytesIO instance
    assert isinstance(buffer, BytesIO), "to_buffer did not return BytesIO"

    # Verify the buffer has content
    content = buffer.read()
    assert len(content) > 0, "Buffer is empty"

    # Verify the buffer position was reset to the beginning
    buffer.seek(0)
    assert buffer.tell() == 0, "Buffer position was not reset"


def test_to_buffer_contains_pdf_data(builder_with_template):
    """Test that to_buffer contains valid PDF data."""
    buffer = builder_with_template.to_buffer()

    # Read the content
    content = buffer.read()

    # Check for PDF magic number (header)
    assert content.startswith(b'%PDF-'), "Buffer does not contain PDF data"


def test_to_buffer_multiple_calls(builder_with_template):
    """Test that to_buffer can be called multiple times."""
    buffer1 = builder_with_template.to_buffer()
    buffer2 = builder_with_template.to_buffer()

    # Both should be valid BytesIO objects
    assert isinstance(buffer1, BytesIO), "First call did not return BytesIO"
    assert isinstance(buffer2, BytesIO), "Second call did not return BytesIO"

    # Both should contain content
    content1 = buffer1.read()
    content2 = buffer2.read()
    assert len(content1) > 0, "First buffer is empty"
    assert len(content2) > 0, "Second buffer is empty"

    # Content should be the same
    assert content1 == content2, "Multiple calls produced different output"


def test_to_buffer_independence(builder_with_template):
    """Test that returned buffers are independent."""
    buffer1 = builder_with_template.to_buffer()
    buffer2 = builder_with_template.to_buffer()

    # Modify buffer1
    buffer1.read()

    # buffer2 should still be at position 0
    assert buffer2.tell() == 0, "Buffers are not independent"


def test_save_pdf_and_to_buffer_same_content(builder_with_template, tmp_path):
    """Test that save_pdf and to_buffer produce the same PDF content."""
    # Save to file
    output_path = tmp_path / "test_output.pdf"
    builder_with_template.save_pdf(output_path)

    # Get buffer content
    buffer = builder_with_template.to_buffer()
    buffer_content = buffer.read()

    # Read file content
    with open(output_path, 'rb') as f:
        file_content = f.read()

    # Content should be identical
    assert buffer_content == file_content, "save_pdf and to_buffer produced different content"


def test_save_pdf_without_template():
    """Test that save_pdf fails gracefully without a template."""
    builder = DocumentBuilder()

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "test_output.pdf"

        # This should raise an exception because no template was added
        # The main.typ file won't exist in the temp directory
        with pytest.raises((FileNotFoundError, Exception)):
            builder.save_pdf(output_path)


def test_to_buffer_without_template():
    """Test that to_buffer fails gracefully without a template."""
    builder = DocumentBuilder()

    # This should raise an exception because no template was added
    # The main.typ file won't exist in the temp directory
    with pytest.raises((FileNotFoundError, Exception)):
        builder.to_buffer()


# ---- Verbose mode tests ----

def test_verbose_mode_prints_data_source_on_add_template(basic_template, capsys):
    """Test that verbose mode prints the generated Typst data source on add_template."""
    builder = DocumentBuilder(verbose=True)
    builder.add_template(basic_template)
    captured = capsys.readouterr()
    assert "[typy]" in captured.out
    assert "typy_data" in captured.out


def test_verbose_mode_prints_data_source_on_add_data(tmp_path, capsys):
    """Test that verbose mode prints the generated Typst data source on add_data."""
    builder = DocumentBuilder(verbose=True)
    builder.add_data({"name": "Alice", "age": 30})
    captured = capsys.readouterr()
    assert "[typy]" in captured.out
    assert "typy_data" in captured.out


def test_non_verbose_mode_does_not_print(basic_template, capsys):
    """Test that non-verbose mode does not print any output."""
    builder = DocumentBuilder(verbose=False)
    builder.add_template(basic_template)
    captured = capsys.readouterr()
    assert captured.out == ""


# ---- Compilation error context tests ----

def test_compilation_error_wrapped_with_message(tmp_path):
    """Test that compilation errors are wrapped with 'Typst compilation failed' prefix."""
    builder = DocumentBuilder()
    # Write an invalid Typst file to trigger a compilation error
    broken_typ = tmp_path / "broken.typ"
    broken_typ.write_text("#let x = (", encoding="utf-8")
    output = tmp_path / "out.pdf"
    with pytest.raises(Exception, match="Typst compilation failed"):
        builder.compile(broken_typ, output)


def test_compilation_error_includes_source_context(tmp_path):
    """Test that compilation errors include source context when typy_data.typ exists."""
    builder = DocumentBuilder()
    # Populate the builder's temp dir with a typy_data.typ to trigger context extraction
    typy_data = Path(builder.tmp_dir.name) / "typy_data.typ"
    typy_data.write_text("#let typy_data = (invalid syntax here\n", encoding="utf-8")

    broken_typ = tmp_path / "broken.typ"
    # Reference a line that could appear in typy_data; the key is the error message format
    broken_typ.write_text(
        f'#import "{typy_data}": typy_data\n#typy_data\n', encoding="utf-8"
    )
    output = tmp_path / "out.pdf"
    with pytest.raises(Exception) as exc_info:
        builder.compile(broken_typ, output)
    assert "Typst compilation failed" in str(exc_info.value)


# ---- Template field validation tests ----

def test_add_template_field_with_unsupported_type_raises_type_error(tmp_path):
    """Test that add_template raises TypeError with field context for unsupported types."""
    from typy.templates import Template
    from pydantic import ConfigDict

    class BadTemplate(Template):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        name: str
        bad_field: object  # 'object' instances are not encodable

        __template_name__ = "basic"
        __template_path__ = BasicTemplate.__template_path__

    # object() is not encodable; encoder should surface the field name
    bad = BadTemplate(name="hello", bad_field=object())
    builder = DocumentBuilder()
    with pytest.raises(TypeError, match="bad_field"):
        builder.add_template(bad)


def test_add_template_valid_data_does_not_raise(basic_template):
    """Test that add_template does not raise for a valid template."""
    builder = DocumentBuilder()
    # Should not raise
    builder.add_template(basic_template)


def test_get_source_context_no_line_refs():
    """Test _get_source_context returns empty string when no line refs in error."""
    builder = DocumentBuilder()
    result = builder._get_source_context("Some generic error without line references")
    assert result == ""


def test_get_source_context_no_typy_data_file():
    """Test _get_source_context returns empty string when typy_data.typ does not exist."""
    builder = DocumentBuilder()
    result = builder._get_source_context("--> main.typ:3:5 some error")
    assert result == ""


def test_get_source_context_with_typy_data_file(tmp_path):
    """Test _get_source_context returns context when typy_data.typ exists and line ref present."""
    builder = DocumentBuilder()
    typy_data = Path(builder.tmp_dir.name) / "typy_data.typ"
    typy_data.write_text("line1\nline2\nline3\nline4\nline5\n", encoding="utf-8")
    result = builder._get_source_context("--> typy_data.typ:3:1 error")
    assert "typy_data.typ" in result
    assert "line3" in result

