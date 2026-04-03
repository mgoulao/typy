import dataclasses
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

from typy.encodable import Encodable


class TypstEncoder:
    SUPPORTED_TYPES = (
        dict,
        str,
        bool,
        float,
        int,
        list,
        tuple,
        Path,
        datetime,
        BaseModel,
        Encodable,
    )

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
        elif isinstance(data, (list, tuple)):
            return cls.encode_list(data)
        elif isinstance(data, Path):
            return cls.encode_path(data)
        elif isinstance(data, datetime):
            from typy.functions import Datetime

            return Datetime(data).encode()
        elif isinstance(data, date):
            from typy.functions import Datetime

            return Datetime(data).encode()
        elif isinstance(data, BaseModel):
            return cls.encode_pydantic_model(data)
        elif data is None:
            return "none"
        elif dataclasses.is_dataclass(data):
            return cls.encode(data.__dict__)
        elif isinstance(data, Encodable):
            return data.encode()
        else:
            try:
                import pandas as pd

                if isinstance(data, pd.DataFrame):
                    return cls.encode_dataframe(data)
            except ImportError:
                pass

            supported = (
                ", ".join(t.__name__ for t in cls.SUPPORTED_TYPES) + ", None, dataclass"
            )
            raise TypeError(
                f"Cannot encode type '{type(data).__name__}' to Typst. "
                f"Supported types: {supported}"
            )

    @classmethod
    def encode_dict(cls, data: Dict) -> str:
        items = [f"{k}: {cls.encode(v)}" for k, v in data.items()]
        return f"({', '.join(items)})"

    @classmethod
    def encode_list(cls, data: List) -> str:
        items = [cls.encode(item) for item in data]
        if not items:
            return "()"
        if len(items) == 1:
            return f"({items[0]},)"
        return f"({', '.join(items)})"

    @classmethod
    def encode_string(cls, data: str) -> str:
        # Escape backslashes first, then double quotes
        data = data.replace("\\", "\\\\")
        data = data.replace('"', '\\"')
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

    @classmethod
    def encode_dataframe(cls, data: "pd.DataFrame") -> str:
        # Convert DataFrame to Typst table via to_dict() (column-oriented format)
        from typy.functions import Table

        return Table(data.to_dict()).encode()
