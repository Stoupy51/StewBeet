
# ruff: noqa: RUF012
# pyright: reportAssignmentType=false
# Imports
from typing import TYPE_CHECKING

from beet import Context

if TYPE_CHECKING:
    from ..plugins.ingame_manual.manual import Manual
    from .cls.external_item import ExternalItem
    from .cls.item import Item


# Shared variables among plugins
class Mem:
    ctx: Context = None
    """ Global context object that holds the beet project configuration.
    This is set during plugins.initialize and used throughout the codebase. """

    definitions: dict[str, Item] = {}
    """ JsonDict storing all item and block definitions for the project. """

    external_definitions: dict[str, ExternalItem] = {}
    """ Secondary JsonDict for storing external items or blocks most likely for recipes. """

    manual: "Manual | None" = None
    """ The ingame_manual Manual handle, used to register pages/hooks during setup.
    Created lazily via stewbeet.get_manual(); reset after each build (for `beet watch`). """

