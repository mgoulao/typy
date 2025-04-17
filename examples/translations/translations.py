from datetime import datetime

from typy.builder import DocumentBuilder
from typy.markup import Heading
from typy.content import Content
from typy.functions import Lorem
from typy.templates import PresentationTemplate

builder = DocumentBuilder()

section1 = Content(
    [
        Heading(2, "Slide 1"),
        Heading(3, "Heading 1.1"),
        Lorem(200),
        Heading(2, "Slide 2"),
        Lorem(300),
    ]
)

section2 = Content(
    [
        Heading(2, "Slide 3"),
        Heading(3, "Heading 3.1"),
        Lorem(100),
        Heading(2, "Slide 4"),
        Lorem(100),
    ]
)

template = PresentationTemplate(
    title="Typy Presentation",
    subtitle="Easy slides in Typst",
    date=datetime(2023, 1, 1).strftime("%Y-%m-%d"),
    authors=["John Doe"],
    toc=True,
    section1=section1,
    section2=section2,
)


builder.add_template(template).save_pdf("presentation.pdf")
