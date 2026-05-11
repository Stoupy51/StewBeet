
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Generate all items/blocks related to the steel_ingot material
    # (reads textures from the configured textures_folder)
    ORES_CONFIGS: dict = {
        "steel_ingot": EquipmentsConfig(
            equivalent_to=DefaultOre.IRON,
            pickaxe_durability=3 * VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"],
            attributes={"attack_damage": 1, "armor": 0.5, "mining_efficiency": 2},
        ),
        # Vanilla material without custom equipments
        "minecraft:stone": None,
    }
    generate_everything_about_these_materials(ORES_CONFIGS)

    # Set vanilla blocks for the generated custom blocks
    Block.from_id("steel_block").vanilla_block = VanillaBlock(id="minecraft:iron_block")
    Block.from_id("raw_steel_block").vanilla_block = VanillaBlock(id="minecraft:raw_iron_block")

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
