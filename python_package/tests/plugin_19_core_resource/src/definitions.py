
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Plain item: exercises loot_table / item_model / model / texture
    Item(id="plain_item", base_item="minecraft:diamond", manual_category="misc")

    # Item whose recipe produces x4: exercises loot_table_for()
    Item(
        id="bulk_item",
        base_item="minecraft:iron_ingot",
        manual_category="misc",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[Ingr("minecraft:iron_nugget")],
                result_count=4,
            )
        ],
    )

    # Item overriding its item_model component: item_model must follow the override,
    # generated_item_model must not
    Item(
        id="overridden_model",
        base_item="minecraft:stick",
        manual_category="misc",
        components={"item_model": "minecraft:air"},
    )

    # Regular custom block: exercises Block.functions.* and no_silk_touch_loot_table
    Block(
        id="regular_block",
        vanilla_block=VanillaBlock(id="minecraft:iron_block"),
        manual_category="misc",
        no_silk_touch_drop=NoSilkTouchDrop(id="plain_item", count=1),
    )

    # Item frame custom block: exercises alternative_advancement
    BlockAlternative(
        id="alternative_block",
        vanilla_block=VanillaBlock(contents=True),
        manual_category="misc",
    )

    # Player head custom block: exercises head_advancement and head_search*
    BlockHead(
        id="head_block",
        vanilla_block=VanillaBlock(id="minecraft:player_head"),
        manual_category="misc",
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
