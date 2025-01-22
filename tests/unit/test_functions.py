import pytest
from typy.functions import Figure, Table
from typy.markup import Raw


def test_table_encode_simple():
    data = {"Name": {0: "Alice", 1: "Bob"}, "Age": {0: 30, 1: 25}}
    table = Table(data)
    expected_output = """table(columns:(auto, auto), table.header(
    [*Name*], [*Age*],
  ),
  [Alice], [30],
  [Bob], [25],
)"""
    assert table.encode() == expected_output


def test_table_encode_empty_data():
    with pytest.raises(TypeError, match="missing 1 required positional argument"):
        Table()


def test_figure_encode_simple():
    content = "Sample content"
    figure = Figure(content)
    expected_output = 'figure("Sample content")'
    assert figure.encode() == expected_output


def test_figure_encode_with_kwargs():
    content = "Sample content"
    figure = Figure(content, width=Raw("100%"), height=Raw("auto"))
    expected_output = 'figure(width:100%,\nheight:auto, "Sample content")'
    assert figure.encode() == expected_output


def test_figure_encode_empty_content():
    with pytest.raises(TypeError, match="missing 1 required positional argument"):
        Figure()
