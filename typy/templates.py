from datetime import datetime
from pathlib import Path

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
    sender_street: str
    sender_city: str
    sender_state: str
    sender_zip: str
    sender_phone: str
    sender_email: str
    recipient_company: str
    recipient_attention: str
    recipient_street: str
    recipient_city: str
    recipient_state: str
    recipient_zip: str
    date: str
    subject: str
    signer: str
    body: Content

    __template_name__ = "letter"
    __template_path__ = Path(__file__).parent.parent / "templates" / "letter.typ"


# =================
# Invoice template
# =================
class InvoiceItem(BaseModel):
    description: str
    price: float


class InvoiceTemplate(Template):
    invoice_nr: str
    invoice_date: datetime
    items: list[InvoiceItem]
    author_name: str
    author_street: str
    author_zip: str
    author_city: str
    author_tax_nr: str
    author_signature: Path
    recipient_name: str
    recipient_street: str
    recipient_zip: str
    recipient_city: str
    account_holder: str
    account_bank: str
    account_iban: str
    account_bic: str
    vat: str
    kleinunternehmer: bool

    __template_name__ = "invoice"
    __template_path__ = Path(__file__).parent.parent / "templates" / "invoice.typ"


# =================
# Presentation template
# =================
class PresentationTemplate(Template):
    title: str
    subtitle: str
    date: str
    authors: list[str]
    toc: bool
    section1: Content
    section2: Content

    __template_name__ = "presentation"
    __template_path__ = Path(__file__).parent.parent / "templates" / "presentation.typ"


# =================
# Basic template
# =================
class BasicTemplate(Template):
    title: str
    date: str
    author: str
    body: Content

    __template_name__ = "basic"
    __template_path__ = Path(__file__).parent.parent / "templates" / "basic.typ"
