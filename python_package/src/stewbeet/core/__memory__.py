
# pyright: reportAssignmentType=false
# Imports
from typing import Any

from beet import Context
from box import Box


# Shared variables among plugins
class Mem:
    ctx: Context = None
    """ Global context object that holds the beet project configuration.
    This is set during plugins.initialize and used throughout the codebase. """

    database: Box[str, Any] = Box({}, default_box=True, default_box_attr={})
    """ Main database that stores all item and block data for the project.
    Uses Box object for dynamic attribute access and automatic dictionary creation. """

    external_database: Box[str, Any] = Box({}, default_box=True, default_box_attr={})
    """ Secondary database for storing external dependencies and compatibility data.
    Uses Box for dynamic attribute access and automatic dictionary creation. """

