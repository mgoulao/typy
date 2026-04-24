"""Unit tests for the Slide model and PresentationTemplate."""

from typy.content import Content
from typy.markup import Raw
from typy.templates import PresentationTemplate, Slide
from typy.typst_encoder import TypstEncoder

# ---- Slide model encoding ----


def test_slide_encodes_title_and_body():
    slide = Slide(title="My Slide", body=Content("Hello world"))
    encoded = TypstEncoder.encode(slide)
    assert '"My Slide"' in encoded
    assert "Hello world" in encoded


def test_slide_notes_none_by_default():
    slide = Slide(title="No Notes", body=Content("Body text"))
    encoded = TypstEncoder.encode(slide)
    assert "none" in encoded  # notes: none


def test_slide_with_notes_encodes_correctly():
    slide = Slide(title="With Notes", body=Content("Body"), notes="Speaker note text")
    encoded = TypstEncoder.encode(slide)
    assert '"Speaker note text"' in encoded


def test_slide_with_subtitle_and_footnote_encodes_correctly():
    slide = Slide(
        title="With Metadata",
        subtitle="Short subtitle",
        body=Content("Body"),
        footnote="Reference 1",
    )
    encoded = TypstEncoder.encode(slide)
    assert '"Short subtitle"' in encoded
    assert '"Reference 1"' in encoded


def test_slide_layout_variant_optional():
    slide = Slide(title="Variant", body=Content("Body"), layout_variant="two-column")
    encoded = TypstEncoder.encode(slide)
    assert '"two-column"' in encoded


def test_slide_body_as_content_block():
    slide = Slide(title="Slide", body=Content("Some content"))
    encoded = TypstEncoder.encode(slide)
    # Content encodes as [...] block
    assert "[" in encoded
    assert "Some content" in encoded


def test_slide_with_raw_body():
    slide = Slide(title="Code Slide", body=Content([Raw("```python\nprint(42)\n```")]))
    encoded = TypstEncoder.encode(slide)
    assert "print(42)" in encoded


# ---- PresentationTemplate encoding ----


def test_presentation_template_encodes_title_and_author():
    template = PresentationTemplate(
        title="My Talk",
        author="Jane Doe",
        date="2024-01-15",
        slides=[Slide(title="Intro", body=Content("Hello"))],
    )
    encoded = TypstEncoder.encode(template.get_data())
    assert '"My Talk"' in encoded
    assert '"Jane Doe"' in encoded
    assert '"2024-01-15"' in encoded


def test_presentation_template_optional_subtitle_none():
    template = PresentationTemplate(
        title="No Subtitle",
        author="Author",
        date="2024-01-01",
        slides=[Slide(title="Slide 1", body=Content("Body"))],
    )
    data = template.get_data()
    assert data["subtitle"] is None
    encoded = TypstEncoder.encode(data)
    assert "none" in encoded


def test_presentation_template_with_subtitle():
    template = PresentationTemplate(
        title="Main Title",
        subtitle="A subtitle",
        author="Author",
        date="2024-01-01",
        slides=[Slide(title="Slide 1", body=Content("Body"))],
    )
    encoded = TypstEncoder.encode(template.get_data())
    assert '"A subtitle"' in encoded


def test_presentation_template_slides_list_encoded():
    template = PresentationTemplate(
        title="Talk",
        author="Author",
        date="2024-01-01",
        slides=[
            Slide(title="First", body=Content("First body")),
            Slide(title="Second", body=Content("Second body")),
        ],
    )
    encoded = TypstEncoder.encode(template.get_data())
    assert '"First"' in encoded
    assert '"Second"' in encoded
    assert "First body" in encoded
    assert "Second body" in encoded


def test_presentation_template_empty_slides_list():
    template = PresentationTemplate(
        title="Empty",
        author="Author",
        date="2024-01-01",
        slides=[],
    )
    encoded = TypstEncoder.encode(template.get_data())
    assert "slides" in encoded


def test_slide_body_accepts_string_via_content_coercion():
    """Content fields auto-convert strings to Markdown."""
    slide = Slide(title="Markdown Slide", body="**Bold text**")
    assert isinstance(slide.body, Content)
    encoded = TypstEncoder.encode(slide)
    assert "Bold text" in encoded


def test_presentation_template_fields():
    """Verify PresentationTemplate has the required fields."""
    template = PresentationTemplate(
        title="T",
        author="A",
        date="2024-01-01",
        slides=[],
    )
    data = template.get_data()
    assert "title" in data
    assert "subtitle" in data
    assert "author" in data
    assert "date" in data
    assert "slides" in data


def test_slide_notes_included_in_template_data():
    template = PresentationTemplate(
        title="T",
        author="A",
        date="2024-01-01",
        slides=[
            Slide(title="S", body=Content("B"), notes="My speaker notes"),
        ],
    )
    encoded = TypstEncoder.encode(template.get_data())
    assert '"My speaker notes"' in encoded


def test_slide_new_fields_included_in_template_data():
    template = PresentationTemplate(
        title="T",
        author="A",
        date="2024-01-01",
        slides=[
            Slide(
                title="S",
                subtitle="Sub",
                body=Content("B"),
                footnote="Fn",
                layout_variant="hero",
            ),
        ],
    )
    encoded = TypstEncoder.encode(template.get_data())
    assert '"Sub"' in encoded
    assert '"Fn"' in encoded
    assert '"hero"' in encoded
