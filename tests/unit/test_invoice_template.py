import pytest

from typy.builder import DocumentBuilder
from typy.templates import InvoiceItem, InvoiceTemplate


@pytest.fixture
def minimal_invoice():
    """Invoice template with required fields only (no optional fields)."""
    return InvoiceTemplate(
        company_name="Acme Corp",
        company_address="123 Main St, Springfield",
        client_name="Jane Smith",
        client_address="456 Oak Ave, Shelbyville",
        invoice_number="INV-001",
        date="2024-01-01",
        due_date="2024-01-31",
        items=[
            InvoiceItem(description="Consulting", quantity=2, unit_price=100.0),
            InvoiceItem(description="Design Work", quantity=5, unit_price=80.0),
        ],
    )


@pytest.fixture
def full_invoice():
    """Invoice template with all optional fields populated."""
    return InvoiceTemplate(
        company_name="Full Stack LLC",
        company_address="789 Tech Blvd, Austin TX 78701",
        client_name="Bob Builder",
        client_address="100 Construction Rd, Dallas TX 75201",
        invoice_number="INV-2024-099",
        date="2024-06-01",
        due_date="2024-06-30",
        items=[
            InvoiceItem(description="Web Development", quantity=10, unit_price=150.0),
            InvoiceItem(description="Hosting", quantity=1, unit_price=50.0),
        ],
        tax_rate=10.0,
        notes="Thank you for your business!",
    )


# ── Model field tests ─────────────────────────────────────────────────────


def test_invoice_item_fields():
    """InvoiceItem has description, quantity, and unit_price."""
    item = InvoiceItem(description="Widget", quantity=3, unit_price=9.99)
    assert item.description == "Widget"
    assert item.quantity == 3
    assert item.unit_price == 9.99


def test_invoice_template_required_fields(minimal_invoice):
    """InvoiceTemplate accepts all required fields."""
    assert minimal_invoice.company_name == "Acme Corp"
    assert minimal_invoice.invoice_number == "INV-001"
    assert len(minimal_invoice.items) == 2


def test_invoice_template_optional_fields_default_to_none(minimal_invoice):
    """Optional fields default to None when not supplied."""
    assert minimal_invoice.tax_rate is None
    assert minimal_invoice.notes is None
    assert minimal_invoice.logo is None


def test_invoice_template_with_tax_rate(full_invoice):
    """tax_rate is stored correctly."""
    assert full_invoice.tax_rate == 10.0


def test_invoice_template_with_notes(full_invoice):
    """notes is stored correctly."""
    assert full_invoice.notes == "Thank you for your business!"


# ── PDF generation tests ──────────────────────────────────────────────────


def test_invoice_pdf_created_without_optional_fields(minimal_invoice, tmp_path):
    """A PDF is generated successfully when optional fields are omitted."""
    output = tmp_path / "invoice.pdf"
    DocumentBuilder().add_template(minimal_invoice).save_pdf(output)
    assert output.exists()
    assert output.stat().st_size > 0
    assert output.read_bytes()[:5] == b"%PDF-"


def test_invoice_pdf_created_with_tax_and_notes(full_invoice, tmp_path):
    """A PDF is generated successfully when tax_rate and notes are provided."""
    output = tmp_path / "invoice_full.pdf"
    DocumentBuilder().add_template(full_invoice).save_pdf(output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_invoice_pdf_is_valid_pdf(minimal_invoice, tmp_path):
    """The generated file starts with the PDF magic bytes."""
    output = tmp_path / "invoice.pdf"
    DocumentBuilder().add_template(minimal_invoice).save_pdf(output)
    assert output.read_bytes().startswith(b"%PDF-")
