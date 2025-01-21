from typy.encodable import Encodable
from typy.typst_encoder import TypstEncoder


class Content(Encodable):
    def __init__(
        self, content, **kwargs
    ):
        if not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content

    def content_item_encode(self, item):
        from typy.functions import Function
        if isinstance(item, Function):
            return "#" + TypstEncoder.encode(item)
        else:
            return TypstEncoder.encode(item)

    def encode(self):
        return (
            "["
            + "\n".join([self.content_item_encode(item) for item in self.content])
            + "]"
        )
