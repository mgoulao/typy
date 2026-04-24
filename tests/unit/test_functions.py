import pytest

from typy.content import Content
from typy.functions import Badge, Callout, Columns, Figure, Grid, Table
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


def test_grid_encode_simple():
    grid = Grid(Content(["Left", "Right"]), columns=2, gutter=Raw("1em"))
    encoded = grid.encode()
    assert encoded.startswith("grid(")
    assert "columns:2" in encoded
    assert "gutter:1em" in encoded


def test_columns_encode_simple():
    columns = Columns(Content(["Col 1", "Col 2"]), count=2)
    encoded = columns.encode()
    assert encoded.startswith("columns(")
    assert "count:2" in encoded


def test_badge_encode_simple():
    badge = Badge("Stable")
    encoded = badge.encode()
    assert encoded.startswith("box(")
    assert '"Stable"' in encoded


def test_callout_encode_with_title():
    callout = Callout("Use caution.", title="Warning")
    encoded = callout.encode()
    assert encoded.startswith("block(")
    assert "*Warning*" in encoded
    assert "Use caution." in encoded
