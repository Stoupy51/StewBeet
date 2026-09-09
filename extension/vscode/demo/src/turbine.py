""" The wind turbine, written with beet alone: no StewBeet helper anywhere in this file. """

# Imports
from beet import Context, Function


# Functions
def beet_default(ctx: Context) -> None:
	ctx.data.functions["voltaic:turbine/tick"] = Function("""
# The higher the turbine stands, the more it makes
execute store result score #height voltaic.data run data get entity @s Pos[1]
execute if score #height voltaic.data matches ..59 run return run function voltaic:turbine/stall
execute if score #height voltaic.data matches 150.. run scoreboard players add @s energy.storage 40
""")

	ctx.data.functions["voltaic:turbine/tick"].append("""
# A full battery stays full
execute if score @s energy.storage > @s energy.capacity run scoreboard players operation @s energy.storage = @s energy.capacity
""")

	ctx.data.functions["voltaic:turbine/stall"] = Function("""
# Too low for any wind to reach it
data modify entity @s item.components."minecraft:item_model" set value "voltaic:turbine"
""")

