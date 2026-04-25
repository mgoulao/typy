#!/usr/bin/env python3
"""Generate PNG preview images for all built-in typy templates.

This script runs each example script to produce a PDF, then converts the
first page of each PDF to a PNG using the ``typst`` Python package (which
supports direct PNG output).  The resulting images are saved to ``assets/``
so they can be referenced by the README and docs.

Usage::

    python scripts/generate_previews.py

Requirements:
    - typy installed (``pip install -e .``)
    - The ``typst`` Python package (already a typy dependency)

The script renders every example listed in ``EXAMPLES`` and writes a PNG to
``assets/previews/<name>.png``.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets" / "previews"

# (name, example_script_path)
EXAMPLES: list[tuple[str, Path]] = [
    ("basic", REPO_ROOT / "examples" / "basic" / "basic.py"),
    ("report", REPO_ROOT / "examples" / "report" / "report.py"),
    ("invoice", REPO_ROOT / "examples" / "invoice" / "invoice.py"),
    ("letter", REPO_ROOT / "examples" / "letter" / "letter.py"),
    ("cv", REPO_ROOT / "examples" / "cv" / "cv.py"),
    ("academic", REPO_ROOT / "examples" / "academic" / "academic.py"),
    ("presentation", REPO_ROOT / "examples" / "presentation" / "presentation.py"),
]

# PNG export resolution (pixels per inch equivalent – typst uses px/pt)
PPI = 144  # 2× standard 72 dpi for retina-quality previews


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_example(script: Path, output_pdf: Path) -> None:
    """Execute *script* and capture the generated PDF at *output_pdf*."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Example script {script.name} failed:\n{result.stderr}")
        # The example scripts write <name>.pdf in cwd
        pdf_candidates = list(tmp_path.glob("*.pdf"))
        if not pdf_candidates:
            raise FileNotFoundError(
                f"No PDF produced by {script.name}. stdout:\n{result.stdout}"
            )
        import shutil

        shutil.copy(pdf_candidates[0], output_pdf)


def _pdf_first_page_to_png(pdf_path: Path, png_path: Path, ppi: int = PPI) -> None:
    """Render the first page of *pdf_path* to *png_path* using the typst package."""
    try:
        import typst  # noqa: F401
    except ImportError:
        raise ImportError(
            "The 'typst' Python package is required. Install it with: pip install typst"
        )

    # typst.compile supports PNG output when the output filename ends in .png.
    # We create a minimal wrapper .typ that imports the PDF as an image of the
    # first page.  A simpler path: use pdf2image if available, fall back to a
    # system `pdftoppm` call.
    try:
        _convert_with_pdf2image(pdf_path, png_path, ppi)
        return
    except ImportError:
        pass

    try:
        _convert_with_pdftoppm(pdf_path, png_path, ppi)
        return
    except FileNotFoundError:
        pass

    # Last resort: inform the user
    raise RuntimeError(
        f"Cannot convert {pdf_path} to PNG. "
        "Install pdf2image (pip install pdf2image) or poppler (pdftoppm)."
    )


def _convert_with_pdf2image(pdf_path: Path, png_path: Path, ppi: int) -> None:
    from pdf2image import convert_from_path  # type: ignore[import]

    pages = convert_from_path(str(pdf_path), dpi=ppi, first_page=1, last_page=1)
    pages[0].save(str(png_path), "PNG")


def _convert_with_pdftoppm(pdf_path: Path, png_path: Path, ppi: int) -> None:
    stem = png_path.stem
    out_dir = png_path.parent
    result = subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-r",
            str(ppi),
            "-f",
            "1",
            "-l",
            "1",
            str(pdf_path),
            str(out_dir / stem),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise FileNotFoundError(f"pdftoppm failed: {result.stderr}")
    # pdftoppm names output as <stem>-1.png
    produced = out_dir / f"{stem}-1.png"
    if produced.exists():
        produced.rename(png_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    failed: list[str] = []
    for name, script in EXAMPLES:
        if not script.exists():
            print(f"[SKIP] {name}: example script not found at {script}")
            continue

        print(f"[RENDER] {name} ...", end=" ", flush=True)
        png_path = ASSETS_DIR / f"{name}.png"

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            pdf_path = Path(tmp_pdf.name)

        try:
            _run_example(script, pdf_path)
            _pdf_first_page_to_png(pdf_path, png_path)
            print(f"-> {png_path.relative_to(REPO_ROOT)}")
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED: {exc}")
            failed.append(name)
        finally:
            pdf_path.unlink(missing_ok=True)

    if failed:
        print(f"\n{len(failed)} template(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\nAll previews written to {ASSETS_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
