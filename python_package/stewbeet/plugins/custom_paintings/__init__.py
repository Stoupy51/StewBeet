
# Imports
import os

import stouputils as stp
from beet import Context, PaintingVariant, PaintingVariantTag
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.painting import Painting
from ...core.constants import PAINTING_DATA
from ...core.utils.io import set_json_encoder, texture_mcmeta


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.custom_paintings'")
def beet_default(ctx: Context) -> None:
    """ Main entry point for the custom paintings plugin.
    This plugin handles the generation of custom paintings for the datapack and resource pack.

    Requires a valid definitions in Mem.definitions in order to function properly using constant 'PAINTING_DATA'.

    Args:
        ctx (Context): The beet context.
    """
    Mem.ctx = ctx
    textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")
    placeable_values: list[str] = []

    # Assertions
    assert textures_folder, "The 'textures_folder' key is missing in the 'stewbeet' section of the beet.yml file."

    # For each item definition that has painting data,
    for item, data in Mem.definitions.items():
        painting_data: JsonDict = data.get(PAINTING_DATA, {})
        if painting_data:
            obj_painting = Painting.from_id(item)

            ## Datapack
            # Add the item id to the list of painting variants values
            if not painting_data.get("not_placeable", False):
                placeable_values.append(obj_painting.variant)

            # Set default author and title if not provided
            if "author" not in painting_data:
                painting_data["author"] = {"text": Mem.ctx.project_author or "Unknown"}
            if "title" not in painting_data:
                painting_data["title"] = data.get("item_name") or {"text": item.replace("_", " ").title()}

            # Create ordered painting data with asset_id first
            ordered_painting_data = {"asset_id": obj_painting.asset_id}
            ordered_painting_data.update(painting_data)
            ordered_painting_data.pop("not_placeable", None)
            ordered_painting_data.pop("texture", None)

            # Create the painting definition
            obj_painting.variant.write(set_json_encoder(PaintingVariant(ordered_painting_data)))

            ## Resource pack
            # Get the texture path
            if "texture" in painting_data:
                texture: str = painting_data["texture"]
                src: str = stp.relative_path(f"{textures_folder}/{texture}.png")
            else:
                matching_textures: list[str] = [
                    stp.relative_path(f"{root}/{file}")
                    for root, _, files in os.walk(textures_folder)
                    for file in files if file == f"{item}.png"
                ]
                if not matching_textures:
                    stp.error(f"No texture found for painting '{item}' in the textures folder '{textures_folder}'. Expected a file named '{item}.png'.")
                    continue
                elif len(matching_textures) > 1:
                    stp.warning(f"Multiple textures found for painting '{item}' in the textures folder '{textures_folder}'. Using the first one found: '{matching_textures[0]}'.")
                src: str = matching_textures[0]
            dst = obj_painting.painting_texture

            # Check if the texture is not already registered
            if not dst.exists():
                dst.write(texture_mcmeta(src))

    # Add the painting variant tag to the context data
    if placeable_values:
        Mem.ctx.data["minecraft"].painting_variant_tags["placeable"] = set_json_encoder(PaintingVariantTag({"values": placeable_values}))

