
# pyright: reportArgumentType=false
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os

import stouputils as stp
from beet import ItemModel, Model, Texture
from PIL import Image

from ...core import (
	CUSTOM_ITEM_VANILLA,
	BlockFunctions,
	Item,
	JsonDict,
	Mem,
	set_json_encoder,
	texture_mcmeta,
	write_advancement,
	write_function,
	write_load_file,
)

# Constants
ENERGY_CABLE_MODELS_FOLDER: str = stp.get_root_path(__file__) + "/energy_cable_models"

# Setup energy cables work and visuals
def energy_cables_models(cables: list[str]) -> None:
	""" Setup energy cables models and functions for SimplEnergy.

	Args:
		cables (list[str]): List of cables to setup. (e.g. ["simple_cable", "advanced_cable", "elite_cable"])
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")

	# Setup parent cable model
	parent_model: JsonDict = {"parent":"block/block","display":{"fixed":{"rotation":[180,0,0],"translation":[0,-4,0],"scale":[1.005,1.005,1.005]}}}
	Mem.ctx.assets[ns].models["block/cable_base"] = set_json_encoder(Model(parent_model))

	# Setup cables models
	for cable in cables:
		# Setup vanilla model for this cable
		content: JsonDict = {"model": {"type": "minecraft:range_dispatch","property": "minecraft:custom_model_data","entries": []}}

		# Create all the cables variants models
		for root, _, files in os.walk(ENERGY_CABLE_MODELS_FOLDER):
			for file in files:
				if file.endswith(".json"):
					path: str = f"{root}/{file}"

					# Load the json file
					json_file: JsonDict = stp.json_load(path)

					# Create the new json
					new_json: JsonDict = {
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

		# Copy texture to resource pack
		Mem.ctx.assets[ns].textures[f"block/{cable}"] = texture_mcmeta(f"{textures_folder}/{cable}.png")

		# On placement, rotate
		write_function(BlockFunctions(cable).place_secondary, f"""
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



# Setup item cables work and visuals
def item_cables_models(cables: dict[str, dict[str, str] | None]) -> None:
	""" Setup item cables models and functions for SimplEnergy.

	Args:
		cables (dict[str, dict[str, str]]): Dictionary of item cables to setup.
			Each key is the cable name, and the value is a dictionary mapping model textures to their paths
			The mapping dictionnary is optional, if not provided, it will use the default model paths.
			(e.g. {"item_cable":{"0":"item_cable/center","1":"item_cable/pillon","2":"item_cable/glass"}})
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")

	# Constants for cable generation (same as your code principle)
	sides: list[str] = ["u", "d", "n", "s", "e", "w"]
	cube_names: list[str] = ["top", "bottom", "north", "south", "east", "west"]

	# Path to the base cable model
	cable_base_path: str = stp.get_root_path(__file__) + "/item_cable_models/cable_base.json"

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
		content: JsonDict = {"model": {"type": "minecraft:range_dispatch","property": "minecraft:custom_model_data","entries": []}}

		# Generate all variants (64 possibilities like your code)
		for i in range(64):
			# Generate indicator like your code: _n _u _d _s _e _w _ns _ne _nw _se _sw etc
			indicator: str = "_"
			for side in sides:
				if i & (1 << sides.index(side)):
					indicator += side

			# Load the base cable model
			base_data: JsonDict = stp.json_load(cable_base_path)

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
				Mem.ctx.assets[ns].textures[dst] = texture_mcmeta(src)

		# On placement, add itemio.cable tag and call init function
		write_function(BlockFunctions(cable).place_secondary, f"""
# Item cable setup for models, and common itemio cable tag
tag @s add {ns}.cable
tag @s add itemio.cable
function #itemio:calls/cables/init
""")

		# On destruction, call destroy function
		write_function(BlockFunctions(cable).destroy, """
# Item cable destruction cleanup
function #itemio:calls/cables/destroy
""")

	# Update cable_model function
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


# Setup servo-mechanisms work and visuals
def servo_mechanisms_models(servos: dict[str, dict[str, str] | None]) -> None:
	""" Setup servo mechanisms models and functions for SimplEnergy.

	Args:
		servos (dict[str, dict[str, str]]): Dictionary of servo mechanisms to setup.
			Each key is the servo name, and the value is a dictionary mapping model textures to their paths (excluding the 'type' key)
			The mapping dictionnary is optional, if not provided, it will use the default model paths.
			(e.g. {"servo_extractor": {"type": "extract", "default": "servo/extract_default", "connected": "servo/extract_connected"}})
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")

	# Path to the base servo models
	models_path: str = stp.get_root_path(__file__) + "/servo_mechanism_models"

	# Register the base block models
	for base in ("block", "item"):
		model_data: JsonDict = stp.json_load(f"{models_path}/base_{base}.json")
		if base == "item":
			model_data["parent"] = f"{ns}:block/servo/base_block"
		Mem.ctx.assets[ns].models[f"block/servo/base_{base}"] = set_json_encoder(Model(model_data), max_level=3)

	# Handle parameters
	for servo, textures in servos.items():
		if textures is None:
			textures = {}
		typ: str = textures.get("type", "extract")  # Default to 'extract' if not specified
		default_texture: str = textures.get("default", f"servo/{typ}_default")
		connected_texture: str = textures.get("connected", f"servo/{typ}_connected")

		# Register the block model
		base_model: JsonDict = stp.json_load(f"{models_path}/{typ}_block.json")
		base_model["parent"] = f"{ns}:block/servo/base_block"
		base_model["textures"] = {"0": f"{ns}:block/{default_texture}", "particle": f"{ns}:block/{default_texture}"}
		Mem.ctx.assets[ns].models[f"block/servo/{typ}_block"] = set_json_encoder(Model(base_model), max_level=3)

		# Register the connected model
		connected_model: JsonDict = stp.json_load(f"{models_path}/{typ}_connected.json")
		connected_model["parent"] = f"{ns}:block/servo/base_block"
		connected_model["textures"] = {"0": f"{ns}:block/{connected_texture}", "particle": f"{ns}:block/{connected_texture}"}
		Mem.ctx.assets[ns].models[f"block/servo/{typ}_connected"] = set_json_encoder(Model(connected_model), max_level=3)

		# Register the off model (grayed out version of the default texture, shown when the servo is disabled)
		off_texture: str = f"servo/{typ}_off"
		off_model: JsonDict = stp.json_load(f"{models_path}/{typ}_block.json")
		off_model["parent"] = f"{ns}:block/servo/base_block"
		off_model["textures"] = {"0": f"{ns}:block/{off_texture}", "particle": f"{ns}:block/{off_texture}"}
		Mem.ctx.assets[ns].models[f"block/servo/{typ}_off"] = set_json_encoder(Model(off_model), max_level=3)

		# Register the item model
		item_model: JsonDict = stp.json_load(f"{models_path}/{typ}_item.json")
		item_model["parent"] = f"{ns}:block/servo/base_item"
		item_model["textures"] = {"0": f"{ns}:block/{default_texture}", "particle": f"{ns}:block/{default_texture}"}
		Mem.ctx.assets[ns].models[f"block/servo/{typ}_item"] = set_json_encoder(Model(item_model), max_level=3)

		# Register items files (for default, connected and off)
		for texture in ("block", "connected", "off"):
			model_data = {
				"model": {
					"type": "minecraft:model",
					"model": f"{ns}:block/servo/{typ}_{texture}"
				}
			}
			Mem.ctx.assets[ns].item_models[f"servo/{typ}_{texture}"] = set_json_encoder(ItemModel(model_data), max_level=3)

		# Copy textures to resource pack
		for texture_key in ("default", "connected"):
			texture_path: str = textures.get(texture_key, f"{typ}_{texture_key}")
			src: str = f"{textures_folder}/{texture_path}.png"
			dst: str = f"block/{texture_path}"

			# Check if the source file exists and if the texture is not already registered
			if os.path.exists(src) and (not Mem.ctx.assets[ns].textures.get(dst)):
				Mem.ctx.assets[ns].textures[dst] = texture_mcmeta(src)

		# Generate the grayed out "off" texture from the default texture (desaturated and darkened)
		off_dst: str = f"block/{off_texture}"
		default_src: str = f"{textures_folder}/{textures.get('default', f'{typ}_default')}.png"
		if os.path.exists(default_src) and (not Mem.ctx.assets[ns].textures.get(off_dst)):
			with Image.open(default_src) as base_image:
				rgba: Image.Image = base_image.convert("RGBA")
			r, g, b, a = rgba.split()
			gray = Image.merge("RGB", (r, g, b)).convert("L").point(lambda p: int(p * 0.5))
			off_image: Image.Image = Image.merge("RGBA", (gray, gray, gray, a))
			Mem.ctx.assets[ns].textures[off_dst] = Texture(off_image)

		## Working functions
		# On placement, add necessary tag and call init function
		item = Item.from_id(servo)
		ns_data: dict[str, int] = item.components.get("custom_data", {}).get(ns, {})
		stack_limit: int = ns_data.get("stack_limit", 1)
		retry_limit: int = ns_data.get("retry_limit", 1)
		write_function(BlockFunctions(servo).place_secondary, f"""
# Servo mechanism setup (1 item by 1 item: stack_limit)
tag @s add itemio.servo.{typ}
tag @s add itemio.servo
tag @s add {ns}.servo
scoreboard players set @s itemio.servo.stack_limit {stack_limit}
scoreboard players set @s itemio.servo.retry_limit {retry_limit}
scoreboard players set @s {ns}.servo_off 0
function #itemio:calls/servos/init
""")
		# On destruction, call destroy function of itemio
		write_function(BlockFunctions(servo).destroy, """
# Servo mechanism destruction cleanup
function #itemio:calls/servos/destroy
""")

	# Update the servo model on itemio network changes (delegates to the shared model logic)
	write_function(f"{ns}:calls/itemio/network_update", f"""
# Stop if not {ns} servo
execute unless entity @s[tag={ns}.custom_block,tag={ns}.servo] run return fail

# Apply the model depending on the on/off state and the network connection
function {ns}:utils/servo/update_model
""", tags=["itemio:event/network_update"])

	# Setup the "rotate to toggle on/off" feature
	servo_toggle(servos)
	return


# Setup the ability to turn servos off and on by rotating (right-clicking) them
def servo_toggle(servos: dict[str, dict[str, str] | None]) -> None:
	""" Setup the functions allowing players to turn servo mechanisms off and on by rotating them.

	Rotating (right-clicking) a servo item frame changes its 'ItemRotation'. A vanilla advancement listening to
	the 'minecraft:player_interacted_with_entity' trigger detects the interaction (so nothing runs every tick),
	then the nearby servos are checked: an odd rotation disables the rotated one (grayed out texture, item
	transfers stopped by removing the 'itemio.servo.extract' / 'itemio.servo.insert' tag), an even rotation
	enables it back to normal. As the check only acts when the parity differs, only the rotated servo toggles.

	Args:
		servos (dict[str, dict[str, str]]): Same servos dictionary as the one passed to 'servo_mechanisms_models'.
	"""
	ns: str = Mem.ctx.project_id
	servo_types: dict[str, str] = {servo: (textures or {}).get("type", "extract") for servo, textures in servos.items()}

	# Score holding the on/off state of each servo (created at load time)
	write_load_file(f"\n# Score for the on/off state of servo mechanisms\nscoreboard objectives add {ns}.servo_off dummy\n")

	# Advancement detecting the interaction with a servo item frame, then revoked and handled by a function
	write_advancement(f"{ns}:technical/servo_toggle", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:player_interacted_with_entity",
				"conditions": {
					"entity": {
						"minecraft:entity_tags": {"any_of": [f"{ns}.servo"]},
					},
				},
			},
		},
		"requirements": [["requirement"]],
		"rewards": {"function": f"{ns}:utils/servo/on_interact"},
	})

	# Reward function: revoke the advancement, then check the servos around the player (only the rotated one toggles)
	write_function(f"{ns}:utils/servo/on_interact", f"""
# Revoke the advancement so it can trigger again
advancement revoke @s only {ns}:technical/servo_toggle

# Check the servos within reach (the change detection makes it a no-op for the ones that did not rotate)
execute as @e[tag={ns}.servo,distance=..24] run function {ns}:utils/servo/check
""")

	# Check the rotation parity and apply the on/off state only when it changed
	write_function(f"{ns}:utils/servo/check", f"""
# Compute the rotation parity (0 = on, 1 = off)
scoreboard players set #two {ns}.data 2
execute store result score #parity {ns}.data run data get entity @s ItemRotation
scoreboard players operation #parity {ns}.data %= #two {ns}.data

# Keep the servo visually aligned while on (any even rotation is normalized to 0)
execute if score #parity {ns}.data matches 0 unless data entity @s {{ItemRotation:0b}} run data modify entity @s ItemRotation set value 0b

# Apply the state only when the parity differs from the current state
execute if score #parity {ns}.data matches 0 unless score @s {ns}.servo_off matches 0 run function {ns}:utils/servo/enable
execute if score #parity {ns}.data matches 1 unless score @s {ns}.servo_off matches 1 run function {ns}:utils/servo/disable
""")

	# Enable: allow item transfers again by adding back the servo tag, then restore the normal model
	enable_tags: str = "\n".join(
		f"execute if entity @s[tag={ns}.{servo}] run tag @s add itemio.servo.{typ}"
		for servo, typ in servo_types.items()
	)
	write_function(f"{ns}:utils/servo/enable", f"""
# Mark the servo as on and allow item transfers again
scoreboard players set @s {ns}.servo_off 0
{enable_tags}

# Restore the normal model and play feedback
function {ns}:utils/servo/update_model
playsound minecraft:block.lever.click block @a[distance=..16] ~ ~ ~ 0.6 1.2
""")

	# Disable: stop item transfers by removing the servo tag, then apply the grayed out model
	write_function(f"{ns}:utils/servo/disable", f"""
# Mark the servo as off and stop item transfers
scoreboard players set @s {ns}.servo_off 1
tag @s remove itemio.servo.extract
tag @s remove itemio.servo.insert

# Apply the grayed out model and play feedback
function {ns}:utils/servo/update_model
playsound minecraft:block.lever.click block @a[distance=..16] ~ ~ ~ 0.6 0.7
""")

	# Shared model logic: grayed out when off, normal (depending on the network connection) when on
	model_lines: list[str] = [
		f'execute if score @s {ns}.servo_off matches 1 if entity @s[tag={ns}.{servo}] run data modify entity @s Item.components."minecraft:item_model" set value "{ns}:servo/{typ}_off"'
		for servo, typ in servo_types.items()
	]
	for servo, typ in servo_types.items():
		for number, texture in ((0, "block"), (1, "connected")):
			model_lines.append(
				f'execute if score @s {ns}.servo_off matches 0 if score @s itemio.math matches {number} if entity @s[tag={ns}.{servo}] run '
				f'data modify entity @s Item.components."minecraft:item_model" set value "{ns}:servo/{typ}_{texture}"'
			)
	write_function(f"{ns}:utils/servo/update_model", "\n".join(model_lines) + "\n")
	return

