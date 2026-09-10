""" Machines, written the StewBeet way: one helper call per function, every path interpolated. """

# Imports
from beet import Context
from stewbeet import McFunction, write_function


# Functions
def beet_default(ctx: Context) -> None:
	ns: str = ctx.project_id

	write_function(f"{ns}:machines/tick", f"""
# Stop unless the machine has the energy it needs this tick
execute unless score @s energy.storage >= @s {ns}.energy_rate run return fail
scoreboard players operation @s energy.storage -= @s {ns}.energy_rate

execute if entity @s[tag={ns}.turbine] run function {ns}:turbine/tick
function {ns}:machines/pulverizer/work
""")

	# One call in a loop writes three functions, and the lens above it says how many
	for speed, interval in (("slow", 20), ("normal", 10), ("fast", 5)):
		write_function(f"{ns}:machines/pulverizer/{speed}", f"""
scoreboard players set #interval {ns}.data {interval}
execute if score #timer {ns}.data matches {interval}.. run function {ns}:machines/pulverizer/work
""")

	# Commands assembled in a variable reach the call below, which is what the annotation says
	work: McFunction = f"""
# One ore in, two dusts out
loot replace block ~ ~ ~ container.1 loot {ns}:pulverizer/iron_dust
playsound {ns}:pulverizer block @a[distance=..8]
"""
	work += f"scoreboard players reset #timer {ns}.data\n"
	write_function(f"{ns}:machines/pulverizer/work", work)

