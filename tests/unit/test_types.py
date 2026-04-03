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


def test_unsupported_type_raises_type_error():
    with pytest.raises(TypeError) as exc_info:
        TypstEncoder.encode({1, 2, 3})
    error_msg = str(exc_info.value)
    assert "set" in error_msg
    assert "Cannot encode type" in error_msg


def test_unsupported_type_error_message_lists_supported_types():
    with pytest.raises(TypeError) as exc_info:
        TypstEncoder.encode(object())
    error_msg = str(exc_info.value)
    assert "Supported types:" in error_msg
    for supported in ("str", "int", "float", "bool", "list", "dict"):
        assert supported in error_msg


def test_unsupported_type_name_in_error():
    class MyCustomClass:
        pass

    with pytest.raises(TypeError) as exc_info:
        TypstEncoder.encode(MyCustomClass())
    assert "MyCustomClass" in str(exc_info.value)
