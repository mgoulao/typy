#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

// ── Data ──────────────────────────────────────────────────────────────────
#let company_name    = typy("company_name",    "str")
#let company_address = typy("company_address", "str")
#let client_name     = typy("client_name",     "str")
#let client_address  = typy("client_address",  "str")
#let invoice_number  = typy("invoice_number",  "str")
#let invoice_date    = typy("date",            "str")
#let due_date        = typy("due_date",        "str")
#let items           = typy("items",           "array")
#let tax_rate        = typy("tax_rate",        "float")
#let notes           = typy("notes",           "str")
#let logo            = typy("logo",            "str")

// ── Calculations ──────────────────────────────────────────────────────────
#let subtotal   = items.fold(0.0, (acc, item) => acc + item.quantity * item.unit_price)
#let tax_amount = if tax_rate != none { subtotal * tax_rate / 100.0 } else { 0.0 }
#let total      = subtotal + tax_amount

// Format a number as a dollar amount with 2 decimal places
#let fmt-money(value) = {
  let r = calc.round(value, digits: 2)
  let s = str(r)
  if not s.contains(".") {
    s += ".00"
  } else {
    let parts = s.split(".")
    if parts.at(1).len() == 1 { s += "0" }
  }
  "$" + s
}

// ── Page Setup ────────────────────────────────────────────────────────────
#set page(paper: "a4", margin: (x: 2cm, y: 2cm))
#set text(font: "Linux Libertine", size: 10pt, fill: rgb("#334155"))

// ── Shared palette ─────────────────────────────────────────────────────────
#let accent   = rgb("#2563eb")  // blue-600 (matches typy family)
#let muted    = rgb("#94a3b8")  // slate-400

// ── Header ────────────────────────────────────────────────────────────────
#grid(
  columns: (1fr, auto),
  gutter: 1em,
  align(left + horizon)[
    #text(size: 22pt, weight: "bold", fill: rgb("#0f172a"))[#company_name]
    #linebreak()
    #text(size: 9pt, fill: muted)[#company_address]
  ],
  align(right + horizon)[
    #if logo != none {
      image(logo, width: 4cm)
    }
  ],
)
#v(0.5cm)
#line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
#v(0.4cm)

// ── Invoice Meta ──────────────────────────────────────────────────────────
#grid(
  columns: (1fr, auto),
  gutter: 1em,
  [
    *Bill To* \
    #v(0.15cm)
    #client_name \
    #text(size: 9pt, fill: muted)[#client_address]
  ],
  align(right)[
    #text(size: 18pt, weight: "bold", fill: accent)[INVOICE] \
    #v(0.2cm)
    \##invoice_number \
    Date: #invoice_date \
    Due: #due_date
  ],
)
#v(0.6cm)

// ── Items Table ───────────────────────────────────────────────────────────
#{
  let header-fill = accent
  let alt-fill    = rgb("#eff6ff")  // blue-50
  let rows = (
    table.cell(fill: header-fill)[#text(fill: white, weight: "bold")[Description]],
    table.cell(fill: header-fill, align: right)[#text(fill: white, weight: "bold")[Qty]],
    table.cell(fill: header-fill, align: right)[#text(fill: white, weight: "bold")[Unit Price]],
    table.cell(fill: header-fill, align: right)[#text(fill: white, weight: "bold")[Amount]],
  )
  for (i, item) in items.enumerate() {
    let bg = if calc.odd(i) { alt-fill } else { none }
    rows += (
      table.cell(fill: bg)[#item.description],
      table.cell(fill: bg, align: right)[#item.quantity],
      table.cell(fill: bg, align: right)[#fmt-money(item.unit_price)],
      table.cell(fill: bg, align: right)[#fmt-money(item.quantity * item.unit_price)],
    )
  }
  table(
    columns: (1fr, auto, auto, auto),
    stroke: none,
    inset: (x: 8pt, y: 6pt),
    ..rows,
  )
}

// ── Totals ────────────────────────────────────────────────────────────────
#v(0.4cm)
#align(right)[
  #let tax-row = if tax_rate != none {(
    [Tax (#tax_rate%)], [#fmt-money(tax_amount)],
  )} else { () }
  #table(
    columns: (auto, auto),
    stroke: none,
    inset: (x: 4pt, y: 3pt),
    [Subtotal], [#fmt-money(subtotal)],
    ..tax-row,
    table.hline(stroke: 0.5pt + rgb("#e2e8f0")),
    [*Total*], [#text(fill: accent, weight: "bold")[#fmt-money(total)]],
  )
]

// ── Notes ─────────────────────────────────────────────────────────────────
#if notes != none [
  #v(0.8cm)
  #line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
  #v(0.3cm)
  #text(weight: "bold", fill: rgb("#0f172a"))[Notes] \
  #v(0.1cm)
  #text(fill: muted)[#notes]
]