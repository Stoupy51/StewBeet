""" Blocks standing in an invisible host with an interaction entity: broken by hitting it, a seat when used. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.items.block import Block
from ....core.cls.items.features import Interaction
from ....core.cls.items.item import Item
from ....core.constants import CUSTOM_BLOCK_VANILLA
from ....core.utils.io import write_advancement, write_function, write_load_file, write_versioned_function
from ....core.utils.loot_table import advancement_entity, entity_type_field, loot_condition

# Constants
CONVENTION_TAGS: tuple[str, ...] = ("global.ignore", "global.ignore.kill", "smithed.entity")
""" Tags keeping other packs from killing or moving the entities of a block. """


# Functions
def interaction_of(block: Block) -> Interaction:
	""" The interaction of a block standing in an invisible host. """
	assert block.vanilla_block and block.vanilla_block.interaction, f"Block '{block.id}' has no interaction"
	return block.vanilla_block.interaction


def interaction_summon(block: Block) -> str:
	""" The commands summoning the block's interaction on its bottom, run at the center of the block. """
	ns: str = Mem.ctx.project_id
	interaction: Interaction = interaction_of(block)
	tags: str = ",".join(f'"{tag}"' for tag in (*CONVENTION_TAGS, f"{ns}.interaction", f"{ns}.{block.id}"))
	return (
		f"\n# Interaction breaking the block when hit\nsummon interaction ~ ~-0.5 ~ "
		f"{{width:{interaction.width}f,height:{interaction.height}f,response:true,Tags:[{tags}]}}\n"
	)


def interaction_destroy(block: Block) -> str:
	""" The commands ending the block's destroy function: feedback, its item unless `#no_drop` is 1, and its entities gone.

	Only a creative player or a weak tool sets `#no_drop`, so anything else breaking the block, such as a quarry, gets the item.
	An item id as `no_silk_touch_drop` drops that item instead, as a lit lamp drops an unlit one.
	"""
	ns: str = Mem.ctx.project_id
	drop: str = block.no_silk_touch_drop if isinstance(block.no_silk_touch_drop, str) else block.id
	lines: str = f"""
# Break feedback, the item, and the interaction gone
{feedback(block, "break")}execute unless score #no_drop {ns}.data matches 1 run loot spawn ~ ~ ~ loot {Item.from_id(drop).loot_table}
execute positioned ~ ~-0.5 ~ run kill @e[type=interaction,tag={ns}.interaction,distance=..0.01]
"""
	if interaction_of(block).seat is not None:
		lines += f"kill @e[type=item_display,tag={ns}.seat,distance=..0.6]\n"
	return lines


def feedback(block: Block, sound: str) -> str:
	""" The particles of the block's item and its `hit` or `break` sound, at the center of the block. """
	count, speed, volume = (8, 0.05, 0.4) if sound == "hit" else (30, 0.1, 1.0)
	return (
		f'particle minecraft:item{{item:{{id:"{CUSTOM_BLOCK_VANILLA}",components:{{"minecraft:item_model":"{block.item_model}"}}}}}} '
		f"~ ~ ~ 0.25 0.25 0.25 {speed} {count}\n"
		f"playsound {interaction_of(block).sound}.{sound} block @a ~ ~ ~ {volume}\n"
	)


def write_interactions(blocks: list[Block]) -> None:
	""" The advancements noticing a player hitting or using an interaction, and what each block does then. """
	ns: str = Mem.ctx.project_id
	entity: JsonDict = advancement_entity({**entity_type_field("minecraft:interaction"), "nbt": f'{{Tags:["{ns}.interaction"]}}'})
	for trigger, name in (("minecraft:player_hurt_entity", "hit"), ("minecraft:player_interacted_with_entity", "used")):
		write_advancement(f"{ns}:custom_blocks/interaction_{name}", {
			"criteria": {"requirement": {"trigger": trigger, "conditions": {"entity": entity}}},
			"rewards": {"function": f"{ns}:custom_blocks/_interaction/{name}"},
		})

	write_function(f"{ns}:custom_blocks/_interaction/hit", f"""
advancement revoke @s only {ns}:custom_blocks/interaction_hit
tag @s add {ns}.breaker
execute as @e[type=interaction,tag={ns}.interaction,distance=..8] if data entity @s attack run function {ns}:custom_blocks/_interaction/dispatch_hit
tag @s remove {ns}.breaker
""")  # noqa: E501
	write_function(f"{ns}:custom_blocks/_interaction/dispatch_hit", "data remove entity @s attack\n" + "".join(
		f"execute if entity @s[tag={ns}.{block.id}] at @s positioned ~ ~0.5 ~ run return run function {block.functions['hit']}\n"
		for block in blocks
	))
	write_function(f"{ns}:custom_blocks/_interaction/break", f"""
setblock ~ ~ ~ air
execute as @e[type=item_display,tag={ns}.custom_block,distance=..0.1] run function {ns}:custom_blocks/destroy
scoreboard players set #no_drop {ns}.data 0
""")
	for block in blocks:
		write_block_hit(block)
	if any(interaction_of(block).hits > 1 for block in blocks):
		write_load_file(f"""
# Hits of interaction blocks
scoreboard objectives add {ns}.hits dummy
scoreboard objectives add {ns}.last_hit dummy
""")

	write_function(f"{ns}:custom_blocks/_interaction/used", f"""
advancement revoke @s only {ns}:custom_blocks/interaction_used
tag @s add {ns}.user
execute as @e[type=interaction,tag={ns}.interaction,distance=..8] if data entity @s interaction at @s run function {ns}:custom_blocks/_interaction/use
tag @s remove {ns}.user
""")  # noqa: E501
	seats: list[Block] = [block for block in blocks if interaction_of(block).seat is not None]
	write_function(f"{ns}:custom_blocks/_interaction/use", "data remove entity @s interaction\n" + "".join(
		f"execute if entity @s[tag={ns}.{block.id}] run return run function {block.functions['sit']}\n" for block in seats
	))
	if seats:
		write_seats(seats)


def write_block_hit(block: Block) -> None:
	""" What hitting the block's interaction does, run as it at the center of the block.

	It counts the hit, then breaks the block once enough came.
	"""
	ns: str = Mem.ctx.project_id
	interaction: Interaction = interaction_of(block)
	counting: str = ""
	if interaction.hits > 1:
		counting = f"""
# A hit coming {interaction.hit_timeout} ticks or more after the previous one starts the count again
{feedback(block, "hit")}execute unless score @s {ns}.last_hit matches -2147483648.. run scoreboard players set @s {ns}.last_hit 0
execute store result score #now {ns}.data run time query gametime
scoreboard players operation #elapsed {ns}.data = #now {ns}.data
scoreboard players operation #elapsed {ns}.data -= @s {ns}.last_hit
execute if score #elapsed {ns}.data matches {interaction.hit_timeout}.. run scoreboard players set @s {ns}.hits 0
scoreboard players operation @s {ns}.last_hit = #now {ns}.data
scoreboard players add @s {ns}.hits 1
execute unless entity @p[tag={ns}.breaker,gamemode=creative] if score @s {ns}.hits matches ..{interaction.hits - 1} run return 0
"""
	tool_check: str = ""
	if block.mining:
		tool_check = (
			f"execute if score #no_drop {ns}.data matches 0 "
			f"unless items entity @p[tag={ns}.breaker] weapon.mainhand #{block.mining.item_tag} "
			f"run scoreboard players set #no_drop {ns}.data 1\n"
		)
	write_function(block.functions["hit"], f"""{counting}
# Break it, dropping nothing for a creative player{" or a tool too weak" if block.mining else ""}
execute store success score #no_drop {ns}.data if entity @p[tag={ns}.breaker,gamemode=creative]
{tool_check}function {ns}:custom_blocks/_interaction/break
""")


def inline_predicate(predicate: JsonDict) -> str:
	""" An entity_properties condition on the executing entity, written inline for `execute if predicate`. """
	return stp.json_dump(loot_condition("minecraft:entity_properties", entity="this", predicate=predicate), max_level=0).strip()


def write_seats(seats: list[Block]) -> None:
	""" Using a seat mounts the player on an invisible display at its height, killed once empty. """
	ns: str = Mem.ctx.project_id
	riding: str = inline_predicate({"vehicle": {}})
	for block in seats:
		write_function(block.functions["sit"], f"""
execute as @p[tag={ns}.user] if predicate {riding} run return fail
execute positioned ~ ~{interaction_of(block).seat} ~ summon item_display run function {ns}:custom_blocks/_interaction/seat
""")
	tags: str = "".join(f"tag @s add {tag}\n" for tag in CONVENTION_TAGS)
	write_function(f"{ns}:custom_blocks/_interaction/seat", tags + f"""tag @s add {ns}.seat
ride @p[tag={ns}.user] mount @s
scoreboard players add #seats {ns}.data 1
""")

	write_versioned_function("second", f"""
# Seats left empty
execute if score #seats {ns}.data matches 1.. as @e[type=item_display,tag={ns}.seat] unless predicate {inline_predicate({"passenger": {}})} run function {ns}:custom_blocks/_interaction/unseat
""")  # noqa: E501
	write_function(f"{ns}:custom_blocks/_interaction/unseat", f"scoreboard players remove #seats {ns}.data 1\nkill @s\n")

