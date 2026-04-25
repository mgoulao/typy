"""template.py for the legal-brief .typy package."""

from pathlib import Path

from typy.templates import LegalBriefTemplate

# __template_path__ is patched by `typy package export` to resolve correctly
# inside the archive.  When developing locally it points to the source tree.
LegalBriefTemplate.__template_path__ = (
    Path(__file__).parent / "templates" / "legal-brief.typ"
)
