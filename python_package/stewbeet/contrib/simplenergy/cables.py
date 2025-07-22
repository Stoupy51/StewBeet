
# Imports
import os

from beet import ItemModel, Model, Texture
from stouputils.io import get_root_path, super_json_load

from ...core import CUSTOM_ITEM_VANILLA, JsonDict, Mem, set_json_encoder, write_function

# Constants
ENERGY_CABLE_MODELS_FOLDER: str = get_root_path(__file__) + "/energy_cable_models"

# Setup machines work and visuals
def energy_cables_models(cables: list[str]) -> None:
	""" Setup energy cables models and functions for SimplEnergy.

	Args:
		cables (list[str]): List of cables to setup. (e.g. ["simple_cable", "advanced_cable", "elite_cable"])
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.stewbeet.textures_folder

	# Setup parent cable model
	parent_model: dict = {"parent":"block/block","display":{"fixed":{"rotation":[180,0,0],"translation":[0,-4,0],"scale":[1.005,1.005,1.005]}}}
	Mem.ctx.assets[ns].models["block/cable_base"] = set_json_encoder(Model(parent_model))

	# Setup cables models
	for cable in cables:
		# Setup vanilla model for this cable
		content: dict = {"model": {"type": "minecraft:range_dispatch","property": "minecraft:custom_model_data","entries": []}}

		# Create all the cables variants models
		for root, _, files in os.walk(ENERGY_CABLE_MODELS_FOLDER):
			for file in files:
				if file.endswith(".json"):
					path: str = f"{root}/{file}"

					# Load the json file
					json_file: dict = super_json_load(path)

					# Create the new json
					new_json: dict = {
						"parent": f"{ns}:block/cable_base",
						"textures": {"0": f"{ns}:block/{cable}", "particle": f"{ns}:block/{cable}"},
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
	cables_str: str = "\n".join([
		f"execute if entity @s[tag={ns}.{cable}] run item replace entity @s contents with {CUSTOM_ITEM_VANILLA}[item_model=\"{ns}:{cable}\"]"
		for cable in cables
	])
	cable_update_content: str = f"""
# Stop if not {ns} cable
execute unless entity @s[tag={ns}.custom_block,tag=energy.cable] run return fail

# Apply the model dynamically based on cable tags
{cables_str}

# Get the right model
item modify entity @s contents {{"function": "minecraft:set_custom_model_data","floats": {{"values": [{{"type": "minecraft:score","target": "this","score": "energy.data"}}],"mode": "replace_all"}}}}
"""
	write_function(f"{ns}:calls/energy/cable_update", cable_update_content, tags=["energy:v1/cable_update"])
	return



# Setup machines work and visuals
def item_cables_models(cables: dict[str, dict[str, str] | None]) -> None:
	""" Setup item cables models and functions for SimplEnergy.

	Args:
		cables (dict[str, dict[str, str]]): Dictionary of item cables to setup.
			Each key is the cable name, and the value is a dictionary mapping model textures to their paths
			The mapping dictionnary is optional, if not provided, it will use the default model paths.
			(e.g. {"item_cable":{"0":"item_cable/center","1":"item_cable/pillon","2":"item_cable/glass"}})
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.stewbeet.textures_folder

	# Constants for cable generation (same as your code principle)
	sides: list[str] = ["u", "d", "n", "s", "e", "w"]
	cube_names: list[str] = ["top", "bottom", "north", "south", "east", "west"]

	# Path to the base cable model
	cable_base_path: str = get_root_path(__file__) + "/item_cable_models/cable_base.json"

	# Handle parameters
	for cable, textures in cables.items():
		if textures is None:
			textures = {}
		if not textures.get("0"):
			textures["0"] = f"{cable}/center"
		if not textures.get("1"):
			textures["1"] = f"{cable}/pillon"
		if not textures.get("2"):
			textures["2"] = f"{cable}/glass"
		if not textures.get("particle"):
			textures["particle"] = f"{cable}/center"

		# Setup vanilla model for this item cable
		content: dict = {"model": {"type": "minecraft:range_dispatch","property": "minecraft:custom_model_data","entries": []}}

		# Generate all variants (64 possibilities like your code)
		for i in range(64):
			# Generate indicator like your code: _n _u _d _s _e _w _ns _ne _nw _se _sw etc
			indicator: str = "_"
			for side in sides:
				if i & (1 << sides.index(side)):
					indicator += side

			# Load the base cable model
			base_data: dict = super_json_load(cable_base_path)

			# Update textures to use the current cable's textures
			base_data["textures"] = {
				"0": f"{ns}:block/{textures['0']}",
				"1": f"{ns}:block/{textures['1']}",
				"2": f"{ns}:block/{textures['2']}",
				"particle": f"{ns}:block/{textures['particle']}"
			}

			# Remove elements for sides that are not connected (same principle as your code)
			for side in sides:
				if side not in indicator:
					cube_name = cube_names[sides.index(side)]
					j = 0
					while j < len(base_data["elements"]):
						element_name = base_data["elements"][j].get("name", "")
						if cube_name in element_name:
							base_data["elements"].pop(j)
							j -= 1
						j += 1

			# Save the variant model
			variant_name = f"variant{indicator}" if indicator != "_" else "no_variant"
			Mem.ctx.assets[ns].models[f"block/{cable}/{variant_name}"] = set_json_encoder(Model(base_data), max_level=3)

			# Add entry to the range dispatch model
			model_path = f"{ns}:block/{cable}/{variant_name}"
			content["model"]["entries"].append({"threshold": i, "model": {"type": "minecraft:model", "model": model_path}})

		# Write the vanilla model for this item cable
		Mem.ctx.assets[ns].item_models[cable] = set_json_encoder(ItemModel(content), max_level=3)

		# Copy textures to resource pack
		for texture_path in textures.values():
			src: str = f"{textures_folder}/{texture_path}.png"
			dst: str = f"block/{texture_path}"

			# Check if the source file exists and if the texture is not already registered
			if os.path.exists(src) and (not Mem.ctx.assets[ns].textures.get(dst)):
				mcmeta: JsonDict | None = None if not os.path.exists(src + ".mcmeta") else super_json_load(f"{src}.mcmeta")
				Mem.ctx.assets[ns].textures[dst] = Texture(source_path=src, mcmeta=mcmeta)

		# On placement, add itemio.cable tag and call init function
		write_function(f"{ns}:custom_blocks/{cable}/place_secondary", f"""
# Item cable setup for models, and common itemio cable tag
tag @s add {ns}.cable
tag @s add itemio.cable
function #itemio:calls/cables/init
""")

		# On destruction, call destroy function
		write_function(f"{ns}:custom_blocks/{cable}/destroy", """
# Item cable destruction cleanup
function #itemio:calls/cables/destroy
""")

	# Update_cable_model function
	cables_str: str = "\n".join([
		f"execute if entity @s[tag={ns}.{cable}] run item replace entity @s contents with {CUSTOM_ITEM_VANILLA}[item_model=\"{ns}:{cable}\"]"
		for cable in cables
	])
	cable_update_content: str = f"""
# Stop if not {ns} cable
execute unless entity @s[tag={ns}.custom_block,tag=itemio.cable] run return fail

# Apply the model dynamically based on cable tags
{cables_str}

# Get the right model
item modify entity @s contents {{"function": "minecraft:set_custom_model_data","floats": {{"values": [{{"type": "minecraft:score","target": "this","score": "itemio.math"}}],"mode": "replace_all"}}}}
"""
	write_function(f"{ns}:calls/itemio/cable_update", cable_update_content, tags=["itemio:event/cable_update"])
	return

