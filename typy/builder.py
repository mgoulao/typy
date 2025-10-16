from io import BytesIO
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Type
import traceback

import typst

from typy.templates import Template
from typy.typst_encoder import TypstEncoder


class DocumentBuilder:
    def __init__(self):
        self.tmp_dir = TemporaryDirectory()
        self.template: Template = None

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

        data_str = f"#let typy_data = {TypstEncoder.encode(template.get_data())}\n"

        with open(
            Path(self.tmp_dir.name) / "typy_data.typ", "w", encoding="utf-8"
        ) as f:
            f.write(data_str)

        return self

    def get_template_data_model(self) -> Type[Template]:
        return self.template.datamodel

    def add_data(self, data: dict | Template):
        data_str = f"#let typy_data = {TypstEncoder.encode(data)}\n"

        with open(
            Path(self.tmp_dir.name) / "typy_data.typ", "w", encoding="utf-8"
        ) as f:
            f.write(data_str)

        return self

    def add_file(self, filepath: Path) -> Path:
        return Path(shutil.copy(filepath, Path(self.tmp_dir.name))).relative_to(
            Path(self.tmp_dir.name)
        )

    def compile(self, typ_file: Path, output: Path):
        try:
            typst.compile(
                typ_file,
                output=output,
            )
        except Exception as e:
            print("Error while compiling the document:")
            traceback.print_exc()
            if typ_file.exists():
                print(f"Typst file content ({typ_file}):")
            raise e

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
