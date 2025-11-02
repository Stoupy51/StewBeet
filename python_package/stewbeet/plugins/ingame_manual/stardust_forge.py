
# Imports

from beet.core.utils import TextComponent

from ...core.__memory__ import Mem
from .shared_import import (
	AWAKENED_FORGE_STRUCT_FONT,
	VERY_SMALL_NONE_FONT,
)


def get_stardust_forge_page() -> list[TextComponent]:
	""" Generate the Stardust Forge manual page content. """
	ns: str = Mem.ctx.project_id
	return [
		"",
		"Awakened Forge",
		[
			{
				"text":"",
				"click_event":{"action":"open_url","url":"https://github.com/Stoupy51/StardustFragment/blob/main/assets/public/awakened_forge.jpg"},
				"hover_event":{"action":"show_text","value":{"text":"Click to view the full image"}}
			},
			{"text":"The Awakened Forge is a powerful crafting station that allows players to craft ","font":"minecraft:default","color":"black"},
			{"text":"end-game","font":"minecraft:default","color":"red","underlined":True},
			{"text":" items in Stardust Fragment.","font":"minecraft:default","color":"black"},
			"\n\n",
			{"text": AWAKENED_FORGE_STRUCT_FONT[0] + VERY_SMALL_NONE_FONT + AWAKENED_FORGE_STRUCT_FONT[1], "font": f"{ns}:manual"},
		]
	]

