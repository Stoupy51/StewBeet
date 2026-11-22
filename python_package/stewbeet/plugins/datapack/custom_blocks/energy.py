""" Registers the custom blocks with energy settings in the energy library, and refuses cables on their blocked faces. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block_functions import BlockFunctions
from ....core.cls.items.item import Item
from ....core.utils.io import write_function, write_load_file

# Constants
ENERGY_DIRECTIONS: tuple[str, ...] = ("up", "down", "north", "south", "east", "west")
""" The directions in the order the energy library numbers them, each followed by its opposite. """

HORIZONTAL_FACINGS: tuple[tuple[str, str], ...] = (
	("north", "-45..45"), ("east", "45..135"), ("south", "135..-135"), ("west", "-135..-45")
)
""" Where a machine's front points for each range of its `y_rotation`, clockwise, as the wrench turns it. """

RELATIVE_FACES: dict[str, int] = {"front": 0, "left": 1, "back": 2, "right": 3}
""" How many clockwise steps each side face is from the front, left and right as seen by a player facing the front. """


# Functions
def write_energy(ns: str) -> None:
	""" Register every placeable custom block whose `custom_data` has `energy`, and refuse cables on its `blocked_faces`. """
	energy_blocks: dict[str, JsonDict] = {
		item: energy for item, data in Mem.definitions.items()
		if (energy := Item.from_dict(data, item).components.get("custom_data", {}).get("energy", {}))
		and BlockFunctions(item).place_secondary in Mem.ctx.data.functions
	}
	if not energy_blocks:
		return

	write_load_file(f"\n# Score for energy usage or generation\nscoreboard objectives add {ns}.energy_rate dummy\n", prepend = True)
	for item, energy in energy_blocks.items():
		write_energy_calls(BlockFunctions(item), energy, ns)

	refusals: list[str] = [
		line for item, energy in energy_blocks.items()
		for face in energy.get("blocked_faces", []) for line in cable_refusals(f"{ns}.{item}", face)
	]
	if refusals:
		write_function(f"{ns}:calls/energy/cable_can_connect", "\n".join(refusals) + "\n", tags=["energy:v1/cable_can_connect"])


def write_energy_calls(funcs: BlockFunctions, energy: JsonDict, ns: str) -> None:
	""" Register one custom block with the energy library, as a cable, a machine or a battery. """
	if "transfer" in energy:
		write_function(funcs.destroy, "# Datapack Energy\nfunction energy:v1/api/break_cable\n", prepend = True)
		write_function(funcs.place_secondary, f"""
tag @s add energy.cable
scoreboard players set @s energy.transfer_rate {energy["transfer"]}
function energy:v1/api/init_cable
""")
		return

	write_function(funcs.destroy, "# Datapack Energy\nfunction energy:v1/api/break_machine\n", prepend = True)
	if "usage" in energy or "generation" in energy:
		write_function(funcs.place_secondary, f"""
# Energy part
tag @s add energy.{"send" if "generation" in energy else "receive"}
scoreboard players set @s {ns}.energy_rate {energy.get("usage", energy.get("generation", 0))}
scoreboard players set @s energy.max_storage {energy["max_storage"]}
scoreboard players operation @s energy.transfer_rate = @s energy.max_storage
scoreboard players add @s energy.storage 0
scoreboard players add @s energy.change_rate 0
function energy:v1/api/init_machine
""")
		return

	# A battery
	write_function(funcs.place_secondary, f"""
# Energy part
tag @s add {ns}.battery_switcher
tag @s add energy.receive
tag @s add energy.send
data modify storage {ns}:temp energy set from entity @p[tag={ns}.placer] SelectedItem.components."minecraft:custom_data".energy
execute store result score @s energy.max_storage run data get storage {ns}:temp energy.max_storage
execute store result score @s energy.storage run data get storage {ns}:temp energy.storage
scoreboard players operation @s energy.transfer_rate = @s energy.max_storage
function energy:v1/api/init_machine
""")


def cable_refusals(tag: str, face: str) -> list[str]:
	""" The commands refusing a cable on one face of the machines with `tag`, for each way the machine can face.

	Args:
		face: `top`, `bottom`, or a key of `RELATIVE_FACES`.

	>>> cable_refusals("a.solar", "top")
	['execute if entity @s[tag=a.solar] if score #cable.in energy.data matches 1 run scoreboard players set #cable.out energy.data 0']
	>>> [line.split(" matches ")[1][0] for line in cable_refusals("a.generator", "front")]
	['3', '5', '2', '4']
	"""
	refuse: str = "run scoreboard players set #cable.out energy.data 0"
	if face in ("top", "bottom"):
		side: int = ENERGY_DIRECTIONS.index("up" if face == "top" else "down")
		return [f"execute if entity @s[tag={tag}] if score #cable.in energy.data matches {side ^ 1} {refuse}"]
	return [
		f"execute if entity @s[tag={tag},y_rotation={yaw}] if score #cable.in energy.data matches "
		f"{ENERGY_DIRECTIONS.index(HORIZONTAL_FACINGS[(turns + RELATIVE_FACES[face]) % 4][0]) ^ 1} {refuse}"
		for turns, (_, yaw) in enumerate(HORIZONTAL_FACINGS)
	]

