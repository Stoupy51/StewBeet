
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ruby_ingot — the "ingot" unit of the ruby material
    Item(
        id="ruby_ingot",
        base_item="minecraft:red_dye",
        manual_category="misc",
        recipes=[
            # 9 rubies from one block (for SimpleDrawer conversion ratio)
            CraftingShapelessRecipe(
                result_count=9,
                category="misc",
                group="ruby",
                ingredients=[Ingr("ruby_block")],
            ),
        ],
    )

    # ruby_nugget — the "nugget" unit
    Item(
        id="ruby_nugget",
        base_item="minecraft:pink_dye",
        manual_category="misc",
        recipes=[
            # 9 nuggets from one ingot
            CraftingShapelessRecipe(
                result_count=9,
                category="misc",
                group="ruby",
                ingredients=[Ingr("ruby_ingot")],
            ),
        ],
    )

    # ruby_block — the "block" unit with smithed.dict
    ruby_block = Item(
        id="ruby_block",
        base_item="minecraft:red_concrete",
        manual_category="misc",
        recipes=[
            # 1 block from 9 ingots
            CraftingShapedRecipe(
                result_count=1,
                category="misc",
                group="ruby",
                shape=["XXX", "XXX", "XXX"],
                ingredients={"X": Ingr("ruby_ingot")},
            ),
        ],
    )
    # Manually inject the smithed dict so SimpleDrawer can discover this material
    ruby_block.components.setdefault("custom_data", {}).setdefault("smithed", {})["dict"] = {
        "block": {"ruby": True}
    }

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
