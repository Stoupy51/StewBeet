""" Built-in recipe-type renderers, one module per family.

Each module registers its renderers when it executes. Importing this package no longer does that
on its own, since PEP 810 defers the imports below: call
:func:`~..registry.load_builtin_renderers` to be sure the registry is populated.
"""

from . import awakened_forge, furnace, linear, shaped, smithing

__all__ = ["awakened_forge", "furnace", "linear", "shaped", "smithing"]
