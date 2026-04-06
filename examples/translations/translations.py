from datetime import datetime

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Lorem
from typy.markup import Heading
from typy.templates import PresentationTemplate, Slide

builder = DocumentBuilder()

template = PresentationTemplate(
    title="Typy Presentation",
    subtitle="Easy slides in Typst",
    author="John Doe",
    date=datetime(2023, 1, 1).strftime("%Y-%m-%d"),
    slides=[
        Slide(
            title="Slide 1",
            body=Content([Heading(3, "Heading 1.1"), Lorem(200)]),
        ),
        Slide(
            title="Slide 2",
            body=Content([Lorem(300)]),
        ),
        Slide(
            title="Slide 3",
            body=Content([Heading(3, "Heading 3.1"), Lorem(100)]),
        ),
        Slide(
            title="Slide 4",
            body=Content([Lorem(100)]),
        ),
    ],
)


builder.add_template(template).save_pdf("presentation.pdf")
