#import "typy.typ": init_typy
#import "typy_data.typ": typy_data
#import "legal-theme.typ": *

#let t = init_typy(typy_data)

// ── Apply shared legal page geometry and typography ──────────────────────────
#legal-page-setup()
#legal-typography()

// ── Extract data ─────────────────────────────────────────────────────────────
#let court_val         = t("court",          "str")
#let case_number_val   = t("case_number",    "str")
#let doc_title_val     = t("document_title", "str")
#let parties_val       = t("parties",        "str")   // decoded as array of dicts
#let attorney_val      = t("attorney_info",  "str")   // decoded as dict
#let line_num_val      = t("line_numbering", "str")   // decoded as dict
#let body_val          = t("body",           "content")
#let cert_val          = t("certificate_of_service", "str")

// ── Case caption ─────────────────────────────────────────────────────────────
#case-caption(
  court: court_val,
  parties: parties_val,
  case_number: case_number_val,
  doc_title: doc_title_val,
)

// ── Body (with optional line numbering) ──────────────────────────────────────
#if line_num_val.enabled == true {
  with-line-numbers(
    body_val,
    start: line_num_val.start,
    interval: line_num_val.interval,
  )
} else {
  body_val
}

// ── Signature block ───────────────────────────────────────────────────────────
#signature-block(attorney: attorney_val)

// ── Certificate of service ────────────────────────────────────────────────────
#certificate-of-service(cert-text: cert_val)
