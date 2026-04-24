#!/usr/bin/env bash
# package-export.sh — Flow C: Export, validate, and re-import a .typy package
#
# STATUS: The `typy package` CLI subcommand is PLANNED (issue #38) and is not
# yet available. This script documents the intended roundtrip workflow.
# Run `typy --help | grep package` to check whether the feature has landed.
#
# Usage (once `typy package` is available):
#   bash examples/package-export.sh

set -euo pipefail

TEMPLATE_PY="examples/author-python-template.py"
PACKAGE_FILE="/tmp/technical_report.typy"
RENDER_OUTPUT="/tmp/package-roundtrip.pdf"

echo "=== Step 1: Export template to .typy package ==="
typy package export "$TEMPLATE_PY" --output "$PACKAGE_FILE"
echo "Exported: $PACKAGE_FILE"

echo ""
echo "=== Step 2: Validate the package ==="
typy package validate "$PACKAGE_FILE"
echo "Validation passed."

echo ""
echo "=== Step 3: Import into local template store ==="
typy package import "$PACKAGE_FILE"
echo "Imported."

echo ""
echo "=== Step 4: Confirm the template is discoverable ==="
typy list | grep technical_report

echo ""
echo "=== Step 5: Render from the imported template ==="
typy scaffold technical_report --output /tmp/package-data.json
typy render --template technical_report --data /tmp/package-data.json --output "$RENDER_OUTPUT"

echo ""
echo "=== Step 6: Verify the rendered PDF ==="
typy verify "$RENDER_OUTPUT"

echo ""
echo "Roundtrip complete. PDF: $RENDER_OUTPUT"
