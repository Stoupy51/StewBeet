""" Furnaces and brewing stands working `VanillaBlock.machine_speed` times faster, pushed one tick at a time while they work. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp

from ....core.__memory__ import Mem
from ....core.cls.items.block import Block
from ....core.utils.io import write_function
from ....core.utils.loot_table import loot_condition


# Functions
def write_machine(block: Block, speed: float) -> None:
	""" Push the progress of the block's host by `speed - 1` ticks every tick, the fractional part as a chance of one more.

	A furnace's own `speed_multiplier` resets whenever it lights up, which is why the progress is written by hand.
	"""
	ns: str = Mem.ctx.project_id
	host: str = block.vanilla_block.base_id if block.vanilla_block else ""
	extra, chance = int(speed - 1), round((speed - 1) % 1, 6)
	random: str = stp.json_dump(loot_condition("minecraft:random_chance", chance=chance), max_level=0).strip()
	if host == "minecraft:brewing_stand":
		# Brewing ends when BrewTime reaches 0 on vanilla's own tick, so it is never pushed below 2
		write_function(block.functions.tick, f"""
# Brew {speed} times faster
execute store result score #brew {ns}.data run data get block ~ ~ ~ BrewTime
execute if score #brew {ns}.data matches ..2 run return 0
{f"execute if score #brew {ns}.data matches {extra + 2}.. run scoreboard players remove #brew {ns}.data {extra}" if extra else ""}
{f"execute if score #brew {ns}.data matches 3.. if predicate {random} run scoreboard players remove #brew {ns}.data 1" if chance else ""}
execute store result block ~ ~ ~ BrewTime short 1 run scoreboard players get #brew {ns}.data
""")  # noqa: E501
		return
	write_function(block.functions.tick, f"""
# Cook {speed} times faster, never reaching the end itself so vanilla still finishes the item
execute unless block ~ ~ ~ {host}[lit=true] run return 0
execute store result score #spent {ns}.data run data get block ~ ~ ~ cooking_time_spent
execute if score #spent {ns}.data matches 0 run return 0
execute store result score #total {ns}.data run data get block ~ ~ ~ cooking_total_time
{f"scoreboard players add #spent {ns}.data {extra}" if extra else ""}
{f"execute if predicate {random} run scoreboard players add #spent {ns}.data 1" if chance else ""}
execute if score #spent {ns}.data >= #total {ns}.data run scoreboard players operation #spent {ns}.data = #total {ns}.data
execute if score #spent {ns}.data = #total {ns}.data run scoreboard players remove #spent {ns}.data 1
execute store result block ~ ~ ~ cooking_time_spent int 1 run scoreboard players get #spent {ns}.data
""")

