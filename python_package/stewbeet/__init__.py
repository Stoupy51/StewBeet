
# ruff: noqa: F401
# Imports
from beet import *

from .__main__ import main
from .core import *
from .plugins.initialize.source_lore_font import find_pack_png
from .plugins.resource_pack.item_models.object import AutoModel
from .plugins.resource_pack.sounds import add_sound


def beet_default(ctx: Context):
    """ Initializes the StewBeet package. """
    ctx.require("stewbeet.plugins.initialize")

