"""Special, non-item pages built on the public API.

- ``register_heavy_workbench`` registers a temporary ``heavy_workbench`` :class:`Block`
  (when the smithed.crafter lib is used) so it flows through the normal item-page pipeline;
  the manual then moves its page to position 2 via ``Manual.move_page`` (no page bumping).
- ``build_stardust_forge_page`` returns the ported Awakened Forge page content, inserted as
  a :class:`~.pages.raw_page.RawPage` via ``Manual.insert_page``.
"""

# ruff: noqa: E501
# Imports
from __future__ import annotations

from beet import Texture
from beet.core.utils import TextComponent

from ...core.__memory__ import Mem
from ...core.cls.block import Block, VanillaBlock
from ...core.cls.ingredients import Ingr
from ...core.cls.recipe import CraftingShapedRecipe
from ...dependencies.official_libs import OFFICIAL_LIBS
from ..resource_pack.item_models.object import AutoModel
from .glyphs import AWAKENED_FORGE_STRUCT_FONT, HEAVY_WORKBENCH_CATEGORY, VERY_SMALL_NONE_FONT
from .paths import TEMPLATES_PATH


def register_heavy_workbench() -> None:
	""" Register the temporary heavy_workbench block/model if smithed.crafter is used. """
	if not OFFICIAL_LIBS["smithed.crafter"]["is_used"]:
		return
	ns = Mem.ctx.project_id
	Mem.ctx.assets[ns].textures["item/heavy_workbench"] = Texture(source_path=f"{TEMPLATES_PATH}/heavy_workbench.png")
	obj = Block(
		id="heavy_workbench",
		vanilla_block=VanillaBlock(id=""),
		manual_category=HEAVY_WORKBENCH_CATEGORY,
		override_model={
			"parent": "minecraft:block/cube",
			"texture_size": [64, 32],
			"textures": {"0": f"{ns}:item/heavy_workbench"},
			"elements": [{"from": [0, 0, 0], "to": [16, 16, 16], "faces": {"north": {"uv": [4, 8, 8, 16], "texture": "#0"}, "east": {"uv": [0, 8, 4, 16], "texture": "#0"}, "south": {"uv": [12, 8, 16, 16], "texture": "#0"}, "west": {"uv": [8, 8, 12, 16], "texture": "#0"}, "up": {"uv": [4, 0, 8, 8], "texture": "#0"}, "down": {"uv": [8, 0, 12, 8], "texture": "#0"}}}],
			"display": {"thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]}, "thirdperson_lefthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]}, "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.4, 0.4, 0.4]}, "firstperson_lefthand": {"rotation": [0, 225, 0], "scale": [0.4, 0.4, 0.4]}, "ground": {"translation": [0, 3, 0], "scale": [0.25, 0.25, 0.25]}, "gui": {"rotation": [30, 225, 0], "scale": [0.625, 0.625, 0.625]}, "head": {"translation": [0, -30.43, 0], "scale": [1.601, 1.601, 1.601]}, "fixed": {"scale": [0.5, 0.5, 0.5]}},
		},
		recipes=[
			CraftingShapedRecipe(shape=["###", "#C#", "SSS"], ingredients={"#": Ingr("minecraft:oak_log"), "C": Ingr("minecraft:crafting_table"), "S": Ingr("minecraft:smooth_stone")})
		],
		components={"item_name": "Heavy Workbench", "item_model": f"{ns}:heavy_workbench"},
	)
	AutoModel.from_definitions(obj, {}, ignore_textures=True).process()


def build_stardust_forge_page() -> list[TextComponent]:
	""" Awakened Forge dialog body (the "Awakened Forge" title is the RawPage's title).

	The first element is the parent: its open_url click + hover cascade to the whole page, and
	``shadow_color`` disables text shadows (dialog look).
	"""
	ns: str = Mem.ctx.project_id
	return [
		{
			"text": "",
			"click_event": {"action": "open_url", "url": "https://github.com/Stoupy51/StardustFragment/blob/main/assets/public/awakened_forge.jpg"},
			"hover_event": {"action": "show_text", "value": {"text": "Click to view the full image"}},
			"shadow_color": [0,0,0,0],
		},
		{"text": "The Awakened Forge is a powerful crafting station that allows players to craft ", "font": "minecraft:default", "color": "black"},
		{"text": "end-game", "font": "minecraft:default", "color": "red", "underlined": True},
		{"text": " items in Stardust Fragment.", "font": "minecraft:default", "color": "black"},
		"\n\n",
		{"text": AWAKENED_FORGE_STRUCT_FONT[0] + VERY_SMALL_NONE_FONT + AWAKENED_FORGE_STRUCT_FONT[1], "font": f"{ns}:manual"},
	]
