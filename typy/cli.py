import importlib.util
import inspect
import json
import sys
import types
import typing
from pathlib import Path
from typing import get_args, get_origin

from typy.templates import (
    AcademicTemplate,
    BasicTemplate,
    CVTemplate,
    InvoiceTemplate,
    LetterTemplate,
    PresentationTemplate,
    ReportTemplate,
    Template,
)

# Registry of built-in templates: name -> (class, one-line description)
BUILTIN_TEMPLATES: dict[str, tuple[type[Template], str]] = {
    "report": (ReportTemplate, "General-purpose report with TOC and sections"),
    "invoice": (InvoiceTemplate, "Business invoice with line items"),
    "letter": (LetterTemplate, "Formal business letter"),
    "cv": (CVTemplate, "CV / resume"),
    "academic": (AcademicTemplate, "Academic paper with citations"),
    "presentation": (PresentationTemplate, "Slide deck (16:9)"),
    "basic": (BasicTemplate, "Basic single-section document"),
}

CLI_HELP = """Generate PDF documents from Typst templates and Markdown.

Quick guide:
    1) Discover templates: typy list
    2) Inspect required fields: typy info report --json
    3) Create starter data: typy scaffold report --output data.json
    4) Render PDF: typy render --template report --data data.json --output report.pdf

Tip: prefer 'typy info <template> --json' when automating with scripts or AI agents.
"""

CLI_EPILOG = """Examples:
    typy list
    typy info report
    typy info report --json
    typy scaffold report --output data.json
    typy render --template report --data data.json --output report.pdf
    typy render --markdown notes.md --output notes.pdf
"""


def _format_type(annotation: object) -> str:
    """Return a concise human-readable string for a type annotation."""
    if annotation is None:
        return "Any"

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle Union / Optional (both typing.Union and Python 3.10+ X | Y)
    if origin is typing.Union or isinstance(annotation, types.UnionType):
        non_none = [a for a in args if a is not types.NoneType]
        if len(non_none) == 1:
            return _format_type(non_none[0])
        return " | ".join(_format_type(a) for a in non_none)

    # Handle list[X]
    if origin is list:
        if args:
            return f"list[{_format_type(args[0])}]"
        return "list"

    # Simple named types (str, int, bool, float, Path, Content, …)
    if hasattr(annotation, "__name__"):
        return annotation.__name__

    return str(annotation)


def _get_field_rows(template_cls: type[Template]) -> list[dict]:
    """Return a list of field info dicts for display or JSON output."""
    rows = []
    for name, field_info in template_cls.model_fields.items():
        required = field_info.is_required()
        default = field_info.default
        rows.append(
            {
                "name": name,
                "type": _format_type(field_info.annotation),
                "required": required,
                "default": None if required else default,
            }
        )
    return rows


def _resolve_template(name_or_path: str) -> type[Template] | None:
    """
    Resolve a template name or path to a Template subclass.

    Accepts:
    - A built-in template name (e.g. "report")
    - A path to a Python file containing a Template subclass
    """
    # 1. Check built-in registry first
    if name_or_path in BUILTIN_TEMPLATES:
        return BUILTIN_TEMPLATES[name_or_path][0]

    # 2. Try to load from a Python file path
    path = Path(name_or_path)
    if path.suffix == ".py" and path.exists():
        spec = importlib.util.spec_from_file_location("_custom_template", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            try:
                if issubclass(obj, Template) and obj is not Template:
                    return obj
            except TypeError:
                continue

    return None


def _load_json_data(data_file: Path) -> dict:
    """Load and parse a JSON data file, raising ValueError on parse errors."""
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")
    try:
        with open(data_file, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in '{data_file}': {e}") from e


def cmd_render(
    template: str | None,
    data_file: Path | None,
    markdown_file: Path | None,
    output: Path,
) -> None:
    """Render a document to PDF."""
    from rich.console import Console

    from typy.builder import DocumentBuilder

    console = Console(stderr=True)

    if template is None and markdown_file is None:
        console.print(
            "[red]Error:[/red] Specify at least one of --template or --markdown."
        )
        sys.exit(1)

    try:
        builder = DocumentBuilder()

        markdown_content: str | None = None
        if markdown_file is not None:
            if not markdown_file.exists():
                console.print(
                    f"[red]Error:[/red] Markdown file not found: {markdown_file}"
                )
                sys.exit(1)
            markdown_content = markdown_file.read_text(encoding="utf-8")
            # Copy files from the markdown file's directory into the build dir so
            # relative asset paths (e.g. "assets/image.png") resolve correctly.
            builder.copy_assets_from(markdown_file.parent.resolve())

        if template is None:
            # --markdown only: render with BasicTemplate and sensible defaults
            from datetime import date

            from typy.markup import Markdown
            from typy.templates import BasicTemplate

            tmpl = BasicTemplate(
                title=markdown_file.stem,  # type: ignore[union-attr]
                date=date.today().strftime("%B %d, %Y"),
                author="",
                body=Markdown(markdown_content),  # type: ignore[arg-type]
            )
            builder.add_template(tmpl)
        else:
            # Load JSON data if provided
            data: dict = {}
            if data_file is not None:
                data = _load_json_data(data_file)

            # Inject markdown into the body field when --markdown is provided
            if markdown_content is not None:
                data["body"] = markdown_content

            template_cls = _resolve_template(template)
            if template_cls is not None:
                # Built-in or .py custom template — validate via Pydantic
                if not data and markdown_content is None:
                    # No data and no markdown: generate sample data automatically
                    data = _generate_sample_data(template_cls)
                    console.print(
                        f"[yellow]Note:[/yellow] No --data provided. "
                        "Rendering with sample data. "
                        f"Run 'typy scaffold {template}' to generate a data.json "
                        "you can edit."
                    )
                try:
                    tmpl = template_cls(**data)
                except Exception as e:
                    console.print(f"[red]Error:[/red] Data validation failed: {e}")
                    sys.exit(1)
                builder.add_template(tmpl)
            else:
                # Try as a raw .typ file
                typ_path = Path(template)
                if typ_path.suffix == ".typ" and typ_path.exists():
                    builder.add_typ_template(typ_path, data if data else None)
                else:
                    console.print(
                        f"[red]Error:[/red] Template '{template}' not found. "
                        "Use 'typy list' to see available built-in templates."
                    )
                    sys.exit(1)

        output.parent.mkdir(parents=True, exist_ok=True)
        builder.save_pdf(output)
        console.print(f"[green]✓[/green] PDF saved to [cyan]{output.resolve()}[/cyan]")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except (ValueError, TypeError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] Rendering failed: {e}")
        sys.exit(1)


def _generate_sample_data(template_cls: type[Template]) -> dict:
    """Generate a sample data dictionary for a template with placeholder values.

    All required fields are filled with sensible placeholders; optional fields
    use their Pydantic-defined defaults.
    """
    from datetime import date as _date

    import pydantic

    from typy.content import Content

    today = _date.today().strftime("%Y-%m-%d")

    def _for_annotation(ann: object, name: str) -> object:
        if ann is None:
            return ""

        origin = get_origin(ann)
        args = get_args(ann)

        # Union / Optional → unwrap to the first non-None type
        if origin is typing.Union or isinstance(ann, types.UnionType):
            non_none = [a for a in args if a is not types.NoneType]
            if not non_none:
                return None
            return _for_annotation(non_none[0], name)

        # list[T] → one sample item
        if origin is list:
            return [_for_annotation(args[0], name)] if args else []

        # Class-based types
        if isinstance(ann, type):
            try:
                if issubclass(ann, Content):
                    return "Sample content for this document."
                if issubclass(ann, pydantic.BaseModel):
                    return _for_model(ann)
            except TypeError:
                pass

        # Primitives
        if ann is str:
            return today if "date" in name else name.replace("_", " ").title()
        if ann is int:
            return 1
        if ann is float:
            return 1.0
        if ann is bool:
            return True
        if ann is Path:
            return "path/to/file"

        return ""

    def _for_model(cls: type[pydantic.BaseModel]) -> dict:
        from pydantic_core import PydanticUndefined

        result = {}
        for field_name, fi in cls.model_fields.items():
            if fi.is_required():
                result[field_name] = _for_annotation(fi.annotation, field_name)
            elif fi.default is not PydanticUndefined:
                result[field_name] = fi.default
            else:
                result[field_name] = _for_annotation(fi.annotation, field_name)
        return result

    return _for_model(template_cls)


def cmd_scaffold(template_name: str, output_file: Path | None) -> None:
    """Generate a sample JSON data file for a template."""
    from rich.console import Console

    console = Console(stderr=True)

    template_cls = _resolve_template(template_name)
    if template_cls is None:
        console.print(
            f"[red]Error:[/red] Template '{template_name}' not found. "
            "Use 'typy list' to see available templates."
        )
        sys.exit(1)

    data = _generate_sample_data(template_cls)
    json_str = json.dumps(data, indent=2, default=str)

    if output_file is None:
        print(json_str)
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json_str, encoding="utf-8")
        Console().print(
            f"Sample data written to [cyan]{output_file}[/cyan]. "
            "Edit it and run:\n"
            f"  typy render --template {template_name} --data {output_file}"
        )


def cmd_list() -> None:
    """List all available built-in templates with a one-line description."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Available templates", show_header=True, header_style="bold")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")
    for name, (_, description) in BUILTIN_TEMPLATES.items():
        table.add_row(name, description)
    console.print(table)


def cmd_info(name_or_path: str, as_json: bool = False) -> None:
    """Print schema information for a template."""
    template_cls = _resolve_template(name_or_path)
    if template_cls is None:
        from rich.console import Console

        console = Console(stderr=True)
        console.print(
            f"[red]Error:[/red] template '{name_or_path}' not found. "
            "Use 'typy list' to see available templates."
        )
        sys.exit(1)

    rows = _get_field_rows(template_cls)

    if as_json:
        output = {
            "template": name_or_path,
            "fields": [
                {
                    "name": r["name"],
                    "type": r["type"],
                    "required": r["required"],
                    "default": r["default"],
                }
                for r in rows
            ],
        }
        print(json.dumps(output, indent=2, default=str))
        return

    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print(f"\nTemplate: [bold cyan]{name_or_path}[/bold cyan]\n")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Type")
    table.add_column("Required")
    table.add_column("Default")
    for r in rows:
        req_text = (
            "[green]required[/green]" if r["required"] else "[yellow]optional[/yellow]"
        )
        default_text = "" if r["required"] else str(r["default"])
        table.add_row(r["name"], r["type"], req_text, default_text)
    console.print(table)


def cmd_package_validate(package_path: Path) -> None:
    """Validate a .typy package and report diagnostics."""
    from rich.console import Console

    from typy.package import validate_package

    console = Console()
    console_err = Console(stderr=True)

    diagnostics = validate_package(package_path)
    if not diagnostics:
        console.print(
            f"[green]✓[/green] [cyan]{package_path}[/cyan] is a valid .typy package."
        )
        return

    console_err.print(
        f"[red]✗[/red] [cyan]{package_path}[/cyan] has {len(diagnostics)} error(s):\n"
    )
    for diag in diagnostics:
        console_err.print(f"  [bold red]{diag.code}[/bold red]  {diag.message}")
        if diag.hint:
            console_err.print(f"          [yellow]Hint:[/yellow] {diag.hint}")
    sys.exit(1)


def cmd_package_export(
    template_py: Path,
    manifest_file: Path,
    output: Path,
    assets_dir: Path | None,
    readme: Path | None,
) -> None:
    """Export a template as a .typy package."""
    from rich.console import Console

    from typy.package import export_package

    console = Console(stderr=True)

    if not template_py.exists():
        console.print(f"[red]Error:[/red] template.py not found: {template_py}")
        sys.exit(1)

    if not manifest_file.exists():
        console.print(f"[red]Error:[/red] manifest file not found: {manifest_file}")
        sys.exit(1)

    try:
        with open(manifest_file, encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON in '{manifest_file}': {e}")
        sys.exit(1)

    try:
        export_package(
            template_py=template_py,
            manifest=manifest,
            output=output,
            assets_dir=assets_dir,
            readme=readme,
        )
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] Export failed: {e}")
        sys.exit(1)

    Console().print(
        f"[green]✓[/green] Package exported to [cyan]{output.resolve()}[/cyan]"
    )


def cmd_package_install(
    package_path: Path,
    store_dir: Path,
    force: bool,
) -> None:
    """Install a .typy package into the local template store."""
    from rich.console import Console

    from typy.package import PackageValidationError, install_package

    console = Console(stderr=True)

    if not package_path.exists():
        console.print(f"[red]Error:[/red] Package file not found: {package_path}")
        sys.exit(1)

    try:
        install_dir = install_package(package_path, store_dir, force=force)
    except PackageValidationError as e:
        console.print("[red]Error:[/red] Package validation failed:\n")
        for diag in e.diagnostics:
            console.print(f"  [bold red]{diag.code}[/bold red]  {diag.message}")
            if diag.hint:
                console.print(f"          [yellow]Hint:[/yellow] {diag.hint}")
        sys.exit(1)
    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] Install failed: {e}")
        sys.exit(1)

    Console().print(
        f"[green]✓[/green] Package installed to [cyan]{install_dir}[/cyan]\n"
        f"Use [cyan]typy render --template {install_dir / 'template.py'}[/cyan] "
        "to render a document."
    )


def _build_app():
    """Build and return the typer CLI app. Exposed for testing."""
    import typer

    app = typer.Typer(
        name="typy",
        help=CLI_HELP,
        epilog=CLI_EPILOG,
        rich_markup_mode="rich",
        no_args_is_help=True,
        add_completion=False,
    )

    @app.command("list")
    def list_cmd():
        """List built-in templates and their intended use."""
        cmd_list()

    @app.command("info")
    def info_cmd(
        template: str = typer.Argument(
            ...,
            help=(
                "Template name (e.g. 'report') or path to a Python file "
                "containing a Template subclass."
            ),
        ),
        json: bool = typer.Option(
            False,
            "--json",
            help=(
                "Output machine-readable schema JSON. "
                "Recommended for scripts and AI agents."
            ),
        ),
    ):
        """Show field schema for a template."""
        cmd_info(template, as_json=json)

    @app.command("scaffold")
    def scaffold_cmd(
        template: str = typer.Argument(
            ...,
            help=(
                "Template name (e.g. 'report') or path to a Python file "
                "containing a Template subclass."
            ),
        ),
        output: typing.Optional[Path] = typer.Option(
            None,
            "--output",
            help=(
                "Write sample JSON to this file. If omitted, JSON is printed to stdout."
            ),
        ),
    ):
        """Generate starter JSON data for a template."""
        cmd_scaffold(template, output)

    @app.command("render")
    def render_cmd(
        template: typing.Optional[str] = typer.Option(
            None,
            "--template",
            help=(
                "Built-in template name (e.g. 'report'), path to a .py template "
                "module, or path to a raw .typ file."
            ),
        ),
        data: typing.Optional[Path] = typer.Option(
            None,
            "--data",
            help="Path to JSON file with template fields.",
            exists=False,
            file_okay=True,
            dir_okay=False,
        ),
        markdown: typing.Optional[Path] = typer.Option(
            None,
            "--markdown",
            help=(
                "Path to Markdown file. Without --template, renders as a basic "
                "document. With --template, content is injected into body."
            ),
            exists=False,
            file_okay=True,
            dir_okay=False,
        ),
        output: Path = typer.Option(
            Path("output.pdf"),
            "--output",
            help="Output PDF path.",
        ),
    ):
        """Render PDF from template data, Markdown, or both."""
        cmd_render(
            template=template,
            data_file=data,
            markdown_file=markdown,
            output=output,
        )

    # ---- package sub-app ----
    package_app = typer.Typer(
        name="package",
        help="Manage .typy template packages (export, install, validate).",
        no_args_is_help=True,
    )
    app.add_typer(package_app, name="package")

    @package_app.command("validate")
    def package_validate_cmd(
        package: Path = typer.Argument(
            ...,
            help="Path to the .typy package file to validate.",
        ),
    ):
        """Validate the structure and manifest of a .typy package."""
        cmd_package_validate(package)

    @package_app.command("export")
    def package_export_cmd(
        template_py: Path = typer.Argument(
            ...,
            help="Path to the template.py file containing the Template subclass.",
        ),
        manifest_file: Path = typer.Option(
            ...,
            "--manifest",
            help="Path to the manifest.json file.",
        ),
        output: Path = typer.Option(
            ...,
            "--output",
            help="Destination path for the generated .typy package.",
        ),
        assets_dir: typing.Optional[Path] = typer.Option(
            None,
            "--assets",
            help="Optional directory of static assets to bundle under assets/.",
        ),
        readme: typing.Optional[Path] = typer.Option(
            None,
            "--readme",
            help="Optional README file to bundle as README.md.",
        ),
    ):
        """Export a template as a .typy package archive."""
        cmd_package_export(template_py, manifest_file, output, assets_dir, readme)

    @package_app.command("install")
    def package_install_cmd(
        package: Path = typer.Argument(
            ...,
            help="Path to the .typy package file to install.",
        ),
        store: Path = typer.Option(
            Path.home() / ".typy" / "packages",
            "--store",
            help="Local template store directory. Defaults to ~/.typy/packages.",
        ),
        force: bool = typer.Option(
            False,
            "--force",
            help="Overwrite an existing installation of the same name and version.",
        ),
    ):
        """Install a .typy package into the local template store."""
        cmd_package_install(package, store, force)

    return app


def main() -> None:
    app = _build_app()
    app()


if __name__ == "__main__":
    main()
