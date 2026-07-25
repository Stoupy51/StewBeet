
# type: ignore
# ruff: noqa: F401
# Imports
from typing import Any

from beet import *

from .cli import main
from .core import *
from .plugins.ingame_manual.api import *
from .plugins.initialize.project_images import find_pack_png
from .plugins.resource_pack.item_models.object import AutoModel
from .plugins.resource_pack.sounds import add_sound


def beet_default(ctx: Context) -> Any:
	""" Initializes the StewBeet package. """
	from .plugins.initialize.__init__ import beet_default as initialize_beet_default
	return initialize_beet_default(ctx)

