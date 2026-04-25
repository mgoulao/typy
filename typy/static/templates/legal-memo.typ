#import "typy.typ": init_typy
#import "typy_data.typ": typy_data
#import "legal-theme.typ": *

#let t = init_typy(typy_data)

// ── Apply shared legal page geometry and typography ──────────────────────────
#legal-page-setup()
#legal-typography()

// ── Extract data ─────────────────────────────────────────────────────────────
#let court_val       = t("court",          "str")
#let case_number_val = t("case_number",    "str")
#let doc_title_val   = t("document_title", "str")
#let date_val        = t("date",           "str")
#let to_val          = t("to",             "str")
#let from_val        = t("from_",          "str")
#let re_val          = t("re",             "str")
#let issue_val       = t("issue",          "content")
#let analysis_val    = t("analysis",       "content")
#let conclusion_val  = t("conclusion",     "content")
#let attorney_val    = t("attorney_info",  "str")

// ── Memo header ──────────────────────────────────────────────────────────────
#align(center)[
  #text(weight: "bold", size: 13pt)[LEGAL MEMORANDUM]
  #v(0.2em)
  #text(size: 10pt)[#upper(court_val) — Case No. #case_number_val]
]

#v(0.8em)
#line(length: 100%, stroke: 1pt + rule-color)
#v(0.6em)

// Standard memo header table
#grid(
  columns: (3cm, 1fr),
  row-gutter: 0.4em,
  [#text(weight: "bold")[TO:]],   [#to_val],
  [#text(weight: "bold")[FROM:]], [#from_val],
  [#text(weight: "bold")[DATE:]], [#date_val],
  [#text(weight: "bold")[RE:]],   [#re_val],
  [#text(weight: "bold")[SUBJ:]], [#doc_title_val],
)

#v(0.6em)
#line(length: 100%, stroke: 1pt + rule-color)
#v(1em)

// ── ISSUE ────────────────────────────────────────────────────────────────────
= Issue

#issue_val

// ── ANALYSIS ─────────────────────────────────────────────────────────────────
= Analysis

#analysis_val

// ── CONCLUSION ───────────────────────────────────────────────────────────────
= Conclusion

#conclusion_val

// ── Signature block ───────────────────────────────────────────────────────────
#signature-block(attorney: attorney_val)
