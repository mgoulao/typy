import json
from unittest.mock import patch

import pytest

from typy.cli import (
    BUILTIN_TEMPLATES,
    _format_type,
    _get_field_rows,
    _resolve_template,
    cmd_info,
    cmd_list,
    main,
)
from typy.templates import ReportTemplate

# ---- _format_type tests ----


def test_format_type_simple_str():
    assert _format_type(str) == "str"


def test_format_type_simple_bool():
    assert _format_type(bool) == "bool"


def test_format_type_simple_int():
    assert _format_type(int) == "int"


def test_format_type_optional_str():
    import typing

    assert _format_type(typing.Optional[str]) == "str"


def test_format_type_list_str():
    assert _format_type(list[str]) == "list[str]"


def test_format_type_list_nested():

    from typy.templates import InvoiceItem

    assert _format_type(list[InvoiceItem]) == "list[InvoiceItem]"


def test_format_type_none_annotation():
    assert _format_type(None) == "Any"


# ---- BUILTIN_TEMPLATES registry tests ----


def test_builtin_templates_contains_expected_names():
    expected = {"report", "invoice", "letter", "cv", "academic", "presentation", "basic"}
    assert set(BUILTIN_TEMPLATES.keys()) == expected


def test_builtin_templates_each_has_description():
    for name, (cls, description) in BUILTIN_TEMPLATES.items():
        assert isinstance(description, str) and len(description) > 0, (
            f"Template '{name}' has no description"
        )


def test_builtin_templates_each_has_template_class():
    from typy.templates import Template

    for name, (cls, _) in BUILTIN_TEMPLATES.items():
        assert issubclass(cls, Template), f"Template '{name}' class is not a Template subclass"


# ---- _resolve_template tests ----


def test_resolve_template_builtin_report():
    cls = _resolve_template("report")
    assert cls is ReportTemplate


def test_resolve_template_builtin_all():
    for name in BUILTIN_TEMPLATES:
        cls = _resolve_template(name)
        assert cls is not None, f"Failed to resolve built-in template '{name}'"


def test_resolve_template_unknown_returns_none():
    assert _resolve_template("nonexistent") is None


def test_resolve_template_custom_py_file(tmp_path):
    custom_file = tmp_path / "custom_template.py"
    custom_file.write_text(
        "from pathlib import Path\n"
        "from typy.templates import Template\n"
        "from typy.content import Content\n"
        "\n"
        "class MyTemplate(Template):\n"
        "    title: str\n"
        "    body: Content\n"
        "    __template_name__ = 'my'\n"
        "    __template_path__ = Path('/tmp/my.typ')\n",
        encoding="utf-8",
    )
    cls = _resolve_template(str(custom_file))
    assert cls is not None
    assert cls.__name__ == "MyTemplate"


def test_resolve_template_nonexistent_py_file():
    assert _resolve_template("/nonexistent/path/template.py") is None


# ---- _get_field_rows tests ----


def test_get_field_rows_report():
    rows = _get_field_rows(ReportTemplate)
    names = [r["name"] for r in rows]
    assert "title" in names
    assert "subtitle" in names
    assert "toc" in names


def test_get_field_rows_required_flag():
    rows = _get_field_rows(ReportTemplate)
    by_name = {r["name"]: r for r in rows}
    assert by_name["title"]["required"] is True
    assert by_name["subtitle"]["required"] is False


def test_get_field_rows_defaults():
    rows = _get_field_rows(ReportTemplate)
    by_name = {r["name"]: r for r in rows}
    assert by_name["toc"]["default"] is True
    assert by_name["subtitle"]["default"] is None


# ---- cmd_list tests ----


def test_cmd_list_prints_all_templates(capsys):
    cmd_list()
    captured = capsys.readouterr()
    for name in BUILTIN_TEMPLATES:
        assert name in captured.out


def test_cmd_list_prints_descriptions(capsys):
    cmd_list()
    captured = capsys.readouterr()
    for _, description in BUILTIN_TEMPLATES.values():
        assert description in captured.out


def test_cmd_list_has_header(capsys):
    cmd_list()
    captured = capsys.readouterr()
    assert "Available templates" in captured.out


# ---- cmd_info tests ----


def test_cmd_info_report_human_readable(capsys):
    cmd_info("report")
    captured = capsys.readouterr()
    assert "Template: report" in captured.out
    assert "title" in captured.out
    assert "required" in captured.out
    assert "optional" in captured.out


def test_cmd_info_report_json(capsys):
    cmd_info("report", as_json=True)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["template"] == "report"
    assert isinstance(data["fields"], list)
    field_names = [f["name"] for f in data["fields"]]
    assert "title" in field_names
    assert "toc" in field_names


def test_cmd_info_json_field_structure(capsys):
    cmd_info("report", as_json=True)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    for field in data["fields"]:
        assert "name" in field
        assert "type" in field
        assert "required" in field
        assert "default" in field


def test_cmd_info_unknown_template_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cmd_info("nonexistent_template")
    assert exc_info.value.code == 1


def test_cmd_info_unknown_template_prints_error(capsys):
    with pytest.raises(SystemExit):
        cmd_info("nonexistent_template")
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cmd_info_all_builtin_templates(capsys):
    for name in BUILTIN_TEMPLATES:
        cmd_info(name)
        captured = capsys.readouterr()
        assert f"Template: {name}" in captured.out


def test_cmd_info_json_required_field_has_null_default(capsys):
    cmd_info("report", as_json=True)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    title_field = next(f for f in data["fields"] if f["name"] == "title")
    assert title_field["required"] is True
    assert title_field["default"] is None


def test_cmd_info_json_optional_field_has_default(capsys):
    cmd_info("report", as_json=True)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    toc_field = next(f for f in data["fields"] if f["name"] == "toc")
    assert toc_field["required"] is False
    assert toc_field["default"] is True


# ---- main() / argparse tests ----


def test_main_list(capsys):
    with patch("sys.argv", ["typy", "list"]):
        main()
    captured = capsys.readouterr()
    assert "Available templates" in captured.out


def test_main_info(capsys):
    with patch("sys.argv", ["typy", "info", "report"]):
        main()
    captured = capsys.readouterr()
    assert "Template: report" in captured.out


def test_main_info_json(capsys):
    with patch("sys.argv", ["typy", "info", "report", "--json"]):
        main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["template"] == "report"


def test_main_no_command_exits_zero(capsys):
    with patch("sys.argv", ["typy"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 0


def test_main_info_custom_py_file(tmp_path, capsys):
    custom_file = tmp_path / "custom.py"
    custom_file.write_text(
        "from pathlib import Path\n"
        "from typy.templates import Template\n"
        "from typy.content import Content\n"
        "\n"
        "class CustomTemplate(Template):\n"
        "    name: str\n"
        "    body: Content\n"
        "    __template_name__ = 'custom'\n"
        "    __template_path__ = Path('/tmp/custom.typ')\n",
        encoding="utf-8",
    )
    with patch("sys.argv", ["typy", "info", str(custom_file)]):
        main()
    captured = capsys.readouterr()
    assert "name" in captured.out
    assert "body" in captured.out
