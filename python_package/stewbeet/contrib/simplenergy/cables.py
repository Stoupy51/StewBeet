
# Imports
import os

from beet import ItemModel, Model, Texture
from stouputils.io import get_root_path, super_json_load

from ...core import CUSTOM_ITEM_VANILLA, JsonDict, Mem, set_json_encoder, write_function

# Constants
CABLE_MODELS_FOLDER: str = get_root_path(__file__) + "/cable_models"

# Setup machines work and visuals
def setup_cables_models(cables: list[str]) -> None:
	""" Setup cables models and functions for SimplEnergy.

	Args:
		cables (list[str]): List of cables to setup. (e.g. ["simple_cable", "advanced_cable", "elite_cable"])
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.stewbeet.textures_folder

	# Setup parent cable model
	parent_model: dict = {"parent":"block/block","display":{"fixed":{"rotation":[180,0,0],"translation":[0,-4,0],"scale":[1.005,1.005,1.005]}}}
	Mem.ctx.assets[ns].models["block/cable_base"] = set_json_encoder(Model(parent_model))

	# Setup cables models
	cables: list[str] = [item for item in Mem.definitions if "cable" in item]
	for cable in cables:
		# Setup vanilla model for this cable
		content: dict = {"model": {"type": "minecraft:range_dispatch","property": "minecraft:custom_model_data","entries": []}}

		# Create all the cables variants models
		for root, _, files in os.walk(CABLE_MODELS_FOLDER):
			for file in files:
				if file.endswith(".json"):
					path: str = f"{root}/{file}"

					# Load the json file
					json_file: dict = super_json_load(path)

					# Create the new json
					new_json: dict = {
						"parent": f"{ns}:block/cable_base",
						"textures": {"0": f"{ns}:block/{cable}"}
					}
					new_json.update(json_file)

					# Write the new json
					no_ext: str = os.path.splitext(file)[0]
					Mem.ctx.assets[ns].models[f"block/{cable}/{no_ext}"] = set_json_encoder(Model(new_json), max_level=3)

		# Link vanilla model
		for i in range(64):
			# Get faces
			down: str = "d" if i & 1 else ""
			up: str = "u" if i & 2 else ""
			north: str = "n" if i & 4 else ""
			south: str = "s" if i & 8 else ""
			west: str = "w" if i & 16 else ""
			east: str = "e" if i & 32 else ""
			model_path: str = f"{ns}:block/{cable}/variant_{up}{down}{north}{south}{east}{west}"
			if model_path.endswith("_"):
				model_path = model_path[:-1]

			# Add override
			content["model"]["entries"].append({"threshold": i, "model":{"type": "minecraft:model", "model": model_path}})

		# Write the vanilla model for this cable
		Mem.ctx.assets[ns].item_models[cable] = set_json_encoder(ItemModel(content), max_level=3)

		# Copy texture
		src: str = f"{textures_folder}/{cable}.png"
		mcmeta: JsonDict | None = None if not os.path.exists(src + ".mcmeta") else super_json_load(f"{src}.mcmeta")
		Mem.ctx.assets[ns].textures[f"block/{cable}"] = Texture(source_path=src, mcmeta=mcmeta)

		# On placement, rotate
		write_function(f"{ns}:custom_blocks/{cable}/place_secondary", f"""
# Cable rotation for models, and common cable tag
data modify entity @s item_display set value "fixed"
tag @s add {ns}.cable
""")

	# Update_cable_model function
	cable_update_content: str = f"""
# Stop if not {ns} cable
execute unless entity @s[tag={ns}.custom_block,tag=energy.cable] run return fail

# Apply the model
execute if entity @s[tag={ns}.simple_cable] run item replace entity @s container.0 with {CUSTOM_ITEM_VANILLA}[item_model="{ns}:simple_cable"]
execute if entity @s[tag={ns}.advanced_cable] run item replace entity @s container.0 with {CUSTOM_ITEM_VANILLA}[item_model="{ns}:advanced_cable"]
execute if entity @s[tag={ns}.elite_cable] run item replace entity @s container.0 with {CUSTOM_ITEM_VANILLA}[item_model="{ns}:elite_cable"]

# Get the right model
data modify storage {ns}:main model_data set value {{"floats":[0.0f]}}
execute store result storage {ns}:main model_data.floats[0] float 1 run scoreboard players get @s energy.data
data modify entity @s item.components."minecraft:custom_model_data" set from storage {ns}:main model_data
data remove storage {ns}:main model_data
"""
	write_function(f"{ns}:calls/cable_update", cable_update_content, tags=["energy:v1/cable_update"])

	return

