from typy.encodable import Encodable
from typy.typst_encoder import TypstEncoder


class Content(Encodable):
    def __init__(self, content, **kwargs):
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

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema

        def validate(v):
            if isinstance(v, str):
                from typy.markup import Markdown

                return cls(Markdown(v))
            if isinstance(v, cls):
                return v
            from typy.encodable import Encodable

            if isinstance(v, (Encodable, list)):
                return cls(v)
            raise ValueError(
                f"Cannot coerce type '{type(v).__name__}' to Content. "
                "Expected a str, Content, Encodable, or list."
            )

        return core_schema.no_info_plain_validator_function(validate)
