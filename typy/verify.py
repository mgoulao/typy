"""Post-render PDF verification checks for typy documents.

This module defines a verification framework that inspects generated PDFs
after compilation to enforce document quality constraints.

Supported checks (all enabled by default):

* **unresolved_placeholders** (``VFY_E001``) – scans rendered PDF text for
  common placeholder patterns such as ``{{FIELD}}``, ``<<FIELD>>``, etc.
* **page_count** (``VFY_E002``) – enforces minimum and maximum page counts.
* **font_policy** (``VFY_E003``) – verifies allowed and/or required fonts.
* **overflow** (``VFY_E004``) – detects suspiciously large page dimensions
  that typically signal a Typst layout-overflow failure.

CLI usage::

    # Verify an existing PDF (text output, exit 0 = pass / 2 = fail)
    typy verify output.pdf

    # With a JSON configuration file and machine-readable output for CI
    typy verify output.pdf --config verify_config.json --format json

    # Automatically verify after rendering
    typy render --template report --data data.json --output report.pdf --verify

Exit codes
----------
* ``0`` – all enabled checks passed (no error-level diagnostics).
* ``1`` – unexpected error (e.g. PDF not found, invalid config file).
* ``2`` – one or more checks produced error-level diagnostics.

Warnings do **not** change the exit code; they are informational only.

Per-template configuration
--------------------------
Templates can embed verification constraints directly::

    from typy.templates import Template
    from typy.verify import VerificationConfig, PageCountConfig, FontPolicyConfig

    class ReportTemplate(Template):
        ...
        verification_config = VerificationConfig(
            page_count=PageCountConfig(min_pages=2, max_pages=50),
            font_policy=FontPolicyConfig(required_fonts=["DejaVu"]),
        )
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Severity constants
# ---------------------------------------------------------------------------

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


# ---------------------------------------------------------------------------
# Diagnostic model
# ---------------------------------------------------------------------------


@dataclass
class VerificationDiagnostic:
    """A structured diagnostic emitted by a single verification check.

    Attributes:
        code:     Machine-readable error code (e.g. ``"VFY_E001"``).
        check:    Identifier of the check that produced this diagnostic
                  (e.g. ``"unresolved_placeholders"``).
        severity: ``"error"`` or ``"warning"``.  Only *error*-level
                  diagnostics cause a non-zero exit code.
        message:  Human-readable description of the issue.
        hint:     Optional remediation hint.
    """

    code: str
    check: str
    severity: str
    message: str
    hint: str = field(default="")

    def __str__(self) -> str:
        s = f"{self.code}  [{self.severity.upper()}]  {self.message}"
        if self.hint:
            s += f"\n          Hint: {self.hint}"
        return s

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation."""
        d: dict = {
            "code": self.code,
            "check": self.check,
            "severity": self.severity,
            "message": self.message,
        }
        if self.hint:
            d["hint"] = self.hint
        return d


# ---------------------------------------------------------------------------
# Verification configuration
# ---------------------------------------------------------------------------


class PageCountConfig(BaseModel):
    """Configuration for the page-count check.

    Example::

        PageCountConfig(min_pages=1, max_pages=20)
    """

    min_pages: Optional[int] = Field(
        None,
        ge=1,
        description="Minimum number of pages (inclusive).  ``None`` means no lower bound.",
    )
    max_pages: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of pages (inclusive).  ``None`` means no upper bound.",
    )


class FontPolicyConfig(BaseModel):
    """Configuration for the font-policy check.

    Font names are compared case-insensitively using substring matching so
    that a policy entry of ``"Helvetica"`` will match the embedded font name
    ``"Helvetica-Bold"`` or ``"HELVETICANEUE"``.

    Example::

        FontPolicyConfig(
            allowed_fonts=["DejaVu", "NotoSans"],
            required_fonts=["DejaVu"],
        )
    """

    allowed_fonts: list[str] = Field(
        default_factory=list,
        description=(
            "If non-empty, only these font names (or substrings thereof) are "
            "permitted in the document."
        ),
    )
    required_fonts: list[str] = Field(
        default_factory=list,
        description="Font names (or substrings) that must appear in the document.",
    )


class PlaceholderConfig(BaseModel):
    """Configuration for the unresolved-placeholder check.

    Each entry in ``patterns`` is a Python regular expression.  A match in the
    extracted PDF text is reported as an error.

    Default patterns detect the most common placeholder styles:

    * ``{{FIELD_NAME}}``
    * ``<<FIELD_NAME>>``
    * ``[PLACEHOLDER]``
    * bare ``TODO`` or ``FIXME`` tokens
    """

    patterns: list[str] = Field(
        default_factory=lambda: [
            r"\{\{[A-Za-z_][A-Za-z0-9_]*\}\}",
            r"<<[A-Z_][A-Z0-9_]*>>",
            r"\[PLACEHOLDER\]",
            r"\bTODO\b",
            r"\bFIXME\b",
        ],
        description=(
            "Regular-expression patterns whose presence in the rendered PDF "
            "text indicates an unresolved placeholder."
        ),
    )


class VerificationConfig(BaseModel):
    """Per-document verification configuration.

    All checks are enabled by default and apply no additional constraints
    unless explicitly configured.

    The canonical way to embed constraints in a template is::

        class MyTemplate(Template):
            ...
            verification_config = VerificationConfig(
                page_count=PageCountConfig(min_pages=2, max_pages=10),
                font_policy=FontPolicyConfig(required_fonts=["DejaVu"]),
                checks={"overflow": False},   # disable a specific check
            )

    Configuration can also be supplied at runtime via a JSON file passed to
    ``typy verify --config`` or ``typy render --verify-config``.
    """

    page_count: PageCountConfig = Field(default_factory=PageCountConfig)
    font_policy: FontPolicyConfig = Field(default_factory=FontPolicyConfig)
    placeholders: PlaceholderConfig = Field(default_factory=PlaceholderConfig)

    checks: dict[str, bool] = Field(
        default_factory=lambda: {
            "placeholders": True,
            "page_count": True,
            "font_policy": True,
            "overflow": True,
        },
        description=(
            "Map of check name to enabled flag.  Missing keys default to "
            "``True`` (enabled)."
        ),
    )


# ---------------------------------------------------------------------------
# Low-level PDF helpers
# ---------------------------------------------------------------------------


def _read_pdf_bytes(pdf_path: Path) -> bytes:
    return pdf_path.read_bytes()


def _count_pdf_pages(data: bytes) -> int | None:
    """Return the total page count from a PDF's page tree.

    Scans for ``/Count N`` entries (as found in ``/Type /Pages`` dictionaries)
    and returns the largest value, which corresponds to the document-level
    page count in well-formed PDFs.  Returns ``None`` when no count is found.
    """
    counts = [int(m.group(1)) for m in re.finditer(rb"/Count\s+(\d+)", data)]
    return max(counts) if counts else None


def _extract_pdf_fonts(data: bytes) -> set[str]:
    """Return the set of base font names embedded in a PDF.

    Scans for ``/BaseFont /Name`` entries in PDF resource dictionaries.
    Subset prefixes (e.g. ``ABCDEF+Helvetica``) are stripped so that the
    returned names reflect only the logical font family.
    """
    fonts: set[str] = set()
    for m in re.finditer(rb"/BaseFont\s*/([A-Za-z0-9+_-]+)", data):
        name = m.group(1).decode("latin-1", errors="replace")
        if "+" in name:
            name = name.split("+", 1)[1]
        fonts.add(name)
    return fonts


def _extract_pdf_text(data: bytes) -> str:
    """Extract a best-effort plain-text view from a PDF byte string.

    Finds text operators inside ``BT``/``ET`` blocks and decodes both
    literal strings ``(…)`` and hex strings ``<…>``.  This is intentionally
    simple and is sufficient for detecting obvious unresolved placeholders;
    it is **not** a full PDF text extractor.
    """
    text_parts: list[str] = []

    for m in re.finditer(rb"BT\s*(.*?)\s*ET", data, re.DOTALL):
        block = m.group(1)

        # Literal strings: (Hello World)
        for sm in re.finditer(rb"\(([^)]*)\)", block):
            try:
                text_parts.append(sm.group(1).decode("latin-1", errors="replace"))
            except Exception:  # noqa: BLE001
                pass

        # Hex strings: <48656C6C6F>
        for sm in re.finditer(rb"<([0-9A-Fa-f]+)>", block):
            try:
                raw = bytes.fromhex(sm.group(1).decode("ascii"))
                text_parts.append(raw.decode("utf-16-be", errors="replace"))
            except Exception:  # noqa: BLE001
                pass

    return " ".join(text_parts)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_placeholders(
    pdf_path: Path,
    config: PlaceholderConfig,
) -> list[VerificationDiagnostic]:
    """VFY_E001 – detect unresolved placeholder patterns in the rendered PDF.

    Args:
        pdf_path: Path to the compiled PDF.
        config:   Placeholder check configuration.

    Returns:
        A list of :class:`VerificationDiagnostic` objects (empty = no issues).

    Failure example::

        VFY_E001  [ERROR]  Unresolved placeholder detected: '{{author}}'
                  Hint: Replace all template placeholders with real values before
                        rendering.  Use 'typy scaffold' to generate a starter
                        data file.
    """
    diagnostics: list[VerificationDiagnostic] = []

    try:
        data = _read_pdf_bytes(pdf_path)
        text = _extract_pdf_text(data)
    except OSError as exc:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E001",
                check="unresolved_placeholders",
                severity=SEVERITY_ERROR,
                message=f"Could not read PDF for placeholder check: {exc}",
            )
        )
        return diagnostics

    for pattern in config.patterns:
        try:
            matches = list(re.finditer(pattern, text))
        except re.error:
            continue
        for match in matches:
            diagnostics.append(
                VerificationDiagnostic(
                    code="VFY_E001",
                    check="unresolved_placeholders",
                    severity=SEVERITY_ERROR,
                    message=(
                        f"Unresolved placeholder detected: {match.group()!r} "
                        f"(matched pattern {pattern!r})"
                    ),
                    hint=(
                        "Replace all template placeholders with real values before "
                        "rendering. Use 'typy scaffold' to generate a starter data file."
                    ),
                )
            )

    return diagnostics


def check_page_count(
    pdf_path: Path,
    config: PageCountConfig,
) -> list[VerificationDiagnostic]:
    """VFY_E002 – enforce page-count constraints.

    The check is skipped when neither ``min_pages`` nor ``max_pages`` is set.

    Args:
        pdf_path: Path to the compiled PDF.
        config:   Page-count configuration.

    Returns:
        A list of :class:`VerificationDiagnostic` objects (empty = no issues).

    Failure examples::

        VFY_E002  [ERROR]  Page count 1 is below the minimum of 2.
                  Hint: Add more content so the document has at least 2 page(s).

        VFY_E002  [ERROR]  Page count 55 exceeds the maximum of 50.
                  Hint: Reduce content so the document has at most 50 page(s).
    """
    diagnostics: list[VerificationDiagnostic] = []

    if config.min_pages is None and config.max_pages is None:
        return diagnostics

    try:
        data = _read_pdf_bytes(pdf_path)
        pages = _count_pdf_pages(data)
    except OSError as exc:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E002",
                check="page_count",
                severity=SEVERITY_ERROR,
                message=f"Could not read PDF for page-count check: {exc}",
            )
        )
        return diagnostics

    if pages is None:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E002",
                check="page_count",
                severity=SEVERITY_WARNING,
                message="Could not determine page count from the PDF structure.",
                hint="Ensure the PDF was generated by a supported renderer.",
            )
        )
        return diagnostics

    if config.min_pages is not None and pages < config.min_pages:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E002",
                check="page_count",
                severity=SEVERITY_ERROR,
                message=(
                    f"Page count {pages} is below the minimum of {config.min_pages}."
                ),
                hint=(
                    f"Add more content so the document has at least "
                    f"{config.min_pages} page(s)."
                ),
            )
        )

    if config.max_pages is not None and pages > config.max_pages:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E002",
                check="page_count",
                severity=SEVERITY_ERROR,
                message=(
                    f"Page count {pages} exceeds the maximum of {config.max_pages}."
                ),
                hint=(
                    f"Reduce content so the document has at most "
                    f"{config.max_pages} page(s)."
                ),
            )
        )

    return diagnostics


def check_font_policy(
    pdf_path: Path,
    config: FontPolicyConfig,
) -> list[VerificationDiagnostic]:
    """VFY_E003 – enforce font policy (allowed and required fonts).

    The check is skipped when both ``allowed_fonts`` and ``required_fonts``
    are empty.

    Args:
        pdf_path: Path to the compiled PDF.
        config:   Font-policy configuration.

    Returns:
        A list of :class:`VerificationDiagnostic` objects (empty = no issues).

    Failure examples::

        VFY_E003  [ERROR]  Font 'Arial' is not in the allowed-fonts list:
                            ['DejaVu', 'NotoSans'].
                  Hint: Update the template to use only allowed fonts, or add
                        this font to the 'allowed_fonts' list.

        VFY_E003  [ERROR]  Required font 'DejaVu' was not found in the document
                            (fonts used: ['Helvetica']).
                  Hint: Ensure the template uses 'DejaVu' for the required font
                        policy to pass.
    """
    diagnostics: list[VerificationDiagnostic] = []

    if not config.allowed_fonts and not config.required_fonts:
        return diagnostics

    try:
        data = _read_pdf_bytes(pdf_path)
        fonts = _extract_pdf_fonts(data)
    except OSError as exc:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E003",
                check="font_policy",
                severity=SEVERITY_ERROR,
                message=f"Could not read PDF for font-policy check: {exc}",
            )
        )
        return diagnostics

    if not fonts:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E003",
                check="font_policy",
                severity=SEVERITY_WARNING,
                message="No embedded fonts detected in the PDF.",
                hint="Ensure the PDF embeds fonts for reproducible rendering.",
            )
        )
        return diagnostics

    # Allowed-fonts: every font used must appear (by substring) in the allowlist
    if config.allowed_fonts:
        allowed_lower = [a.lower() for a in config.allowed_fonts]
        for font in sorted(fonts):
            font_lower = font.lower()
            if not any(
                allowed in font_lower or font_lower in allowed
                for allowed in allowed_lower
            ):
                diagnostics.append(
                    VerificationDiagnostic(
                        code="VFY_E003",
                        check="font_policy",
                        severity=SEVERITY_ERROR,
                        message=(
                            f"Font '{font}' is not in the allowed-fonts list: "
                            f"{config.allowed_fonts!r}."
                        ),
                        hint=(
                            "Update the template to use only allowed fonts, or add "
                            "this font to the 'allowed_fonts' list in VerificationConfig."
                        ),
                    )
                )

    # Required-fonts: each required name must appear (by substring) in the used set
    if config.required_fonts:
        fonts_lower = {f.lower() for f in fonts}
        for required in config.required_fonts:
            req_lower = required.lower()
            if not any(
                req_lower in f_lower or f_lower in req_lower
                for f_lower in fonts_lower
            ):
                diagnostics.append(
                    VerificationDiagnostic(
                        code="VFY_E003",
                        check="font_policy",
                        severity=SEVERITY_ERROR,
                        message=(
                            f"Required font '{required}' was not found in the "
                            f"document (fonts used: {sorted(fonts)!r})."
                        ),
                        hint=(
                            f"Ensure the template uses '{required}' for the "
                            "required font policy to pass."
                        ),
                    )
                )

    return diagnostics


def check_overflow(pdf_path: Path) -> list[VerificationDiagnostic]:
    """VFY_E004 – detect potential layout-overflow failures.

    Typst does not embed overflow markers in compiled PDFs.  This check uses a
    structural heuristic: a ``/MediaBox`` dimension larger than 5 000 points
    (~176 cm) almost always indicates that the layout engine expanded the page
    to accommodate content that did not fit within the intended bounds.

    Args:
        pdf_path: Path to the compiled PDF.

    Returns:
        A list of :class:`VerificationDiagnostic` objects (empty = no issues).

    Failure example::

        VFY_E004  [WARNING]  Unusually large page dimensions detected
                              (8500×11000 pts).  This may indicate a
                              layout-overflow failure.
                  Hint: Review the template layout for content that causes
                        the page to expand beyond expected bounds.
    """
    diagnostics: list[VerificationDiagnostic] = []

    try:
        data = _read_pdf_bytes(pdf_path)
    except OSError as exc:
        diagnostics.append(
            VerificationDiagnostic(
                code="VFY_E004",
                check="overflow",
                severity=SEVERITY_ERROR,
                message=f"Could not read PDF for overflow check: {exc}",
            )
        )
        return diagnostics

    _OVERFLOW_THRESHOLD = 5000.0  # points (~176 cm)

    for m in re.finditer(rb"/MediaBox\s*\[([^\]]+)\]", data):
        try:
            parts = m.group(1).split()
            if len(parts) == 4:
                width = float(parts[2])
                height = float(parts[3])
                if width > _OVERFLOW_THRESHOLD or height > _OVERFLOW_THRESHOLD:
                    diagnostics.append(
                        VerificationDiagnostic(
                            code="VFY_E004",
                            check="overflow",
                            severity=SEVERITY_WARNING,
                            message=(
                                f"Unusually large page dimensions detected "
                                f"({width:.0f}×{height:.0f} pts). "
                                "This may indicate a layout-overflow failure."
                            ),
                            hint=(
                                "Review the template layout for content that causes "
                                "the page to expand beyond expected bounds."
                            ),
                        )
                    )
                    break  # one warning is sufficient
        except (ValueError, IndexError):
            continue

    return diagnostics


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------


class VerificationResult:
    """Aggregated result of running all enabled verification checks on a PDF.

    Attributes:
        pdf_path:    Path to the verified PDF.
        diagnostics: All emitted diagnostics (errors and warnings combined).
    """

    def __init__(
        self,
        pdf_path: Path,
        diagnostics: list[VerificationDiagnostic],
    ) -> None:
        self.pdf_path = pdf_path
        self.diagnostics = diagnostics

    @property
    def passed(self) -> bool:
        """``True`` when no *error*-level diagnostics were emitted."""
        return not any(d.severity == SEVERITY_ERROR for d in self.diagnostics)

    @property
    def errors(self) -> list[VerificationDiagnostic]:
        """All error-level diagnostics."""
        return [d for d in self.diagnostics if d.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[VerificationDiagnostic]:
        """All warning-level diagnostics."""
        return [d for d in self.diagnostics if d.severity == SEVERITY_WARNING]

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation suitable for CI output."""
        return {
            "pdf": str(self.pdf_path),
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def verify_pdf(
    pdf_path: Path,
    config: VerificationConfig | None = None,
) -> VerificationResult:
    """Run all enabled verification checks on a compiled PDF.

    Args:
        pdf_path: Path to the compiled PDF to verify.
        config:   Verification configuration.  When *None* a default
                  :class:`VerificationConfig` is used (all checks enabled,
                  no additional constraints applied).

    Returns:
        A :class:`VerificationResult` containing all emitted diagnostics.
        Inspect :attr:`VerificationResult.passed` to determine whether the
        document passed all checks.

    Example::

        from pathlib import Path
        from typy.verify import VerificationConfig, PageCountConfig, verify_pdf

        result = verify_pdf(
            Path("report.pdf"),
            VerificationConfig(page_count=PageCountConfig(min_pages=2)),
        )
        if not result.passed:
            for diag in result.errors:
                print(diag)
    """
    if config is None:
        config = VerificationConfig()

    enabled = config.checks
    all_diagnostics: list[VerificationDiagnostic] = []

    if enabled.get("placeholders", True):
        all_diagnostics.extend(check_placeholders(pdf_path, config.placeholders))

    if enabled.get("page_count", True):
        all_diagnostics.extend(check_page_count(pdf_path, config.page_count))

    if enabled.get("font_policy", True):
        all_diagnostics.extend(check_font_policy(pdf_path, config.font_policy))

    if enabled.get("overflow", True):
        all_diagnostics.extend(check_overflow(pdf_path))

    return VerificationResult(pdf_path, all_diagnostics)
