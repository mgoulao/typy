from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict

from typy.content import Content


class Template(BaseModel):
    __template_name__: str
    __template_path__: Path

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
