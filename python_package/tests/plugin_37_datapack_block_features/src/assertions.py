
# Imports
from beet import Context
from stouputils.typing import JsonList


# Main entry point
def beet_default(ctx: Context):
	ns: str = ctx.project_id

	def text(path: str) -> str:
		assert path in ctx.data.functions, f"Missing function {path}"
		return ctx.data.functions[path].text

	# The interaction is summoned with the block and gone with it, the item dropping unless a creative player broke it
	assert "summon interaction ~ ~-0.5 ~ {width:1.01f,height:1.01f" in text(f"{ns}:custom_blocks/bf_seat/place_secondary")
	destroy: str = text(f"{ns}:custom_blocks/bf_seat/destroy")
	assert f"execute unless score #no_drop {ns}.data matches 1 run loot spawn ~ ~ ~ loot {ns}:i/bf_seat" in destroy
	assert "kill @e[type=interaction" in destroy and "playsound minecraft:block.metal.break" in destroy
	assert "particle minecraft:item{item:" in destroy

	# Three hits within the timeout, and an iron pickaxe for the item
	hit: str = text(f"{ns}:custom_blocks/bf_seat/hit")
	assert "time query gametime" in hit and f"matches 20.. run scoreboard players set @s {ns}.hits 0" in hit
	assert f"if score @s {ns}.hits matches ..2 run return 0" in hit
	assert f"weapon.mainhand #{ns}:mining/pickaxe_iron" in hit
	assert "minecraft:iron_pickaxe" in ctx.data.item_tags[f"{ns}:mining/pickaxe_iron"].text
	assert "time query" not in text(f"{ns}:custom_blocks/bf_lamp/hit"), "A one hit block counts nothing"

	# Seats mount the user and are killed once empty
	seat: str = f"execute positioned ~ ~0.5 ~ summon item_display run function {ns}:custom_blocks/_interaction/seat"
	assert seat in text(f"{ns}:custom_blocks/bf_seat/sit")
	assert f"{ns}:custom_blocks/interaction_hit" in ctx.data.advancements
	assert f"{ns}:custom_blocks/_interaction/unseat" in text(f"{ns}:v1.0.0/second")

	# A block with a mining level and no host gets the default host of that level
	assert "setblock ~ ~ ~ minecraft:diamond_block" in text(f"{ns}:custom_blocks/bf_storage/place_main")

	# Halves from where the player clicks, stairs facing the way the player looks
	slab: str = text(f"{ns}:custom_blocks/bf_slab/place_main")
	assert f"summon marker run function {ns}:custom_blocks/_aim/main" in slab
	assert f"if score #upper {ns}.data matches 1 run setblock ~ ~ ~ minecraft:oak_slab[type=top]" in slab
	stairs: str = text(f"{ns}:custom_blocks/bf_stairs/place_main")
	assert f"matches 1 if score #upper {ns}.data matches 0 run setblock ~ ~ ~ minecraft:oak_stairs[half=bottom,facing=south]" in stairs

	# Baked uvlock: turned copies of the model instead of a turned display
	stairs_display: str = text(f"{ns}:custom_blocks/bf_stairs/place_secondary")
	assert f'set value "{ns}:bf_stairs_y90"' in stairs_display and "Rotation[0]" not in stairs_display
	assert ctx.assets.models[f"{ns}:item/bf_stairs_y90"].data["parent"] == f"{ns}:item/bf_stairs"

	# Each element grown by the margin, 1.002 by default, and a flipped copy of the model for the upper half
	assert [round(v, 4) for v in ctx.assets.models[f"{ns}:item/bf_slab"].data["elements"][0]["from"]] == [-0.016, -0.016, -0.016]
	assert f"{ns}:item/bf_slab_up" in ctx.assets.models
	assert f'set value "{ns}:bf_slab_up"' in text(f"{ns}:custom_blocks/bf_slab/place_secondary")

	# Stairs showing the corner their host makes with its neighbours, the upper outer corner turned west keeping the shared quarter
	follow: str = text(f"{ns}:custom_blocks/bf_stairs/follow_host")
	assert 'oak_stairs[shape=inner_left] unless items entity @s contents *[custom_model_data={strings:["shape=inner_left"]}]' in follow
	assert f"function {ns}:custom_blocks/bf_stairs/follow_host" in text(f"{ns}:custom_blocks/bf_stairs/second")
	corner: JsonList = ctx.assets.models[f"{ns}:item/bf_stairs_outer_right_y90_up"].data["elements"]
	outer: list[list[float]] = [[round(v) for v in element["from"] + element["to"]] for element in corner]
	assert outer == [[0, 8, 0, 16, 16, 16], [0, 0, 0, 8, 8, 8]], outer
	turned_stairs: str = ctx.assets.item_models[f"{ns}:bf_stairs_y90_up"].text
	assert '"when": "shape=outer_right"' in turned_stairs and f"{ns}:item/bf_stairs_outer_right_y90_up" in turned_stairs

	# A furnace cooking twice as fast, its display shown lit while the host burns, and no flipped copy without a half
	assert f"scoreboard players add #spent {ns}.data 1" in text(f"{ns}:custom_blocks/bf_furnace/tick")
	assert "if block ~ ~ ~ minecraft:furnace[lit=true]" in text(f"{ns}:custom_blocks/bf_furnace/follow_host")
	assert '"when": "lit=true"' in ctx.assets.item_models[f"{ns}:bf_furnace"].text
	assert f"{ns}:item/bf_furnace_up" not in ctx.assets.models

	# A loot table drop with experience, vanishing with a weak tool
	replace_item: str = text(f"{ns}:custom_blocks/bf_ore/replace_item")
	assert f"loot spawn ~ ~ ~ loot {ns}:custom_blocks/no_silk_touch_drop/bf_ore" in replace_item
	assert "random value 2..4" in replace_item
	assert replace_item.index("run return run kill @s") < replace_item.index("If silk touch applied")

	# The drink carries its mug as use remainder
	drink: str = ctx.data.loot_tables[f"{ns}:i/bf_drink"].text
	assert '"minecraft:use_remainder"' in drink and f'"minecraft:item_model": "{ns}:bf_mug"' in drink

	# The crossbow: its enchantment, bolts only, and a crossbow model
	enchantment: str = ctx.data.enchantments[f"{ns}:ranged_weapon/bf_crossbow"].text
	assert '"minecraft:crossbow_charge_time"' in enchantment and '"factor": 1.5' in enchantment
	assert f"{ns}:ranged_weapon/bf_crossbow" in ctx.data.enchantment_tags["minecraft:curse"].text
	unload: str = f"{ns}.bf_bolt run function {ns}:ranged_weapon/bf_crossbow/unload_mainhand"
	assert unload in text(f"{ns}:ranged_weapon/bf_crossbow/loaded")
	crossbow: str = ctx.assets.item_models[f"{ns}:bf_crossbow"].text
	assert '"minecraft:crossbow/pull"' in crossbow and '"minecraft:charge_type"' in crossbow

