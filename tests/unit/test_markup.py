from typy.markup import Heading, Markdown


def test_heading_encode_level_1():
    heading = Heading(1, "Test Heading")
    assert heading.encode() == "= Test Heading\n"


def test_heading_encode_level_2():
    heading = Heading(2, "Test Heading")
    assert heading.encode() == "== Test Heading\n"


def test_heading_encode_level_3():
    heading = Heading(3, "Test Heading")
    assert heading.encode() == "=== Test Heading\n"


def test_heading_encode_empty_text():
    heading = Heading(1, "")
    assert heading.encode() == "= \n"


def test_heading_encode_special_characters():
    heading = Heading(2, "Special & Characters!")
    assert heading.encode() == "== Special & Characters!\n"


def test_markdown_encode_simple():
    md = Markdown("## Hello")
    encoded = md.encode()
    assert 'render("## Hello",' in encoded
    assert encoded.startswith(
        "#{"
    )  # no outer content brackets; Content.encode() provides them
    assert not encoded.startswith("[#")


def test_markdown_encode_multiline():
    md = Markdown("## Hello\n\nSome **bold** text")
    encoded = md.encode()
    assert "@preview/cmarker" in encoded
    assert "render(" in encoded


def test_markdown_encode_escapes_backslash():
    md = Markdown("path\\to\\file")
    encoded = md.encode()
    assert "path\\\\to\\\\file" in encoded


def test_markdown_encode_escapes_quotes():
    md = Markdown('say "hello"')
    encoded = md.encode()
    assert '\\"hello\\"' in encoded


def test_markdown_encode_empty():
    md = Markdown("")
    encoded = md.encode()
    assert 'render("",' in encoded
    assert encoded.startswith("#{")
