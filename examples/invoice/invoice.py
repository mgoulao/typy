from typy.builder import DocumentBuilder
from typy.templates import InvoiceItem, InvoiceTemplate

builder = DocumentBuilder()

template = InvoiceTemplate(
    company_name="Acme Corp",
    company_address="123 Business Ave, Suite 100\nNew York, NY 10001",
    client_name="Jane Smith",
    client_address="456 Client Street\nSan Francisco, CA 94102",
    invoice_number="INV-2024-001",
    date="January 1, 2024",
    due_date="January 31, 2024",
    items=[
        InvoiceItem(description="Web Design", quantity=10, unit_price=120.0),
        InvoiceItem(description="Backend Development", quantity=20, unit_price=150.0),
        InvoiceItem(description="Hosting Setup", quantity=1, unit_price=250.0),
    ],
    tax_rate=10.0,
    notes="Payment due within 30 days. Thank you for your business!",
    # Optionally pass a logo:
    # logo=builder.add_file(Path(__file__).parent / "logo.png"),
)

builder.add_template(template).save_pdf("invoice.pdf")
