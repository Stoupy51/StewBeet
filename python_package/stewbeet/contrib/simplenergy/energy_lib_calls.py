
# Imports
from ...core import Mem, write_function


# Add commands to place and destroy functions for energy items
def insert_lib_calls() -> None:
	ns: str = Mem.ctx.project_id

	for item, data in Mem.definitions.items():
		energy: dict = data.get("custom_data", {}).get("energy", {})
		if len(energy) > 0:
			placement: str = f"{ns}:custom_blocks/{item}/place_secondary"
			destroy: str = f"{ns}:custom_blocks/{item}/destroy"
			if placement not in Mem.ctx.data.functions: # Skip if no custom block
				continue

			# If the item is a cable
			if "transfer" in energy:
				write_function(destroy, "# Datapack Energy\nfunction energy:v1/api/break_cable\n", prepend = True)
				write_function(f"{ns}:custom_blocks/{item}/place_secondary", f"""
tag @s add energy.cable
scoreboard players set @s energy.transfer_rate {energy["transfer"]}
function energy:v1/api/init_cable
""")
			else:
				# Else, if if's a machine
				write_function(destroy, "# Datapack Energy\nfunction energy:v1/api/break_machine\n", prepend = True)
				if "usage" in energy or "generation" in energy:
					write_function(f"{ns}:custom_blocks/{item}/place_secondary", f"""
# Energy part
tag @s add energy.{"send" if "generation" in energy else "receive"}
scoreboard players set @s energy.max_storage {energy["max_storage"]}
scoreboard players operation @s energy.transfer_rate = @s energy.max_storage
scoreboard players add @s energy.storage 0
scoreboard players add @s energy.change_rate 0
function energy:v1/api/init_machine
""")
				else:
					# Else, it's a battery.
					write_function(f"{ns}:custom_blocks/{item}/place_secondary", f"""
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

