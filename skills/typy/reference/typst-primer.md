# Typst Primer for typy

This primer covers only the Typst constructs that appear in typy templates.
For full Typst documentation see [typst.app/docs](https://typst.app/docs).

---

## Imports

```typst
#import "file.typ": symbol          // import a symbol from a local file
#import "@preview/package:1.0.0": * // import from Typst Universe (requires network)
```

typy templates always need these two local imports:

```typst
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data
```

---

## Variables

```typst
#let x = 42
#let greeting = "Hello"
#let typy = init_typy(typy_data)    // typy accessor function
```

---

## Function calls

A `#` prefix calls a function and renders the result inline:

```typst
#typy("title", "str")               // call typy accessor
#lorem(50)                          // built-in placeholder text
#pagebreak()                        // page break
```

With a content block argument:

```typst
#block(fill: luma(230), inset: 8pt)[
  This is inside a grey block.
]
```

---

## Content blocks

Square brackets `[...]` create a content block (rich text):

```typst
[This is *bold* and _italic_ text]
[
  Line one.
  Line two.
]
```

---

## Show rules

`#show` applies a transformation to all subsequent content of a given type:

```typst
#show: columns.with(2)              // two-column layout
#show heading: it => text(blue)[#it]// colour all headings blue
```

typy presentation templates use `#show` to apply slide styling.

---

## Headings

```typst
= Level 1 heading
== Level 2 heading
=== Level 3 heading
```

---

## Text formatting

```typst
*bold*
_italic_
`code`
```

---

## Page settings

```typst
#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 2.5cm, right: 2.5cm),
)
#set text(font: "New Computer Modern", size: 11pt)
```

---

## Conditionals

```typst
#if condition [
  Content when true
]
```

Example used in templates:

```typst
#if typy("subtitle", "str") != "" [
  #text(style: "italic")[#typy("subtitle", "str")]
]
```

---

## Loops

```typst
#for item in typy("items", "list") [
  - #item
]
```

---

## Images and figures

```typst
#figure(
  image("path/to/image.png", width: 80%),
  caption: [Figure caption],
)
```

The image path must be relative to the `.typ` file's location (in typy: use
`builder.add_file(...)` and pass the returned path to `Image(...)`).

---

## Tables

```typst
#figure(
  table(
    columns: (auto, auto),
    table.header([*Name*], [*Value*]),
    [Alice], [42],
    [Bob],   [7],
  ),
  caption: [Summary table],
)
```

---

## Vertical spacing

```typst
#v(1em)     // 1em vertical gap
#v(0.5cm)   // 0.5cm vertical gap
```

---

## Alignment

```typst
#align(center)[Centred text]
#align(right)[Right-aligned text]
```

---

## Math

```typst
$x^2 + y^2 = z^2$          // inline math
$ integral_0^1 f(x) d x $  // display math
```

---

## Comments

```typst
// single-line comment
/* multi-line
   comment */
```
