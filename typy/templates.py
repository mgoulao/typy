from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Optional

from pydantic import BaseModel, ConfigDict

from typy.content import Content

if TYPE_CHECKING:
    from typy.verify import VerificationConfig


class TemplateFamily:
    """Descriptor for a vertical design system — a named family of related templates
    that share a common Typst theme file, Python base models, and assets.

    Example::

        legal = TemplateFamily(
            name="legal",
            description="Legal document vertical for court filings and memos",
            theme_path=Path(__file__).parent / "static" / "templates" / "legal-theme.typ",
        )

    Template subclasses declare membership via the ``__template_family__`` class
    attribute (a plain string matching the family's ``name``).  The family
    descriptor is used for documentation, CLI discovery, and package metadata —
    it does not change template rendering behaviour.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        theme_path: Optional[Path] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.theme_path = theme_path

    def __repr__(self) -> str:
        return f"TemplateFamily(name={self.name!r})"


class Template(BaseModel):
    __template_name__: str
    __template_path__: Path

    #: Optional family membership — set to a family ``name`` string on a subclass
    #: to declare that the template belongs to a vertical design system.
    __template_family__: ClassVar[Optional[str]] = None

    #: Optional post-render verification constraints for this template.
    #: Set to a :class:`~typy.verify.VerificationConfig` instance on a
    #: subclass to enforce page-count, font-policy, or placeholder checks
    #: automatically when ``typy render --verify`` is used.
    verification_config: ClassVar[Optional[VerificationConfig]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_data(self) -> dict:
        return self.model_dump()


# =================
# Letter template
# =================
class LetterTemplate(Template):
    sender_name: str
    sender_address: str
    recipient_name: str
    recipient_address: str
    date: str
    subject: str
    body: Content
    closing: str = "Sincerely"
    signature_name: str
    logo: str = ""

    __template_name__ = "letter"
    __template_path__ = Path(__file__).parent / "static" / "templates" / "letter.typ"


# =================
# Invoice template
# =================
class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


class InvoiceTemplate(Template):
    company_name: str
    company_address: str
    client_name: str
    client_address: str
    invoice_number: str
    date: str
    due_date: str
    items: list[InvoiceItem]
    tax_rate: float | None = None
    notes: str | None = None
    logo: Path | None = None

    __template_name__ = "invoice"
    __template_path__ = Path(__file__).parent / "static" / "templates" / "invoice.typ"


# =================
# Presentation template
# =================
class Slide(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str
    subtitle: Optional[str] = None
    body: Content
    footnote: Optional[str] = None
    layout_variant: Optional[str] = None
    notes: Optional[str] = None


class PresentationTemplate(Template):
    title: str
    subtitle: Optional[str] = None
    author: str
    date: str
    slides: list[Slide]
    theme: Optional[str] = None

    __template_name__ = "presentation"
    __template_path__ = (
        Path(__file__).parent / "static" / "templates" / "presentation.typ"
    )


# =================
# Academic template
# =================
class AcademicAuthor(BaseModel):
    name: str
    affiliation: str = ""


class AcademicTemplate(Template):
    title: str
    authors: list[AcademicAuthor]
    abstract: str
    keywords: list[str]
    body: Content
    two_column: bool = False
    bibliography_path: Optional[Path] = None

    __template_name__ = "academic"
    __template_path__ = Path(__file__).parent / "static" / "templates" / "academic.typ"


# =================
# Basic template
# =================
class BasicTemplate(Template):
    title: str
    date: str
    author: str
    body: Content

    __template_name__ = "basic"
    __template_path__ = Path(__file__).parent / "static" / "templates" / "basic.typ"


# =================
# CV / Resume template
# =================
class CVContact(BaseModel):
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[str] = []


class CVExperience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: str
    location: str = ""
    description: str = ""


class CVEducation(BaseModel):
    degree: str
    institution: str
    start_date: str
    end_date: str
    location: str = ""
    description: str = ""


class CVLanguage(BaseModel):
    name: str
    level: str


class CVCertification(BaseModel):
    name: str
    issuer: str
    date: str


class CVTemplate(Template):
    name: str
    contact: CVContact
    summary: str = ""
    experience: list[CVExperience]
    education: list[CVEducation]
    skills: list[str]
    languages: list[CVLanguage] = []
    certifications: list[CVCertification] = []

    __template_name__ = "cv"
    __template_path__ = Path(__file__).parent / "static" / "templates" / "cv.typ"


# =================
# Report template
# =================
class ReportTemplate(Template):
    title: str
    subtitle: Optional[str] = None
    author: str
    date: str
    body: Content
    abstract: Optional[Content] = None
    toc: bool = True

    __template_name__ = "report"
    __template_path__ = Path(__file__).parent / "static" / "templates" / "report.typ"


# =========================================================
# Legal vertical design system
# =========================================================

#: Family descriptor for the legal vertical.  Import and reference this object
#: in third-party code to discover the shared theme path.
legal_family = TemplateFamily(
    name="legal",
    description=(
        "Legal document vertical — court filings, memos, and motions with "
        "case captions, line numbering, and signature blocks."
    ),
    theme_path=Path(__file__).parent / "static" / "templates" / "legal-theme.typ",
)


# ── Shared legal sub-models ────────────────────────────────────────────────


class LegalParty(BaseModel):
    """A party in a legal proceeding."""

    name: str
    role: str  # e.g. "Plaintiff", "Defendant", "Petitioner", "Respondent"


class LegalAttorneyInfo(BaseModel):
    """Attorney / counsel information for signature blocks."""

    name: str
    bar_number: str = ""
    firm: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""


class LegalLineNumbering(BaseModel):
    """Configuration for court-required line numbering."""

    enabled: bool = True
    start: int = 1
    interval: int = 1  # print a number every N lines


# ── Legal base class ───────────────────────────────────────────────────────


class LegalBase(Template):
    """Abstract base for all legal document templates in the legal vertical.

    Subclass this instead of :class:`Template` when building legal documents
    so that shared fields (court, case number, jurisdiction, parties, attorney)
    flow consistently across briefs, memos, and motions.

    This class must not be instantiated directly — it does not define
    ``__template_name__`` or ``__template_path__``.
    """

    court: str
    case_number: str
    jurisdiction: str = ""
    parties: list[LegalParty]
    attorney_info: LegalAttorneyInfo

    __template_family__: ClassVar[Optional[str]] = "legal"

    model_config = ConfigDict(arbitrary_types_allowed=True)


# ── LegalBriefTemplate ────────────────────────────────────────────────────


class LegalBriefTemplate(LegalBase):
    """Court filing / brief with a case caption, numbered lines, signature
    block, and certificate of service.

    **Shared fields** (from :class:`LegalBase`): ``court``, ``case_number``,
    ``jurisdiction``, ``parties``, ``attorney_info``.

    **Brief-specific fields**:

    * ``document_title`` — e.g. ``"MOTION FOR SUMMARY JUDGMENT"``
    * ``body`` — the substantive body of the filing.
    * ``line_numbering`` — :class:`LegalLineNumbering` config.
    * ``certificate_of_service`` — optional attestation text.
    """

    document_title: str
    body: Content
    line_numbering: LegalLineNumbering = LegalLineNumbering()
    certificate_of_service: str = ""

    __template_name__ = "legal-brief"
    __template_path__ = (
        Path(__file__).parent / "static" / "templates" / "legal-brief.typ"
    )


# ── LegalMemoTemplate ─────────────────────────────────────────────────────


class LegalMemoTemplate(LegalBase):
    """Internal legal memorandum using the IRAC structure (Issue / Analysis /
    Conclusion) with citation-friendly formatting.

    **Shared fields** (from :class:`LegalBase`): ``court``, ``case_number``,
    ``jurisdiction``, ``parties``, ``attorney_info``.

    **Memo-specific fields**:

    * ``document_title`` — memo subject line.
    * ``date`` — memo date.
    * ``to`` — recipient(s).
    * ``from_`` — author(s).
    * ``re`` — subject / re line.
    * ``issue`` — issue statement section.
    * ``analysis`` — analysis / discussion section.
    * ``conclusion`` — conclusion section.
    """

    document_title: str
    date: str
    to: str
    from_: str
    re: str
    issue: Content
    analysis: Content
    conclusion: Content

    __template_name__ = "legal-memo"
    __template_path__ = (
        Path(__file__).parent / "static" / "templates" / "legal-memo.typ"
    )
