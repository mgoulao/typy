""".typy template package format: validate, export, and install.

See ``docs/package-format.md`` for the full specification.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from packaging.specifiers import InvalidSpecifier, SpecifierSet

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

# Semantic version: MAJOR.MINOR.PATCH with optional pre-release
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Package name: lowercase alphanumeric with hyphens, min length 2
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

SUPPORTED_MANIFEST_VERSIONS: frozenset[int] = frozenset({1})

# Required manifest fields and their expected Python types
_MANIFEST_REQUIRED_FIELDS: dict[str, type] = {
    "name": str,
    "version": str,
    "description": str,
    "author": str,
    "typy_compatibility": str,
}


# ---------------------------------------------------------------------------
# Diagnostic model
# ---------------------------------------------------------------------------


@dataclass
class PackageDiagnostic:
    """A structured diagnostic emitted by the package validator."""

    code: str
    message: str
    hint: str = ""

    def __str__(self) -> str:
        s = f"{self.code}  {self.message}"
        if self.hint:
            s += f"\n          Hint: {self.hint}"
        return s


class PackageValidationError(Exception):
    """Raised when a ``.typy`` package fails one or more validation checks."""

    def __init__(self, diagnostics: list[PackageDiagnostic]) -> None:
        self.diagnostics = diagnostics
        messages = "\n".join(str(d) for d in diagnostics)
        super().__init__(f"Package validation failed:\n{messages}")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_package(
    path: Path, *, check_compatibility: bool = True
) -> list[PackageDiagnostic]:
    """Validate a ``.typy`` package file and return all diagnostics.

    All errors are collected before returning so users can fix everything in a
    single pass.  An empty list means the package is valid.

    Args:
        path: Path to the ``.typy`` file.
        check_compatibility: If *True* (default), also check that the installed
            typy version satisfies ``typy_compatibility`` (PKG_E013).

    Returns:
        A (possibly empty) list of :class:`PackageDiagnostic` objects.
    """
    diagnostics: list[PackageDiagnostic] = []

    # PKG_E001 – must be a valid ZIP archive
    if not zipfile.is_zipfile(path):
        diagnostics.append(
            PackageDiagnostic(
                code="PKG_E001",
                message="Not a valid .typy package: file is not a ZIP archive.",
                hint="Create the package using 'typy package export'.",
            )
        )
        return diagnostics  # cannot open the file further

    with zipfile.ZipFile(path, "r") as zf:
        names = set(zf.namelist())

        # PKG_E011 – no path traversal
        for name in sorted(names):
            if ".." in PurePosixPath(name).parts:
                diagnostics.append(
                    PackageDiagnostic(
                        code="PKG_E011",
                        message=(
                            f"Unsafe path detected in archive: '{name}'. "
                            "Paths must not traverse outside the package root."
                        ),
                        hint="Remove or rename files with '..' in their paths.",
                    )
                )

        # PKG_E002 – manifest.json must exist
        if "manifest.json" not in names:
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E002",
                    message="manifest.json not found in package root.",
                    hint="Add a manifest.json file to the archive root.",
                )
            )
            if "template.py" not in names:
                diagnostics.append(
                    PackageDiagnostic(
                        code="PKG_E010",
                        message=(
                            "template.py not found in package root. "
                            "The Template subclass must be defined in template.py."
                        ),
                        hint=(
                            "Add a template.py file to the archive root that "
                            "defines a subclass of typy.templates.Template."
                        ),
                    )
                )
            return diagnostics

        # PKG_E003 – manifest.json must be valid JSON
        try:
            manifest_bytes = zf.read("manifest.json")
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E003",
                    message=f"manifest.json contains invalid JSON: {exc}.",
                    hint="Fix the JSON syntax in manifest.json.",
                )
            )
            if "template.py" not in names:
                diagnostics.append(
                    PackageDiagnostic(
                        code="PKG_E010",
                        message=(
                            "template.py not found in package root. "
                            "The Template subclass must be defined in template.py."
                        ),
                        hint=(
                            "Add a template.py file to the archive root that "
                            "defines a subclass of typy.templates.Template."
                        ),
                    )
                )
            return diagnostics

        if not isinstance(manifest, dict):
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E003",
                    message="manifest.json must contain a JSON object at the top level.",
                    hint="Make sure manifest.json is a JSON object { ... }.",
                )
            )
            return diagnostics

        # PKG_E004 – manifest_version must be present
        if "manifest_version" not in manifest:
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E004",
                    message="manifest.json is missing required field: 'manifest_version'.",
                    hint="Add '\"manifest_version\": 1' to manifest.json.",
                )
            )
            return diagnostics

        # PKG_E005 – manifest_version must be a recognised value
        mv = manifest["manifest_version"]
        if not isinstance(mv, int) or mv not in SUPPORTED_MANIFEST_VERSIONS:
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E005",
                    message=(
                        f"Unsupported manifest_version: {mv!r}. "
                        "This version of typy supports manifest_version 1."
                    ),
                    hint="Set '\"manifest_version\"' to 1.",
                )
            )
            return diagnostics

        # PKG_E006 / PKG_E007 – required field presence and type
        for field_name, expected_type in _MANIFEST_REQUIRED_FIELDS.items():
            if field_name not in manifest:
                diagnostics.append(
                    PackageDiagnostic(
                        code="PKG_E006",
                        message=f"manifest.json is missing required field: '{field_name}'.",
                        hint=f"Add a '{field_name}' field to manifest.json.",
                    )
                )
            elif not isinstance(manifest[field_name], expected_type):
                actual = type(manifest[field_name]).__name__
                diagnostics.append(
                    PackageDiagnostic(
                        code="PKG_E007",
                        message=(
                            f"manifest.json field '{field_name}' must be "
                            f"{expected_type.__name__}, got {actual}."
                        ),
                        hint=f"Change '{field_name}' to a {expected_type.__name__} value.",
                    )
                )

        # PKG_E008 – name must match the allowed pattern
        name_val = manifest.get("name")
        if isinstance(name_val, str) and not _NAME_RE.match(name_val):
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E008",
                    message=(
                        f"'name' must match ^[a-z0-9][a-z0-9-]*[a-z0-9]$, "
                        f"got '{name_val}'."
                    ),
                    hint=(
                        "Use only lowercase letters, digits, and hyphens "
                        "(e.g. 'my-template')."
                    ),
                )
            )

        # PKG_E009 – version must be a valid semver string
        version_val = manifest.get("version")
        if isinstance(version_val, str) and not _SEMVER_RE.match(version_val):
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E009",
                    message=(
                        f"'version' must be a valid semantic version "
                        f"(e.g. '1.0.0'), got '{version_val}'."
                    ),
                    hint="Use MAJOR.MINOR.PATCH format as defined at https://semver.org.",
                )
            )

        # PKG_E012 / PKG_E013 – typy_compatibility
        compat = manifest.get("typy_compatibility")
        if isinstance(compat, str):
            try:
                spec = SpecifierSet(compat)
            except InvalidSpecifier:
                diagnostics.append(
                    PackageDiagnostic(
                        code="PKG_E012",
                        message=(
                            f"'typy_compatibility' is not a valid version specifier: "
                            f"'{compat}'."
                        ),
                        hint="Use PEP 440 version specifiers (e.g. '>=0.1.0').",
                    )
                )
            else:
                if check_compatibility:
                    try:
                        from importlib.metadata import version as _pkg_version

                        typy_ver = _pkg_version("typy")
                        if not spec.contains(typy_ver, prereleases=True):
                            diagnostics.append(
                                PackageDiagnostic(
                                    code="PKG_E013",
                                    message=(
                                        f"Package requires typy {compat} but "
                                        f"typy {typy_ver} is installed."
                                    ),
                                    hint=(
                                        f"Install a compatible version of typy "
                                        f"(requires {compat})."
                                    ),
                                )
                            )
                    except Exception:  # noqa: BLE001  # importlib may vary; skip gracefully
                        pass  # Can't determine installed version – skip

        # PKG_E010 – template.py must be present
        if "template.py" not in names:
            diagnostics.append(
                PackageDiagnostic(
                    code="PKG_E010",
                    message=(
                        "template.py not found in package root. "
                        "The Template subclass must be defined in template.py."
                    ),
                    hint=(
                        "Add a template.py file to the archive root that "
                        "defines a subclass of typy.templates.Template."
                    ),
                )
            )

    return diagnostics


# ---------------------------------------------------------------------------
# Helpers for export
# ---------------------------------------------------------------------------


def _load_template_class_from_file(path: Path):
    """Load and return the first ``Template`` subclass found in *path*."""
    from typy.templates import Template

    if not path.exists():
        raise FileNotFoundError(f"Template file not found: '{path}'.")

    spec = importlib.util.spec_from_file_location("_pkg_template", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load Python module from '{path}'.")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as exc:
        raise ValueError(
            f"Failed to execute '{path}': {exc}. "
            "Ensure template.py is valid Python and all imports are available."
        ) from exc
    for _, obj in inspect.getmembers(module, inspect.isclass):
        try:
            if issubclass(obj, Template) and obj is not Template:
                return obj
        except TypeError:
            continue
    raise ValueError(
        f"No Template subclass found in '{path}'. "
        "Make sure template.py defines a class that inherits from "
        "typy.templates.Template."
    )


def _patch_template_path(source: str, typ_basename: str) -> str:
    """Rewrite the ``__template_path__`` assignment in *source*.

    The replacement uses ``Path(__file__).parent / "templates" / "<basename>"``
    so the path resolves correctly wherever the package is later installed.
    If no ``__template_path__`` assignment is found the source is returned
    unchanged.
    """
    replacement = (
        f'__template_path__ = Path(__file__).parent / "templates" / "{typ_basename}"'
    )
    patched, count = re.subn(
        r"__template_path__\s*=\s*.+",
        replacement,
        source,
    )
    return patched if count else source


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def export_package(
    template_py: Path,
    manifest: dict,
    output: Path,
    *,
    assets_dir: Path | None = None,
    readme: Path | None = None,
) -> None:
    """Export a template as a ``.typy`` package archive.

    Args:
        template_py: Path to the Python file containing the Template subclass.
            The class must set ``__template_path__`` to the entry ``.typ`` file.
        manifest: Manifest data dict conforming to manifest schema v1.
        output: Destination path for the generated ``.typy`` file.
        assets_dir: Optional directory of static assets (images, fonts, …) to
            include under ``assets/`` in the archive.
        readme: Optional README file to bundle as ``README.md``.

    Raises:
        ValueError: if no Template subclass is found in *template_py*.
        FileNotFoundError: if the ``.typ`` file referenced by the template does
            not exist.
    """
    cls = _load_template_class_from_file(template_py)
    typ_src: Path = cls.__template_path__

    if not typ_src.exists():
        raise FileNotFoundError(
            f"Template file '{typ_src}' referenced by "
            f"{cls.__name__}.__template_path__ does not exist."
        )

    typ_basename = typ_src.name
    archive_typ_path = f"templates/{typ_basename}"

    # Patch __template_path__ in template.py so it resolves correctly when
    # the package is extracted anywhere.
    template_src = template_py.read_text(encoding="utf-8")
    template_src = _patch_template_path(template_src, typ_basename)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False)
        )
        zf.writestr("template.py", template_src)
        zf.write(typ_src, archive_typ_path)

        if assets_dir is not None and assets_dir.is_dir():
            for asset in sorted(assets_dir.rglob("*")):
                if asset.is_file():
                    relative = asset.relative_to(assets_dir)
                    zf.write(asset, f"assets/{relative.as_posix()}")

        if readme is not None and readme.is_file():
            zf.write(readme, "README.md")


# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------


def install_package(
    package_path: Path,
    store_dir: Path,
    *,
    force: bool = False,
) -> Path:
    """Validate and install a ``.typy`` package into the local template store.

    The package is extracted to ``<store_dir>/<name>/<version>/``.

    Args:
        package_path: Path to the ``.typy`` file.
        store_dir: Root directory of the local template store.
        force: If *True*, overwrite an existing installation.

    Returns:
        The path to the installation directory.

    Raises:
        :class:`PackageValidationError`: if the package does not pass validation.
        FileExistsError: if the package is already installed and *force* is *False*.
    """
    diagnostics = validate_package(package_path)
    if diagnostics:
        raise PackageValidationError(diagnostics)

    with zipfile.ZipFile(package_path, "r") as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))

    name = manifest["name"]
    version = manifest["version"]
    install_dir = store_dir / name / version

    if install_dir.exists() and not force:
        raise FileExistsError(
            f"Package '{name}@{version}' is already installed at '{install_dir}'. "
            "Use --force to overwrite."
        )

    if install_dir.exists():
        shutil.rmtree(install_dir)

    install_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(package_path, "r") as zf:
        zf.extractall(install_dir)

    return install_dir
