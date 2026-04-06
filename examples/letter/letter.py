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
    sender_address="123 Main St\nAnytown, CA 12345",
    recipient_name="Jane Smith",
    recipient_address="Jane Smith Inc.\n456 Elm St\nOthertown, NY 67890",
    date="January 1, 2023",
    subject="Account Closure Request",
    body=body,
    closing="Sincerely",
    signature_name="John Doe",
)

builder.add_template(template)
builder.save_pdf("letter.pdf")
