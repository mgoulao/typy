from dataclasses import dataclass, field
from pathlib import Path

from typy.content import Content


@dataclass
class Template:
    __template_name__: str = field(init=False, repr=False)
    __template_path__: Path = field(init=False, repr=False)

    def get_data(self):
        return {k: v for k, v in self.__dict__.items()}


# Letter template
@dataclass
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


# Invoice template
@dataclass
class InvoiceItem:
    description: str
    price: float


@dataclass
class InvoiceTemplate(Template):
    invoice_nr: str
    invoice_date: str
    items: list[InvoiceItem]
    author_name: str
    author_street: str
    author_zip: str
    author_city: str
    author_tax_nr: str
    author_signature: Content
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


@dataclass
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

@dataclass
class BasicTemplate(Template):
    title: str
    date: str
    author: str
    body: Content

    __template_name__ = "basic"
    __template_path__ = Path(__file__).parent.parent / "templates" / "basic.typ"