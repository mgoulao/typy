from pathlib import Path

import pandas as pd

from typy.builder import (
    DocumentBuilder,
)
from typy.content import Content
from typy.functions import Block, Figure, Image, Table
from typy.markup import Text
from typy.templates import BasicTemplate

builder = DocumentBuilder()
# Files must be explicitly added to the document builder
img_path = builder.add_file(Path(__file__).parent / "example.png")

table_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

# Build like you would using Typst
body = Block(
    Content(
        [
            Text("This is a text"),
            Figure(Image(img_path), caption="This is a caption"),
            Figure(Table(table_df.to_dict()), caption="This is a caption"),
        ]
    )
)

template = BasicTemplate(
    title="Basic Template",
    date="2023-01-01",
    author="John Doe",
    body=body,
)

builder.add_template(template).save_pdf("basic.pdf")
