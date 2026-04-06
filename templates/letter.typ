#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#let logo_path = typy("logo", "str")
#let has_logo = logo_path != ""

#set page(margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm))
#set text(font: "New Computer Modern", size: 11pt)
#set par(leading: 0.65em)

// Letterhead
#if has_logo [
  #grid(
    columns: (1fr, auto),
    align(left)[
      *#typy("sender_name", "str")* \
      #typy("sender_address", "str")
    ],
    image(logo_path, height: 2.5cm),
  )
] else [
  *#typy("sender_name", "str")* \
  #typy("sender_address", "str")
]

#v(1cm)
#line(length: 100%, stroke: 0.5pt)
#v(0.5cm)

// Date
#typy("date", "str")

#v(0.8cm)

// Recipient
*#typy("recipient_name", "str")* \
#typy("recipient_address", "str")

#v(0.8cm)

// Subject
*Re: #typy("subject", "str")*

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
#typy("signature_name", "str")
