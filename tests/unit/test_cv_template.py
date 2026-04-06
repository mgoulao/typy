import pytest

from typy.builder import DocumentBuilder
from typy.templates import (
    CVCertification,
    CVContact,
    CVEducation,
    CVExperience,
    CVLanguage,
    CVTemplate,
)


@pytest.fixture
def minimal_cv_template():
    """Minimal CVTemplate with only required fields."""
    return CVTemplate(
        name="Jane Smith",
        contact=CVContact(email="jane@example.com"),
        experience=[],
        education=[],
        skills=[],
    )


@pytest.fixture
def full_cv_template():
    """CVTemplate with all optional fields populated."""
    return CVTemplate(
        name="Jane Smith",
        contact=CVContact(
            email="jane@example.com",
            phone="+1 555 000 1234",
            location="San Francisco, CA",
            links=["linkedin.com/in/jane", "github.com/jane"],
        ),
        summary="Experienced software engineer.",
        experience=[
            CVExperience(
                title="Senior Engineer",
                company="Acme Corp",
                start_date="Jan 2021",
                end_date="Present",
                location="Remote",
                description="Led API redesign.",
            )
        ],
        education=[
            CVEducation(
                degree="B.S. Computer Science",
                institution="UC Berkeley",
                start_date="2013",
                end_date="2017",
                location="Berkeley, CA",
                description="Dean's List.",
            )
        ],
        skills=["Python", "Go", "Kubernetes"],
        languages=[CVLanguage(name="English", level="Native")],
        certifications=[
            CVCertification(name="AWS SAA", issuer="Amazon", date="2022")
        ],
    )


# ── Model validation ──────────────────────────────────────────────────────────


def test_cv_template_minimal_creation(minimal_cv_template):
    assert minimal_cv_template.name == "Jane Smith"
    assert minimal_cv_template.summary == ""
    assert minimal_cv_template.experience == []
    assert minimal_cv_template.education == []
    assert minimal_cv_template.skills == []
    assert minimal_cv_template.languages == []
    assert minimal_cv_template.certifications == []


def test_cv_template_full_creation(full_cv_template):
    assert full_cv_template.name == "Jane Smith"
    assert full_cv_template.summary == "Experienced software engineer."
    assert len(full_cv_template.experience) == 1
    assert full_cv_template.experience[0].title == "Senior Engineer"
    assert len(full_cv_template.education) == 1
    assert full_cv_template.education[0].degree == "B.S. Computer Science"
    assert full_cv_template.skills == ["Python", "Go", "Kubernetes"]
    assert len(full_cv_template.languages) == 1
    assert full_cv_template.languages[0].name == "English"
    assert len(full_cv_template.certifications) == 1
    assert full_cv_template.certifications[0].name == "AWS SAA"


def test_cv_contact_defaults():
    contact = CVContact()
    assert contact.email == ""
    assert contact.phone == ""
    assert contact.location == ""
    assert contact.links == []


def test_cv_experience_optional_fields():
    exp = CVExperience(
        title="Engineer", company="Corp", start_date="2020", end_date="2022"
    )
    assert exp.location == ""
    assert exp.description == ""


def test_cv_education_optional_fields():
    edu = CVEducation(
        degree="B.S.", institution="University", start_date="2016", end_date="2020"
    )
    assert edu.location == ""
    assert edu.description == ""


def test_cv_template_name():
    assert CVTemplate.__template_name__ == "cv"


# ── PDF compilation ───────────────────────────────────────────────────────────


def test_cv_template_compiles_to_pdf_minimal(minimal_cv_template):
    """Ensure the minimal CV template compiles to a valid PDF."""
    buffer = DocumentBuilder().add_template(minimal_cv_template).to_buffer()
    assert buffer.read().startswith(b"%PDF-"), "Output is not a valid PDF"


def test_cv_template_compiles_to_pdf_full(full_cv_template):
    """Ensure the fully-populated CV template compiles to a valid PDF."""
    buffer = DocumentBuilder().add_template(full_cv_template).to_buffer()
    assert buffer.read().startswith(b"%PDF-"), "Output is not a valid PDF"


def test_cv_template_save_pdf(full_cv_template, tmp_path):
    """Ensure save_pdf produces a non-empty PDF file."""
    output = tmp_path / "cv.pdf"
    DocumentBuilder().add_template(full_cv_template).save_pdf(output)
    assert output.exists()
    assert output.stat().st_size > 0
