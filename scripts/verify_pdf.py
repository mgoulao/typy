#!/usr/bin/env python3
"""
verify_pdf.py — Thin backward-compatibility wrapper around `typy verify`

This script is superseded by the ``typy verify`` CLI command introduced in
typy 0.6.0.  It is kept here to avoid breaking existing CI pipelines that
call it directly.  New usage should prefer ``typy verify`` instead:

    typy verify output.pdf
    typy verify output.pdf --config verify_config.json --format json

Legacy usage (still supported via this wrapper):
    python scripts/verify_pdf.py output.pdf
    python scripts/verify_pdf.py output.pdf --min-pages 2
    python scripts/verify_pdf.py output.pdf --quiet     # exit code only, no stdout
"""

import argparse
import sys
from pathlib import Path


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

    from typy.verify import PageCountConfig, VerificationConfig, verify_pdf

    config = VerificationConfig(page_count=PageCountConfig(min_pages=args.min_pages))
    result = verify_pdf(args.pdf, config)

    if not args.quiet:
        if result.passed:
            size = args.pdf.stat().st_size if args.pdf.exists() else 0
            print(f"✓ {args.pdf} — valid PDF, {size:,} bytes", flush=True)
        else:
            for diag in result.errors:
                print(f"✗ {diag.message}", file=sys.stderr)

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()

