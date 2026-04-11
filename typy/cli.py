import argparse
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
    """Print all available built-in templates with a one-line description."""
    print("Available templates:")
    name_width = max(len(n) for n in BUILTIN_TEMPLATES) + 2
    for name, (_, description) in BUILTIN_TEMPLATES.items():
        print(f"  {name:<{name_width}}{description}")


def cmd_info(name_or_path: str, as_json: bool = False) -> None:
    """Print schema information for a template."""
    template_cls = _resolve_template(name_or_path)
    if template_cls is None:
        print(
            f"Error: template '{name_or_path}' not found. "
            "Use 'typy list' to see available templates.",
            file=sys.stderr,
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

    # Human-readable output
    print(f"Template: {name_or_path}\n")
    print("Fields:")
    name_w = max((len(r["name"]) for r in rows), default=0) + 2
    type_w = max((len(r["type"]) for r in rows), default=0) + 2
    for r in rows:
        req_label = "required" if r["required"] else "optional"
        default_part = "" if r["required"] else f"    default: {r['default']}"
        print(
            f"  {r['name']:<{name_w}}{r['type']:<{type_w}}{req_label}{default_part}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="typy",
        description="typy — generate PDF documents from Typst templates",
    )
    subparsers = parser.add_subparsers(dest="command")

    # typy list
    subparsers.add_parser("list", help="List all available built-in templates")

    # typy info
    info_parser = subparsers.add_parser(
        "info", help="Show schema for a template"
    )
    info_parser.add_argument(
        "template",
        help="Template name (e.g. 'report') or path to a Python file",
    )
    info_parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output schema as JSON",
    )

    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "info":
        cmd_info(args.template, as_json=args.as_json)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
