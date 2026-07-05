"""Shared wiki-button hover line builders (ported from v1 ``append_ingredient_hover``).

The base :meth:`~.registry.CraftRenderer.append_hover` covers the single-ingredient case; these
helpers cover the grid (shaped/forge), smithing and mining shapes that several renderers share.
"""

# Imports
import stouputils as stp
from beet.core.utils import TextComponent

from ....core.cls.ingredients import Ingr


def ingredients_hover(craft: stp.JsonDict, hover: list[TextComponent]) -> None:
	""" Count + list ingredients for grid crafts (shaped dict via shape, or shapeless/forge list). """
	if stp.is_generic_instance(craft["ingredients"], stp.JsonDict):
		for k, v in craft["ingredients"].items():
			count = sum([line.count(k) for line in craft["shape"]])
			hover.append({"text": f"\n- x{count} ", "color": "gray"})
			hover.append({"text": Ingr(v).to_name(), "color": "gray"})
	elif stp.is_generic_instance(craft["ingredients"], list[stp.JsonDict]):
		ids: dict[str, int] = {}
		for ingr in craft["ingredients"]:
			id = Ingr(ingr).to_name()
			ids[id] = ids.get(id, 0) + ingr.get("count", 1)
		for id, count in ids.items():
			hover.append({"text": f"\n- x{count} ", "color": "gray"})
			hover.append({"text": id, "color": "gray"})


def smithing_hover(craft: stp.JsonDict, hover: list[TextComponent]) -> None:
	""" Base / Template / Addition / Pattern lines for smithing crafts. """
	if craft.get("base"):
		hover.append({"text": "\n- Base: ", "color": "gray"})
		hover.append({"text": Ingr(craft["base"]).to_name(), "color": "gray"})
	if craft.get("template"):
		hover.append({"text": "\n- Template: ", "color": "gray"})
		hover.append({"text": Ingr(craft["template"]).to_name(), "color": "gray"})
	if craft.get("addition"):
		hover.append({"text": "\n- Addition: ", "color": "gray"})
		hover.append({"text": Ingr(craft["addition"]).to_name(), "color": "gray"})
	if craft.get("pattern"):
		pattern_name = str(craft["pattern"]).replace("minecraft:", "").replace("_", " ").title()
		hover.append({"text": "\n- Pattern: ", "color": "gray"})
		hover.append({"text": pattern_name, "color": "gray"})


def mining_hover(craft: stp.JsonDict, hover: list[TextComponent]) -> None:
	""" Mine / Drops / Silk-touch lines for mining pseudo-recipes. """
	ore_name = Ingr(craft["ingredient"]).to_name()
	hover.append({"text": "\n- Mine: ", "color": "gray"})
	hover.append({"text": ore_name, "color": "gray"})
	if craft.get("dynamic_drop", False):
		hover.append({"text": "\n- Drops: variable (loot table)", "color": "gray"})
		hover.append({"text": f"\n- Silk touch drop: {ore_name}", "color": "gray"})
	else:
		result_name = Ingr(craft["result"]).to_name()
		result_count = craft.get("result_count", "1")
		hover.append({"text": f"\n- Drops: x{result_count} ", "color": "gray"})
		hover.append({"text": result_name, "color": "gray"})

