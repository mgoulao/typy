"""Unit tests for built-in template file locations."""

from typy.templates import (
    AcademicTemplate,
    BasicTemplate,
    CVTemplate,
    InvoiceTemplate,
    LegalBriefTemplate,
    LegalMemoTemplate,
    LetterTemplate,
    PresentationTemplate,
    ReportTemplate,
)


def test_builtin_template_paths_exist_in_package_tree():
    templates = [
        AcademicTemplate,
        BasicTemplate,
        CVTemplate,
        InvoiceTemplate,
        LegalBriefTemplate,
        LegalMemoTemplate,
        LetterTemplate,
        PresentationTemplate,
        ReportTemplate,
    ]

    for template_cls in templates:
        template_path = template_cls.__template_path__
        assert template_path.exists(), f"Missing template file: {template_path}"
        assert template_path.is_file(), f"Template path is not a file: {template_path}"
        assert "static" in template_path.parts
        assert "templates" in template_path.parts
