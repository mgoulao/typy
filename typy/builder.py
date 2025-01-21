from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import typst

from typy.typst_encoder import TypstEncoder


class DocumentBuilder:
    def __init__(self):
        self.tmp_dir = TemporaryDirectory()

    def from_template(self, template_name: str, data: dict):
        template = Path(__file__).parent.parent / "templates" / (template_name + ".typ")
        typy_module = Path(__file__).parent.parent / "lib" / "typy.typ"

        shutil.copy(template, Path(self.tmp_dir.name) / "main.typ")
        shutil.copy(typy_module, Path(self.tmp_dir.name) / "typy.typ")

        data_str = f"#let typy_data = {TypstEncoder.encode(data)}\n"
        print(data_str)
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
