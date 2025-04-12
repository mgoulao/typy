import importlib
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Type

import typst

from typy.templates import Template
from typy.typst_encoder import TypstEncoder


class DocumentBuilder:
    def __init__(self):
        self.tmp_dir = TemporaryDirectory()
        self.template: Template = None

    def add_template(self, template: Template):
        with importlib.resources.path("lib", "typy.typ") as typy_module_path:
            shutil.copy(template.__template_path__, Path(self.tmp_dir.name) / "main.typ")
            shutil.copy(typy_module_path, Path(self.tmp_dir.name) / "typy.typ")

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

    def save_pdf(self, filepath: Path):
        self.compile(Path(self.tmp_dir.name) / "main.typ")
        shutil.copy(Path(self.tmp_dir.name) / "output.pdf", filepath)

    def save_source(self, dirpath: Path):
        shutil.copy(Path(self.tmp_dir.name), dirpath)

    def __del__(self):
        self.tmp_dir.cleanup()
