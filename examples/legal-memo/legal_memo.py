"""Legal memo example — demonstrates LegalMemoTemplate with IRAC structure
(Issue / Analysis / Conclusion) and citation-friendly formatting."""

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.markup import Heading, Text
from typy.templates import (
    LegalAttorneyInfo,
    LegalMemoTemplate,
    LegalParty,
)

parties = [
    LegalParty(name="ACME CORPORATION", role="Plaintiff"),
    LegalParty(name="DELTA INDUSTRIES INC.", role="Defendant"),
]

attorney = LegalAttorneyInfo(
    name="Robert J. Williams",
    bar_number="NY-987654",
    firm="Williams Legal Group",
    address="250 Park Avenue, 10th Floor\nNew York, NY 10177",
    phone="(212) 555-0200",
    email="rwilliams@williamslegal.example.com",
)

issue = Content(
    [
        Text(
            "Whether Defendant Delta Industries Inc. is liable for breach of "
            "contract based on its failure to deliver 5,000 units of Model X "
            "components by the contractually specified deadline of March 1, 2025, "
            "and whether Plaintiff Acme Corporation is entitled to expectation "
            "damages under New York law."
        ),
    ]
)

analysis = Content(
    [
        Heading(2, "Applicable Law"),
        Text(
            "Under New York law, a breach of contract claim requires: "
            "(1) the existence of a contract, (2) the plaintiff's performance "
            "of the contract or a valid excuse for non-performance, (3) the "
            "defendant's material breach, and (4) resulting damages. "
            "Flomenbaum v. New York Univ., 71 A.D.3d 80, 91 (1st Dep't 2009)."
        ),
        Heading(2, "Application"),
        Text(
            "First, the January 15, 2025 written agreement between the parties "
            "constitutes an enforceable contract supported by mutual consideration. "
            "Second, Plaintiff fully performed its obligations by tendering payment "
            "in accordance with the contract terms. Third, Defendant's failure to "
            "deliver any units by March 1, 2025 constitutes a material breach, as "
            "timely delivery was an express condition of the contract. "
            "Fourth, Plaintiff suffered direct damages including lost revenue and "
            "emergency procurement costs totaling approximately $2.3 million."
        ),
        Heading(2, "Damages"),
        Text(
            "Plaintiff is entitled to expectation damages placing it in the position "
            "it would have occupied had the contract been performed. "
            "Bi-Economy Mkt., Inc. v. Harleysville Ins. Co. of N.Y., 10 N.Y.3d 187 "
            "(2008). These include direct damages of $1.8M for the cost differential "
            "of emergency substitute procurement and consequential damages of $500K "
            "for lost production contracts, which were foreseeable at the time of "
            "contracting."
        ),
    ]
)

conclusion = Content(
    [
        Text(
            "Defendant Delta Industries is liable to Plaintiff Acme Corporation for "
            "breach of contract. We recommend proceeding with a demand letter for "
            "$2.3 million in damages, followed by litigation if no settlement is "
            "reached within thirty days. The strength of our documentary evidence "
            "supports a motion for summary judgment at the appropriate stage."
        ),
    ]
)

template = LegalMemoTemplate(
    court="SUPREME COURT OF THE STATE OF NEW YORK\nCOUNTY OF NEW YORK",
    case_number="2025-012345",
    jurisdiction="New York State",
    parties=parties,
    attorney_info=attorney,
    document_title="Liability Analysis and Damages Assessment",
    date="April 25, 2026",
    to="Senior Partners",
    from_="Robert J. Williams",
    re="Acme Corp. v. Delta Industries — Breach of Contract Assessment",
    issue=issue,
    analysis=analysis,
    conclusion=conclusion,
)

DocumentBuilder().add_template(template).save_pdf("legal-memo.pdf")
print("Generated: legal-memo.pdf")
