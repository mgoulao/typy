#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#let logo_path = typy("logo", "str")
#let has_logo = logo_path != ""

// ── Shared palette ──────────────────────────────────────────────────────────
#let accent   = rgb("#2563eb")  // blue-600 (shared typy palette)
#let body-ink = rgb("#1e293b")  // slate-800 — main text
#let meta-ink = rgb("#475569")  // slate-600 — addresses, date (readable, not washed-out)

#set page(margin: (top: 2.5cm, bottom: 2.5cm, left: 2.8cm, right: 2.8cm))
#set text(font: "New Computer Modern", size: 11pt, fill: body-ink)
#set par(leading: 0.7em, spacing: 1.2em)

// ── Letterhead ───────────────────────────────────────────────────────────────
#if has_logo [
  #grid(
    columns: (1fr, auto),
    gutter: 1em,
    align(left + horizon)[
      #text(weight: "bold", size: 14pt)[#typy("sender_name", "str")] \
      #text(size: 10pt, fill: meta-ink)[#typy("sender_address", "str")]
    ],
    image(logo_path, height: 2.5cm),
  )
] else [
  #text(weight: "bold", size: 14pt)[#typy("sender_name", "str")] \
  #text(size: 10pt, fill: meta-ink)[#typy("sender_address", "str")]
]

#v(0.5cm)
#line(length: 100%, stroke: 1.5pt + accent)
#v(0.6cm)

// ── Date ─────────────────────────────────────────────────────────────────────
#text(size: 10pt, fill: meta-ink)[#typy("date", "str")]

#v(0.7cm)

// ── Recipient ─────────────────────────────────────────────────────────────────
#text(weight: "semibold")[#typy("recipient_name", "str")] \
#text(size: 10pt, fill: meta-ink)[#typy("recipient_address", "str")]

#v(0.7cm)

// ── Subject ───────────────────────────────────────────────────────────────────
#text(weight: "bold", fill: accent)[Re: #typy("subject", "str")]

#v(0.7cm)

// ── Salutation ────────────────────────────────────────────────────────────────
Dear #typy("recipient_name", "str"),

// ── Body ──────────────────────────────────────────────────────────────────────
#typy("body", "content")

// ── Closing ───────────────────────────────────────────────────────────────────
#v(0.5cm)
#typy("closing", "str")

#v(1.5cm)

// ── Signature ─────────────────────────────────────────────────────────────────
#text(weight: "semibold")[#typy("signature_name", "str")]
