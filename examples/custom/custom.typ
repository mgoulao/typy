#import "@preview/classy-german-invoice:0.3.1": invoice
#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)


= #typy("title", "str")

#typy("body", "content")
