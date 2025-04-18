from typy.typst_encoder import TypstEncoder
import pytest


@pytest.mark.parametrize(
    "input_list, expected_output",
    [
        (["test", "test2"], '("test", "test2",)'),
        ([1], "(1,)"),
        ([], "()"),
    ],
)
def test_list(input_list, expected_output):
    assert TypstEncoder.encode(input_list) == expected_output


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("test", '"test"'),
        ("test test", '"test test"'),
        ("test test test", '"test test test"'),
        ("test\ntest", '"test\ntest"'),
        ('test "test"', '"test \\"test\\""'),
    ],
)
def test_str(input_str, expected_output):
    assert TypstEncoder.encode(input_str) == expected_output
