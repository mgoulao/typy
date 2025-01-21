#import "@preview/classy-german-invoice:0.3.1": invoice
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)

#show: invoice(
  // Invoice number
  typy("invoice_nr", "str"),
  // Invoice date
  typy("invoice_date", "str"),
  // Items
  typy("items", "array"),
  // Author
  (
    name: typy("author_name", "str"),
    street: typy("author_street", "str"),
    zip: typy("author_zip", "str"),
    city: typy("author_city", "str"),
    tax_nr: typy("author_tax_nr", "str"),
    // optional signature, can be omitted
    signature: image(typy("author_signature", "str"), width: 5em)
  ),
  // Recipient
  (
    name: typy("recipient_name", "str"),
    street: typy("recipient_street", "str"),
    zip: typy("recipient_zip", "str"),
    city: typy("recipient_city", "str"),
  ),
  // Bank account
  (
    name: typy("account_holder", "str"),
    bank: typy("account_bank", "str"),
    iban: typy("account_iban", "str"),
    bic: typy("account_bic", "str"),
  ),
  // Umsatzsteuersatz (VAT)
  vat: typy("vat", "str"),
  kleinunternehmer: true,
)