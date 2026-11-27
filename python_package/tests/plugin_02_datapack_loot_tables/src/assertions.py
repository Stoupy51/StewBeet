
# Assertions for: stewbeet.plugins.datapack.loot_tables

# Imports
from beet import Context
from stouputils.typing import JsonDict

from stewbeet.plugins.datapack.loot_tables import CreativeTab


# Main entry point
def beet_default(ctx: Context):
	ns: str = ctx.project_id

	# Per-item loot tables
	assert f"{ns}:i/obtainable" in ctx.data.loot_tables, \
		"obtainable must have a loot table"
	assert f"{ns}:i/hidden" not in ctx.data.loot_tables, \
		"hidden (skip_gives=True) must NOT have a loot table"
	assert f"{ns}:i/bulk_item" in ctx.data.loot_tables, \
		"bulk_item must have a loot table"

	# Count-variant loot table (x4 recipe)
	assert f"{ns}:i/bulk_item_x4" in ctx.data.loot_tables, \
		"bulk_item with result_count=4 must generate an _x4 loot table variant"

	# Unjank creative tab
	assert f"{ns}:creative_loot_table" not in ctx.data.loot_tables, \
		"creative_loot_table must not be generated"
	creative_tab: JsonDict = ctx.data[CreativeTab][f"{ns}:{ns}"].data
	assert creative_tab["icon"]["id"] == "minecraft:diamond", \
		"the creative tab icon must be the first item"
	assert creative_tab["items"] == [{"type": "unjank:loot", "loot": [f"{ns}:i/obtainable", f"{ns}:i/bulk_item"]}], \
		"the creative tab must list every item but the hidden one, in definition order"

	# _give_all function
	assert f"{ns}:_give_all" in ctx.data.functions, \
		"_give_all function must be generated"
	give_all_text: str = ctx.data.functions[f"{ns}:_give_all"].text
	# The function packs all non-hidden items into chests via 'give @s chest[...]'
	assert "give @s chest" in give_all_text, \
		"_give_all must use 'give @s chest' to distribute items"
	assert "obtainable" in give_all_text, \
		"_give_all must include obtainable"
	assert "bulk_item" in give_all_text, \
		"_give_all must include bulk_item"
	assert "hidden" not in give_all_text, \
		"_give_all must exclude hidden (skip_gives=True)"

	# Loot table content correctness
	obtainable_text: str = ctx.data.loot_tables[f"{ns}:i/obtainable"].text
	assert "minecraft:diamond" in obtainable_text, \
		"obtainable loot table must reference the base item"
	assert "set_components" in obtainable_text, \
		"obtainable loot table must use set_components loot function"

