
# pyright: reportAssignmentType=false
# Imports
from typing import Any

from beet import Context, ListOption
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


# Utility function for assertions on ctx
def assert_ctx(members: ListOption) -> None:
    """ Assert that required context metadata paths exist.

    Args:
        members (ListOption): List of paths to check in ctx.
    """
    for path in members:
        if path == "meta.stewbeet.sounds_folder":
            assert Mem.ctx.meta.stewbeet.sounds_folder, "Sounds folder not found in context metadata, please fill meta.stewbeet.sounds_folder with a directory path."
        elif path == "meta.stewbeet.records_folder":
            assert Mem.ctx.meta.stewbeet.records_folder, "Records folder not found in context metadata, please fill meta.stewbeet.records_folder with a directory path."
        elif path == "meta.stewbeet.textures_folder":
            assert Mem.ctx.meta.stewbeet.textures_folder, "Textures folder not found in context metadata, please fill meta.stewbeet.textures_folder with a directory path."

