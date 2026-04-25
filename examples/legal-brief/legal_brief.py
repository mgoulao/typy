"""Legal brief example — demonstrates LegalBriefTemplate with case caption,
line numbering, signature block, and certificate of service."""

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.markup import Heading, Text
from typy.templates import (
    LegalAttorneyInfo,
    LegalBriefTemplate,
    LegalLineNumbering,
    LegalParty,
)

parties = [
    LegalParty(name="ACME CORPORATION", role="Plaintiff"),
    LegalParty(name="DELTA INDUSTRIES INC.", role="Defendant"),
]

attorney = LegalAttorneyInfo(
    name="Jane A. Smith",
    bar_number="CA-123456",
    firm="Smith & Associates LLP",
    address="100 Legal Ave, Suite 500\nSan Francisco, CA 94102",
    phone="(415) 555-0100",
    email="jsmith@smithlaw.example.com",
)

body = Content(
    [
        Heading(1, "Introduction"),
        Text(
            "Plaintiff Acme Corporation respectfully submits this Motion for Summary "
            "Judgment pursuant to Federal Rule of Civil Procedure 56. "
            "There is no genuine dispute as to any material fact and Plaintiff "
            "is entitled to judgment as a matter of law."
        ),
        Heading(1, "Statement of Undisputed Facts"),
        Text(
            "1. On January 15, 2025, Defendant Delta Industries entered into a "
            "written contract with Plaintiff for the supply of 5,000 units of "
            "Model X components.\n"
            "2. The agreed delivery date was March 1, 2025.\n"
            "3. Defendant failed to deliver any units by the contractual deadline."
        ),
        Heading(1, "Legal Standard"),
        Text(
            "Summary judgment is appropriate when 'there is no genuine dispute as "
            "to any material fact and the movant is entitled to judgment as a matter "
            "of law.' Fed. R. Civ. P. 56(a). The moving party bears the initial "
            "burden of demonstrating the absence of a genuine dispute of material "
            "fact. Celotex Corp. v. Catrett, 477 U.S. 317, 323 (1986)."
        ),
        Heading(1, "Argument"),
        Heading(2, "I. Defendant Breached the Contract"),
        Text(
            "The undisputed facts establish that Defendant failed to deliver the "
            "contracted goods by the agreed date, constituting a material breach."
        ),
        Heading(1, "Conclusion"),
        Text(
            "For the foregoing reasons, Plaintiff respectfully requests that this "
            "Court grant summary judgment in its favor on all counts."
        ),
    ]
)

template = LegalBriefTemplate(
    court="UNITED STATES DISTRICT COURT\nNORTHERN DISTRICT OF CALIFORNIA",
    case_number="3:25-cv-01234-JCS",
    jurisdiction="Federal",
    parties=parties,
    attorney_info=attorney,
    document_title="MOTION FOR SUMMARY JUDGMENT",
    body=body,
    line_numbering=LegalLineNumbering(enabled=True, start=1, interval=5),
    certificate_of_service=(
        "I hereby certify that on this date I caused a true and correct copy "
        "of the foregoing Motion for Summary Judgment to be served upon counsel "
        "of record for all parties via the Court's CM/ECF electronic filing system."
    ),
)

DocumentBuilder().add_template(template).save_pdf("legal-brief.pdf")
print("Generated: legal-brief.pdf")
