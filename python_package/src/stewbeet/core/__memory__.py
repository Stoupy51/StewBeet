
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

    definitions: JsonDict = {}
    """ JsonDict storing all item and block definitions for the project. """

    external_definitions: JsonDict = {}
    """ Secondary JsonDict for storing external items or blocks most likely for recipes. """

