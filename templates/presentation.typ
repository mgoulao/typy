#import "@preview/diatypst:0.9.1": *
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#show: slides.with(
  title: typy("title", "str"),
  subtitle: typy("subtitle", "str"),
  date: typy("date", "str"),
  authors: (typy("author", "str"),),
  ratio: 16/9,
  layout: "medium",
  title-color: blue.darken(60%),
  toc: false,
)

#for slide in typy("slides", "array") [
  == #slide.title

  #slide.body

  #if slide.notes != none [
    #place(bottom + left, dy: -0.5em)[
      #line(length: 100%, stroke: 0.5pt + luma(180))
      #set text(size: 0.65em, fill: luma(100), style: "italic")
      *Notes:* #slide.notes
    ]
  ]
]
