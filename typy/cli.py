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


def _build_app():
    """Build and return the typer CLI app. Exposed for testing."""
    import typer

    app = typer.Typer(
        name="typy",
        help="typy — generate PDF documents from Typst templates",
        no_args_is_help=True,
        add_completion=False,
    )

    @app.command("list")
    def list_cmd():
        """List all available built-in templates."""
        cmd_list()

    @app.command("info")
    def info_cmd(
        template: str = typer.Argument(
            ..., help="Template name (e.g. 'report') or path to a Python file"
        ),
        json: bool = typer.Option(False, "--json", help="Output schema as JSON"),
    ):
        """Show schema for a template."""
        cmd_info(template, as_json=json)

    return app


def main() -> None:
    app = _build_app()
    app()


if __name__ == "__main__":
    main()
