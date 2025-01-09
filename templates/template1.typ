#import "@preview/diatypst:0.4.0": *
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#let typy_template(id, template_func, data) = {
  return template_func(data)
}

#let sections(data) = {
  for value in data {
    [= #value]

  }
}

#show: slides.with(
  title: typy("title", "str"), // Required
  subtitle: "easy slides in typst",
  date: typy("date", "str"),
  authors: (typy("author", "str")),
  // Optional Styling (for more / explanation see in the typst universe)
  ratio: 16/9,
  layout: "medium",
  title-color: blue.darken(60%),
  toc: true,
)

= First Section

#typy("content1", "content")

#typy_template("content2", sections, ("t1", "t2", "t3"))

== First Slide

#lorem(20)

/ *Term*: Definition
