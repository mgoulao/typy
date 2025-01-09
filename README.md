# typy

typy is a Python library to generate reports, presentations, and other documents (for now, only PDFs) using Typst. The library offers an easy-to-use API to create documents from predefined templates, templates that you can create, or from scratch.

Warning: This library is still very experimental.

typy is composed of two main components:
* the Python library, which is the interface to create documents
* the Typst library, which acts as glue code between the Python library and the Typst markup language.

## Installation

To install typy, you can use pip:

```bash
pip install git+https://github.com/mgoulao/typy.git
```

## Basic usage

The following code snippet shows how to create a simple PDF document using typy:

```python
from typy import DocumentBuilder

builder = DocumentBuilder()

# Files must be explicitly added to the document builder
img_path = builder.add_file(Path("example.png"))

table_df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

# Build like you would using Typst
content = Block(
    Content(
        [
            Text("This is a text"),
            Figure(Image(img_path), caption="This is a caption"),
            Figure(Table(table_df.to_dict()), caption="This is a caption"),
        ]
    )
)

# Build the document from a template
builder.from_template(
    "template1",
    data={
        "title": "Hello, World!",
        "date": "12/12/2023",
        "author": "John Doe",
        "content1": content
    }
)

builder.save_pdf("output.pdf")
```


## Templates

Templates must:
* import the `typy` Typst library which exposes the `init_typy` function, which initializes the data for the placeholder functions
* import the `typy_data.typ` file, which will be created by the Python library during build time and which will contain the data to be used in the template
* initialize typy using the `init_typy` function

```typst
#import "@preview/diatypst:0.4.0": *
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#show: slides.with(
  title: typy("title", "str"), // Required
  subtitle: "easy slides in typst",
  date: typy("date", "str"),
  authors: (typy("author", "str")),
  // Optional Styling (for more / explanation see in the typst universe)
  ratio: 16/9,
  layout: "medium",
  title-color: blue.darken(60%),
  toc: true,
)

= First Section

#typy("content1", "content")

== First Slide

#lorem(20)

/ *Term*: Definition
```

## Typst encoding

The current code to encode the data into Typst markup is still very basic and only supports a few types, functions, and markup elements.
