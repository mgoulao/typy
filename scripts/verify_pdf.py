#!/usr/bin/env python3
"""
verify_pdf.py — Headless PDF verification helper

Checks that a produced PDF:
  1. Exists at the declared path
  2. Is a valid PDF (starts with the %PDF magic bytes)
  3. Has at least one page (configurable via --min-pages)

Usage:
    python scripts/verify_pdf.py output.pdf
    python scripts/verify_pdf.py output.pdf --min-pages 2
    python scripts/verify_pdf.py output.pdf --quiet     # exit code only, no stdout

Exit codes:
    0  — PDF passes all checks
    1  — One or more checks failed (details printed to stderr)
"""

import argparse
import struct
import sys
from pathlib import Path


def _count_pages(data: bytes) -> int:
    """Return a best-effort page count by counting /Page dictionary entries.

    This is a simple heuristic scan of the raw PDF bytes that works for the
    vast majority of PDFs produced by Typst. It does not require any
    third-party PDF library.
    """
    # Count occurrences of b"/Type /Page" (with optional whitespace variants)
    # Typst-produced PDFs use "/Type /Page" without extra whitespace.
    count = data.count(b"/Type /Page")
    # Subtract any /Type /Pages (catalogue) entries to avoid double-counting.
    count -= data.count(b"/Type /Pages")
    return max(count, 0)


def verify_pdf(path: Path, min_pages: int = 1, quiet: bool = False) -> bool:
    """Verify that `path` is a valid, non-empty PDF with at least `min_pages` pages.

    Returns True on success, False on any failure.
    """
    errors = []

    # Check 1: file exists
    if not path.exists():
        errors.append(f"File not found: {path}")
        _report(errors, quiet)
        return False

    # Check 2: non-empty
    size = path.stat().st_size
    if size == 0:
        errors.append(f"File is empty (0 bytes): {path}")
        _report(errors, quiet)
        return False

    # Read the file once for remaining checks
    data = path.read_bytes()

    # Check 3: valid PDF magic bytes
    if not data.startswith(b"%PDF"):
        errors.append(
            f"Not a valid PDF (missing %PDF magic bytes). "
            f"First 8 bytes: {data[:8]!r}"
        )

    # Check 4: page count
    if not errors:  # only check pages if file looks like a PDF
        pages = _count_pages(data)
        if pages < min_pages:
            errors.append(
                f"Expected at least {min_pages} page(s), found {pages}. "
                f"File: {path}"
            )

    if errors:
        _report(errors, quiet)
        return False

    if not quiet:
        pages = _count_pages(data)
        print(
            f"✓ {path} — valid PDF, {pages} page(s), {size:,} bytes",
            flush=True,
        )
    return True


def _report(errors: list[str], quiet: bool) -> None:
    if not quiet:
        for err in errors:
            print(f"✗ {err}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify that a PDF file exists, is valid, and has sufficient pages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pdf", type=Path, help="Path to the PDF file to verify")
    parser.add_argument(
        "--min-pages",
        type=int,
        default=1,
        metavar="N",
        help="Minimum expected page count (default: 1)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout; use exit code only",
    )
    args = parser.parse_args()

    ok = verify_pdf(args.pdf, min_pages=args.min_pages, quiet=args.quiet)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
