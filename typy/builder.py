import re
import shutil
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Type

import typst

from typy.templates import Template
from typy.typst_encoder import TypstEncoder


class DocumentBuilder:
    def __init__(self, verbose: bool = False):
        self.tmp_dir = TemporaryDirectory()
        self.template: Template = None
        self.verbose = verbose

    def add_template(self, template: Template):
        typy_module = Path(__file__).parent / "static" / "typy.typ"

        if not template.__template_path__.exists():
            raise FileNotFoundError(
                f"Template file not found: {template.__template_path__}"
            )
        elif template.__template_path__.is_dir():
            shutil.copytree(
                template.__template_path__, Path(self.tmp_dir.name), dirs_exist_ok=True
            )  #
        else:
            shutil.copy(
                template.__template_path__, Path(self.tmp_dir.name) / "main.typ"
            )
        shutil.copy(typy_module, Path(self.tmp_dir.name) / "typy.typ")

        template_name = type(template).__name__
        data = template.get_data()
        for field_name, value in data.items():
            try:
                TypstEncoder.encode(value)
            except TypeError as e:
                raise TypeError(
                    f"Failed to encode field '{field_name}' of template "
                    f"'{template_name}': {e}"
                ) from e

        encoded = TypstEncoder.encode(data)
        data_str = f"#let typy_data = {encoded}\n"

        if self.verbose:
            print(
                f"[typy] Generated Typst data source for template '{template_name}':\n{data_str}"
            )

        with open(
            Path(self.tmp_dir.name) / "typy_data.typ", "w", encoding="utf-8"
        ) as f:
            f.write(data_str)

        return self

    def get_template_data_model(self) -> Type[Template]:
        return self.template.datamodel

    def add_data(self, data: dict | Template):
        encoded = TypstEncoder.encode(data)
        data_str = f"#let typy_data = {encoded}\n"

        if self.verbose:
            print(f"[typy] Generated Typst data source:\n{data_str}")

        with open(
            Path(self.tmp_dir.name) / "typy_data.typ", "w", encoding="utf-8"
        ) as f:
            f.write(data_str)

        return self

    def add_file(self, filepath: Path) -> Path:
        return Path(shutil.copy(filepath, Path(self.tmp_dir.name))).relative_to(
            Path(self.tmp_dir.name)
        )

    def _get_source_context(self, error_message: str) -> str:
        """Extract source context (line number + snippet) from a Typst error message."""
        line_refs = re.findall(r"-->.*?:(\d+):\d+", error_message)
        if not line_refs:
            return ""

        typy_data_file = Path(self.tmp_dir.name) / "typy_data.typ"
        if not typy_data_file.exists():
            return ""

        lines = typy_data_file.read_text(encoding="utf-8").splitlines()
        context_parts = ["\n\nGenerated Typst source context (typy_data.typ):"]
        for ref in line_refs:
            line_num = int(ref) - 1
            start = max(0, line_num - 2)
            end = min(len(lines), line_num + 3)
            for i in range(start, end):
                marker = ">" if i == line_num else " "
                context_parts.append(f"  {marker} {i + 1:3d} | {lines[i]}")
        return "\n".join(context_parts)

    def compile(self, typ_file: Path, output: Path):
        if self.verbose and typ_file.exists():
            print(f"[typy] Compiling: {typ_file}")
            print(f"[typy] Source:\n{typ_file.read_text(encoding='utf-8')}")

        try:
            typst.compile(
                typ_file,
                output=output,
            )
        except Exception as e:
            error_message = str(e)
            context = self._get_source_context(error_message)
            e.args = (f"Typst compilation failed: {error_message}{context}",)
            raise

        return self

    def save_pdf(self, filepath: Path):
        output = Path(self.tmp_dir.name) / "output.pdf"
        self.compile(Path(self.tmp_dir.name) / "main.typ", output)
        shutil.copy(output, filepath)

    def to_buffer(self) -> BytesIO:
        # Compile to a temporary file first since typst.compile doesn't support BytesIO output
        output = Path(self.tmp_dir.name) / "output.pdf"
        self.compile(Path(self.tmp_dir.name) / "main.typ", output)

        # Read the compiled PDF into a BytesIO buffer
        buffer = BytesIO()
        with open(output, "rb") as f:
            buffer.write(f.read())
        buffer.seek(0)
        return buffer

    def save_source(self, dirpath: Path):
        shutil.copy(Path(self.tmp_dir.name), dirpath)

    def __del__(self):
        self.tmp_dir.cleanup()
