
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Painting with all fields explicitly set
    Painting(
        id="test_painting_explicit",
        painting_data=PaintingData(
            texture="stewbeet_painting_2x2",
            author={"text": "TestAuthor", "color": "yellow"},
            title={"text": "Test Piece", "color": "gray"},
            width=2, height=2
        ),
        recipes=[
            CraftingShapedRecipe(
                category="decorations",
                shape=["###", "#F#", "###"],
                ingredients={"#": Ingr("minecraft:egg"), "F": Ingr("minecraft:beetroot")},
            )
        ]
    )

    # Painting with default title and author (derived from project config)
    Painting(
        id="test_painting_defaults",
        painting_data=PaintingData(
            # texture defaults to "test_painting_defaults" (same as item id)
            width=1, height=1
        ),
        recipes=[
            CraftingShapelessRecipe(
                category="decorations",
                ingredients=[Ingr("minecraft:painting"), Ingr("minecraft:red_dye")],
            )
        ]
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
