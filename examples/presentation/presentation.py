from datetime import datetime

from typy.builder import DocumentBuilder
from typy.content import Content
from typy.functions import Lorem
from typy.markup import Raw
from typy.templates import PresentationTemplate, Slide

builder = DocumentBuilder()

template = PresentationTemplate(
    title="Typy Presentation",
    subtitle="Easy slides in Typst",
    author="Jane Doe",
    date=datetime(2024, 1, 15).strftime("%B %d, %Y"),
    slides=[
        Slide(
            title="Introduction",
            body=Content(
                [
                    "Welcome to **typy** — a Python library for generating "
                    "Typst documents and presentations.\n\n"
                    "This deck was built entirely from Python.",
                ]
            ),
            notes="Introduce yourself and explain what typy is.",
        ),
        Slide(
            title="Key Features",
            body=Content(
                [
                    "- Pure-Python template API\n"
                    "- Markdown support via cmarker\n"
                    "- Tables, figures, and code blocks\n"
                    "- PDF output powered by Typst\n"
                    "- 16:9 aspect ratio by default",
                ]
            ),
        ),
        Slide(
            title="Code Example",
            body=Content(
                [
                    Raw(
                        "```python\n"
                        "from typy.templates import PresentationTemplate, Slide\n"
                        "from typy.content import Content\n\n"
                        "template = PresentationTemplate(\n"
                        '    title="My Talk",\n'
                        '    author="Jane Doe",\n'
                        '    date="2024-01-15",\n'
                        "    slides=[\n"
                        "        Slide(\n"
                        '            title="Hello",\n'
                        '            body=Content(["Hello world"]),\n'
                        "        ),\n"
                        "    ],\n"
                        ")\n"
                        "```"
                    ),
                ]
            ),
            notes="Walk through the code line by line.",
        ),
        Slide(
            title="Generated Content",
            body=Content(
                [
                    "typy can also generate filler content for prototyping:\n\n",
                    Lorem(40),
                ]
            ),
        ),
        Slide(
            title="Thank You",
            body=Content(
                [
                    "Thank you for your attention!\n\n"
                    "Find typy at: *github.com/mgoulao/typy*",
                ]
            ),
            notes="Leave time for questions.",
        ),
    ],
)

builder.add_template(template).save_pdf("presentation.pdf")
