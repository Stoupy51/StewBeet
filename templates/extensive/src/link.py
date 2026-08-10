
# ruff: noqa
# Imports
from beet import Context
from stouputils.typing import JsonDict
from stewbeet import *  # type: ignore


# Main entry point (ran just before making finalyzing the build process (zip, headers, lang, ...))
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    definitions: JsonDict = Mem.definitions # type: ignore

    # Generate ores in the world
    CustomOreGeneration.all_with_config(ore_configs = {
        "steel_ore": [
            CustomOreGeneration(
                dimensions = ["minecraft:overworld","stardust:cavern","some_other:dimension"],
                maximum_height = 50,
                minimum_height = 0,
                veins_per_region = 1.2,
                vein_size_logic = 0.4,
            )
        ],
        "deepslate_steel_ore": [
            CustomOreGeneration(
                dimensions = ["minecraft:overworld"],
                maximum_height = 0,
                veins_per_region = 1.2,
                vein_size_logic = 0.4,
            ),
            CustomOreGeneration(
                dimensions = ["stardust:cavern"],
                maximum_height = 0,
                veins_per_region = 3.6,
                vein_size_logic = 0.8,
            )
        ],
    })


    # Add some commands when loading datapack.
    # The "render" keys are replaced by the auto.text_renders plugin with glyphs of a generated font,
    # so any item image can be shown in chat: a project item, a vanilla one, or one from another pack.
    write_load_file("""
# Add a message when loading
tellraw @a ["Here is a message when loading the datapack, located in `src/link.py`\\n\\n\\n"]
tellraw @a [{"render":"steel_block","height":64},{"render":"minecraft:diamond","height":64},"\\n\\n\\n\\n"]
""")
    #	write_function("v{version}/load/confirm_load", ...)	<- This is the same as the previous line


    ## Clock functions
    # When you write to the following files: "tick_2", "second", "second_5", "minute"... the tick function will automatically call them, ex:
    write_versioned_function("minute", f"execute if score #spam {ns}.data matches 1 run say This is a message every minute\n")
    write_versioned_function("second_5", f"execute if score #spam {ns}.data matches 1 run say This is a SPAM message every 5 seconds\n")
    write_versioned_function("tick_2", f"execute if score #spam {ns}.data matches 1 run say This is a SPAM message every 2 ticks\n")
    # The two following functions calls are equivalent:
    #	write_tick_file(config, ...)
    #	write_versioned_file(config, "tick", ...)

    # Create a random function
    write_function(f"{ns}:path/to/a/random/function/i/guess", """tellraw @a {"text":"Hello world!"}""")

    # Call a bookshelf module (Every single module from https://docs.mcbookshelf.dev/en/latest/ is supported)
    write_function(f"{ns}:bookshelf/test", """
# Once
scoreboard players set $math.divide.x bs.in 9
scoreboard players set $math.divide.y bs.in 5
function #bs.math:divide
tellraw @a [{"text": "9 / 5 = ", "color": "dark_gray"},{"score":{"name":"$math.divide", "objective": "bs.out"}, "color": "gold"}]
""")

    # Run commands as the block entity when it is placed, by appending to the place_secondary
    # Function object directly. This must happen after the datapack.custom_blocks plugin
    # (hence src/link.py, and not src/setup_definitions.py): .obj raises KeyError if the function
    # doesn't exist yet, so doing it too early fails loudly instead of silently misplacing commands.
    stone = Block.from_id("super_stone")
    stone.functions.place_secondary.obj.append(f"""
say Omg, @p[tag={ns}.placer] placed the super stone block!
particle minecraft:explosion ~ ~ ~
""")
    # Alternatively, you can use this directly
    write_function(stone.functions.place_secondary, "say another way to append to the place_secondary function")

    # A custom block ticking example.
    # Block.functions gives you every mcfunction of a custom block.
    steel_block = Block.from_id("steel_block")
    write_function(steel_block.functions.tick, """
# This function is called every tick for the custom block "steel_block"
particle heart ~ ~1 ~ 0.5 0.5 0.5 0.01 1
""")
    write_function(steel_block.functions.second, """
# This function is called every second for the custom block "steel_block"
particle angry_villager ~ ~1 ~ 0.2 0.2 0.2 0.01 10
""")

    # Equation example
    equation = ScoreboardEquation("#value", f"{ns}.data").set(10).add(5).multiply(2).divide(3).modulo(100)
    equation2 = (ScoreboardEquation("#value2", f"{ns}.data").set(20) - 6 + 7) * 8 // 4 % 5
    write_function(f"{ns}:equation/test", str(equation) + "\n" + str(equation2))


    # DO NOT CROSS: THIS IS A WAR CRIME YOU NEED TO REMOVE, IT'S JUST FUNNY THAT YOU *CAN* DO THAT
    suffixes = ["", "_again"]
    my_range = range(1, 6)
    write_function(f"{ns}:war_crime/test", f"""
for i in {my_range}:
    say f"Hello, world! {{i}}"

execute function ./goodbye:
    say Goodbye, world!
    for suffix in {suffixes}:
        execute function f"{ns}:war_crime/farewell{{suffix}}":
            say f"Farewell, world! with {{suffix}}"
""")
    del ctx.data[ns].functions["war_crime/test"]

    pass

