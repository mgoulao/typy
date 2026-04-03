#import "@preview/diatypst:0.9.1": *
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#show: slides.with(
  title: typy("title", "str"),
  subtitle: typy("subtitle", "str"),
  date: typy("date", "str"),
  authors: typy("authors", "array"),
  ratio: 16/9,
  layout: "medium",
  title-color: blue.darken(60%),
  toc: typy("toc", "bool"),
)

= First Section

#typy("section1", "content")

= Second Section

#typy("section2", "content")
