#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

// Page settings
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 3cm),
  numbering: "1",
  number-align: center,
)

#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true)

// Numbered sections and figures
#set heading(numbering: "1.1")
#set figure(numbering: "1")

// Title block
#align(center)[
  #v(0.5cm)
  #text(17pt, weight: "bold")[#typy("title", "str")]
  #v(0.8em)
  #for author in typy("authors", "array") {
    text(12pt)[#author.at("name")]
    let affil = author.at("affiliation")
    if affil != "" {
      linebreak()
      text(9pt, style: "italic")[#affil]
    }
    h(2em)
  }
]

#v(1.2em)

// Abstract and keywords
#block(width: 100%, inset: (x: 1.5cm))[
  #align(center)[#text(weight: "bold")[Abstract]]
  #v(0.4em)
  #text(10pt)[#typy("abstract", "str")]
  #let kws = typy("keywords", "array")
  #if kws.len() > 0 [
    #v(0.4em)
    #text(10pt)[#text(weight: "bold")[Keywords: ]#kws.join(", ")]
  ]
]

#v(1em)
#line(length: 100%)
#v(0.8em)

// Body (single or two-column)
#let two_col = typy("two_column", "bool")
#if two_col [
  #columns(2)[
    #typy("body", "content")
  ]
] else [
  #typy("body", "content")
]

// Optional bibliography
#let bib = typy("bibliography_path", "str")
#if bib != none [
  #bibliography(bib)
]
