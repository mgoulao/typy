from typy.markup import Heading


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
