
# Imports
from stewbeet import *  # type: ignore


# Main entry point
def main():

    # Configuration to generate everything about the material based on "steel_ingot"
    ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
        "steel_ingot":	EquipmentsConfig(
            # This steel is equivalent to iron,
            equivalent_to = DefaultOre.IRON,

            # But, has more durability (3 times more)
            pickaxe_durability = 3 * VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"],

            # And, does 1 more damage per hit (mainhand), and has 0.5 more armor, and mines 20% faster (pickaxe)
            attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 2}
        ),

        # Simple material stone, this will automatically detect stone stick and rod textures.
        "minecraft:stone": None,
    }

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    # This will add:
    #   "steel_ingot", "steel_pickaxe", "steel_axe", "steel_shovel", "steel_sword", "steel_hoe", "steel_helmet",
    #   "steel_chestplate", "steel_leggings", "steel_boots", "steel_block", "raw_steel", "raw_steel_block", etc.
    # And "stone_stick", "stone_rod", etc.
    generate_everything_about_these_materials(ORES_CONFIGS)

    # Don't forget to set the vanilla blocks for the custom blocks
    # (not automatic even though they was recognized by generate_everything_about_these_materials(), because it's your choice of base block)
    Block.from_id("steel_block").vanilla_block = VanillaBlock(id="minecraft:iron_block")
    Block.from_id("raw_steel_block").vanilla_block = VanillaBlock(id="minecraft:raw_iron_block")

    # Keep steel_ore default no_silk_touch_drop from generate_everything_about_these_materials().
    # Example: direct beet LootTable support for no_silk_touch_drop on another block.
    Block.from_id("raw_steel_block").no_silk_touch_drop = LootTable({
        "type": "minecraft:fishing",
        "pools": [{
            "rolls": 1,
            "entries": [{
                "type": "minecraft:loot_table",
                "value": Item.from_id("raw_steel").loot_table,
                "functions": [{
                    "function": "minecraft:set_count",
                    "count": {"type": "minecraft:uniform", "min": 4, "max": 9}
                }]
            }]
        }]
    })

    return

