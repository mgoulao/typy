from datetime import datetime
from pathlib import Path

from typy.builder import (
    DocumentBuilder,
)
from typy.templates import InvoiceItem, InvoiceTemplate

builder = DocumentBuilder()
signature_img = builder.add_file(Path(__file__).parent / "signature.png")

template = InvoiceTemplate(
    invoice_nr="INV-2023-001",
    invoice_date=datetime(2023, 1, 1),
    items=[
        InvoiceItem(description="Item 1", price=50),
        InvoiceItem(description="Item 2", price=100),
        InvoiceItem(description="Item 3", price=223),
    ],
    author_name="John Doe",
    author_street="123 Main St",
    author_zip="12345",
    author_city="Anytown",
    author_tax_nr="TAX123456",
    author_signature=signature_img,
    recipient_name="Jane Smith",
    recipient_street="456 Elm St",
    recipient_zip="67890",
    recipient_city="Othertown",
    account_holder="John Doe",
    account_bank="Bank of Python",
    account_iban="DE89 3704 0044 0532 0130 00",
    account_bic="COBADEFFXXX",
    vat="19%",
    kleinunternehmer=True,
)

builder.add_template(template).save_pdf("invoice.pdf")
