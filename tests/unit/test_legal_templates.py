"""Tests for the legal vertical design system templates."""

from io import BytesIO

import pytest

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.markup import Heading, Text
from typy.templates import (
    LegalAttorneyInfo,
    LegalBase,
    LegalBriefTemplate,
    LegalLineNumbering,
    LegalMemoTemplate,
    LegalParty,
    TemplateFamily,
    legal_family,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def parties():
    return [
        LegalParty(name="ACME CORPORATION", role="Plaintiff"),
        LegalParty(name="DELTA INDUSTRIES INC.", role="Defendant"),
    ]


@pytest.fixture()
def attorney():
    return LegalAttorneyInfo(
        name="Jane Smith",
        bar_number="CA-123456",
        firm="Smith & Associates LLP",
        address="100 Legal Ave\nSan Francisco, CA 94102",
        phone="(415) 555-0100",
        email="jsmith@example.com",
    )


@pytest.fixture()
def brief_template(parties, attorney):
    return LegalBriefTemplate(
        court="UNITED STATES DISTRICT COURT\nNORTHERN DISTRICT OF CALIFORNIA",
        case_number="3:25-cv-01234-JCS",
        jurisdiction="Federal",
        parties=parties,
        attorney_info=attorney,
        document_title="MOTION FOR SUMMARY JUDGMENT",
        body=Content(
            [
                Heading(1, "Introduction"),
                Text("Plaintiff respectfully submits this motion."),
                Heading(1, "Conclusion"),
                Text("Plaintiff requests judgment as a matter of law."),
            ]
        ),
        line_numbering=LegalLineNumbering(enabled=True, start=1, interval=5),
        certificate_of_service="I certify that this document was served on all parties.",
    )


@pytest.fixture()
def memo_template(parties, attorney):
    return LegalMemoTemplate(
        court="SUPREME COURT OF NEW YORK\nCOUNTY OF NEW YORK",
        case_number="2025-012345",
        jurisdiction="New York State",
        parties=parties,
        attorney_info=attorney,
        document_title="Liability Analysis",
        date="April 25, 2026",
        to="Senior Partners",
        from_="Jane Smith",
        re="Contract breach assessment",
        issue=Content(Text("Whether defendant is liable for breach of contract.")),
        analysis=Content(
            [
                Heading(2, "Applicable Law"),
                Text("Under New York law, a breach requires four elements."),
            ]
        ),
        conclusion=Content(Text("Defendant is liable; recommend filing suit.")),
    )


# ── TemplateFamily tests ───────────────────────────────────────────────────────


def test_template_family_name():
    """TemplateFamily stores the name correctly."""
    fam = TemplateFamily(name="clinical", description="Clinical document vertical")
    assert fam.name == "clinical"
    assert fam.description == "Clinical document vertical"
    assert fam.theme_path is None


def test_template_family_repr():
    """TemplateFamily __repr__ includes the name."""
    fam = TemplateFamily(name="financial")
    assert "financial" in repr(fam)


def test_legal_family_descriptor():
    """The built-in legal_family descriptor is configured correctly."""
    assert legal_family.name == "legal"
    assert legal_family.theme_path is not None
    assert legal_family.theme_path.exists()
    assert legal_family.theme_path.name == "legal-theme.typ"


# ── LegalParty / LegalAttorneyInfo / LegalLineNumbering tests ─────────────────


def test_legal_party_fields():
    party = LegalParty(name="Acme Corp", role="Plaintiff")
    assert party.name == "Acme Corp"
    assert party.role == "Plaintiff"


def test_legal_attorney_info_defaults():
    att = LegalAttorneyInfo(name="John Doe")
    assert att.bar_number == ""
    assert att.firm == ""
    assert att.address == ""
    assert att.phone == ""
    assert att.email == ""


def test_legal_line_numbering_defaults():
    ln = LegalLineNumbering()
    assert ln.enabled is True
    assert ln.start == 1
    assert ln.interval == 1


def test_legal_line_numbering_custom():
    ln = LegalLineNumbering(enabled=False, start=5, interval=5)
    assert ln.enabled is False
    assert ln.start == 5
    assert ln.interval == 5


# ── LegalBase is abstract (no template_name / template_path) ──────────────────


def test_legal_base_is_subclass_of_template():
    """LegalBase inherits from Template."""
    from typy.templates import Template

    assert issubclass(LegalBase, Template)


def test_legal_base_family():
    """LegalBase declares membership in the 'legal' family."""
    assert LegalBase.__template_family__ == "legal"


# ── LegalBriefTemplate tests ──────────────────────────────────────────────────


def test_brief_template_fields(brief_template):
    assert brief_template.court.startswith("UNITED STATES")
    assert brief_template.case_number == "3:25-cv-01234-JCS"
    assert brief_template.jurisdiction == "Federal"
    assert len(brief_template.parties) == 2
    assert brief_template.document_title == "MOTION FOR SUMMARY JUDGMENT"
    assert brief_template.certificate_of_service != ""


def test_brief_template_family():
    assert LegalBriefTemplate.__template_family__ == "legal"


def test_brief_template_name():
    assert LegalBriefTemplate.__template_name__ == "legal-brief"


def test_brief_template_path_exists():
    assert LegalBriefTemplate.__template_path__.exists()
    assert LegalBriefTemplate.__template_path__.is_file()


def test_brief_line_numbering_disabled(parties, attorney):
    """Brief with line_numbering disabled still creates successfully."""
    t = LegalBriefTemplate(
        court="Test Court",
        case_number="1:23-cv-00001",
        parties=parties,
        attorney_info=attorney,
        document_title="TEST MOTION",
        body=Content(Text("Body.")),
        line_numbering=LegalLineNumbering(enabled=False),
    )
    assert t.line_numbering.enabled is False


def test_brief_certificate_defaults_empty(parties, attorney):
    t = LegalBriefTemplate(
        court="Test Court",
        case_number="1:23-cv-00001",
        parties=parties,
        attorney_info=attorney,
        document_title="TEST MOTION",
        body=Content(Text("Body.")),
    )
    assert t.certificate_of_service == ""


def test_brief_get_data_keys(brief_template):
    data = brief_template.get_data()
    for key in (
        "court",
        "case_number",
        "jurisdiction",
        "parties",
        "attorney_info",
        "document_title",
        "body",
        "line_numbering",
        "certificate_of_service",
    ):
        assert key in data, f"Missing key: {key}"


def test_brief_produces_valid_pdf(brief_template):
    """Integration test: LegalBriefTemplate builds a valid PDF."""
    builder = DocumentBuilder()
    builder.add_template(brief_template)
    buf = builder.to_buffer()
    assert isinstance(buf, BytesIO)
    content = buf.read()
    assert content.startswith(b"%PDF-"), "Output is not a valid PDF"
    assert len(content) > 0


# ── LegalMemoTemplate tests ───────────────────────────────────────────────────


def test_memo_template_fields(memo_template):
    assert memo_template.court.startswith("SUPREME COURT")
    assert memo_template.case_number == "2025-012345"
    assert memo_template.to == "Senior Partners"
    assert memo_template.from_ == "Jane Smith"
    assert memo_template.re == "Contract breach assessment"
    assert memo_template.date == "April 25, 2026"


def test_memo_template_family():
    assert LegalMemoTemplate.__template_family__ == "legal"


def test_memo_template_name():
    assert LegalMemoTemplate.__template_name__ == "legal-memo"


def test_memo_template_path_exists():
    assert LegalMemoTemplate.__template_path__.exists()
    assert LegalMemoTemplate.__template_path__.is_file()


def test_memo_get_data_keys(memo_template):
    data = memo_template.get_data()
    for key in (
        "court",
        "case_number",
        "jurisdiction",
        "parties",
        "attorney_info",
        "document_title",
        "date",
        "to",
        "from_",
        "re",
        "issue",
        "analysis",
        "conclusion",
    ):
        assert key in data, f"Missing key: {key}"


def test_memo_produces_valid_pdf(memo_template):
    """Integration test: LegalMemoTemplate builds a valid PDF."""
    builder = DocumentBuilder()
    builder.add_template(memo_template)
    buf = builder.to_buffer()
    assert isinstance(buf, BytesIO)
    content = buf.read()
    assert content.startswith(b"%PDF-"), "Output is not a valid PDF"
    assert len(content) > 0


# ── Template path consistency ─────────────────────────────────────────────────


def test_legal_template_paths_in_static_tree():
    """Both legal templates resolve inside the 'static/templates' directory."""
    for cls in (LegalBriefTemplate, LegalMemoTemplate):
        p = cls.__template_path__
        assert p.exists(), f"Missing template file: {p}"
        assert p.is_file()
        assert "static" in p.parts
        assert "templates" in p.parts
