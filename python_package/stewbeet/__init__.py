
# type: ignore
# ruff: noqa: F401
# Imports
from beet import *

from .cli import main
from .core import *
from .plugins.initialize.source_lore_font import find_pack_png
from .plugins.resource_pack.item_models.object import AutoModel
from .plugins.resource_pack.sounds import add_sound


def beet_default(ctx: Context) -> Generator[None, None, None]:
	""" Initializes the StewBeet package. """
	from .plugins.initialize.__init__ import beet_default
	return beet_default(ctx)

