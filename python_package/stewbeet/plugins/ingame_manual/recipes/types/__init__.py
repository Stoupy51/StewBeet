""" Built-in recipe-type renderers, one module per family.

Each module registers its renderers when it executes. Importing this package no longer does that
on its own, since PEP 810 defers the imports below: call
:func:`~..registry.load_builtin_renderers` to be sure the registry is populated.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from . import awakened_forge, furnace, linear, shaped, smithing

__all__ = ["awakened_forge", "furnace", "linear", "shaped", "smithing"]
