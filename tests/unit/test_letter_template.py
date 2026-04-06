"""Tests for the LetterTemplate."""

from io import BytesIO

import pytest

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.markup import Text
from typy.templates import LetterTemplate


@pytest.fixture()
def letter_template():
    """Create a LetterTemplate with required fields."""
    return LetterTemplate(
        sender_name="John Doe",
        sender_address="123 Main St\nAnytown, CA 12345",
        recipient_name="Jane Smith",
        recipient_address="Jane Smith Inc.\n456 Elm St\nOthertown, NY 67890",
        date="January 1, 2023",
        subject="Account Closure Request",
        body=Content(Text("Please close my account.")),
        signature_name="John Doe",
    )


def test_letter_template_fields(letter_template):
    """Test that LetterTemplate exposes the required fields."""
    assert letter_template.sender_name == "John Doe"
    assert letter_template.sender_address == "123 Main St\nAnytown, CA 12345"
    assert letter_template.recipient_name == "Jane Smith"
    assert (
        letter_template.recipient_address
        == "Jane Smith Inc.\n456 Elm St\nOthertown, NY 67890"
    )
    assert letter_template.date == "January 1, 2023"
    assert letter_template.subject == "Account Closure Request"
    assert letter_template.signature_name == "John Doe"


def test_letter_template_closing_default(letter_template):
    """Test that closing defaults to 'Sincerely'."""
    assert letter_template.closing == "Sincerely"


def test_letter_template_closing_override():
    """Test that closing can be overridden."""
    template = LetterTemplate(
        sender_name="John Doe",
        sender_address="123 Main St",
        recipient_name="Jane Smith",
        recipient_address="456 Elm St",
        date="2023-01-01",
        subject="Hello",
        body=Content(Text("Hi.")),
        closing="Best regards",
        signature_name="John Doe",
    )
    assert template.closing == "Best regards"


def test_letter_template_logo_default(letter_template):
    """Test that logo defaults to empty string (no logo)."""
    assert letter_template.logo == ""


def test_letter_template_logo_optional():
    """Test that logo can be set to a file path."""
    template = LetterTemplate(
        sender_name="John Doe",
        sender_address="123 Main St",
        recipient_name="Jane Smith",
        recipient_address="456 Elm St",
        date="2023-01-01",
        subject="Hello",
        body=Content(Text("Hi.")),
        signature_name="John Doe",
        logo="logo.png",
    )
    assert template.logo == "logo.png"


def test_letter_template_get_data(letter_template):
    """Test that get_data returns the expected keys."""
    data = letter_template.get_data()
    expected_keys = {
        "sender_name",
        "sender_address",
        "recipient_name",
        "recipient_address",
        "date",
        "subject",
        "body",
        "closing",
        "signature_name",
        "logo",
    }
    assert expected_keys.issubset(data.keys())


def test_letter_template_produces_valid_pdf(letter_template):
    """Integration test: LetterTemplate builds a valid PDF."""
    builder = DocumentBuilder()
    builder.add_template(letter_template)
    buf = builder.to_buffer()
    assert isinstance(buf, BytesIO)
    content = buf.read()
    assert content.startswith(b"%PDF-"), "Output is not a valid PDF"
    assert len(content) > 0
