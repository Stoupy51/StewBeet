
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from ...core import BlockFunctions, Item, Mem, write_function, write_load_file


# Add commands to place and destroy functions for energy items
def insert_lib_calls() -> None:
	ns: str = Mem.ctx.project_id

	# Create new energy_rate scoreboard objective
	write_load_file(f"\n# Score for energy usage or generation\nscoreboard objectives add {ns}.energy_rate dummy\n", prepend = True)

	# Loop through all items with energy data
	for item, data in Mem.definitions.items():
		obj = Item.from_dict(data, item)
		energy: dict[str, int] = obj.components.get("custom_data", {}).get("energy", {})
		if len(energy) > 0:
			funcs: BlockFunctions = BlockFunctions(item)
			if funcs.place_secondary not in Mem.ctx.data.functions: # Skip if no custom block
				continue

			# If the item is a cable
			if "transfer" in energy:
				write_function(funcs.destroy, "# Datapack Energy\nfunction energy:v1/api/break_cable\n", prepend = True)
				write_function(funcs.place_secondary, f"""
tag @s add energy.cable
scoreboard players set @s energy.transfer_rate {energy["transfer"]}
function energy:v1/api/init_cable
""")
			else:
				# Else, if if's a machine
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
				else:
					# Else, it's a battery.
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

