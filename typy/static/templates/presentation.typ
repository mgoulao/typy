#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

// ── Shared palette (matches typy family: blue-600 accent) ──────────────────
#let accent      = rgb("#2563eb")  // blue-600
#let accent-dark = rgb("#1d4ed8")  // blue-700
#let slide-bg    = rgb("#f8fafc")  // near-white
#let heading-fg  = rgb("#0f172a")  // slate-900
#let body-fg     = rgb("#334155")  // slate-700
#let muted-fg    = rgb("#94a3b8")  // slate-400

// ── Page: 16:9 ──────────────────────────────────────────────────────────────
#set page(
  width:  254mm,
  height: 143mm,
  margin: 0pt,
  fill:   slide-bg,
)
#set text(font: "Linux Libertine", size: 12pt, fill: body-fg)
#set par(leading: 0.6em, spacing: 0.9em)

// ── Data ────────────────────────────────────────────────────────────────────
#let deck-title    = typy("title",    "str")
#let deck-subtitle = typy("subtitle", "str")
#let deck-author   = typy("author",   "str")
#let deck-date     = typy("date",     "str")
#let slides        = typy("slides",   "array")

// ── Layout helpers ──────────────────────────────────────────────────────────
// Header bar shared by default and two-column layouts
#let slide-header(title, subtitle) = block(
  width: 100%,
  height: 18mm,
  fill: accent,
  inset: (x: 12mm, top: 0pt, bottom: 0pt),
)[
  #align(horizon)[
    #text(fill: white, weight: "bold", size: 14pt)[#title]
    #if subtitle != none [
      #h(0.8em)
      #text(fill: white.lighten(25%), size: 9.5pt, style: "italic")[#subtitle]
    ]
  ]
]

// Footer row for footnote / notes
#let slide-footer(footnote, notes) = {
  if footnote != none or notes != none {
    place(bottom + left, dy: 0pt)[
      #block(
        width: 254mm,
        fill: rgb("#f1f5f9"),
        inset: (x: 12mm, y: 2mm),
        stroke: (top: 0.5pt + rgb("#e2e8f0")),
      )[
        #set text(size: 7.5pt, fill: muted-fg)
        #if notes != none [
          #text(weight: "bold")[Notes:] #notes
          #if footnote != none [ #h(1fr) #footnote ]
        ] else [
          #align(right)[#footnote]
        ]
      ]
    ]
  }
}

// ── Default layout: accent header + body ────────────────────────────────────
#let layout-default(slide) = {
  slide-header(slide.title, slide.subtitle)
  block(
    width: 100%,
    height: 107mm,
    inset: (x: 12mm, top: 8mm, bottom: 0pt),
    clip: true,
  )[
    #set text(size: 12pt, fill: body-fg)
    #slide.body
  ]
  slide-footer(slide.footnote, slide.notes)
}

// ── Hero layout: full accent background, large centered title ────────────────
#let layout-hero(slide) = {
  place(top + left, block(width: 254mm, height: 143mm, fill: accent)[])
  place(top + left, dx: 12mm, dy: 0pt,
    block(width: 230mm, height: 143mm, inset: (x: 4mm, y: 14mm))[
      #v(1fr)
      #align(center)[
        #text(fill: white, weight: "bold", size: 26pt)[#slide.title]
        #if slide.subtitle != none [
          #v(0.4em)
          #text(fill: white.lighten(25%), size: 14pt)[#slide.subtitle]
        ]
        #v(0.9em)
        #line(length: 40mm, stroke: 2pt + white.lighten(40%))
        #v(0.9em)
        #block(width: 85%)[
          #set text(fill: white, size: 12pt)
          #set par(leading: 0.65em)
          #slide.body
        ]
      ]
      #v(1fr)
    ]
  )
  if slide.footnote != none {
    place(bottom + right, dx: -6mm, dy: -4mm)[
      #text(size: 7.5pt, fill: white.lighten(40%))[#slide.footnote]
    ]
  }
}

// ── Two-column layout: accent header + 2-column body ────────────────────────
#let layout-two-column(slide) = {
  slide-header(slide.title, slide.subtitle)
  block(
    width: 100%,
    height: 107mm,
    inset: (x: 12mm, top: 8mm, bottom: 0pt),
    clip: true,
  )[
    #set text(size: 12pt, fill: body-fg)
    #columns(2, gutter: 10mm)[
      #slide.body
    ]
  ]
  slide-footer(slide.footnote, slide.notes)
}

// ── Blank layout: no header, full body area ──────────────────────────────────
#let layout-blank(slide) = {
  block(
    width: 100%,
    height: 143mm,
    inset: (x: 12mm, top: 10mm, bottom: 0pt),
    clip: true,
  )[
    #set text(size: 12pt, fill: body-fg)
    #slide.body
  ]
  slide-footer(slide.footnote, slide.notes)
}

// ── Title slide ─────────────────────────────────────────────────────────────
// Left accent sidebar + centred meta block
#place(top + left, block(width: 14mm, height: 143mm, fill: accent)[])
#place(top + left, dx: 14mm, dy: 0pt,
  block(width: 240mm, height: 143mm, inset: (x: 14mm, y: 0mm))[
    #v(1fr)
    #text(size: 30pt, weight: "bold", fill: heading-fg)[#deck-title]
    #if deck-subtitle != none [
      #v(0.35em)
      #text(size: 16pt, fill: accent)[#deck-subtitle]
    ]
    #v(1em)
    #line(length: 44mm, stroke: 2.5pt + accent)
    #v(0.85em)
    #text(size: 11pt, fill: body-fg)[#deck-author]
    #v(0.25em)
    #text(size: 10pt, fill: muted-fg)[#deck-date]
    #v(1fr)
  ]
)

// ── Render each slide ────────────────────────────────────────────────────────
#for slide in slides [
  #pagebreak()
  #let variant = slide.layout_variant

  #if variant == "hero" [
    #layout-hero(slide)
  ] else if variant == "two-column" [
    #layout-two-column(slide)
  ] else if variant == "blank" [
    #layout-blank(slide)
  ] else [
    #layout-default(slide)
  ]
]
