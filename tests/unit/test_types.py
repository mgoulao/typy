from datetime import date, datetime

import pytest

from typy.typst_encoder import TypstEncoder


@pytest.mark.parametrize(
    "input_list, expected_output",
    [
        (["test", "test2"], '("test", "test2")'),
        ([1], "(1,)"),
        ([], "()"),
        ([1, 2, 3], "(1, 2, 3)"),
        ((1, 2), "(1, 2)"),
        ((42,), "(42,)"),
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
        ("", '""'),
        ("hello\\world", '"hello\\\\world"'),
        ('back\\slash and "quote"', '"back\\\\slash and \\"quote\\""'),
        ("café ñoño", '"café ñoño"'),
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


@pytest.mark.parametrize(
    "input_bool, expected_output",
    [
        (True, "true"),
        (False, "false"),
    ],
)
def test_bool(input_bool, expected_output):
    assert TypstEncoder.encode(input_bool) == expected_output


@pytest.mark.parametrize(
    "input_int, expected_output",
    [
        (0, "0"),
        (1, "1"),
        (-1, "-1"),
        (999999, "999999"),
    ],
)
def test_int(input_int, expected_output):
    assert TypstEncoder.encode(input_int) == expected_output


@pytest.mark.parametrize(
    "input_float, expected_output",
    [
        (0.0, "0.0"),
        (1.5, "1.5"),
        (-3.14, "-3.14"),
    ],
)
def test_float(input_float, expected_output):
    assert TypstEncoder.encode(input_float) == expected_output


def test_none():
    assert TypstEncoder.encode(None) == "none"


@pytest.mark.parametrize(
    "input_dict, expected_output",
    [
        ({}, "()"),
        ({"key": "value"}, '(key: "value")'),
        ({"a": 1, "b": 2}, "(a: 1, b: 2)"),
        ({"flag": True}, "(flag: true)"),
        ({"nothing": None}, "(nothing: none)"),
    ],
)
def test_dict(input_dict, expected_output):
    assert TypstEncoder.encode(input_dict) == expected_output


def test_date():
    d = date(2024, 3, 15)
    assert TypstEncoder.encode(d) == "datetime(year:2024,\nmonth:3,\nday:15)"


def test_datetime():
    dt = datetime(2024, 3, 15)
    assert TypstEncoder.encode(dt) == "datetime(year:2024,\nmonth:3,\nday:15)"


def test_nested_list_of_dicts():
    data = [{"x": 1}, {"x": 2}]
    assert TypstEncoder.encode(data) == "((x: 1), (x: 2))"


def test_nested_dict_of_lists():
    data = {"items": [1, 2, 3]}
    assert TypstEncoder.encode(data) == "(items: (1, 2, 3))"


def test_deeply_nested():
    data = {"a": {"b": {"c": [1, 2]}}}
    assert TypstEncoder.encode(data) == "(a: (b: (c: (1, 2))))"


def test_list_with_none_and_bool():
    data = [None, True, False]
    assert TypstEncoder.encode(data) == "(none, true, false)"


def test_dataframe():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [30, 25]})
    result = TypstEncoder.encode(df)
    assert "table(" in result
    assert "[*Name*]" in result
    assert "[*Age*]" in result
    assert "[Alice]" in result
    assert "[30]" in result


def test_dataframe_empty():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame()
    result = TypstEncoder.encode(df)
    assert "table(" in result


def test_dataframe_mixed_dtypes():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"val": [1, 2.5, 3], "flag": [True, False, True]})
    result = TypstEncoder.encode(df)
    assert "table(" in result
    assert "[*val*]" in result
    assert "[*flag*]" in result
