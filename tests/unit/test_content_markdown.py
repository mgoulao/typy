"""Tests for auto-conversion of markdown strings in Content fields."""

import pytest
from pydantic import ValidationError

from typy.content import Content
from typy.markup import Markdown, Text
from typy.templates import BasicTemplate


# ---- Content constructor: no auto-conversion ----


def test_content_with_string_stores_string_directly():
    """Passing a str directly to Content() stores it as-is (no auto-conversion)."""
    c = Content("plain text")
    assert len(c.content) == 1
    assert isinstance(c.content[0], str)


def test_content_with_list_of_strings_stores_strings():
    """Passing a list of strs to Content() stores them as-is."""
    c = Content(["hello", "world"])
    assert all(isinstance(item, str) for item in c.content)


def test_content_with_markdown_object_unchanged():
    """Passing a Markdown object to Content() stores it unchanged."""
    md = Markdown("## Hello")
    c = Content(md)
    assert c.content[0] is md


def test_content_with_text_object_unchanged():
    """Passing a Text object to Content() stores it unchanged."""
    t = Text("hello")
    c = Content(t)
    assert c.content[0] is t


# ---- Pydantic coercion: Content field accepts raw strings ----


def test_pydantic_content_field_coerces_string_to_markdown():
    """A str assigned to a Content-typed Pydantic field is wrapped in Markdown."""
    template = BasicTemplate(
        title="Test",
        date="2024-01-01",
        author="Author",
        body="## Hello\n\nThis is **markdown**.",
    )
    assert isinstance(template.body, Content)
    assert len(template.body.content) == 1
    assert isinstance(template.body.content[0], Markdown)
    assert template.body.content[0].text == "## Hello\n\nThis is **markdown**."


def test_pydantic_content_field_accepts_content_object_unchanged():
    """A Content object assigned to a Content-typed field passes through unchanged."""
    body = Content(Text("hello"))
    template = BasicTemplate(
        title="Test",
        date="2024-01-01",
        author="Author",
        body=body,
    )
    assert template.body is body


def test_pydantic_content_field_accepts_explicit_markdown():
    """An explicit Markdown(...) object passes through unchanged as the field value."""
    md = Markdown("## Explicit Markdown")
    template = BasicTemplate(
        title="Test",
        date="2024-01-01",
        author="Author",
        body=md,
    )
    assert isinstance(template.body, Content)
    assert isinstance(template.body.content[0], Markdown)
    assert template.body.content[0].text == "## Explicit Markdown"


def test_pydantic_str_field_remains_plain_string():
    """Fields typed as str are never converted to Markdown."""
    template = BasicTemplate(
        title="## This is NOT markdown",
        date="2024-01-01",
        author="Author",
        body=Content(Text("body")),
    )
    assert isinstance(template.title, str)
    assert template.title == "## This is NOT markdown"


# ---- Encoding of auto-converted Content ----


def test_string_coerced_to_markdown_encodes_with_cmarker():
    """A string coerced to Content via Pydantic encodes using the cmarker renderer."""
    template = BasicTemplate(
        title="Test",
        date="2024-01-01",
        author="Author",
        body="## Hello\n\n**bold**",
    )
    encoded = template.body.encode()
    assert "@preview/cmarker" in encoded
    assert "render(" in encoded
    assert "## Hello" in encoded


def test_string_coerced_encodes_escaping_backslash():
    """Backslashes in auto-converted strings are properly escaped for cmarker."""
    template = BasicTemplate(
        title="T",
        date="2024-01-01",
        author="A",
        body="path\\to\\file",
    )
    encoded = template.body.encode()
    assert "path\\\\to\\\\file" in encoded


def test_string_coerced_encodes_escaping_quotes():
    """Double quotes in auto-converted strings are properly escaped for cmarker."""
    template = BasicTemplate(
        title="T",
        date="2024-01-01",
        author="A",
        body='say "hello"',
    )
    encoded = template.body.encode()
    assert '\\"hello\\"' in encoded


# ---- get_data round-trip ----


def test_get_data_returns_content_object_for_body():
    """get_data() returns the Content object for the body field (not a plain dict)."""
    template = BasicTemplate(
        title="Title",
        date="2024-01-01",
        author="Author",
        body="Some **markdown**.",
    )
    data = template.get_data()
    assert isinstance(data["body"], Content)


def test_get_data_str_fields_remain_plain_strings():
    """get_data() preserves str-typed fields as plain strings."""
    template = BasicTemplate(
        title="## Title",
        date="2024-01-01",
        author="Author",
        body=Content(Text("body")),
    )
    data = template.get_data()
    assert data["title"] == "## Title"
    assert isinstance(data["title"], str)
