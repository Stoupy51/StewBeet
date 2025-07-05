
# ruff: noqa: RUF012
# Imports
import json
import os
from enum import Enum

from beet import ItemModel, Model, Texture
from stouputils.io import super_json_dump, super_json_load

from ...core import Mem


# GUI Translation for
class GuiTranslation(Enum):
	brewing_stand: list[int] = [ 0, 38, -76 ]
	""" Assume you are placing GUI item model in the __fuel__ slot of a brewing stand. """
	furnace_bottom: list[int] = [ 0, 75, -76 ]
	""" Assume you are placing GUI item model in the __fuel__ slot of a furnace. """
	furnace_top: list[int] = [ 0, 39, -76 ]
	""" Assume you are placing GUI item model in the __ingredient__ slot of a furnace. """
	barrel_bottom_right: list[int] = [ -78, 75, -76 ]
	""" Assume you are placing GUI item model in the __27th__ slot of a barrel. """

# Setup GUI in resource packs
def setup_gui_in_resource_packs(gui_translations: dict[str, GuiTranslation]) -> dict[str, str]:
	""" Setup GUI item models in resource packs by creating item models and textures for each GUI.

	Args:
		gui_translations	(dict[str, GuiTranslation]): A dictionary mapping GUI names to their translation offsets.
			(e.g. {'electric_brewing_stand': GuiTranslation.brewing_stand, 'electric_furnace': GuiTranslation.furnace_bottom, ...})
	Returns:
		dict[str, str]: A dictionary mapping GUI filenames to their model paths.
			(e.g. {'gui/electric_brewing_stand.png': 'namespace:gui/electric_brewing_stand'})
	"""
	namespace: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.stewbeet.textures_folder

	# List gui asset filenames and map with 'gui/{filename}' keys
	filenames: list[str] = os.listdir(f"{textures_folder}/gui")
	gui_models: dict[str, str] = {f"gui/{x}": f"{namespace}:gui/{x.replace('.png', '')}" for x in filenames if x.endswith(".png")}

	# Write custom models
	base: dict = {
		"textures" : {},
		"elements": [
			{
				"from": [ -16, -16, 15.9375 ],
				"to": [ 32, 32, 16 ],
				"faces": {
					"north": { "uv": [ 11, 16, 0, 5 ], "rotation": 180, "texture": "#layer0" },
					"south": { "uv": [ 0, 5, 11, 16 ], "texture": "#layer0" }
				}
			}
		],
		"display": {
			"firstperson_lefthand": {"rotation": [ 0, 0, 0 ],"translation": [ 0, 0, 0 ],"scale": [ 0, 0, 0 ]},
			"gui": {"rotation": [ 0, 0, 0 ],"scale": [ 3.66, 3.66, 3.66 ]},
			"ground": {"rotation": [ 0, 0, 0 ],"translation": [ 0, 0, 0 ],"scale": [ 0, 0, 0 ]}
		},
		"gui_light":"front"
	}
	for gui, model in gui_models.items():
		content: dict = json.loads(json.dumps(base))  # Deep copy the base model
		content["textures"]["layer0"] = model.replace(":", ":item/")

		# If any translation is provided, add it to the model
		for item, translation in gui_translations.items():
			if item in gui:
				content["display"]["gui"]["translation"] = translation.value
				break

		# Else, remove the gui display and set parent to item/generated
		else:
			content["display"].pop("gui")
			content.pop("elements")
			content["parent"] = "item/generated"

		# Write the model in models/item/
		model_name = gui.replace('.png', '')
		Mem.ctx.assets[namespace].models[f"item/{model_name}"] = Model(
			super_json_dump(content, max_level=3)
		)

		# Copy the textures
		src = f"{textures_folder}/{gui}"
		mcmeta = None if not os.path.exists(src + ".mcmeta") else super_json_load(src + ".mcmeta")
		Mem.ctx.assets[namespace].textures[f"item/{model_name}"] = Texture(
			source_path=src,
			mcmeta=mcmeta
		)

		# Write the file in items/
		Mem.ctx.assets[namespace].item_models[model_name] = ItemModel(
			super_json_dump({
				"model": {
					"type": "minecraft:model",
					"model": f"{namespace}:item/{model_name}"
				},
				"oversized_in_gui": True
			}, max_level=3)
		)

	return gui_models


