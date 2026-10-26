""" Assertions for: stewbeet.core.utils.fonts.item_images

A missing texture renders transparent, so a trim layer that failed to resolve leaves both chestplate renders identical.
"""
# Imports
from beet import Context
from PIL import Image

from stewbeet import Mem, ensure_item_images


# Main entry point
def beet_default(ctx: Context):
	Mem.ctx = ctx
	images: dict[str, str] = ensure_item_images(["plain_chestplate", "trimmed_chestplate", "animated_block"], cache_assets=False)
	assert set(images) == {"tir:plain_chestplate", "tir:trimmed_chestplate", "tir:animated_block"}, images

	plain: Image.Image = Image.open(images["tir:plain_chestplate"]).convert("RGBA")
	trimmed: Image.Image = Image.open(images["tir:trimmed_chestplate"]).convert("RGBA")
	assert plain.getbbox() is not None, "the plain chestplate rendered fully transparent"
	assert plain.tobytes() != trimmed.tobytes(), "the quartz trim layer is missing from the render"

	# An animated texture is rendered on its first frame only, into the same single file
	assert Image.open(images["tir:animated_block"]).getbbox() is not None, "the animated block rendered fully transparent"

