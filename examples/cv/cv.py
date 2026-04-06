from typy.builder import DocumentBuilder
from typy.templates import (
    CVCertification,
    CVContact,
    CVEducation,
    CVExperience,
    CVLanguage,
    CVTemplate,
)

builder = DocumentBuilder()

template = CVTemplate(
    name="Jane Smith",
    contact=CVContact(
        email="jane.smith@example.com",
        phone="+1 (555) 000-1234",
        location="San Francisco, CA",
        links=["linkedin.com/in/janesmith", "github.com/janesmith"],
    ),
    summary=(
        "Experienced software engineer with 8+ years building scalable web applications "
        "and distributed systems. Passionate about clean code, developer experience, and "
        "mentoring junior engineers."
    ),
    experience=[
        CVExperience(
            title="Senior Software Engineer",
            company="Acme Corp",
            start_date="Jan 2021",
            end_date="Present",
            location="San Francisco, CA",
            description=(
                "Led a team of 6 engineers to redesign the core API platform, "
                "reducing p99 latency by 40%. Introduced observability tooling and "
                "on-call runbooks that cut incident resolution time by half."
            ),
        ),
        CVExperience(
            title="Software Engineer",
            company="Startup XYZ",
            start_date="Jun 2017",
            end_date="Dec 2020",
            location="Remote",
            description=(
                "Built and maintained microservices handling 50 M+ requests/day. "
                "Migrated CI/CD pipeline to GitHub Actions, cutting build times by 30%."
            ),
        ),
    ],
    education=[
        CVEducation(
            degree="B.S. Computer Science",
            institution="University of California, Berkeley",
            start_date="2013",
            end_date="2017",
            location="Berkeley, CA",
            description="Dean's List. Capstone project: distributed key-value store in Go.",
        ),
    ],
    skills=[
        "Python",
        "Go",
        "TypeScript",
        "PostgreSQL",
        "Kubernetes",
        "gRPC",
        "AWS",
        "Terraform",
    ],
    languages=[
        CVLanguage(name="English", level="Native"),
        CVLanguage(name="Spanish", level="Intermediate"),
    ],
    certifications=[
        CVCertification(
            name="AWS Certified Solutions Architect",
            issuer="Amazon Web Services",
            date="2022",
        ),
    ],
)

builder.add_template(template).save_pdf("cv.pdf")
