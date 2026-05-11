
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Explicit painting data (texture name, author, title, size)
    Painting(
        id="test_painting",
        painting_data=PaintingData(
            texture="stewbeet_painting_2x2",
            author={"text": "Test Author", "color": "yellow"},
            title={"text": "Test Title", "color": "gray"},
            width=2,
            height=2,
        ),
    )

    # Minimal painting — defaults for author (project_author) and title (item_name)
    Painting(
        id="stewbeet_painting",
        painting_data=PaintingData(width=1, height=1),
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
