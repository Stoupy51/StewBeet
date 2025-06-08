
# ruff: noqa: RUF012
# pyright: reportAssignmentType=false
# Imports
from beet import Context
from beet.core.utils import JsonDict


# Shared variables among plugins
class Mem:
    ctx: Context = None
    """ Global context object that holds the beet project configuration.
    This is set during plugins.initialize and used throughout the codebase. """

    database: JsonDict = {}
    """ Main database that stores all item and block data for the project. """

    external_database: JsonDict = {}
    """ Secondary database for storing external dependencies and compatibility data. """

