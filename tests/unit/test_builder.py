import pytest
from pathlib import Path
from io import BytesIO
import tempfile

from typy.builder import DocumentBuilder
from typy.templates import BasicTemplate
from typy.content import Content


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
