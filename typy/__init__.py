from abc import ABC, abstractmethod
import shutil
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import List
import typst


class Markup(ABC):
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
        return f'{"=" * self.level} {self.text}\n'


class Function:
    def __init__(self, name: str, content=None, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.content = content

    def encode(self):
        encoded_kwargs = ",\n".join(
            [f"{k}:{default_encoder.encode(v)}" for k, v in self.kwargs.items()]
        )
        encoded_content_arg = default_encoder.encode(self.content)
        all_encoded_args = filter(lambda x: x, [encoded_kwargs, encoded_content_arg])
        return f"{self.name}({', '.join(all_encoded_args)})"


class Content:
    def __init__(self, content: Function | Markup | List[Function | Markup], **kwargs):
        if not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content

    def content_item_encode(self, item):
        if isinstance(item, Function):
            return "#" + default_encoder.encode(item)
        else:
            return default_encoder.encode(item)

    def encode(self):
        return (
            "["
            + "\n".join([self.content_item_encode(item) for item in self.content])
            + "]"
        )


class Block(Function):
    def __init__(self, content: Function | Markup | Content, **kwargs):
        super().__init__("block", content, **kwargs)

    def encode(self):
        encoded_kwargs = ",\n".join(
            [f"{k}:{default_encoder.encode(v)}" for k, v in self.kwargs.items()]
        )
        encoded_content_arg = default_encoder.encode(self.content)
        all_encoded_args = filter(lambda x: x, [encoded_kwargs, encoded_content_arg])
        return f"{self.name}({', '.join(all_encoded_args)})"


class Figure(Function):
    def __init__(self, content, **kwargs):
        super().__init__("figure", content, **kwargs)


class Image(Function):
    def __init__(self, src: Path, **kwargs):
        super().__init__("image", src, **kwargs)


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
        data_encoded += (
            "    " + ", ".join(f"[*{header}*]" for header in headers) + ",\n  ),\n"
        )
        # Rows
        for row in rows:
            data_encoded += "  " + ", ".join(f"[{cell}]" for cell in row) + ",\n"

        return Raw(data_encoded)


class TypstEncoder:
    def encode(self, data):
        if isinstance(data, dict):
            return self.encode_dict(data)
        elif isinstance(data, str):
            return self.encode_string(data)
        elif isinstance(data, float):
            return self.encode_float(data)
        elif isinstance(data, int):
            return self.encode_int(data)
        elif isinstance(data, list) or isinstance(data, tuple):
            return self.encode_list(data)
        elif isinstance(data, Path):
            return self.encode_path(data)
        elif (
            isinstance(data, Function)
            or isinstance(data, Markup)
            or isinstance(data, Content)
        ):
            return data.encode()
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

    def encode_dict(self, data):
        items = [f"{self.encode(k)}: {self.encode(v)}" for k, v in data.items()]
        return f"({', '.join(items)})"

    def encode_list(self, data):
        items = [self.encode(item) for item in data]
        return f"({', '.join(items)})"

    def encode_string(self, data):
        return f'"{data}"'

    def encode_int(self, data):
        return str(data)

    def encode_float(self, data):
        return str(data)

    def encode_path(self, data):
        return f'"{str(data)}"'


class DocumentBuilder:
    def __init__(self):
        self.tmp_dir = TemporaryDirectory()

    def from_template(self, template_name: str, data: dict):
        template = Path(__file__).parent.parent / "templates" / (template_name + ".typ")
        typy_module = Path(__file__).parent.parent / "lib" / "typy.typ"

        shutil.copy(template, Path(self.tmp_dir.name) / "main.typ")
        shutil.copy(typy_module, Path(self.tmp_dir.name) / "typy.typ")

        data_str = f"#let typy_data = {default_encoder.encode(data)}\n"
        with open(
            Path(self.tmp_dir.name) / "typy_data.typ", "w", encoding="utf-8"
        ) as f:
            f.write(data_str)

        return self.compile(Path(self.tmp_dir.name) / "main.typ")

    def compile(self, typ_file: Path):
        try:
            typst.compile(
                typ_file,
                output=Path(self.tmp_dir.name) / "output.pdf",
            )
        except Exception as e:
            print("Error while compiling the document:")
            with open(typ_file, "r", encoding="utf-8") as f:
                print(f.read())
            raise e

        return self

    def __del__(self):
        self.tmp_dir.cleanup()

    def add_file(self, filepath: Path) -> Path:
        return Path(shutil.copy(filepath, Path(self.tmp_dir.name))).relative_to(
            Path(self.tmp_dir.name)
        )

    def save_pdf(self, filepath: Path):
        shutil.copy(Path(self.tmp_dir.name) / "output.pdf", filepath)

    def save_source(self, dirpath: Path):
        shutil.copy(Path(self.tmp_dir.name), dirpath)


default_encoder = TypstEncoder()
