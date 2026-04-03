import dataclasses
from datetime import date, datetime
from pathlib import Path

import pytest
from pydantic import BaseModel

from typy.encodable import Encodable
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


# ---- Path ----


@pytest.mark.parametrize(
    "input_path, expected_output",
    [
        (Path("/some/path/to/file.txt"), '"/some/path/to/file.txt"'),
        (Path("relative/path.pdf"), '"relative/path.pdf"'),
        (Path("."), '"."'),
    ],
)
def test_path(input_path, expected_output):
    assert TypstEncoder.encode(input_path) == expected_output


# ---- Pydantic BaseModel ----


def test_pydantic_base_model():
    class PersonModel(BaseModel):
        name: str
        age: int

    model = PersonModel(name="Alice", age=30)
    assert TypstEncoder.encode(model) == '(name: "Alice", age: 30)'


def test_pydantic_base_model_nested():
    class AddressModel(BaseModel):
        city: str
        zip_code: str

    class PersonModel(BaseModel):
        name: str
        address: AddressModel

    model = PersonModel(
        name="Bob", address=AddressModel(city="Berlin", zip_code="10115")
    )
    result = TypstEncoder.encode(model)
    assert '"Bob"' in result
    assert '"Berlin"' in result
    assert '"10115"' in result


# ---- Encodable ----


def test_encodable_custom_class():
    class MyEncodable(Encodable):
        def encode(self):
            return '"custom_value"'

    obj = MyEncodable()
    assert TypstEncoder.encode(obj) == '"custom_value"'


def test_encodable_returning_dict_syntax():
    class PointEncodable(Encodable):
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def encode(self):
            return f"(x: {self.x}, y: {self.y})"

    obj = PointEncodable(3, 4)
    assert TypstEncoder.encode(obj) == "(x: 3, y: 4)"


# ---- Dataclass ----


def test_dataclass_simple():
    @dataclasses.dataclass
    class Point:
        x: int
        y: int

    assert TypstEncoder.encode(Point(1, 2)) == "(x: 1, y: 2)"


def test_dataclass_with_string_fields():
    @dataclasses.dataclass
    class Person:
        name: str
        role: str

    assert (
        TypstEncoder.encode(Person("Alice", "admin"))
        == '(name: "Alice", role: "admin")'
    )


def test_dataclass_nested():
    @dataclasses.dataclass
    class Inner:
        value: int

    @dataclasses.dataclass
    class Outer:
        inner: Inner
        label: str

    result = TypstEncoder.encode(Outer(inner=Inner(42), label="test"))
    assert "(value: 42)" in result
    assert '"test"' in result


# ---- Edge case strings ----


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("Hello # world", '"Hello # world"'),
        ("Price: $100", '"Price: $100"'),
        ("// this is a comment", '"// this is a comment"'),
        ("Code: #let x = 1", '"Code: #let x = 1"'),
        ("Formula: $x^2$", '"Formula: $x^2$"'),
        ("Hello 🌍", '"Hello 🌍"'),
        ("emoji: 😀🎉🚀", '"emoji: 😀🎉🚀"'),
        ("A" * 1000, '"' + "A" * 1000 + '"'),
    ],
)
def test_str_edge_cases(input_str, expected_output):
    assert TypstEncoder.encode(input_str) == expected_output


# ---- DataFrame edge cases ----


def test_dataframe_single_row():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"Name": ["Alice"], "Age": [30]})
    result = TypstEncoder.encode(df)
    assert "table(" in result
    assert "[*Name*]" in result
    assert "[*Age*]" in result
    assert "[Alice]" in result
    assert "[30]" in result


def test_dataframe_nan_handling():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"a": [1.0, float("nan"), 3.0], "b": ["x", None, "z"]})
    result = TypstEncoder.encode(df)
    assert "table(" in result
    assert "[*a*]" in result
    assert "[*b*]" in result


def test_dataframe_multi_index():
    pd = pytest.importorskip("pandas")
    index = pd.MultiIndex.from_tuples([(1, "a"), (1, "b"), (2, "a"), (2, "b")])
    df = pd.DataFrame({"val": [10, 20, 30, 40]}, index=index)
    result = TypstEncoder.encode(df)
    assert "table(" in result
    assert "[*val*]" in result
    assert "[10]" in result
