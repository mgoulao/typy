

from dataclasses import dataclass
from pathlib import Path
from typy.builder import (
    DocumentBuilder,
)
from typy.content import (
    Content,
)
from typy.markup import (
    Text,
)
from typy.templates import Template


@dataclass
class CustomTemplate(Template):
    title: str
    body: Content

    __template_name__ = "custom"
    __template_path__ = Path(__file__).parent / "custom.typ"

builder = DocumentBuilder()



builder.add_template(CustomTemplate(
    title="Custom Template",
    body=Content(
        [
            Text("Hello, world!"),
        ]
    )
))
builder.save_pdf("custom.pdf")
