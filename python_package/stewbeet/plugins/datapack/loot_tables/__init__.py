""" 🎁 Sets up loot tables for the items of the definitions and external items. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, LootTable
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.ingredients import Ingr
from ....core.cls.item import Item
from ....core.cls.recipe import RecipeBase
from ....core.cls.resource import Resource
from ....core.constants import ITEMS_LOOT_FOLDER
from ....core.utils.io import write_function
from ....core.utils.loot_table import loot_function, loot_modifiers


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.datapack.loot_tables'")
def beet_default(ctx: Context):
	""" Main entry point for the loot tables plugin.
	This plugin sets up loot tables for items in the definitions and external items.

	Args:
		ctx: The beet context.
	"""
	# Get data from memory
	Mem.ctx = ctx
	assert ctx.meta["stewbeet"].get("source_lore", None) is not None, "Source lore is not set in the context metadata."
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# Creative loot table (sort of give all loot table)
	creative_loot_table: JsonDict = {"pools": []}
	not_skipped_items: list[str] = [item for item in Mem.definitions if not Item.from_id(item).skip_gives]
	for item in not_skipped_items:
		obj = Item.from_id(item)
		write_item_loot_table(obj)
		creative_loot_table["pools"].append({"rolls": 1, "entries":[{"type":"minecraft:loot_table","value":obj.loot_table}] })
	for item in not_skipped_items:
		write_count_loot_tables(item, Item.from_id(item))

	# Second loot table for the manual (if present), a namespaced alias rather than an item of its own
	if "manual" in not_skipped_items:
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:loot_table",
					"value": Item.from_id("manual").loot_table
				}]
			}]
		}
		Resource(LootTable, f"{ITEMS_LOOT_FOLDER}/{ns}_manual").write(LootTable(stp.json_dump(loot_table, max_level=10)))

	if creative_loot_table["pools"]:
		ctx.data[ns].loot_tables["creative_loot_table"] = LootTable(stp.json_dump(creative_loot_table, max_level=2))

	lore: str = stp.json_dump(ctx.meta["stewbeet"]["source_lore"], max_level=0).strip()
	write_function(f"{ns}:_give_all", "\n" + "\n\n".join(give_all_chests(not_skipped_items, lore)) + "\n\n")


def write_item_loot_table(obj: Item) -> None:
	""" Write the loot table giving one of an item, its base item with every component set, a `!` one removed. """
	set_components: JsonDict = loot_function("minecraft:set_components", components={})
	for k, v in obj.components.items():
		if k.startswith("!"):
			set_components["components"][f"!minecraft:{k[1:]}"] = {}
		else:
			set_components["components"][f"minecraft:{k}"] = v
	loot_table: JsonDict = {
		"pools": [{
			"rolls": 1,
			"entries": [{
				"type": "minecraft:item",
				"name": obj.base_item,
				**loot_modifiers([set_components]),
			}]
		}]
	}
	obj.loot_table.write(LootTable(stp.json_dump(loot_table, max_level = 10)))


def write_count_loot_tables(item: str, obj: Item) -> None:
	""" Write a loot table per count other than 1 that the item's own recipes give, wrapping its loot table. """
	own_recipes: list[RecipeBase] = [
		recipe for recipe in obj.recipes if not recipe.get("result") or Ingr(recipe["result"]).to_id(add_namespace=False) == item
	]
	results: list[int | JsonDict] = [recipe.get("result_count", 1) for recipe in own_recipes if recipe.get("result_count", 1) != 1]
	for result_count in results:
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:loot_table",
					"value": obj.loot_table,
					**loot_modifiers([loot_function("minecraft:set_count", count=result_count)])
				}]
			}]
		}
		obj.loot_table_for(result_count).write(LootTable(stp.json_dump(loot_table, max_level=10)))


def give_all_chests(items: list[str], lore: str) -> list[str]:
	""" The commands giving chests that hold every item, 27 per chest, each chest numbered and carrying the source lore. """
	chest_size: int = 27
	objects: list[Item] = [Item.from_id(item) for item in items]
	chunks: list[list[Item]] = [objects[i:i + chest_size] for i in range(0, len(objects), chest_size)]
	chests: list[str] = []
	for i, chunk in enumerate(chunks):
		joined_content: str = ",".join(
			f'{{slot:{j},item:{{count:1,id:"{obj.base_item}",components:{stp.json_dump(obj.components, max_level=0).strip()}}}}}'
			for j, obj in enumerate(chunk)
		)
		chests.append(
			f'give @s chest[container=[{joined_content}],'
			f'custom_name={{"text":"Chest [{i+1}/{len(chunks)}]","color":"yellow"}},lore=[{lore}]]'
		)
	return chests

