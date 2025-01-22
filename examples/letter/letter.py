from typy.builder import (
    DocumentBuilder,
)
from typy.content import (
    Content,
)
from typy.markup import (
    Text,
)
from typy.templates import LetterTemplate

builder = DocumentBuilder()

body = Content(
    Text("""I am writing to formally request the closure of the enchanted vault at Fantasy Finance Faucets held in my name, Alexandra Bloom.

Attached is the official Fae Council Closure Order for your verification and records.

The account is identified by the vault number: *12345FAE*.

As the rightful owner, I _authorize the closure of the aforementioned vault_ and _request that all enchanted funds be redirected to the Fae Council Reserve_. Please find the necessary details for the transfer enclosed.

Thank you for your prompt attention to this magical matter.""")
)

template = LetterTemplate(
    sender_name="John Doe",
    sender_street="123 Main St",
    sender_city="Anytown",
    sender_state="CA",
    sender_zip="12345",
    sender_phone="555-1234",
    sender_email="john.doe@example.com",
    recipient_company="Jane Smith Inc.",
    recipient_attention="Jane Smith",
    recipient_street="456 Elm St",
    recipient_city="Othertown",
    recipient_state="NY",
    recipient_zip="67890",
    date="2023-01-01",
    subject="Invoice INV-2023-001",
    signer="John Doe",
    body=body,
)

builder.add_template(template)
builder.save_pdf("letter.pdf")
