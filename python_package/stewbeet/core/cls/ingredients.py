
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from typing import Any, cast

import stouputils as stp
from beet import LootTable, LootTableTag
from stouputils.typing import JsonDict

from ..__memory__ import Mem
from ..constants import EXTERNAL_RECIPES_FOLDER, ITEMS_LOOT_FOLDER
from ..utils.io import set_json_encoder
from ..utils.loot_table import loot_function, loot_modifiers, result_count_to_suffix
from ..utils.text_component import item_id_to_name
from ..utils.versions import minecraft_version_at_least
from .resource import Resource

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
ALL_RECIPES_TYPES: tuple[str, ...] = (
	*FURNACES_RECIPES_TYPES, *CRAFTING_RECIPES_TYPES, *OTHER_RECIPES_TYPES, *UNUSED_RECIPES_TYPES, *SPECIAL_RECIPES_TYPES
)

# Ingr class
class Ingr(dict[str, Any]):
	__slots__ = ()

	def __init__(self, id: str | JsonDict, ns: str | None = None, count: int | None = None, **kwargs: Any) -> None:
		""" Identity of an ingredient for custom crafts, from its id. Aliased as Ingredient() and IngrRepr().

		Args:
			ns:    The namespace of the ingredient, ex: iyc, the current project id by default and unused for a vanilla item.
			count: Only used for a result item, or by a special recipe type that supports counts.

		>>> Ingr("minecraft:stick")
		{'item': 'minecraft:stick'}
		>>> Ingr("adamantium_fragment", ns="iyc")
		{'components': {'minecraft:custom_data': {'iyc': {'adamantium_fragment': True}}}}
		>>> Ingr("adamantium_fragment", ns="iyc", count=3)
		{'components': {'minecraft:custom_data': {'iyc': {'adamantium_fragment': True}}}, 'count': 3}
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
				ns = Mem.ctx.project_id
			self["components"] = {"minecraft:custom_data":{ns:{id:True}}}
		if count is not None:
			self["count"] = count
		self.update(kwargs)

	def copy(self) -> Ingr:
		return Ingr(dict(self))

	@stp.simple_cache(method="str")
	def item_to_id(self) -> Ingr:
		""" Replace the "item" key by "id" in an item ingredient representation.

		>>> i = Ingr("minecraft:stick")
		>>> (i, i.item_to_id())
		({'item': 'minecraft:stick'}, {'id': 'minecraft:stick'})
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

	@stp.simple_cache(method="str")
	def to_id(self, add_namespace: bool = True) -> str:
		""" Get the id from an ingredient dict

		Args:
			add_namespace: Whether to add the namespace to the id
		Returns:
			str: The id of the ingredient, ex: "minecraft:stick" or "iyc:adamantium_ingot"
		"""
		for k in ("item", "id"):
			if self.get(k):
				if not add_namespace and ":" in self[k]:
					return self[k].split(":")[1]
				if add_namespace and ":" not in self[k]:
					return "minecraft:" + self[k]
				return self[k]

		custom_data: JsonDict = self["components"]["minecraft:custom_data"]
		namespace, id = self.custom_data_id(custom_data)
		if not namespace:
			stp.error(f"No namespace found in custom data: {custom_data}, ingredient: {self}")
		return namespace + ":" + id if add_namespace else id

	@staticmethod
	def custom_data_id(custom_data: JsonDict) -> tuple[str, str]:
		""" The namespace and id a custom item names itself by in its custom data, as `{namespace: {id: true}}`, or two empty strings.

		>>> Ingr.custom_data_id({"smithed": {"ignore": {}}, "iyc": {"adamantium_ingot": True}})
		('iyc', 'adamantium_ingot')
		"""
		return next((
			(cd_ns, next(iter(cast(JsonDict, cd_data))))
			for cd_ns, cd_data in custom_data.items()
			if isinstance(cd_data, dict) and cd_data and isinstance(next(iter(cast(JsonDict, cd_data).values())), bool)
		), ("", ""))

	def to_name(self) -> str:
		""" Get the name of the ingredient, ex: "Stick" or "Adamantium Ingot" """
		return item_id_to_name(self.to_id(add_namespace=True))

	@stp.simple_cache(method="str")
	def to_vanilla_item_id(self, add_namespace: bool = True) -> str:
		""" Get the id of the vanilla item from an ingredient dict

		Args:
			add_namespace: Whether to add the namespace to the id
		Returns:
			str: The id of the vanilla item, ex: "minecraft:stick"
		"""
		ns, ingr_id = self.to_id().split(":")
		from .item import Item

		if ns == Mem.ctx.project_id:
			if add_namespace:
				return Item.from_id(ingr_id).base_item
			return Item.from_id(ingr_id).base_item.split(":")[1]

		if ns == "minecraft":
			if add_namespace:
				return f"{ns}:{ingr_id}"
			return ingr_id

		item: str = f"{ns}:{ingr_id}"
		if Mem.external_definitions.get(item):
			if add_namespace:
				return Item.from_id(item).base_item
			return Item.from_id(item).base_item.split(":")[1]
		stp.error(f"External item '{item}' not found in the external definitions")
		return ""

	def to_item(self, id_key: str = "id") -> Ingr:
		""" Get the item data dict from an ingredient

		Args:
			id_key: The key to use for the item id, either "id" or "item" (default: "id")
		Returns:
			Ingr: The item data dict, ex: {"id": "minecraft:stick", "count": 1}
		"""
		ingr_id: str = self.to_id()
		ns, id = ingr_id.split(":")

		# Minecraft item
		if ns == "minecraft":
			return Ingr({id_key: id, "count": 1})

		# An item of the project, or one the external definitions describe
		from .item import Item
		if ns != Mem.ctx.project_id and not Mem.external_definitions.get(ingr_id):
			stp.error(f"External item '{ingr_id}' not found in the external definitions")
			return Ingr({})
		item_data = Item.from_id(id if ns == Mem.ctx.project_id else ingr_id)
		result = Ingr({id_key: item_data.base_item, "count": 1})
		components: JsonDict = {
			f"!minecraft:{k[1:]}" if k.startswith("!") else f"minecraft:{k}": {} if k.startswith("!") else v
			for k, v in item_data.components.items()
		}
		if components:
			result["components"] = components
		return result

	def to_predicate(self, **kwargs: Any) -> Ingr:
		""" Get the predicate representation of the ingredient (for functions)

		Args:
			kwargs: Key-value arguments to add to the ingredient representation (e.g. count=2, Slot=0, etc.)
				kwargs values take precedence over the ingredient's own fields.
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
			item.update(self)
		item.update(kwargs)
		return Ingr(item).item_to_id()

	@stp.simple_cache(method="str")
	def register_loot_table(self, result_count: int | JsonDict) -> Resource[LootTable]:
		""" Get the loot table for an ingredient dict, generating it when the item is external

		Args:
			result_count: The count of the result item, can be an int or a dict for random counts
				ex: 1
				ex: {"type": "minecraft:uniform","min": 4,"max": 6}
		Returns:
			Resource[LootTable]: The loot table, ex: "my_datapack:i/stick"
		"""
		# If item from this datapack
		item: str = self.to_id()
		if item.startswith(Mem.ctx.project_id):
			item = item.split(":")[1]
			return Resource(LootTable, f"{ITEMS_LOOT_FOLDER}/{item}{result_count_to_suffix(result_count)}")

		# Else, external item (minecraft or another datapack)
		namespace, item = item.split(":")
		loot_table: Resource[LootTable] = Resource(
			LootTable, f"{EXTERNAL_RECIPES_FOLDER}/{namespace}/{item}{result_count_to_suffix(result_count)}"
		)

		# If item from another datapack, generate the loot table
		if namespace != "minecraft":
			from .external_item import ExternalItem
			obj = ExternalItem.from_id(f"{namespace}:{item}")
			assert obj.loot_table is not None, \
				f"External item '{namespace}:{item}' has no loot table defined, please define one to use it in recipes."
			value: str = obj.loot_table

			# A tag resolves lazily, so an absent datapack leaves it empty instead of leaving the registry unbound
			if minecraft_version_at_least((26, 3)):
				tag: Resource[LootTableTag] = Resource(LootTableTag, f"{EXTERNAL_RECIPES_FOLDER}/{namespace}/{item}")
				tag.write(set_json_encoder(LootTableTag({"values": [{"id": obj.loot_table, "required": False}]}), max_level=2))
				value = f"#{tag}"

			file: JsonDict = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:loot_table","value": value}] }] }
		else:
			file: JsonDict = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":f"{namespace}:{item}"}] }] }

		# Add set_count function if needed
		if (isinstance(result_count, int) and result_count > 1) or hasattr(result_count, "get"):
			file["pools"][0]["entries"][0].update(loot_modifiers([loot_function("minecraft:set_count", count=result_count)]))

		loot_table.write(set_json_encoder(LootTable(file), max_level=9))
		return loot_table

	@staticmethod
	@stp.simple_cache(method="str")
	def get_ingredients_from_vanilla_recipe(recipe: JsonDict) -> list[str]:
		""" Get the ingredients from a vanilla recipe dict

		Args:
			recipe: The final recipe JSON dict, ex:

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
		if recipe.get("ingredients"):
			return recipe["ingredients"]
		if recipe.get("ingredient"):
			return [recipe["ingredient"]]
		if recipe.get("template"):
			return [recipe["template"]]
		return []

# Type aliases
IngrRepr = Ingredient = Ingr


__test__: dict[str, str] = {
	"Ingr.__init__": """
	>>> Ingr("diamond")
	{'components': {'minecraft:custom_data': {'your_namespace': {'diamond': True}}}}
	>>> print(Ingr("diamond"))
	{'components': {'minecraft:custom_data': {'your_namespace': {'diamond': True}}}}
	""",
}

