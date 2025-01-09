from pathlib import Path

import pandas as pd
from typy import (
    Block,
    Content,
    DocumentBuilder,
    Figure,
    Heading,
    Image,
    Table,
    Text,
    TypstEncoder,
)

DocumentBuilder().from_template(
    "template1", {"title": "Hello, World!", "date": "12/12/2023"}
).save_pdf("output.pdf")

print(TypstEncoder().encode({"title": ["asdads", "bjhbvd"]}))

print(Heading(2, "Test").encode())

table_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

builder = DocumentBuilder()
img_path = builder.add_file(Path("arcane_me.png"))
breakpoint()

content = Block(
    Content(
        [
            Text("This is a text"),
            Figure(Image(img_path), caption="This is a caption"),
            Figure(Table(table_df.to_dict()), caption="This is a caption"),
        ]
    )
)

print(content.encode())


builder.from_template(
    "template1",
    data={
        "title": "Hello, World!",
        "date": "12/12/2023",
        "author": "JOhn Doe",
        "content1": content,
    },
).save_pdf("output1.pdf")
