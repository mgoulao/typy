#import "@preview/pro-letter:0.1.1": pro-letter

#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#show: pro-letter.with(
  sender: (
    name: typy("sender_name", "str"),
    street: typy("sender_street", "str"),
    city: typy("sender_city", "str"),
    state: typy("sender_state", "str"),
    zip: typy("sender_zip", "str"),
    phone: typy("sender_phone", "str"),
    email: typy("sender_email", "str"),
  ),

  recipient: (
    company: typy("recipient_company", "str"),
    attention: typy("recipient_attention", "str"),
    street: typy("recipient_street", "str"),
    city: typy("recipient_city", "str"),
    state: typy("recipient_state", "str"),
    zip: typy("recipient_zip", "str"),
  ),

  date: typy("date", "str"),

  subject: typy("subject", "str"),

  signer: typy("signer", "str"),

  attachments: "",
)

#typy("body", "content")
