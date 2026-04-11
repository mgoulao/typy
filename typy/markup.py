from abc import ABC, abstractmethod

from typy.encodable import Encodable


class Markup(Encodable, ABC):
    def __init__(self, text: str):
        self.text = text

    @abstractmethod
    def encode(self):
        pass


class Text(Markup):
    def encode(self):
        return f"{self.text}"


class Raw(Markup):
    def encode(self):
        return f"{self.text}"


class Heading(Markup):
    def __init__(self, level: int, text: str):
        super().__init__(text)
        self.level = level

    def encode(self):
        return f"{'=' * self.level} {self.text}\n"


class Markdown(Markup):
    def encode(self):
        text = self.text.replace("\\", "\\\\").replace('"', '\\"')
        return (
            f'#{{ import "@preview/cmarker:0.1.8": render; render("{text}",'
            " scope: (image: (source, alt: none, format: auto) =>"
            " image(source, alt: alt, format: format))) }"
        )
