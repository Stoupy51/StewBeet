
# ruff: noqa: RUF012
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import TYPE_CHECKING

from beet import Context

from .placeholder_context import PLACEHOLDER_CTX

if TYPE_CHECKING:
    from ..plugins.auto.text_renders.emit import GlyphEmitter
    from ..plugins.ingame_manual.manual import Manual
    from .cls.external_item import ExternalItem
    from .cls.item import Item


# Shared variables among plugins
class Mem:
    """ Global memory shared among all StewBeet plugins.

    Examples:
        >>> from stewbeet import PLACEHOLDER_CTX, Mem
        >>> Mem.ctx.project_id  # Out of a build, the placeholder context is active
        'your_namespace'
        >>> Mem.ctx is PLACEHOLDER_CTX
        True
    """

    # Public and should be used
    ctx: Context = PLACEHOLDER_CTX
    """ Global context object that holds the beet project configuration.
    This is set during plugins.initialize and used throughout the codebase. """

    definitions: dict[str, Item] = {}
    """ JsonDict storing all item and block definitions for the project. """

    external_definitions: dict[str, ExternalItem] = {}
    """ Secondary JsonDict for storing external items or blocks most likely for recipes. """


    # Very internal,
    manual: Manual | None = None
    """ The ingame_manual Manual handle, used to register pages/hooks during setup.
    Created lazily via stewbeet.get_manual(); reset after each build (for `beet watch`). """

    text_renders: GlyphEmitter | None = None
    """ The auto.text_renders glyph emitter, shared by the build pass and resolve_renders() so both
    draw glyph characters from the same allocator. Created lazily; reset by plugins.initialize. """

    used_textures: set[str] = set()
    """ Source texture paths consumed by generators (e.g. manual book_texture / TexturePage
    backgrounds) that get re-encoded under new names. The check_unused_textures plugin treats
    them as used. Reset by plugins.initialize (for `beet watch`). """

