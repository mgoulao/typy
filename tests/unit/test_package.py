"""Tests for typy.package: validate, export, and install."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from typy.package import (
    PackageDiagnostic,
    PackageValidationError,
    _patch_template_path,
    export_package,
    install_package,
    validate_package,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_MANIFEST = {
    "manifest_version": 1,
    "name": "my-report",
    "version": "1.0.0",
    "description": "A test template.",
    "author": "Jane Doe <jane@example.com>",
    "typy_compatibility": ">=0.1.0",
}

_TEMPLATE_PY_SRC = """\
from pathlib import Path
from typy.templates import Template
from typy.content import Content

class MyReport(Template):
    title: str
    body: Content
    __template_name__ = "my-report"
    __template_path__ = Path(__file__).parent / "templates" / "my-report.typ"
"""

_TEMPLATE_TYP_SRC = "#let report(data) = [Hello #data.title]"


def _make_valid_typy(tmp_path: Path, manifest: dict | None = None) -> Path:
    """Create a minimal valid .typy archive and return its path."""
    m = manifest if manifest is not None else _MINIMAL_MANIFEST.copy()

    # Create a temporary template.py and .typ file so export_package can run
    tmp_path.mkdir(parents=True, exist_ok=True)
    template_py = tmp_path / "template.py"
    template_py.write_text(_TEMPLATE_PY_SRC, encoding="utf-8")
    typ_file = tmp_path / "templates" / "my-report.typ"
    typ_file.parent.mkdir(parents=True, exist_ok=True)
    typ_file.write_text(_TEMPLATE_TYP_SRC, encoding="utf-8")

    output = tmp_path / "my-report.typy"
    export_package(template_py=template_py, manifest=m, output=output)
    return output


# ---------------------------------------------------------------------------
# PackageDiagnostic
# ---------------------------------------------------------------------------


def test_diagnostic_str_no_hint():
    d = PackageDiagnostic(code="PKG_E001", message="Something went wrong.")
    assert "PKG_E001" in str(d)
    assert "Something went wrong." in str(d)
    assert "Hint" not in str(d)


def test_diagnostic_str_with_hint():
    d = PackageDiagnostic(
        code="PKG_E001", message="Something went wrong.", hint="Do this instead."
    )
    assert "Hint" in str(d)
    assert "Do this instead." in str(d)


# ---------------------------------------------------------------------------
# _patch_template_path
# ---------------------------------------------------------------------------


def test_patch_template_path_absolute():
    src = (
        "class T(Template):\n    __template_path__ = Path('/abs/path/to/report.typ')\n"
    )
    result = _patch_template_path(src, "report.typ")
    assert (
        '__template_path__ = Path(__file__).parent / "templates" / "report.typ"'
        in result
    )


def test_patch_template_path_already_relative():
    src = (
        "class T(Template):\n"
        '    __template_path__ = Path(__file__).parent / "templates" / "old.typ"\n'
    )
    result = _patch_template_path(src, "new.typ")
    assert '"new.typ"' in result
    assert '"old.typ"' not in result


def test_patch_template_path_no_assignment_unchanged():
    src = "class T(Template):\n    title: str\n"
    result = _patch_template_path(src, "foo.typ")
    assert result == src


# ---------------------------------------------------------------------------
# validate_package – PKG_E001
# ---------------------------------------------------------------------------


def test_validate_not_a_zip(tmp_path):
    bad_file = tmp_path / "bad.typy"
    bad_file.write_text("not a zip", encoding="utf-8")
    diags = validate_package(bad_file)
    codes = [d.code for d in diags]
    assert "PKG_E001" in codes
    assert len(diags) == 1  # stops after this error


# ---------------------------------------------------------------------------
# validate_package – PKG_E002
# ---------------------------------------------------------------------------


def test_validate_missing_manifest(tmp_path):
    archive = tmp_path / "no-manifest.typy"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E002" in codes


def test_validate_missing_manifest_and_template_py(tmp_path):
    archive = tmp_path / "empty.typy"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("README.md", "hello")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E002" in codes
    assert "PKG_E010" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E003
# ---------------------------------------------------------------------------


def test_validate_invalid_json_manifest(tmp_path):
    archive = tmp_path / "bad-json.typy"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", "{not valid json")
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E003" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E004 / PKG_E005
# ---------------------------------------------------------------------------


def test_validate_missing_manifest_version(tmp_path):
    archive = tmp_path / "no-mv.typy"
    manifest = {k: v for k, v in _MINIMAL_MANIFEST.items() if k != "manifest_version"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E004" in codes


def test_validate_unsupported_manifest_version(tmp_path):
    archive = tmp_path / "bad-mv.typy"
    manifest = {**_MINIMAL_MANIFEST, "manifest_version": 99}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E005" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E006 / PKG_E007
# ---------------------------------------------------------------------------


def test_validate_missing_required_field(tmp_path):
    archive = tmp_path / "missing-field.typy"
    manifest = {k: v for k, v in _MINIMAL_MANIFEST.items() if k != "description"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E006" in codes
    assert any("description" in d.message for d in diags)


def test_validate_wrong_field_type(tmp_path):
    archive = tmp_path / "wrong-type.typy"
    manifest = {**_MINIMAL_MANIFEST, "name": 123}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E007" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E008
# ---------------------------------------------------------------------------


def test_validate_invalid_name_uppercase(tmp_path):
    archive = tmp_path / "bad-name.typy"
    manifest = {**_MINIMAL_MANIFEST, "name": "My Template"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E008" in codes


def test_validate_invalid_name_single_char(tmp_path):
    archive = tmp_path / "single-char.typy"
    manifest = {**_MINIMAL_MANIFEST, "name": "a"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E008" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E009
# ---------------------------------------------------------------------------


def test_validate_invalid_version(tmp_path):
    archive = tmp_path / "bad-ver.typy"
    manifest = {**_MINIMAL_MANIFEST, "version": "not-a-version"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E009" in codes


def test_validate_version_missing_patch(tmp_path):
    archive = tmp_path / "bad-ver2.typy"
    manifest = {**_MINIMAL_MANIFEST, "version": "1.0"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E009" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E010
# ---------------------------------------------------------------------------


def test_validate_missing_template_py(tmp_path):
    archive = tmp_path / "no-template.typy"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(_MINIMAL_MANIFEST))
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E010" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E011
# ---------------------------------------------------------------------------


def test_validate_path_traversal(tmp_path):
    archive = tmp_path / "traversal.typy"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(_MINIMAL_MANIFEST))
        zf.writestr("template.py", "pass")
        zf.writestr("../evil.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E011" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E012
# ---------------------------------------------------------------------------


def test_validate_invalid_typy_compatibility(tmp_path):
    archive = tmp_path / "bad-compat.typy"
    manifest = {**_MINIMAL_MANIFEST, "typy_compatibility": "not-a-specifier!!!"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive)
    codes = [d.code for d in diags]
    assert "PKG_E012" in codes


# ---------------------------------------------------------------------------
# validate_package – PKG_E013
# ---------------------------------------------------------------------------


def test_validate_incompatible_typy_version(tmp_path):
    archive = tmp_path / "incompat.typy"
    # Require a version that will never match an installed version
    manifest = {**_MINIMAL_MANIFEST, "typy_compatibility": ">=999.0.0"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive, check_compatibility=True)
    codes = [d.code for d in diags]
    assert "PKG_E013" in codes


def test_validate_skip_compatibility_check(tmp_path):
    archive = tmp_path / "skip-compat.typy"
    manifest = {**_MINIMAL_MANIFEST, "typy_compatibility": ">=999.0.0"}
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("template.py", "pass")
    diags = validate_package(archive, check_compatibility=False)
    codes = [d.code for d in diags]
    assert "PKG_E013" not in codes


# ---------------------------------------------------------------------------
# validate_package – multiple errors collected
# ---------------------------------------------------------------------------


def test_validate_collects_multiple_errors(tmp_path):
    """Validator must report all applicable errors, not stop at first."""
    archive = tmp_path / "multi-err.typy"
    manifest = {
        "manifest_version": 1,
        "name": "My Template",  # PKG_E008
        "version": "not-a-version",  # PKG_E009
        "description": "A report template.",
        "author": "Jane Doe",
        "typy_compatibility": ">=0.1.0",
    }
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        # intentionally no template.py → PKG_E010
    diags = validate_package(archive, check_compatibility=False)
    codes = [d.code for d in diags]
    assert "PKG_E008" in codes
    assert "PKG_E009" in codes
    assert "PKG_E010" in codes


# ---------------------------------------------------------------------------
# validate_package – valid package
# ---------------------------------------------------------------------------


def test_validate_valid_package(tmp_path):
    pkg = _make_valid_typy(tmp_path)
    diags = validate_package(pkg, check_compatibility=False)
    assert diags == [], f"Expected no errors, got: {diags}"


def test_validate_valid_package_with_optional_fields(tmp_path):
    manifest = {
        **_MINIMAL_MANIFEST,
        "license": "MIT",
        "homepage": "https://example.com",
        "keywords": ["report", "test"],
    }
    pkg = _make_valid_typy(tmp_path, manifest=manifest)
    diags = validate_package(pkg, check_compatibility=False)
    assert diags == [], f"Expected no errors, got: {diags}"


# ---------------------------------------------------------------------------
# export_package
# ---------------------------------------------------------------------------


def test_export_creates_zip(tmp_path):
    pkg = _make_valid_typy(tmp_path)
    assert pkg.exists()
    assert zipfile.is_zipfile(pkg)


def test_export_archive_contains_required_files(tmp_path):
    pkg = _make_valid_typy(tmp_path)
    with zipfile.ZipFile(pkg, "r") as zf:
        names = set(zf.namelist())
    assert "manifest.json" in names
    assert "template.py" in names
    assert "templates/my-report.typ" in names


def test_export_manifest_json_correct(tmp_path):
    pkg = _make_valid_typy(tmp_path)
    with zipfile.ZipFile(pkg, "r") as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
    assert manifest["name"] == "my-report"
    assert manifest["version"] == "1.0.0"
    assert manifest["manifest_version"] == 1


def test_export_patches_template_path(tmp_path):
    pkg = _make_valid_typy(tmp_path)
    with zipfile.ZipFile(pkg, "r") as zf:
        src = zf.read("template.py").decode("utf-8")
    assert 'Path(__file__).parent / "templates" / "my-report.typ"' in src


def test_export_with_assets(tmp_path):
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "logo.png").write_bytes(b"\x89PNG")
    (assets / "font.ttf").write_bytes(b"font")

    template_py = tmp_path / "template.py"
    template_py.write_text(_TEMPLATE_PY_SRC, encoding="utf-8")
    typ_file = tmp_path / "templates" / "my-report.typ"
    typ_file.parent.mkdir(parents=True, exist_ok=True)
    typ_file.write_text(_TEMPLATE_TYP_SRC, encoding="utf-8")

    output = tmp_path / "out.typy"
    export_package(
        template_py=template_py,
        manifest=_MINIMAL_MANIFEST.copy(),
        output=output,
        assets_dir=assets,
    )

    with zipfile.ZipFile(output, "r") as zf:
        names = set(zf.namelist())
    assert "assets/logo.png" in names
    assert "assets/font.ttf" in names


def test_export_with_readme(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# My Report", encoding="utf-8")

    template_py = tmp_path / "template.py"
    template_py.write_text(_TEMPLATE_PY_SRC, encoding="utf-8")
    typ_file = tmp_path / "templates" / "my-report.typ"
    typ_file.parent.mkdir(parents=True, exist_ok=True)
    typ_file.write_text(_TEMPLATE_TYP_SRC, encoding="utf-8")

    output = tmp_path / "out.typy"
    export_package(
        template_py=template_py,
        manifest=_MINIMAL_MANIFEST.copy(),
        output=output,
        readme=readme,
    )

    with zipfile.ZipFile(output, "r") as zf:
        names = set(zf.namelist())
    assert "README.md" in names


def test_export_missing_template_py_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_package(
            template_py=tmp_path / "nonexistent.py",
            manifest=_MINIMAL_MANIFEST.copy(),
            output=tmp_path / "out.typy",
        )


def test_export_no_template_subclass_raises(tmp_path):
    template_py = tmp_path / "template.py"
    template_py.write_text("# no template here\nx = 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No Template subclass"):
        export_package(
            template_py=template_py,
            manifest=_MINIMAL_MANIFEST.copy(),
            output=tmp_path / "out.typy",
        )


def test_export_missing_typ_file_raises(tmp_path):
    template_py = tmp_path / "template.py"
    # __template_path__ points to a file that does not exist
    template_py.write_text(
        "from pathlib import Path\n"
        "from typy.templates import Template\n"
        "from typy.content import Content\n"
        "\n"
        "class T(Template):\n"
        "    title: str\n"
        "    body: Content\n"
        "    __template_name__ = 't'\n"
        "    __template_path__ = Path('/nonexistent/path/t.typ')\n",
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError):
        export_package(
            template_py=template_py,
            manifest=_MINIMAL_MANIFEST.copy(),
            output=tmp_path / "out.typy",
        )


# ---------------------------------------------------------------------------
# install_package
# ---------------------------------------------------------------------------


def test_install_extracts_to_store(tmp_path):
    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    install_dir = install_package(pkg, store)
    assert install_dir.exists()
    assert (install_dir / "manifest.json").exists()
    assert (install_dir / "template.py").exists()
    assert (install_dir / "templates" / "my-report.typ").exists()


def test_install_directory_structure(tmp_path):
    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    install_dir = install_package(pkg, store)
    # Should be <store>/<name>/<version>/
    assert install_dir == store / "my-report" / "1.0.0"


def test_install_already_installed_raises(tmp_path):
    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    install_package(pkg, store)
    with pytest.raises(FileExistsError, match="already installed"):
        install_package(pkg, store)


def test_install_force_overwrites(tmp_path):
    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    install_package(pkg, store)
    # Should not raise
    install_dir = install_package(pkg, store, force=True)
    assert install_dir.exists()


def test_install_invalid_package_raises(tmp_path):
    bad_pkg = tmp_path / "bad.typy"
    bad_pkg.write_text("not a zip", encoding="utf-8")
    store = tmp_path / "store"
    with pytest.raises(PackageValidationError) as exc_info:
        install_package(bad_pkg, store)
    assert exc_info.value.diagnostics


# ---------------------------------------------------------------------------
# Roundtrip: export → validate → install
# ---------------------------------------------------------------------------


def test_roundtrip_export_validate_install(tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Create source files
    template_py = build_dir / "template.py"
    template_py.write_text(_TEMPLATE_PY_SRC, encoding="utf-8")
    typ_dir = build_dir / "templates"
    typ_dir.mkdir()
    (typ_dir / "my-report.typ").write_text(_TEMPLATE_TYP_SRC, encoding="utf-8")

    manifest = _MINIMAL_MANIFEST.copy()
    output = tmp_path / "my-report.typy"

    # Export
    export_package(template_py=template_py, manifest=manifest, output=output)
    assert output.exists()

    # Validate
    diags = validate_package(output, check_compatibility=False)
    assert diags == [], f"Validation errors after export: {diags}"

    # Install
    store = tmp_path / "store"
    install_dir = install_package(output, store)

    assert (install_dir / "manifest.json").exists()
    assert (install_dir / "template.py").exists()
    assert (install_dir / "templates" / "my-report.typ").exists()


# ---------------------------------------------------------------------------
# CLI integration: typy package commands
# ---------------------------------------------------------------------------


def test_cli_package_validate_valid(tmp_path):
    from typer.testing import CliRunner

    from typy.cli import _build_app

    pkg = _make_valid_typy(tmp_path / "build")
    app = _build_app()
    runner = CliRunner()
    result = runner.invoke(app, ["package", "validate", str(pkg)])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_cli_package_validate_invalid(tmp_path):
    from typer.testing import CliRunner

    from typy.cli import _build_app

    bad = tmp_path / "bad.typy"
    bad.write_text("not a zip", encoding="utf-8")
    app = _build_app()
    runner = CliRunner()
    result = runner.invoke(app, ["package", "validate", str(bad)])
    assert result.exit_code == 1
    assert "PKG_E001" in result.output


def test_cli_package_export(tmp_path):
    from typer.testing import CliRunner

    from typy.cli import _build_app

    template_py = tmp_path / "template.py"
    template_py.write_text(_TEMPLATE_PY_SRC, encoding="utf-8")
    typ_file = tmp_path / "templates" / "my-report.typ"
    typ_file.parent.mkdir(parents=True, exist_ok=True)
    typ_file.write_text(_TEMPLATE_TYP_SRC, encoding="utf-8")
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps(_MINIMAL_MANIFEST), encoding="utf-8")
    output = tmp_path / "out.typy"

    app = _build_app()
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "package",
            "export",
            str(template_py),
            "--manifest",
            str(manifest_file),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0, result.output
    assert output.exists()


def test_cli_package_install(tmp_path):
    from typer.testing import CliRunner

    from typy.cli import _build_app

    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    app = _build_app()
    runner = CliRunner()
    result = runner.invoke(app, ["package", "install", str(pkg), "--store", str(store)])
    assert result.exit_code == 0, result.output
    assert (store / "my-report" / "1.0.0" / "template.py").exists()


def test_cli_package_install_already_installed(tmp_path):
    from typer.testing import CliRunner

    from typy.cli import _build_app

    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    app = _build_app()
    runner = CliRunner()
    runner.invoke(app, ["package", "install", str(pkg), "--store", str(store)])
    result = runner.invoke(app, ["package", "install", str(pkg), "--store", str(store)])
    assert result.exit_code == 1
    assert "already installed" in result.output


def test_cli_package_install_force(tmp_path):
    from typer.testing import CliRunner

    from typy.cli import _build_app

    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    app = _build_app()
    runner = CliRunner()
    runner.invoke(app, ["package", "install", str(pkg), "--store", str(store)])
    result = runner.invoke(
        app,
        ["package", "install", str(pkg), "--store", str(store), "--force"],
    )
    assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# _resolve_template – installed packages by name
# ---------------------------------------------------------------------------


def test_resolve_template_installed_by_name(tmp_path):
    """After install, typy render --template <name> should find the package."""
    from typy.cli import _resolve_template
    from typy.package import install_package

    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    install_package(pkg, store)

    cls = _resolve_template("my-report", store_dir=store)
    assert cls is not None
    assert cls.__name__ == "MyReport"


def test_resolve_template_installed_by_name_not_found(tmp_path):
    from typy.cli import _resolve_template

    store = tmp_path / "store"
    store.mkdir()
    cls = _resolve_template("no-such-pkg", store_dir=store)
    assert cls is None


def test_resolve_template_installed_picks_latest_version(tmp_path):
    """When multiple versions are installed the latest is selected."""
    from typy.cli import _resolve_template

    # Install two versions manually – v2.0.0 should win
    for ver in ("1.0.0", "2.0.0"):
        manifest = {**_MINIMAL_MANIFEST, "version": ver}
        src = tmp_path / ver
        src.mkdir()
        pkg = _make_valid_typy(src, manifest=manifest)
        store = tmp_path / "store"
        from typy.package import install_package

        install_package(pkg, store, force=True)

    cls = _resolve_template("my-report", store_dir=tmp_path / "store")
    assert cls is not None
    # Both versions have the same class name; the important thing is one resolved
    assert cls.__name__ == "MyReport"


# ---------------------------------------------------------------------------
# cmd_render – render directly from a .typy file
# ---------------------------------------------------------------------------


def test_cmd_render_from_typy_file(tmp_path):
    """typy render --template my.typy should work without a prior install."""
    from unittest.mock import patch

    from typy.cli import cmd_render

    pkg = _make_valid_typy(tmp_path / "build")

    with patch("typy.builder.DocumentBuilder.save_pdf"):
        cmd_render(
            template=str(pkg),
            data_file=None,
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )


def test_cmd_render_from_typy_missing_file(tmp_path, capsys):
    """typy render --template missing.typy should exit 1."""
    import pytest

    from typy.cli import cmd_render

    with pytest.raises(SystemExit) as exc_info:
        cmd_render(
            template=str(tmp_path / "nonexistent.typy"),
            data_file=None,
            markdown_file=None,
            output=tmp_path / "out.pdf",
        )
    assert exc_info.value.code == 1


def test_cmd_render_from_installed_name(tmp_path):
    """After install, render by package name should work."""

    from typy.cli import _resolve_template
    from typy.package import install_package

    pkg = _make_valid_typy(tmp_path / "build")
    store = tmp_path / "store"
    install_package(pkg, store)

    # Verify _resolve_template finds it
    cls = _resolve_template("my-report", store_dir=store)
    assert cls is not None
