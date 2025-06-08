
# Imports
from beet import Context
from beet.core.utils import JsonDict
from stewbeet import core

# Configuration to generate everything about the material based on "steel_ingot"
ORES_CONFIGS: dict[str, core.EquipmentsConfig|None] = {
    "steel_ingot":	core.EquipmentsConfig(
        # This steel is equivalent to iron,
        equivalent_to = core.DefaultOre.IRON,

        # But, has more durability (3 times more)
        pickaxe_durability = 3 * core.VanillaEquipments.PICKAXE.value[core.DefaultOre.IRON]["durability"],

        # And, does 1 more damage per hit (mainhand), and has 0.5 more armor, and mines 20% faster (pickaxe)
        attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
    ),

    # Simple material stone, this will automatically detect stone stick and rod textures.
    "minecraft:stone": None,
}

# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    database: JsonDict = core.Mem.database

    # Generate ores in database (add every stuff (found in the textures folder) related to the given materials, to the database)
    core.generate_everything_about_these_materials(ORES_CONFIGS)

    database["steel_ingot"][core.WIKI_COMPONENT] = [
        {"text":"Here is an example of a wiki component, this text component will be displayed as a button in the manual.\n"},
        {"text":"You can write anything you want here.","color":"yellow"},
    ]

    # Generate custom disc records
    core.generate_custom_records("auto")

    # Add a super stone block that can be crafted with 9 deepslate or stone, and has cobblestone as base block
    database["super_stone"] = {
        "id": core.CUSTOM_BLOCK_VANILLA,												# Placeholder for the base block
        core.VANILLA_BLOCK: {"id": "minecraft:cobblestone", "apply_facing": False},	# Base block
        core.RESULT_OF_CRAFTING: [													# Crafting recipes (shaped and shapeless examples)
            {"type":"crafting_shaped","result_count":1,"group":"super_stone","category":"blocks","shape":["XXX","XXX","XXX"],"ingredients": {"X": core.ingr_repr("minecraft:stone")}},
            {"type":"crafting_shapeless","result_count":1,"group":"super_stone","category":"blocks","ingredients": 9 * [core.ingr_repr("minecraft:deepslate")] },
        ],
        # Exemple of recipe with vanilla result (not custom item)
        core.USED_FOR_CRAFTING: [
            {"type":"smelting","result_count":1,"cookingtime":200,"experience":0.1,"group":"super_stone",
             "category":"blocks","ingredient":core.ingr_repr("super_stone", ns),"result":core.ingr_repr("minecraft:diamond")},
        ]
    }

    # Don't forget to add the vanilla blocks for the custom blocks (not automatic even though they was recognized by generate_everything_about_these_materials())
    database["steel_block"][core.VANILLA_BLOCK] = {"id": "minecraft:iron_block", "apply_facing": False}			# Placeholder for the base block
    database["raw_steel_block"][core.VANILLA_BLOCK] = {"id": "minecraft:raw_iron_block", "apply_facing": False}	# Placeholder for the base block

    # Add a recipe for the future generated manual (the manual recipe will show up in itself)
    database["manual"] = {
        "id": "minecraft:written_book", "category": "misc", "item_name": ctx.meta.stewbeet.manual.name,
        core.RESULT_OF_CRAFTING: [
            # Put a book and a steel ingot in the crafting grid to get the manual
            {"type":"crafting_shapeless","result_count":1,"group":"manual","category":"misc","ingredients": [core.ingr_repr("minecraft:book"), core.ingr_repr("steel_ingot", ns)]},

            # Put the manual in the crafting grid to get the manual back (update the manual)
            {"type":"crafting_shapeless","result_count":1,"group":"manual","category":"misc","ingredients": [core.ingr_repr("manual", ns)]},
        ],
    }

    # Add item categories to the remaining items (should select 'shazinho' and 'super_stone')
    for item in database.values():
        if not item.get("category"):
            item["category"] = "misc"

    # Final adjustments, you definitively should keep them!
    core.add_item_model_component(black_list = ["item_ids","you_don't_want","in_that","list"])
    core.add_item_name_and_lore_if_missing()
    core.add_private_custom_data_for_namespace()		# Add a custom namespace for easy item detection
    core.add_smithed_ignore_vanilla_behaviours_convention()	# Smithed items convention

