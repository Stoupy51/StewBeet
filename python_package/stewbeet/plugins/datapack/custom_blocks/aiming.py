""" Where the placer clicked a block being placed, found by stepping along their look, for the hosts of `VanillaBlock.half`. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from ....core.utils.io import write_function


# Functions
def write_aim(ns: str) -> None:
	""" `{ns}:custom_blocks/_aim/main`, run as a marker summoned at the center of a block being placed, which it kills.

	`#upper` ends at 1 when the look of the `{ns}.placer` player leaves the block through its upper half,
	which is how vanilla picks a top slab, and `#floor` at 1 when it leaves through the bottom face,
	the player having clicked the top of the block below.
	"""
	write_function(f"{ns}:custom_blocks/_aim/main", f"""
tag @s add {ns}.aimed
scoreboard players set #upper {ns}.data 0
scoreboard players set #floor {ns}.data 0
scoreboard players set #inside {ns}.data 0
scoreboard players set #steps {ns}.data 0
execute as @p[tag={ns}.placer] at @s anchored eyes positioned ^ ^ ^ anchored feet run function {ns}:custom_blocks/_aim/ray
kill @s
""")
	write_function(f"{ns}:custom_blocks/_aim/ray", f"""
# A box test from 0.5 below a point holds when the point is in the block, from 1 below when it is in its upper half
scoreboard players add #steps {ns}.data 1
execute if score #steps {ns}.data matches 120.. run return 0
scoreboard players operation #was_inside {ns}.data = #inside {ns}.data
execute positioned ~-0.5 ~-0.5 ~-0.5 store success score #inside {ns}.data if entity @e[type=marker,tag={ns}.aimed,dx=0,dy=0,dz=0]
execute if score #inside {ns}.data matches 1 positioned ~-0.5 ~-1 ~-0.5 store success score #upper {ns}.data if entity @e[type=marker,tag={ns}.aimed,dx=0,dy=0,dz=0]
execute if score #was_inside {ns}.data matches 1 if score #inside {ns}.data matches 0 positioned ~-0.5 ~0.5 ~-0.5 store success score #floor {ns}.data if entity @e[type=marker,tag={ns}.aimed,dx=0,dy=0,dz=0]
execute if score #was_inside {ns}.data matches 1 if score #inside {ns}.data matches 0 run return 0
execute positioned ^ ^ ^0.05 run function {ns}:custom_blocks/_aim/ray
""")  # noqa: E501

