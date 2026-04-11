from importlib.metadata import PackageNotFoundError, version

import typy.builder as builder  # noqa: F401
import typy.content as content  # noqa: F401
import typy.encodable as encodable  # noqa: F401
import typy.functions as functions  # noqa: F401
import typy.markup as markup  # noqa: F401
import typy.typst_encoder as typst_encoder  # noqa: F401

try:
	__version__ = version("typy")
except PackageNotFoundError:
	__version__ = "0+unknown"

__all__ = [
	"__version__",
	"builder",
	"content",
	"encodable",
	"functions",
	"markup",
	"typst_encoder",
]
