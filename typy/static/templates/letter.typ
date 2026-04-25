#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#let logo_path = typy("logo", "str")
#let has_logo = logo_path != ""

// ── Shared palette ──────────────────────────────────────────────────────────
#let accent = rgb("#2563eb")  // blue-600 (shared typy palette)
#let muted  = rgb("#94a3b8")  // slate-400

#set page(margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm))
#set text(font: "New Computer Modern", size: 11pt, fill: rgb("#334155"))
#set par(leading: 0.65em)

// Letterhead
#if has_logo [
  #grid(
    columns: (1fr, auto),
    align(left)[
      #text(weight: "bold", fill: rgb("#0f172a"))[#typy("sender_name", "str")] \
      #text(size: 10pt, fill: muted)[#typy("sender_address", "str")]
    ],
    image(logo_path, height: 2.5cm),
  )
] else [
  #text(weight: "bold", size: 13pt, fill: rgb("#0f172a"))[#typy("sender_name", "str")] \
  #text(size: 10pt, fill: muted)[#typy("sender_address", "str")]
]

#v(0.8cm)
#line(length: 100%, stroke: 1.5pt + accent)
#v(0.6cm)

// Date
#text(size: 10pt, fill: muted)[#typy("date", "str")]

#v(0.8cm)

// Recipient
#text(weight: "semibold", fill: rgb("#0f172a"))[#typy("recipient_name", "str")] \
#text(size: 10pt, fill: muted)[#typy("recipient_address", "str")]

#v(0.8cm)

// Subject
#text(weight: "bold", fill: accent)[Re: #typy("subject", "str")]

#v(0.8cm)

// Salutation
Dear #typy("recipient_name", "str"),

#v(0.4cm)

// Body
#typy("body", "content")

#v(0.8cm)

// Closing
#typy("closing", "str")

#v(1.5cm)

// Signature
#text(weight: "semibold")[#typy("signature_name", "str")]
