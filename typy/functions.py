from datetime import datetime
from pathlib import Path

from typy.content import Content
from typy.encodable import Encodable
from typy.markup import Markup, Raw
from typy.typst_encoder import TypstEncoder


class Function(Encodable):
    def __init__(self, name: str, content=None, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.content = content

    def encode(self):
        encoded_kwargs = ",\n".join(
            [f"{k}:{TypstEncoder.encode(v)}" for k, v in self.kwargs.items()]
        )
        encoded_content_arg = (
            TypstEncoder.encode(self.content) if self.content else None
        )
        all_encoded_args = list(
            filter(lambda x: x, [encoded_kwargs, encoded_content_arg])
        )
        return f"{self.name}({', '.join(all_encoded_args)})"


class Block(Function):
    def __init__(self, content: Function | Markup | Content, **kwargs):
        super().__init__("block", content, **kwargs)

    def encode(self):
        encoded_kwargs = ",\n".join(
            [f"{k}:{TypstEncoder.encode(v)}" for k, v in self.kwargs.items()]
        )
        encoded_content_arg = TypstEncoder.encode(self.content)
        all_encoded_args = filter(lambda x: x, [encoded_kwargs, encoded_content_arg])
        return f"{self.name}({', '.join(all_encoded_args)})"


class Figure(Function):
    def __init__(self, content, **kwargs):
        super().__init__("figure", content, **kwargs)


class Image(Function):
    def __init__(self, src: Path, **kwargs):
        super().__init__("image", src, **kwargs)


class Grid(Function):
    def __init__(self, content: Content, **kwargs):
        super().__init__("grid", content, **kwargs)


class Columns(Function):
    def __init__(self, content: Content, **kwargs):
        super().__init__("columns", content, **kwargs)


class Badge(Function):
    def __init__(
        self,
        label: str,
        fill: Raw = Raw("luma(235)"),
        stroke: Raw = Raw("none"),
        radius: Raw = Raw("0.3em"),
        inset: Raw = Raw("(x: 0.45em, y: 0.12em)"),
        **kwargs,
    ):
        super().__init__(
            "box",
            label,
            fill=fill,
            stroke=stroke,
            radius=radius,
            inset=inset,
            **kwargs,
        )


class Callout(Function):
    def __init__(
        self,
        content,
        title: str | None = None,
        fill: Raw = Raw("luma(245)"),
        stroke: Raw = Raw("1pt + luma(180)"),
        radius: Raw = Raw("0.3em"),
        inset: Raw = Raw("0.8em"),
        **kwargs,
    ):
        if title:
            callout_content = Content([Raw(f"*{title}*"), content])
        else:
            callout_content = Content(content)
        super().__init__(
            "block",
            callout_content,
            fill=fill,
            stroke=stroke,
            radius=radius,
            inset=inset,
            **kwargs,
        )


class Table(Function):
    def __init__(self, data: dict, **kwargs):
        if "columns" not in kwargs:
            kwargs["columns"] = [Raw("auto")] * len(data.keys())
        data_content = self._encode_data(data)
        super().__init__("table", data_content, **kwargs)

    def _encode_data(self, data: dict):
        # Extract headers and rows
        headers = list(data.keys())
        rows = zip(*[data[header].values() for header in headers])

        data_encoded = "table.header(\n"
        # Headers
        if headers:
            data_encoded += (
                "    " + ", ".join(f"[*{header}*]" for header in headers) + ",\n  ),\n"
            )
        else:
            data_encoded += "  ),\n"
        # Rows
        for row in rows:
            data_encoded += "  " + ", ".join(f"[{cell}]" for cell in row) + ",\n"

        return Raw(data_encoded)


class Datetime(Function):
    def __init__(self, date: datetime = None, **kwargs):
        if date:
            kwargs["year"] = date.year
            kwargs["month"] = date.month
            kwargs["day"] = date.day
        super().__init__("datetime", **kwargs)


class Lorem(Function):
    def __init__(self, words: int = 100):
        super().__init__("lorem", words)
