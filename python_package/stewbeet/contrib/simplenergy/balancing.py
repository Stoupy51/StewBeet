
# Imports
from ...core import Mem, write_function, write_versioned_function


# Setup energy balancing
def setup_energy_balancing(can_balance: list[str]) -> None:
	""" Setup energy balancing for devices.

	Args:
		can_balance (list[str]): List of devices that can balance energy between them.
			(e.g. ["solar_panel", "cauldron_generator", "simple_battery", "advanced_battery", "elite_battery"]).
	"""
	ns: str = Mem.ctx.project_id
	can_balance_tag: str = f"{ns}.can_balance"
	balanced_tag: str = f"{ns}.balanced"
	adjacent_tag: str = f"{ns}.adjacent"

	# Write in second_5.mcfunction a call to balancing function
	write_versioned_function("second_5", f"""
# Energy Balancing system (balance every device having at least 20 kJ)
execute as @e[tag={can_balance_tag},scores={{energy.storage=20..}}] at @s[tag=!{balanced_tag}] run function {ns}:balancing/main
tag @e[tag={balanced_tag}] remove {balanced_tag}
""")

	# Write balancing/main.mcfunction
	device_main_calls: str = ""
	for device in can_balance:
		device_main_calls += f"\nexecute if entity @s[tag={ns}.{device}] run function {ns}:balancing/{device}/main"
	balancing_content: str = f"""
# Stop if already balanced
execute if entity @s[tag={balanced_tag}] run return 0

# Copy max storage from device to scoreboard & add balance tags
scoreboard players operation #max_storage {ns}.data = @s energy.max_storage

# For each balancing device, run the main function{device_main_calls}

# Remove adjacent tags
tag @e[tag={adjacent_tag}] remove {adjacent_tag}
"""
	write_function(f"{ns}:balancing/main", balancing_content)

	# For each balancing device, write the balancing functions
	for device in can_balance:

		# Write balancing/device/found.mcfunction
		selector: str = f"@e[tag={ns}.{device},tag={can_balance_tag},tag=!{adjacent_tag},dx=0,dy=0,dz=0]"
		condition_run: str = f"if score @s energy.max_storage = #max_storage {ns}.data at @s run function {ns}:balancing/{device}/found"
		write_function(f"{ns}:balancing/{device}/found", f"""
# Add tags and scores
tag @s add {adjacent_tag}
tag @s add {balanced_tag}
scoreboard players add #count {ns}.data 1
scoreboard players operation #total_energy {ns}.data += @s energy.storage

# Check nearby {device} recursively
execute align xyz positioned ~ ~1 ~ as {selector} {condition_run}
execute align xyz positioned ~ ~-1 ~ as {selector} {condition_run}
execute align xyz positioned ~ ~ ~1 as {selector} {condition_run}
execute align xyz positioned ~ ~ ~-1 as {selector} {condition_run}
execute align xyz positioned ~1 ~ ~ as {selector} {condition_run}
execute align xyz positioned ~-1 ~ ~ as {selector} {condition_run}
""")
		# Write balancing/device/main.mcfunction
		write_function(f"{ns}:balancing/{device}/main", f"""
# Collect energy from nearby blocks recursively
scoreboard players set #count {ns}.data 0
scoreboard players set #total_energy {ns}.data 0
function {ns}:balancing/{device}/found

# If there are no adjacent device or the sum is higher than integer limit, stop here
execute if score #count {ns}.data matches 1 run return 0
execute if score #total_energy {ns}.data matches ..0 run return 0

# Redistributes energy to all adjacent devices
scoreboard players operation #per_device {ns}.data = #total_energy {ns}.data
scoreboard players operation #per_device {ns}.data /= #count {ns}.data
scoreboard players operation @e[tag={adjacent_tag}] energy.storage = #per_device {ns}.data

# Add the remaining energy to the current device
scoreboard players operation #remaining {ns}.data = #total_energy {ns}.data
scoreboard players operation #remaining {ns}.data %= #count {ns}.data
scoreboard players operation @s energy.storage += #remaining {ns}.data

# Sometimes the remaining energy is too high, so we set it to the max storage resulting in a loss of energy (lets assume it's a feature: energy transformed in heat)
execute if score @s energy.storage > @s energy.max_storage run scoreboard players operation @s energy.storage = @s energy.max_storage
""")


	# Add in the placement function the balancing tag
	for device in can_balance:
		write_function(f"{ns}:custom_blocks/{device}/place_secondary", f"\n# Add balancing tag\ntag @s add {can_balance_tag}")

