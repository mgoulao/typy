"""Markdown example — showcases the full range of Markdown markup that typy
renders through the ``Markdown`` markup class."""

from pathlib import Path

from typy.builder import DocumentBuilder
from typy.markup import Markdown
from typy.templates import BasicTemplate

builder = DocumentBuilder()

# Images referenced from Markdown must be added to the builder first; the
# returned path is what the ``![alt](path)`` syntax points at.
image_path = builder.add_file(Path(__file__).parent / "example.png")

body = Markdown(f"""
# Heading level 1
## Heading level 2
### Heading level 3
#### Heading level 4
##### Heading level 5
###### Heading level 6

## Text formatting

Text can be **bold**, *italic*, ***both***, ~~struck through~~, and include
`inline code`. Paragraphs are separated by a blank line and may contain
[links](https://github.com/mgoulao/typy) or bare autolinks such as
<https://typst.app>. End a line with a backslash to force\\
a hard line break.

## Lists

Unordered lists, with nesting:

- First item
- Second item
  - Nested item
  - Another nested item
- Third item

Ordered lists, also nestable:

1. Prepare the data
2. Render the template
   1. Choose a template
   2. Provide the data
3. Verify the PDF

## Quotes and rules

> Blockquotes are useful for callouts and cited passages.
> They can span multiple lines.

---

## Tables

| Metric     | Before | After |
|------------|-------:|------:|
| Latency    |  120ms |  45ms |
| Throughput |   1000 |  3200 |

## Images

![An example image]({image_path})

## Footnotes

Markdown supports footnotes,[^1] which are collected at the bottom of the page.

[^1]: This is the footnote text.

## Code blocks

Fenced code blocks preserve formatting and are syntax highlighted:

```python
from typy.builder import DocumentBuilder
from typy.templates import BasicTemplate

template = BasicTemplate(title="Hello", date="2024-01-01", author="Me", body="Hi")
DocumentBuilder().add_template(template).save_pdf("hello.pdf")
```
""")

template = BasicTemplate(
    title="Markdown Showcase",
    date="2024-01-01",
    author="Jane Doe",
    body=body,
)

builder.add_template(template).save_pdf("markdown.pdf")
