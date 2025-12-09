
# Imports
import os

from beet import Context, PaintingVariant, PaintingVariantTag
from beet.core.utils import JsonDict
from stouputils.decorators import measure_time
from stouputils.io import relative_path
from stouputils.print import error, warning

from ...core.__memory__ import Mem
from ...core.constants import PAINTING_DATA
from ...core.utils.io import set_json_encoder, texture_mcmeta


# Main entry point
@measure_time(message="Execution time of 'stewbeet.plugins.custom_paintings'")
def beet_default(ctx: Context) -> None:
    """ Main entry point for the custom paintings plugin.
    This plugin handles the generation of custom paintings for the datapack and resource pack.

    Requires a valid definitions in Mem.definitions in order to function properly using constant 'PAINTING_DATA'.

    Args:
        ctx (Context): The beet context.
    """
    if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
        Mem.ctx = ctx
    ns: str = ctx.project_id
    textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")
    placeable_values: list[str] = []

    # Assertions
    assert textures_folder, "The 'textures_folder' key is missing in the 'stewbeet' section of the beet.yml file."

    # For each item definition that has painting data,
    for item, data in Mem.definitions.items():
        painting_data: JsonDict = data.get(PAINTING_DATA, {})
        if painting_data:

            ## Datapack
            # Add the item id to the list of painting variants values
            if not painting_data.get("not_placeable", False):
                placeable_values.append(f"{ns}:{item}")

            # Set default author and title if not provided
            if "author" not in painting_data:
                painting_data["author"] = {"text": Mem.ctx.project_author or "Unknown"}
            if "title" not in painting_data:
                painting_data["title"] = data.get("item_name") or {"text": item.replace("_", " ").title()}

            # Create ordered painting data with asset_id first
            texture_name: str = painting_data.get("texture", item)
            ordered_painting_data = {"asset_id": f"{ns}:{texture_name}"}
            ordered_painting_data.update(painting_data)
            ordered_painting_data.pop("not_placeable", None)
            ordered_painting_data.pop("texture", None)

            # Create the painting definition
            Mem.ctx.data[ns].painting_variants[item] = set_json_encoder(PaintingVariant(ordered_painting_data))

            ## Resource pack
            # Get the texture path
            if "texture" in painting_data:
                texture: str = painting_data["texture"]
                src: str = relative_path(f"{textures_folder}/{texture}.png")
            else:
                matching_textures: list[str] = [
                    relative_path(f"{root}/{file}")
                    for root, _, files in os.walk(textures_folder)
                    for file in files if file == f"{item}.png"
                ]
                if not matching_textures:
                    error(f"No texture found for painting '{item}' in the textures folder '{textures_folder}'. Expected a file named '{item}.png'.")
                    continue
                elif len(matching_textures) > 1:
                    warning(f"Multiple textures found for painting '{item}' in the textures folder '{textures_folder}'. Using the first one found: '{matching_textures[0]}'.")
                src: str = matching_textures[0]
            dst: str = f"painting/{texture_name}"

            # Check if the texture is not already registered
            if not Mem.ctx.assets[ns].textures.get(dst):
                Mem.ctx.assets[ns].textures[dst] = texture_mcmeta(src)

    # Add the painting variant tag to the context data
    if placeable_values:
        Mem.ctx.data["minecraft"].painting_variant_tags["placeable"] = set_json_encoder(PaintingVariantTag({"values": placeable_values}))

