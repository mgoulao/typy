import dataclasses
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel
from typy.encodable import Encodable


class TypstEncoder:
    @classmethod
    def encode(cls, data):
        if isinstance(data, dict):
            return cls.encode_dict(data)
        elif isinstance(data, str):
            return cls.encode_string(data)
        elif isinstance(data, bool):
            return "true" if data else "false"
        elif isinstance(data, float):
            return cls.encode_float(data)
        elif isinstance(data, int):
            return cls.encode_int(data)
        elif isinstance(data, list) or isinstance(data, tuple):
            return cls.encode_list(data)
        elif isinstance(data, Path):
            return cls.encode_path(data)
        elif isinstance(data, datetime):
            from typy.functions import Datetime
            return Datetime(data).encode()
        elif isinstance(data, BaseModel):
            return cls.encode_pydantic_model(data)
        elif data is None:
            return "null"
        elif dataclasses.is_dataclass(data):
            return cls.encode(data.__dict__)
        elif isinstance(data, Encodable):
            return data.encode()
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

    @classmethod
    def encode_dict(cls, data: Dict) -> str:
        items = [f"{k}: {cls.encode(v)}" for k, v in data.items()]
        return f"({', '.join(items)})"

    @classmethod
    def encode_list(cls, data: List) -> str:
        items = [cls.encode(item) for item in data]
        if not items:
            return "()"
        return f"({', '.join(items)},)"

    @classmethod
    def encode_string(cls, data: str) -> str:
        # Escape double quotes with backslash
        data = data.replace('"', r'\"')
        return f'"{data}"'

    @classmethod
    def encode_int(cls, data: int) -> str:
        return str(data)

    @classmethod
    def encode_float(cls, data: float) -> str:
        return str(data)

    @classmethod
    def encode_path(cls, data: Path) -> str:
        return f'"{str(data)}"'

    @classmethod
    def encode_pydantic_model(cls, data: BaseModel) -> str:
        return cls.encode(data.model_dump())
