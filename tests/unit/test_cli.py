import json
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from typy.cli import (
    BUILTIN_TEMPLATES,
    _build_app,
    _format_type,
    _generate_sample_data,
    _get_field_rows,
    _load_json_data,
    _resolve_template,
    cmd_info,
    cmd_list,
    cmd_render,
    cmd_scaffold,
)
from typy.templates import ReportTemplate

runner = CliRunner()


def _plain_help(text: str) -> str:
    """Strip ANSI escape sequences to make help assertions stable."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


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
    expected = {
        "report",
        "invoice",
        "letter",
        "cv",
        "academic",
        "presentation",
        "basic",
    }
    assert set(BUILTIN_TEMPLATES.keys()) == expected


def test_builtin_templates_each_has_description():
    for name, (cls, description) in BUILTIN_TEMPLATES.items():
        assert isinstance(description, str) and len(description) > 0, (
            f"Template '{name}' has no description"
        )


def test_builtin_templates_each_has_template_class():
    from typy.templates import Template

    for name, (cls, _) in BUILTIN_TEMPLATES.items():
        assert issubclass(cls, Template), (
            f"Template '{name}' class is not a Template subclass"
        )


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


# ---- main() / typer CliRunner tests ----


def test_main_list():
    app = _build_app()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Available templates" in result.output


def test_main_info():
    app = _build_app()
    result = runner.invoke(app, ["info", "report"])
    assert result.exit_code == 0
    assert "Template: report" in result.output


def test_main_info_json():
    app = _build_app()
    result = runner.invoke(app, ["info", "report", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["template"] == "report"


def test_main_no_command_shows_help():
    app = _build_app()
    result = runner.invoke(app, [])
    assert "typy" in result.output


def test_main_help_includes_quick_guide_steps():
    app = _build_app()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    plain = _plain_help(result.output)
    assert "Quick guide" in plain
    assert "typy info report --json" in plain
    assert "typy render --template report --data data.json" in plain


def test_main_help_mentions_agent_friendly_json_schema_output():
    app = _build_app()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    plain = _plain_help(result.output)
    assert "scripts" in plain
    assert "AI" in plain
    assert "agents" in plain


def test_main_info_custom_py_file(tmp_path):
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
    app = _build_app()
    result = runner.invoke(app, ["info", str(custom_file)])
    assert result.exit_code == 0
    assert "name" in result.output
    assert "body" in result.output


# ---- _generate_sample_data tests ----


def test_generate_sample_data_report_has_all_fields():
    data = _generate_sample_data(ReportTemplate)
    assert "title" in data
    assert "author" in data
    assert "date" in data
    assert "body" in data
    assert "toc" in data


def test_generate_sample_data_report_required_str_fields_are_strings():
    data = _generate_sample_data(ReportTemplate)
    assert isinstance(data["title"], str) and data["title"]
    assert isinstance(data["author"], str) and data["author"]


def test_generate_sample_data_report_body_is_string():
    data = _generate_sample_data(ReportTemplate)
    assert isinstance(data["body"], str)
    assert len(data["body"]) > 0


def test_generate_sample_data_report_toc_uses_default():
    data = _generate_sample_data(ReportTemplate)
    assert data["toc"] is True  # Pydantic default


def test_generate_sample_data_report_optional_uses_default():
    data = _generate_sample_data(ReportTemplate)
    assert data["subtitle"] is None  # Pydantic default


def test_generate_sample_data_all_builtin_templates():
    for name, (cls, _) in BUILTIN_TEMPLATES.items():
        data = _generate_sample_data(cls)
        assert isinstance(data, dict), f"Sample data for '{name}' is not a dict"
        assert data, f"Sample data for '{name}' is empty"


def test_generate_sample_data_is_json_serializable():
    """All generated sample data must be JSON-serializable."""
    for _name, (cls, _) in BUILTIN_TEMPLATES.items():
        data = _generate_sample_data(cls)
        # Should not raise
        json.dumps(data, default=str)


def test_generate_sample_data_invoice_has_items_list():
    from typy.templates import InvoiceTemplate

    data = _generate_sample_data(InvoiceTemplate)
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 1
    assert "description" in data["items"][0]


def test_generate_sample_data_cv_has_nested_contact():
    from typy.templates import CVTemplate

    data = _generate_sample_data(CVTemplate)
    assert isinstance(data["contact"], dict)
    assert "email" in data["contact"]


# ---- cmd_scaffold tests ----


def test_cmd_scaffold_prints_json_to_stdout(capsys):
    cmd_scaffold("report", output_file=None)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "title" in data
    assert "body" in data


def test_cmd_scaffold_writes_to_file(tmp_path):
    output = tmp_path / "data.json"
    cmd_scaffold("report", output_file=output)
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert "title" in data


def test_cmd_scaffold_creates_output_parent_dirs(tmp_path):
    output = tmp_path / "subdir" / "data.json"
    cmd_scaffold("report", output_file=output)
    assert output.exists()


def test_cmd_scaffold_unknown_template_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cmd_scaffold("nonexistent", output_file=None)
    assert exc_info.value.code == 1


def test_cmd_scaffold_unknown_template_error_message(capsys):
    with pytest.raises(SystemExit):
        cmd_scaffold("nonexistent", output_file=None)
    captured = capsys.readouterr()
    assert "nonexistent" in captured.err


def test_main_scaffold_report_to_stdout(capsys):
    app = _build_app()
    result = runner.invoke(app, ["scaffold", "report"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "title" in data


def test_main_scaffold_report_to_file(tmp_path):
    output = tmp_path / "data.json"
    app = _build_app()
    result = runner.invoke(app, ["scaffold", "report", "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert "title" in data


def test_main_scaffold_unknown_template_exits():
    app = _build_app()
    result = runner.invoke(app, ["scaffold", "nonexistent"])
    assert result.exit_code == 1


# ---- _load_json_data tests ----


def test_load_json_data_valid(tmp_path):
    data_file = tmp_path / "data.json"
    data_file.write_text('{"title": "Test", "author": "Alice"}', encoding="utf-8")
    result = _load_json_data(data_file)
    assert result == {"title": "Test", "author": "Alice"}


def test_load_json_data_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="Data file not found"):
        _load_json_data(tmp_path / "nonexistent.json")


def test_load_json_data_invalid_json(tmp_path):
    data_file = tmp_path / "bad.json"
    data_file.write_text("{not valid json}", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        _load_json_data(data_file)


# ---- cmd_render error tests (no compilation) ----


def test_cmd_render_no_template_no_markdown_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template=None, data_file=None, markdown_file=None, output=Path("out.pdf")
        )
    assert exc_info.value.code == 1


def test_cmd_render_no_template_no_markdown_error_message(capsys):
    with pytest.raises(SystemExit):
        cmd_render(
            template=None, data_file=None, markdown_file=None, output=Path("out.pdf")
        )
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cmd_render_missing_markdown_file_exits(capsys, tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template=None,
            data_file=None,
            markdown_file=tmp_path / "missing.md",
            output=tmp_path / "out.pdf",
        )
    assert exc_info.value.code == 1


def test_cmd_render_missing_markdown_file_error_message(capsys, tmp_path):
    with pytest.raises(SystemExit):
        cmd_render(
            template=None,
            data_file=None,
            markdown_file=tmp_path / "missing.md",
            output=tmp_path / "out.pdf",
        )
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cmd_render_template_no_data_no_markdown_uses_sample_data(capsys, tmp_path):
    """When --template is given without --data or --markdown, sample data is auto-generated."""
    with patch("typy.builder.DocumentBuilder.save_pdf"):
        cmd_render(
            template="report",
            data_file=None,
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )
    captured = capsys.readouterr()
    assert "sample data" in captured.err.lower()


def test_cmd_render_template_no_data_no_markdown_renders(capsys, tmp_path):
    """No --data with --template renders successfully using auto-generated data."""
    with patch("typy.builder.DocumentBuilder.save_pdf") as mock_save:
        cmd_render(
            template="report",
            data_file=None,
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )
    mock_save.assert_called_once_with(tmp_path / "out.pdf")


def test_cmd_render_unknown_template_exits(capsys, tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Hello", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template="nonexistent_template",
            data_file=None,
            markdown_file=md,
            output=tmp_path / "out.pdf",
        )
    assert exc_info.value.code == 1


def test_cmd_render_unknown_template_error_message(capsys, tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Hello", encoding="utf-8")
    with pytest.raises(SystemExit):
        cmd_render(
            template="nonexistent_template",
            data_file=None,
            markdown_file=md,
            output=tmp_path / "out.pdf",
        )
    captured = capsys.readouterr()
    assert "nonexistent_template" in captured.err


def test_cmd_render_invalid_json_data_exits(capsys, tmp_path):
    data_file = tmp_path / "bad.json"
    data_file.write_text("{bad json}", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template="report",
            data_file=data_file,
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )
    assert exc_info.value.code == 1


def test_cmd_render_missing_data_file_exits(capsys, tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template="report",
            data_file=tmp_path / "missing.json",
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )
    assert exc_info.value.code == 1


def test_cmd_render_validation_error_exits(capsys, tmp_path):
    """Report template validation fails when required fields are missing."""
    data_file = tmp_path / "data.json"
    data_file.write_text(
        '{"title": "Test"}', encoding="utf-8"
    )  # missing required fields
    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template="report",
            data_file=data_file,
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )
    assert exc_info.value.code == 1


# ---- cmd_render success tests (mocked compilation) ----


def test_cmd_render_markdown_only_calls_save_pdf(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Hello\n\nWorld.", encoding="utf-8")
    output = tmp_path / "notes.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf") as mock_save:
        cmd_render(template=None, data_file=None, markdown_file=md, output=output)

    mock_save.assert_called_once_with(output)


def test_cmd_render_prints_success_message(capsys, tmp_path):
    """After a successful render, the output path is printed to stderr."""
    md = tmp_path / "notes.md"
    md.write_text("# Hello", encoding="utf-8")
    output = tmp_path / "notes.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf"):
        cmd_render(template=None, data_file=None, markdown_file=md, output=output)

    captured = capsys.readouterr()
    assert "PDF saved" in captured.err
    assert output.name in captured.err


def test_cmd_render_markdown_copies_assets(tmp_path):
    """When --markdown is given, assets from the markdown's directory are copied."""
    md = tmp_path / "notes.md"
    md.write_text("# Hello", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "logo.png").write_bytes(b"\x89PNG")

    with patch("typy.builder.DocumentBuilder.save_pdf"):
        with patch("typy.builder.DocumentBuilder.copy_assets_from") as mock_copy:
            cmd_render(
                template=None,
                data_file=None,
                markdown_file=md,
                output=tmp_path / "out.pdf",
            )

    mock_copy.assert_called_once_with(tmp_path.resolve())


def test_cmd_render_markdown_uses_filename_as_title(tmp_path):
    md = tmp_path / "my_notes.md"
    md.write_text("# Hello", encoding="utf-8")
    output = tmp_path / "out.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf"):
        with patch("typy.builder.DocumentBuilder.add_template") as mock_add:
            cmd_render(template=None, data_file=None, markdown_file=md, output=output)

    added_template = mock_add.call_args[0][0]
    assert added_template.title == "my_notes"


def test_cmd_render_builtin_template_with_data(tmp_path):
    data_file = tmp_path / "data.json"
    data = {
        "title": "My Report",
        "author": "Alice",
        "date": "2025-01-01",
        "body": "# Hello",
        "toc": False,
    }
    data_file.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "out.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf") as mock_save:
        cmd_render(
            template="report", data_file=data_file, markdown_file=None, output=output
        )

    mock_save.assert_called_once_with(output)


def test_cmd_render_markdown_with_builtin_template(tmp_path):
    md = tmp_path / "analysis.md"
    md.write_text("# Analysis\n\nContent here.", encoding="utf-8")
    data_file = tmp_path / "data.json"
    data = {
        "title": "Analysis Report",
        "author": "Bob",
        "date": "2025-01-01",
        "toc": False,
    }
    data_file.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "out.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf") as mock_save:
        cmd_render(
            template="report",
            data_file=data_file,
            markdown_file=md,
            output=output,
        )

    mock_save.assert_called_once_with(output)


def test_cmd_render_markdown_body_overrides_data_body(tmp_path):
    md = tmp_path / "analysis.md"
    md.write_text("# From Markdown", encoding="utf-8")
    data_file = tmp_path / "data.json"
    data = {
        "title": "Report",
        "author": "Alice",
        "date": "2025-01-01",
        "body": "# From Data",
        "toc": False,
    }
    data_file.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "out.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf"):
        with patch("typy.builder.DocumentBuilder.add_template") as mock_add:
            cmd_render(
                template="report",
                data_file=data_file,
                markdown_file=md,
                output=output,
            )

    added_template = mock_add.call_args[0][0]
    # body should be the markdown content (not the data.json body)
    # Content stores items as a list; each item is a Markdown object with a .text attribute
    body_items = added_template.body.content
    assert any(
        "From Markdown" in item.text for item in body_items if hasattr(item, "text")
    )


def test_cmd_render_custom_typ_file(tmp_path):
    typ_file = tmp_path / "custom.typ"
    typ_file.write_text("#let x = 1", encoding="utf-8")
    data_file = tmp_path / "data.json"
    data_file.write_text('{"name": "Alice"}', encoding="utf-8")
    output = tmp_path / "out.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf") as mock_save:
        with patch("typy.builder.DocumentBuilder.add_typ_template") as mock_add_typ:
            cmd_render(
                template=str(typ_file),
                data_file=data_file,
                markdown_file=None,
                output=output,
            )

    mock_add_typ.assert_called_once()
    mock_save.assert_called_once_with(output)


def test_cmd_render_creates_output_parent_dirs(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Hello", encoding="utf-8")
    output = tmp_path / "subdir" / "nested" / "out.pdf"

    with patch("typy.builder.DocumentBuilder.save_pdf"):
        cmd_render(template=None, data_file=None, markdown_file=md, output=output)

    assert output.parent.exists()


# ---- render CLI command tests ----


def test_main_render_no_args_shows_error():
    app = _build_app()
    result = runner.invoke(app, ["render"])
    assert result.exit_code == 1


def test_main_render_help():
    app = _build_app()
    result = runner.invoke(app, ["render", "--help"])
    assert result.exit_code == 0
    plain = _plain_help(result.output)
    assert "--template" in plain
    assert "--data" in plain
    assert "--markdown" in plain
    assert "--output" in plain
    assert "template module" in plain
    assert ".typ file" in plain


def test_main_render_markdown_only(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Hello\n\nWorld.", encoding="utf-8")
    output = tmp_path / "notes.pdf"

    app = _build_app()
    with patch("typy.builder.DocumentBuilder.save_pdf"):
        result = runner.invoke(
            app, ["render", "--markdown", str(md), "--output", str(output)]
        )

    assert result.exit_code == 0


def test_main_render_template_with_data(tmp_path):
    data_file = tmp_path / "data.json"
    data = {
        "title": "My Report",
        "author": "Alice",
        "date": "2025-01-01",
        "body": "# Hello",
        "toc": False,
    }
    data_file.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "out.pdf"

    app = _build_app()
    with patch("typy.builder.DocumentBuilder.save_pdf"):
        result = runner.invoke(
            app,
            [
                "render",
                "--template",
                "report",
                "--data",
                str(data_file),
                "--output",
                str(output),
            ],
        )

    assert result.exit_code == 0


def test_main_render_default_output(tmp_path):
    """--output defaults to output.pdf in the current directory."""
    md = tmp_path / "notes.md"
    md.write_text("# Hello", encoding="utf-8")

    app = _build_app()
    with patch("typy.builder.DocumentBuilder.save_pdf") as mock_save:
        result = runner.invoke(app, ["render", "--markdown", str(md)])

    assert result.exit_code == 0
    # Default output should be output.pdf
    called_path = mock_save.call_args[0][0]
    assert called_path.name == "output.pdf"


def test_main_render_missing_markdown_exits(tmp_path):
    app = _build_app()
    result = runner.invoke(app, ["render", "--markdown", str(tmp_path / "missing.md")])
    assert result.exit_code == 1


def test_main_render_unknown_template_exits(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Hi", encoding="utf-8")
    app = _build_app()
    result = runner.invoke(
        app,
        ["render", "--markdown", str(md), "--template", "nonexistent"],
    )
    assert result.exit_code == 1
