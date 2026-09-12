
# ruff: noqa: RUF012
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import TYPE_CHECKING, Any

from beet import Context
from beet.core.file import TextFileBase

from .placeholder_context import PLACEHOLDER_CTX

if TYPE_CHECKING:
    from ..plugins.auto.text_renders.emit import GlyphEmitter
    from ..plugins.ingame_manual.manual import Manual
    from ..plugins.sniffer.model import AttributionScope, WriteChunk
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

    # Sniffer
    sniffer_enabled: bool = False
    """ Whether the sniffer plugin is active. Gates the provenance capture in write_function so a
    build without the plugin pays nothing. """

    source_map_chunks: dict[str, list[WriteChunk]] = {}
    """ Provenance recorded during the build, keyed by resource location, in write order.
    Reset by plugins.sniffer, which owns it, so consecutive builds in one process start clean. """

    source_map_origins: dict[str, str] = {}
    """ Resource location a function now sits at, to the one it was first put in the pack under.
    A versioning refactor deletes every `ns:impl/**` key and puts the same objects back under
    `ns:v1.2.3/**`, which is what both halves of the sniffer follow through this. """

    source_map_files: dict[TextFileBase[Any], str] = {}
    """ Pack file to the path on disk it was loaded from.
    beet drops `source_path` as soon as any plugin reads a file's text, and mecha names a
    compilation unit after that path, so this is recorded while the pack is still being loaded.
    Keyed by the file itself, the one handle a rename cannot move. """

    attribution: list[AttributionScope] = []
    """ Ambient stack used when no project frame is on the stack, so content a plugin generates from
    a declaration reaches that declaration instead of the plugin. Reset by plugins.sniffer. """


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

