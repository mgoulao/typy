// author-typst-template.typ — Flow B: Author a Typst template
//
// Minimal working Typst template that pairs with the Python examples
// consume-custom.py and author-python-template.py.
//
// Required boilerplate (all three lines are mandatory):
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

// ── Page settings ───────────────────────────────────────────────────────────
#set page(paper: "a4", margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 3cm))
#set text(font: "New Computer Modern", size: 11pt)
#set heading(numbering: "1.")

// ── Title block ─────────────────────────────────────────────────────────────
#align(center)[
  #text(size: 18pt, weight: "bold")[#typy("title", "str")]
  \
  #text(size: 11pt)[#typy("author", "str")]
]

#v(1em)
#line(length: 100%, stroke: 0.5pt)
#v(1em)

// ── Body content ────────────────────────────────────────────────────────────
#typy("body", "content")
