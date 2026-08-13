
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Predicate
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.external_item import ExternalItem
from ...core.cls.ingredients import Ingr
from ...core.cls.item import Item
from ...core.cls.recipe import AwakenedForgeRecipe
from ...core.utils.io import set_json_encoder, write_function, write_load_file, write_versioned_function


class AwakenedForgeRecipeHandler:
    """ Handler for awakened forge recipe generation.

    This class handles the generation of awakened forge recipes.
    """
    @classmethod
    def routine(cls) -> None:
        """ Main routine for awakened forge recipe generation. """
        handler = cls()
        handler.generate_recipes()

    @stp.simple_cache(method="str")
    def stardust_awakened_forge_recipe(self, recipe: JsonDict, item: str) -> str:
        """ Generate a awakened forge recipe.

        Args:
            recipe (JsonDict): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            str: The generated recipe command.
        """
        # Determine the result
        result: Ingr = Ingr(recipe["result"]).to_item().item_to_id() if recipe.get("result") else Ingr(item)
        result_function: str = result.to_id(add_namespace=True).replace(":", "/")

        # Get ingredients
        ingredients: list[Ingr] = recipe["ingredients"]
        first_ingredient: Ingr = ingredients[0]
        first_count: int = first_ingredient.get("count", 1)
        assert first_count <= 64, f"First ingredient must have count <= 64, for {item} recipe {recipe}"
        ingredients = ingredients[1:]

        # Prepare the check line
        line: str = "execute if data entity @s Item" + ExternalItem.json_dump(first_ingredient.to_predicate(count=first_count))
        for ingredient in ingredients:
            count: int = ingredient.get("count", 1)
            while True:
                this_count = count if count < 64 else 64
                line += f" if entity @n[type=item,nbt={{Item:{ExternalItem.json_dump(ingredient.to_predicate(count=this_count))}}},distance=..1]"
                count -= 64
                if count <= 0:
                    break
        line += f" run return run function {Mem.ctx.project_id}:calls/stardust/forge_recipes/{result_function}/timer"

        # Write the first result function
        particle: str = recipe.get("particle", r"minecraft:dust{color:[0,0,1],scale:2}")
        write_function(f"{Mem.ctx.project_id}:calls/stardust/forge_recipes/{result_function}/timer", f"""
# Timer
scoreboard players add @s stardust.forge_timer 4
scoreboard players remove @s[scores={{stardust.forge_timer=1..}}] stardust.forge_timer 3
scoreboard players reset @s[scores={{stardust.forge_timer=..0}}] stardust.forge_timer
execute if score @s stardust.forge_timer matches 1 run playsound stardust:awakened_forge_crafting ambient @a[distance=..25]
execute if score @s stardust.forge_timer matches 1.. run particle {particle} ~ ~ ~ 5 5 5 0.1 125

# When timer reaches 4, craft the item
execute if score @s stardust.forge_timer matches 4 run function {Mem.ctx.project_id}:calls/stardust/forge_recipes/{result_function}/craft
""")
        # Write the second result function
        kill_ingredients: str = ""
        for ingredient in ingredients:
            count: int = ingredient.get("count", 1)
            while True:
                this_count = count if count < 64 else 64
                kill_ingredients += f"kill @n[type=item,nbt={{Item:{ExternalItem.json_dump(ingredient.to_predicate(count=this_count))}}},distance=..1]\n"
                count -= 64
                if count <= 0:
                    break
        write_function(f"{Mem.ctx.project_id}:calls/stardust/forge_recipes/{result_function}/craft", f"""
# Visual and audio feedback
advancement grant @a[distance=..25] only stardust:visible/adventure/use_awakened_forge
playsound block.anvil.use block @a[distance=..25]
particle smoke ~ ~ ~ 0.4 0.4 0.4 0.2 1000

# Kill ingredients
kill @s
{kill_ingredients}

# Spawn result item with Motion [0.0,1.0,0.0]
tag @e[type=item] add stardust.temp
execute align xyz run loot spawn ~0.5 ~0.5 ~0.5 loot {result.register_loot_table(recipe['result_count'])}
execute as @e[type=item,tag=!stardust.temp] run data merge entity @s {{Motion:[0.0d,1.0d,0.0d],Glowing:true}}
tag @e[type=item,tag=stardust.temp] remove stardust.temp
""")

        # Return check line
        return line

    def generate_recipes(self) -> None:
        """ Generate all pulverizer recipes. """
        for item in Mem.definitions.keys():
            obj = Item.from_id(item)

            for recipe in obj.recipes:
                if recipe["type"] == AwakenedForgeRecipe.type:
                    recipe = AwakenedForgeRecipe.from_dict(recipe)
                    write_function(
                        f"{Mem.ctx.project_id}:calls/stardust/awakened_forge_recipes",
                        self.stardust_awakened_forge_recipe(recipe, item),
                        tags=["stardust:calls/awakened_forge_recipes"],
                    )

        # Second clock function
        if Mem.ctx.project_id == "stardust" and Mem.ctx.data["stardust"].functions.get("calls/stardust/awakened_forge_recipes"):
            write_load_file("\n# Awakened Forge timer\nscoreboard objectives add stardust.forge_timer dummy\n", prepend=True)
            write_versioned_function("second", """
# Awakened Forge recipes
execute as @e[type=item,predicate=stardust:awakened_forge_input] at @s run function stardust:forge/second
""")
            Mem.ctx.data["stardust"].predicates["awakened_forge_input"] = set_json_encoder(Predicate({
                    "condition": "minecraft:entity_properties",
                    "entity": "this",
                    "predicate": {
                        "nbt": """{Item:{components:{"minecraft:custom_data":{}}}}""",
                        "stepping_on": {
                            "block": {
                                "blocks": "minecraft:glass"
                            }
                        }
                    }
            }), max_level=-1)

            # Second function, check the structure and call the recipes
            write_function("stardust:forge/second", """
# Check for Awakened Forge structure
execute unless function stardust:forge/verify_structure run return fail

# Call Awakened Forge recipes
function #stardust:calls/awakened_forge_recipes
""")

            # Check structure function
            write_function("stardust:forge/verify_structure", """
## Verify Awakened Forge multiblock structure
scoreboard players set #success stardust.data 0

# Structure Orientation
execute if block ~-2 ~-2 ~-2 #minecraft:diamond_ores if block ~-2 ~-1 ~-2 #minecraft:iron_ores if block ~2 ~-2 ~-2 #minecraft:emerald_ores if block ~2 ~-1 ~-2 #minecraft:coal_ores if block ~2 ~-2 ~2 nether_quartz_ore if block ~2 ~-1 ~2 #minecraft:redstone_ores if block ~-2 ~-2 ~2 #minecraft:gold_ores if block ~-2 ~-1 ~2 #minecraft:lapis_ores run scoreboard players set #success stardust.data 1
execute if block ~2 ~-2 ~2 #minecraft:diamond_ores if block ~2 ~-1 ~2 #minecraft:iron_ores if block ~-2 ~-2 ~2 #minecraft:emerald_ores if block ~-2 ~-1 ~2 #minecraft:coal_ores if block ~-2 ~-2 ~-2 nether_quartz_ore if block ~-2 ~-1 ~-2 #minecraft:redstone_ores if block ~2 ~-2 ~-2 #minecraft:gold_ores if block ~2 ~-1 ~-2 #minecraft:lapis_ores run scoreboard players set #success stardust.data 1
execute if block ~2 ~-2 ~-2 #minecraft:diamond_ores if block ~2 ~-1 ~-2 #minecraft:iron_ores if block ~2 ~-2 ~2 #minecraft:emerald_ores if block ~2 ~-1 ~2 #minecraft:coal_ores if block ~-2 ~-2 ~2 nether_quartz_ore if block ~-2 ~-1 ~2 #minecraft:redstone_ores if block ~-2 ~-2 ~-2 #minecraft:gold_ores if block ~-2 ~-1 ~-2 #minecraft:lapis_ores run scoreboard players set #success stardust.data 1
execute if block ~-2 ~-2 ~2 #minecraft:diamond_ores if block ~-2 ~-1 ~2 #minecraft:iron_ores if block ~-2 ~-2 ~-2 #minecraft:emerald_ores if block ~-2 ~-1 ~-2 #minecraft:coal_ores if block ~2 ~-2 ~-2 nether_quartz_ore if block ~2 ~-1 ~-2 #minecraft:redstone_ores if block ~2 ~-2 ~2 #minecraft:gold_ores if block ~2 ~-1 ~2 #minecraft:lapis_ores run scoreboard players set #success stardust.data 1

# Continuation of the structure
execute if score #success stardust.data matches 1 if block ~ ~-1 ~ glass if block ~2 ~ ~2 glass if block ~-2 ~ ~-2 glass if block ~-2 ~ ~2 glass if block ~2 ~ ~-2 glass if block ~ ~-2 ~ diamond_block if block ~1 ~-1 ~1 dragon_egg if block ~-1 ~-1 ~-1 dragon_egg if block ~-1 ~-1 ~1 dragon_egg if block ~1 ~-1 ~-1 dragon_egg if block ~2 ~-2 ~ beacon if block ~ ~-2 ~2 beacon if block ~-2 ~-2 ~ beacon if block ~ ~-2 ~-2 beacon if block ~1 ~-2 ~ red_concrete if block ~-1 ~-2 ~ red_concrete if block ~ ~-2 ~1 red_concrete if block ~ ~-2 ~-1 red_concrete if block ~1 ~-2 ~1 red_concrete if block ~-1 ~-2 ~1 red_concrete if block ~-1 ~-2 ~-1 red_concrete if block ~1 ~-2 ~-1 red_concrete if block ~1 ~-2 ~2 black_concrete if block ~-1 ~-2 ~2 black_concrete if block ~1 ~-2 ~-2 black_concrete if block ~-1 ~-2 ~-2 black_concrete if block ~2 ~-2 ~1 black_concrete if block ~-2 ~-2 ~1 black_concrete if block ~2 ~-2 ~-1 black_concrete if block ~-2 ~-2 ~-1 black_concrete run return 1

# Else, fail
return fail
""")  # noqa: E501

