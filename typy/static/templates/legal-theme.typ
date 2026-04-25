// legal-theme.typ — shared Typst theme for the legal vertical design system.
//
// Import this file at the top of every legal template to ensure a consistent
// typographic identity across the family:
//
//   #import "legal-theme.typ": *
//
// The theme exposes:
//   - Page geometry constants (margins, paper)
//   - Colour palette
//   - Typography rules (set text / set par / show heading)
//   - Reusable components: case-caption, signature-block, cert-of-service

// ── Palette ──────────────────────────────────────────────────────────────────
#let ink        = rgb("#1a1a1a")   // near-black body text
#let rule-color = rgb("#333333")   // rule lines
#let meta-ink   = rgb("#444444")   // headings, labels
#let caption-bg = rgb("#f5f5f5")   // case-caption background

// ── Page geometry ────────────────────────────────────────────────────────────
// US Letter, 1-inch margins on all sides — common for federal court filings.
// Individual templates may override these for jurisdiction-specific rules.
#let legal-page-setup() = {
  set page(
    paper: "us-letter",
    margin: (top: 2.54cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm),
    footer: context {
      set text(size: 9pt, fill: meta-ink)
      line(length: 100%, stroke: 0.4pt + rule-color)
      align(center, counter(page).display())
    },
  )
}

// ── Typography ───────────────────────────────────────────────────────────────
#let legal-typography() = {
  set text(font: "New Computer Modern", size: 12pt, fill: ink, lang: "en")
  set par(justify: true, leading: 0.65em, spacing: 1.2em)
  show heading.where(level: 1): it => {
    v(1em, weak: true)
    set text(size: 12pt, weight: "bold", fill: meta-ink)
    upper(it.body)
    v(0.4em, weak: true)
  }
  show heading.where(level: 2): it => {
    v(0.8em, weak: true)
    set text(size: 12pt, weight: "bold", fill: meta-ink)
    it
    v(0.3em, weak: true)
  }
  show heading.where(level: 3): it => {
    v(0.6em, weak: true)
    set text(size: 12pt, weight: "semibold")
    it
    v(0.2em, weak: true)
  }
}

// ── Line numbering helper ─────────────────────────────────────────────────────
// Wraps the document body in a numbered-paragraph show rule.
// Each paragraph is counted; numbers appear every `interval` paragraphs.
//
// Arguments:
//   body     content  — the content to render with numbered paragraphs
//   start    int      — paragraph number to start from (default 1)
//   interval int      — show a number every N paragraphs (default 1)
#let with-line-numbers(body, start: 1, interval: 1) = {
  let para-counter = counter("legal-lines")
  para-counter.update(start - 1)
  show par: it => {
    para-counter.step()
    context {
      let n = para-counter.get().first()
      if calc.rem(n, interval) == 0 {
        grid(
          columns: (1.8em, 1fr),
          gutter: 0.3em,
          align(right + top, text(size: 8pt, fill: luma(140))[#n]),
          it,
        )
      } else {
        grid(
          columns: (1.8em, 1fr),
          gutter: 0.3em,
          [],
          it,
        )
      }
    }
  }
  body
}

// ── Case caption ─────────────────────────────────────────────────────────────
// Renders the standard court filing caption block:
//   - Court name centred at the top
//   - Left column: parties listed with "Plaintiff / Defendant" labels
//   - Right column: case number and document title
//
// Arguments:
//   court         string  — full court name
//   parties       array   — array of (name: str, role: str) dicts
//   case_number   string  — docket / case number
//   doc_title     string  — document title (e.g. "MOTION FOR SUMMARY JUDGMENT")
#let case-caption(court: "", parties: (), case_number: "", doc_title: "") = {
  align(center)[
    #text(weight: "bold", size: 11pt)[#upper(court)]
  ]
  v(0.6em)
  line(length: 100%, stroke: 1pt + rule-color)

  // Build party list text
  let party-lines = parties.map(p => {
    p.name + ", " + upper(p.role)
  }).join("\n")

  grid(
    columns: (1fr, 1fr),
    gutter: 0pt,
    [
      #set text(size: 11pt)
      #party-lines
    ],
    [
      #align(right + top)[
        #text(size: 11pt)[Case No. #case_number]
        #v(0.4em)
        #text(weight: "bold", size: 11pt)[#upper(doc_title)]
      ]
    ],
  )

  line(length: 100%, stroke: 1pt + rule-color)
  v(0.8em)
}

// ── Signature block ───────────────────────────────────────────────────────────
// Renders an attorney signature block.
//
// Arguments:
//   attorney  dict  — (name, bar_number, firm, address, phone, email)
#let signature-block(attorney: (:)) = {
  v(1.5em)
  line(length: 40%, stroke: 0.5pt + rule-color)
  v(0.3em)
  [
    #text(weight: "semibold")[#attorney.name]
    #if attorney.bar_number != "" [ \ Bar No. #attorney.bar_number ]
    #if attorney.firm != "" [ \ #attorney.firm ]
    #if attorney.address != "" [ \ #attorney.address ]
    #if attorney.phone != "" [ \ #attorney.phone ]
    #if attorney.email != "" [ \ #attorney.email ]
  ]
}

// ── Certificate of service ────────────────────────────────────────────────────
// Renders a certificate of service section if text is provided.
//
// Arguments:
//   text  string  — certificate of service body text (empty = omit)
#let certificate-of-service(cert-text: "") = {
  if cert-text != "" {
    pagebreak(weak: true)
    align(center)[
      #text(weight: "bold", size: 12pt)[CERTIFICATE OF SERVICE]
    ]
    v(0.8em)
    line(length: 100%, stroke: 0.5pt + rule-color)
    v(0.8em)
    cert-text
  }
}

