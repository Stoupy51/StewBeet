
# Imports
from __future__ import annotations

from typing import Any, cast

import stouputils as stp
from beet import LootTable
from beet.core.utils import JsonDict

from ..__memory__ import Mem
from ..utils.io import set_json_encoder
from ..utils.loot_table import result_count_to_suffix
from ..utils.text_component import item_id_to_name

# Recipes constants
FURNACES_RECIPES_TYPES: tuple[str, ...] = ("smelting", "blasting", "smoking", "campfire_cooking")
CRAFTING_RECIPES_TYPES: tuple[str, ...] = ("crafting_shaped", "crafting_shapeless")
OTHER_RECIPES_TYPES: tuple[str, ...] = ("smithing_transform", "smithing_trim", "stonecutting")
UNUSED_RECIPES_TYPES: tuple[str, ...] = (
	"crafting_decorated_pot", "crafting_special_armordye", "crafting_special_bannerduplicate",
	"crafting_special_bookcloning", "crafting_special_firework_rocket", "crafting_special_firework_star",
	"crafting_special_firework_star_fade", "crafting_special_mapcloning", "crafting_special_mapextending",
	"crafting_special_repairitem", "crafting_special_shielddecoration", "crafting_special_tippedarrow",
	"crafting_transmute",
)
SPECIAL_RECIPES_TYPES: tuple[str, ...] = ("simplenergy_pulverizing", "stardust_awakened_forge")
ALL_RECIPES_TYPES: tuple[str, ...] = (*FURNACES_RECIPES_TYPES, *CRAFTING_RECIPES_TYPES, *OTHER_RECIPES_TYPES, *UNUSED_RECIPES_TYPES, *SPECIAL_RECIPES_TYPES)

# Ingr class
class Ingr(JsonDict):

	def __init__(self, id: str | JsonDict, ns: str | None = None, count: int | None = None, **kwargs: Any) -> None:
		""" Get the identity of the ingredient from its id for custom crafts

		Aliases: Ingredient(), IngrRepr()

		Args:
			id		(str):		The id of the ingredient, ex: adamantium_fragment
			ns		(str|None):	The namespace of the ingredient (optional if 'id' argument is a vanilla item), ex: iyc (default: current project id)
			count	(int|None):	The count of the ingredient (optional, used only when this ingredient format is a result item) (or use a special type of recipe that supports counts)
		Returns:
			str: The identity of the ingredient for custom crafts,
				ex: {"components":{"minecraft:custom_data":{"iyc":{"adamantium_fragment":True}}}}
				ex: {"item": "minecraft:stick"}
		Examples:
			>>> Ingr("minecraft:stick")
			{'item': 'minecraft:stick'}
			>>> Ingr("adamantium_fragment", ns="iyc")
			{'components': {'minecraft:custom_data': {'iyc': {'adamantium_fragment': True}}}}
			>>> Ingr("adamantium_fragment", ns="iyc", count=3)
			{'components': {'minecraft:custom_data': {'iyc': {'adamantium_fragment': True}}}, 'count': 3}
			>>> Ingr("diamond")
			{'components': {'minecraft:custom_data': {'detected_namespace': {'diamond': True}}}}
			>>> print(Ingr("diamond"))
			{'components': {'minecraft:custom_data': {'detected_namespace': {'diamond': True}}}}
		"""
		# Copy from another dict
		if isinstance(id, dict):
			self.update(id)
			return

		# Create from id, ns, count
		if ":" in id:
			self["item"] = id
		else:
			if ns is None:
				ns = Mem.ctx.project_id if Mem.ctx else "detected_namespace"
			self["components"] = {"minecraft:custom_data":{ns:{id:True}}}
		if count is not None:
			self["count"] = count
		self.update(kwargs)

	def copy(self) -> Ingr:
		return Ingr(dict(self))

	@stp.simple_cache
	def item_to_id(self) -> Ingr:
		""" Replace the "item" key by "id" in an item ingredient representation

		Args:
			ingr (dict): The item ingredient, ex: {"item": "minecraft:stick"}
		Returns:
			Ingr: The item ingredient representation, ex: {"id": "minecraft:stick"}

		>>> i = Ingr("minecraft:stick")
		>>> (i, i.item_to_id())
		({'item': 'minecraft:stick'}, {'id': 'minecraft:stick'})

		>>> i["Slot"] = 0

		>>> j = Ingr("adamantium_fragment", ns="iyc")
		>>> j == j.item_to_id()
		True
		"""
		if self.get("item") is None:
			return self
		if "Slot" in self:
			r: JsonDict = {"Slot": self["Slot"], "id": self["item"]}
		else:
			r: JsonDict = {"id": self["item"]}
		r.update(self)
		r.pop("item")
		return Ingr(r)

	@stp.simple_cache
	def to_id(self, add_namespace: bool = True) -> str:
		""" Get the id from an ingredient dict

		Args:
			add_namespace (bool): Whether to add the namespace to the id
		Returns:
			str: The id of the ingredient, ex: "minecraft:stick" or "iyc:adamantium_ingot"
		"""
		for k in ("item", "id"):
			if self.get(k):
				if not add_namespace and ":" in self[k]:
					return self[k].split(":")[1]
				elif add_namespace and ":" not in self[k]:
					return "minecraft:" + self[k]
				return self[k]

		custom_data: JsonDict = self["components"]["minecraft:custom_data"]
		namespace: str = ""
		id: str = ""
		for cd_ns, cd_data in custom_data.items():
			if isinstance(cd_data, dict) and cd_data:
				cd_data = cast(JsonDict, cd_data)
				first_value = next(iter(cd_data.values()))
				if isinstance(first_value, bool):
					namespace = cd_ns
					id = next(iter(cd_data.keys()))
					break
		if not namespace:
			stp.error(f"No namespace found in custom data: {custom_data}, ingredient: {self}")
		if add_namespace:
			return namespace + ":" + id
		return id

	@stp.simple_cache
	def to_name(self) -> str:
		""" Get the name of the ingredient, ex: "Stick" or "Adamantium Ingot" """
		return item_id_to_name(self.to_id(add_namespace=True))

	@stp.simple_cache
	def to_vanilla_item_id(self, add_namespace: bool = True) -> str:
		""" Get the id of the vanilla item from an ingredient dict

		Args:
			add_namespace (bool): Whether to add the namespace to the id
		Returns:
			str: The id of the vanilla item, ex: "minecraft:stick"
		"""
		ns, ingr_id = self.to_id().split(":")
		from .item import Item
		if ns == Mem.ctx.project_id:
			if add_namespace:
				return Item.from_id(ingr_id).base_item
			return Item.from_id(ingr_id).base_item.split(":")[1]
		elif ns == "minecraft":
			if add_namespace:
				return f"{ns}:{ingr_id}"
			return ingr_id
		else:
			item: str = f"{ns}:{ingr_id}"
			if Mem.external_definitions.get(item):
				if add_namespace:
					return Item.from_id(item).base_item
				return Item.from_id(item).base_item.split(":")[1]
			else:
				stp.error(f"External item '{item}' not found in the external definitions")
		return ""

	def to_item(self, id_key: str = "id") -> Ingr:
		""" Get the item data dict from an ingredient

		Args:
			id_key (str): The key to use for the item id, either "id" or "item" (default: "id")
		Returns:
			Ingr: The item data dict, ex: {"id": "minecraft:stick", "count": 1}
		"""
		ingr_id: str = self.to_id()
		ns, id = ingr_id.split(":")

		# Minecraft item
		if ns == "minecraft":
			return Ingr({id_key: id, "count": 1})

		# Get from internal definitions
		from .item import Item
		if ns == Mem.ctx.project_id:
			item_data = Item.from_id(id)
			result = Ingr({id_key: item_data.base_item, "count": 1})

			# Add components
			for k, v in item_data.components.items():
				if result.get("components") is None:
					result["components"] = {}
				if k.startswith("!"):
					result["components"][f"!minecraft:{k[1:]}"] = {}
				else:
					result["components"][f"minecraft:{k}"] = v
			return result

		# External definitions
		if Mem.external_definitions.get(ingr_id):
			item_data = Item.from_id(ingr_id)
			result = Ingr({id_key: item_data.base_item, "count": 1})

			# Add components
			for k, v in item_data.components.items():
				if result.get("components") is None:
					result["components"] = {}
				if k.startswith("!"):
					result["components"][f"!minecraft:{k[1:]}"] = {}
				else:
					result["components"][f"minecraft:{k}"] = v
			return result

		stp.error(f"External item '{ingr_id}' not found in the external definitions")
		return Ingr({})

	def to_predicate(self, **kwargs: Any) -> Ingr:
		""" Get the predicate representation of the ingredient (for functions)

		The 'count' field of the ingredient is intentionally excluded from the predicate,
		since it represents a result item count (not a recipe matching count).
		Use the 'count' kwarg to specify the recipe matching count explicitly.

		Args:
			kwargs: Key-value arguments to add to the ingredient representation (e.g. count=2, Slot=0, etc.)
		Returns:
			Ingr: The predicate representation of the ingredient, ex:
				{"count": 2, "components": {"minecraft:custom_data": {"iyc": {"adamantium_fragment": True}}}}
		"""
		item: JsonDict = {}
		ns_id: str = self.to_id()
		if ns_id in Mem.external_definitions:
			from .external_item import ExternalItem
			item.update({"components": {"minecraft:custom_data": ExternalItem.from_id(ns_id).custom_data_predicate}})
		else:
			item.update({k: v for k, v in self.items() if k != "count"})
		item.update(kwargs)
		return Ingr(item).item_to_id()

	@stp.simple_cache
	def register_loot_table(self, result_count: int | JsonDict) -> str:
		""" Get the loot table for an ingredient dict

		Args:
			result_count (int|dict): The count of the result item, can be an int or a dict for random counts
				ex: 1
				ex: {"type": "minecraft:uniform","min": 4,"max": 6}
		Returns:
			str: The loot table path, ex: "my_datapack:i/stick"
		"""
		# If item from this datapack
		item: str = self.to_id()
		if item.startswith(Mem.ctx.project_id):
			item = item.split(":")[1]
			loot_table = f"{Mem.ctx.project_id}:i/{item}{result_count_to_suffix(result_count)}"
			return loot_table

		# Else, external item (minecraft or another datapack)
		namespace, item = item.split(":")
		loot_table = f"{Mem.ctx.project_id}:recipes/{namespace}/{item}{result_count_to_suffix(result_count)}"

		# If item from another datapack, generate the loot table
		if namespace != "minecraft":
			from .external_item import ExternalItem
			obj = ExternalItem.from_id(f"{namespace}:{item}")
			assert obj.loot_table is not None, f"External item '{namespace}:{item}' has no loot table defined, please define one to use it in recipes."
			file: JsonDict = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:loot_table","value": obj.loot_table}] }] }
		else:
			file: JsonDict = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":f"{namespace}:{item}"}] }] }

		# Add set_count function if needed
		if (isinstance(result_count, int) and result_count > 1) or hasattr(result_count, "get"):
			file["pools"][0]["entries"][0]["functions"] = [{"function": "minecraft:set_count","count": result_count}]

		Mem.ctx.data[loot_table] = set_json_encoder(LootTable(file), max_level=9)
		return loot_table

	@staticmethod
	@stp.simple_cache
	def get_ingredients_from_vanilla_recipe(recipe: JsonDict) -> list[str]:
		""" Get the ingredients from a vanilla recipe dict

		Args:
			recipe (dict): The final recipe JSON dict, ex:

			{
				"type": "minecraft:crafting_shaped",
				"pattern": [...],
				"key": {...},
				"result": {...}
			}
		Returns:
			list[str]: The ingredients ids
		"""
		if recipe.get("key"):
			return list(recipe["key"].values())
		elif recipe.get("ingredients"):
			return recipe["ingredients"]
		elif recipe.get("ingredient"):
			return [recipe["ingredient"]]
		elif recipe.get("template"):
			return [recipe["template"]]
		else:
			return []

# Type aliases
IngrRepr = Ingredient = Ingr

