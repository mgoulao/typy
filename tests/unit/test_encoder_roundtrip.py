"""Round-trip tests: encode a Python value and verify the result compiles with Typst."""

import dataclasses
import tempfile
from datetime import date, datetime
from pathlib import Path

import pytest
import typst
from pydantic import BaseModel

from typy.encodable import Encodable
from typy.typst_encoder import TypstEncoder


def _compile_encoded(encoded: str) -> bytes:
    """Write encoded value into a minimal Typst document and compile it to PDF."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        typ_file = Path(tmp_dir) / "test.typ"
        out_file = Path(tmp_dir) / "test.pdf"
        typ_file.write_text(f"#let data = {encoded}\nDocument.", encoding="utf-8")
        typst.compile(typ_file, output=out_file)
        return out_file.read_bytes()


# ---- Primitive types ----


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "",
        "test with spaces",
        'has "quotes"',
        "has\\backslash",
        0,
        1,
        -42,
        999999,
        0.0,
        3.14,
        -1.5,
        True,
        False,
        None,
    ],
)
def test_primitive_roundtrip(value):
    """Encoded primitive types produce valid Typst that compiles without error."""
    encoded = TypstEncoder.encode(value)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"
    assert len(pdf) > 0


# ---- Strings with Typst-reserved and special characters ----


@pytest.mark.parametrize(
    "value",
    [
        "Hello # world",
        "Price: $100",
        "// this is a comment",
        "Code: #let x = 1",
        "Formula: $x^2$",
        "Hello 🌍",
        "emoji 😀🎉🚀",
        "café ñoño",
        "A" * 1000,
        "line1\nline2\nline3",
    ],
)
def test_string_edge_case_roundtrip(value):
    """Strings with special or non-ASCII characters compile without error."""
    encoded = TypstEncoder.encode(value)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- Collections ----


@pytest.mark.parametrize(
    "value",
    [
        [],
        [1],
        [1, 2, 3],
        ("a", "b"),
        (42,),
        {},
        {"key": "value"},
        {"a": 1, "b": True, "c": None},
        [{"x": 1}, {"x": 2}],
        {"items": [1, 2, 3]},
        {"a": {"b": {"c": [1, 2]}}},
    ],
)
def test_collection_roundtrip(value):
    """Encoded collection types produce valid Typst that compiles without error."""
    encoded = TypstEncoder.encode(value)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- Path ----


@pytest.mark.parametrize(
    "value",
    [
        Path("/absolute/path/to/file.pdf"),
        Path("relative/path.typ"),
        Path("."),
    ],
)
def test_path_roundtrip(value):
    """Encoded Path values compile without error."""
    encoded = TypstEncoder.encode(value)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- datetime and date ----


def test_date_roundtrip():
    """Encoded date values compile without error."""
    encoded = TypstEncoder.encode(date(2024, 3, 15))
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


def test_datetime_roundtrip():
    """Encoded datetime values compile without error."""
    encoded = TypstEncoder.encode(datetime(2024, 3, 15, 10, 30))
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- Pydantic BaseModel ----


def test_pydantic_model_roundtrip():
    """Encoded Pydantic model compiles without error."""

    class PersonModel(BaseModel):
        name: str
        age: int
        active: bool

    model = PersonModel(name="Alice", age=30, active=True)
    encoded = TypstEncoder.encode(model)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- Encodable ----


def test_encodable_roundtrip():
    """Custom Encodable objects compile without error."""

    class TagEncodable(Encodable):
        def __init__(self, tag: str):
            self.tag = tag

        def encode(self):
            return TypstEncoder.encode({"tag": self.tag})

    obj = TagEncodable("important")
    encoded = TypstEncoder.encode(obj)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- Dataclass ----


def test_dataclass_roundtrip():
    """Encoded dataclass instances compile without error."""

    @dataclasses.dataclass
    class Point:
        x: float
        y: float

    encoded = TypstEncoder.encode(Point(1.5, -2.5))
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


# ---- DataFrame ----


def test_dataframe_roundtrip():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [30, 25]})
    encoded = TypstEncoder.encode(df)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


def test_dataframe_single_row_roundtrip():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"Name": ["Alice"], "Score": [99.5]})
    encoded = TypstEncoder.encode(df)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


def test_dataframe_empty_roundtrip():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame()
    encoded = TypstEncoder.encode(df)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


def test_dataframe_nan_roundtrip():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"a": [1.0, float("nan"), 3.0], "b": ["x", None, "z"]})
    encoded = TypstEncoder.encode(df)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


def test_dataframe_mixed_dtypes_roundtrip():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"val": [1, 2.5, 3], "flag": [True, False, True]})
    encoded = TypstEncoder.encode(df)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"


def test_dataframe_multi_index_roundtrip():
    pd = pytest.importorskip("pandas")
    index = pd.MultiIndex.from_tuples([(1, "a"), (1, "b"), (2, "a"), (2, "b")])
    df = pd.DataFrame({"val": [10, 20, 30, 40]}, index=index)
    encoded = TypstEncoder.encode(df)
    pdf = _compile_encoded(encoded)
    assert pdf.startswith(b"%PDF-"), "Output is not a valid PDF"
