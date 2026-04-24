#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#let title_val    = typy("title",    "str")
#let subtitle_val = typy("subtitle", "str")
#let author_val   = typy("author",   "str")
#let date_val     = typy("date",     "str")
#let toc_val      = typy("toc",      "bool")

// ---------------------------------------------------------------------------
// Page layout
// ---------------------------------------------------------------------------
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 2.5cm),
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 9pt, fill: luma(120))
      grid(
        columns: (1fr, 1fr),
        align(left,  emph(title_val)),
        align(right, author_val),
      )
      line(length: 100%, stroke: 0.4pt + luma(160))
    }
  },
  footer: context {
    set text(size: 9pt, fill: luma(120))
    line(length: 100%, stroke: 0.4pt + luma(160))
    align(center, counter(page).display("1 / 1", both: true))
  },
)

// ---------------------------------------------------------------------------
// Typography
// ---------------------------------------------------------------------------
#set text(font: "New Computer Modern", size: 11pt, lang: "en")
#set par(justify: true, leading: 0.65em, spacing: 1.2em)
#set heading(numbering: "1.1")

#show heading.where(level: 1): it => {
  v(1.2em, weak: true)
  set text(size: 14pt, weight: "bold")
  it
  v(0.4em, weak: true)
}

#show heading.where(level: 2): it => {
  v(0.9em, weak: true)
  set text(size: 12pt, weight: "bold")
  it
  v(0.3em, weak: true)
}

#show heading.where(level: 3): it => {
  v(0.7em, weak: true)
  set text(size: 11pt, weight: "bold")
  it
  v(0.2em, weak: true)
}

// Code blocks
#show raw.where(block: true): it => {
  set text(size: 9pt)
  block(
    width: 100%,
    inset: (x: 1em, y: 0.8em),
    radius: 3pt,
    fill: luma(245),
    stroke: 0.5pt + luma(200),
    it,
  )
}

// ---------------------------------------------------------------------------
// Title block (first page)
// ---------------------------------------------------------------------------
#align(center)[
  #v(1.5cm)
  #text(size: 24pt, weight: "bold")[#title_val]
  #if subtitle_val != none {
    v(0.4em)
    text(size: 14pt, fill: luma(80))[#subtitle_val]
  }
  #v(1em)
  #text(size: 11pt)[#author_val]
  #v(0.3em)
  #text(size: 11pt, fill: luma(100))[#date_val]
  #v(1.5cm)
]

// ---------------------------------------------------------------------------
// Abstract (optional)
// ---------------------------------------------------------------------------
#let abstract_val = typy("abstract", "content")
#if abstract_val != none {
  block(
    width: 88%,
    inset: (x: 1.2em, y: 0.9em),
    radius: 3pt,
    stroke: 0.5pt + luma(200),
    [
      #align(center, text(weight: "bold", size: 10pt)[Abstract])
      #v(0.4em)
      #set text(size: 10pt)
      #abstract_val
    ],
  )
  align(center, block(width: 88%)[])
  v(0.5em)
}

// ---------------------------------------------------------------------------
// Table of contents (optional)
// ---------------------------------------------------------------------------
#if toc_val == true {
  outline(
    title: "Contents",
    indent: auto,
  )
  pagebreak(weak: true)
}

// ---------------------------------------------------------------------------
// Body
// ---------------------------------------------------------------------------
#typy("body", "content")
