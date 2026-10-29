""" Assertions for: stewbeet.core.utils.fonts.item_images

A missing texture renders transparent, so a trim layer that failed to resolve leaves both chestplate renders identical.
"""
# Imports
from beet import Context
from PIL import Image

from stewbeet import Item, Mem, ensure_item_images


# Main entry point
def beet_default(ctx: Context):
	Mem.ctx = ctx
	models: list[str] = ["plain_chestplate", "trimmed_chestplate", "animated_block", "corner_marker"]
	images: dict[str, str] = ensure_item_images(models, cache_assets=False)
	assert set(images) == {f"tir:{model}" for model in models}, images

	plain: Image.Image = Image.open(images["tir:plain_chestplate"]).convert("RGBA")
	corner: bytes = Image.open(images["tir:corner_marker"]).convert("RGBA").tobytes()
	trimmed: Image.Image = Image.open(images["tir:trimmed_chestplate"]).convert("RGBA")
	assert plain.getbbox() is not None, "the plain chestplate rendered fully transparent"
	assert plain.tobytes() != trimmed.tobytes(), "the quartz trim layer is missing from the render"

	# An animated texture is rendered on its first frame only, into the same single file
	assert Image.open(images["tir:animated_block"]).getbbox() is not None, "the animated block rendered fully transparent"

	# A user-set item model renders through its items/ definition, whose condition reads the item components
	dyed_model: str = "tir:dyed_composite_chestplate"
	Item(id="dyed", base_item="minecraft:iron_chestplate", components={"item_model": dyed_model, "dyed_color": 0xFFFFFF})
	Item(id="undyed", base_item="minecraft:iron_chestplate", components={"item_model": dyed_model})
	Item(id="vanilla_look", components={"item_model": "minecraft:diamond"})
	Item(id="missing_look", components={"item_model": "tir:does_not_exist"})
	images = ensure_item_images(["dyed", "undyed", "vanilla_look", "missing_look"], cache_assets=False)
	assert set(images) == {"tir:dyed", "tir:undyed", "tir:vanilla_look"}, images

	dyed: Image.Image = Image.open(images["tir:dyed"]).convert("RGBA")
	undyed: Image.Image = Image.open(images["tir:undyed"]).convert("RGBA")
	assert undyed.tobytes() == plain.tobytes(), "the condition did not fall back to the plain chestplate"
	assert dyed.tobytes() not in (plain.tobytes(), corner), "the composite did not draw both of its models"
	assert Image.open(images["tir:vanilla_look"]).getbbox() is not None, "the vanilla item model rendered fully transparent"

