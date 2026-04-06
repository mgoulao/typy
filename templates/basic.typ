#import "typy.typ": init_typy
#import "typy_data.typ": typy_data

#let typy = init_typy(typy_data)


= #typy("title", "str")

Date: #typy("date", "str")

Author: #typy("author", "str")

#typy("body", "content")
