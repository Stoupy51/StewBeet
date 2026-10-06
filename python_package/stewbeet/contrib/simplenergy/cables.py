
# pyright: reportArgumentType=false
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from collections.abc import Iterable

import stouputils as stp
from beet import ItemModel, Model, Texture
from PIL import Image

from ...core import (
	CUSTOM_ITEM_VANILLA,
	BlockFunctions,
	Item,
	JsonDict,
	Mem,
	advancement_entity,
	float_score,
	loot_function,
	set_json_encoder,
	texture_mcmeta,
	write_advancement,
	write_function,
	write_load_file,
)

# Constants
ENERGY_CABLE_MODELS_FOLDER: str = stp.get_root_path(__file__) + "/energy_cable_models"

ENERGY_CABLE_FACES: tuple[tuple[str, int], ...] = (("u", 2), ("d", 1), ("n", 4), ("s", 8), ("e", 32), ("w", 16))
""" Each face of an energy cable in the order its variant name lists them, and its bit in the `energy.data` model score. """

ITEM_CABLE_SIDES: tuple[tuple[str, str], ...] = (
	("u", "top"), ("d", "bottom"), ("n", "north"), ("s", "south"), ("e", "east"), ("w", "west")
)
""" Each side of an item cable, its bit in the `itemio.math` model score being its index, and the elements drawing it. """

ITEM_CABLE_TEXTURES: tuple[tuple[str, str], ...] = (("0", "center"), ("1", "pillon"), ("2", "glass"), ("particle", "center"))
""" The textures of an item cable model, and the file under the cable's folder each defaults to. """


# Setup energy cables work and visuals
def energy_cables_models(cables: list[str]) -> None:
	""" Setup energy cables models and functions for SimplEnergy.

	Args:
		cables: List of cables to setup. (e.g. ["simple_cable", "advanced_cable", "elite_cable"])
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")
	parent_model: JsonDict = {
		"parent":"block/block",
		"display":{"fixed":{"rotation":[180,0,0],"translation":[0,-4,0],"scale":[1.005,1.005,1.005]}},
	}
	Mem.ctx.assets[ns].models["block/cable_base"] = set_json_encoder(Model(parent_model))

	for cable in cables:
		write_energy_cable_variants(cable)
		entries: list[JsonDict] = [
			{"threshold": i, "model":{"type": "minecraft:model", "model": f"{ns}:block/{cable}/{energy_cable_variant(i)}"}}
			for i in range(64)
		]
		Mem.ctx.assets[ns].item_models[cable] = set_json_encoder(ItemModel(model_dispatch(entries)), max_level=3)
		Mem.ctx.assets[ns].textures[f"block/{cable}"] = texture_mcmeta(f"{textures_folder}/{cable}.png")
		write_function(BlockFunctions(cable).place_secondary, f"""
# Cable rotation for models, and common cable tag
data modify entity @s item_display set value "fixed"
tag @s add {ns}.cable
""")
	write_cable_update(cables, family="energy", score="energy.data", tag="energy:v1/cable_update")


def write_energy_cable_variants(cable: str) -> None:
	""" Write the cable's model of every connection variant, from the shapes under `ENERGY_CABLE_MODELS_FOLDER`. """
	ns: str = Mem.ctx.project_id
	for root, dirs, files in os.walk(ENERGY_CABLE_MODELS_FOLDER):
		dirs.sort()
		for file in sorted(f for f in files if f.endswith(".json")):
			new_json: JsonDict = {
				"parent": f"{ns}:block/cable_base",
				"textures": {"0": f"{ns}:block/{cable}", "particle": f"{ns}:block/{cable}"},
			}
			new_json.update(stp.json_load(f"{root}/{file}"))
			variant: str = os.path.splitext(file)[0]
			Mem.ctx.assets[ns].models[f"block/{cable}/{variant}"] = set_json_encoder(Model(new_json), max_level=3)


def energy_cable_variant(i: int) -> str:
	""" The variant model of an energy cable connected on the faces the bits of `i` set.

	>>> energy_cable_variant(0), energy_cable_variant(1 | 2 | 32)
	('variant', 'variant_ude')
	"""
	return ("variant_" + "".join(face for face, bit in ENERGY_CABLE_FACES if i & bit)).removesuffix("_")


def write_cable_update(cables: Iterable[str], family: str, score: str, tag: str) -> None:
	""" Write the function giving a cable of `family` its item model, then the variant its connections score names. """
	ns: str = Mem.ctx.project_id
	cables_str: str = "\n".join([
		f"execute if entity @s[tag={ns}.{cable}] run item replace entity @s contents with "
		f"{CUSTOM_ITEM_VANILLA}[item_model=\"{ns}:{cable}\"]"
		for cable in cables
	])
	cable_update_content: str = f"""
# Stop if not {ns} cable
execute unless entity @s[tag={ns}.custom_block,tag={family}.cable] run return fail

# Apply the model dynamically based on cable tags
{cables_str}

# Get the right model
item modify entity @s contents {stp.json_dump(loot_function("minecraft:set_custom_model_data", floats={"values": [float_score(score)], "mode": "replace_all"}), max_level=0)}
"""  # noqa: E501
	write_function(f"{ns}:calls/{family}/cable_update", cable_update_content, tags=[tag])


# Setup item cables work and visuals
def item_cables_models(cables: dict[str, dict[str, str] | None]) -> None:
	""" Setup item cables models and functions for SimplEnergy.

	Args:
		cables: Dictionary of item cables to setup.
			Each key is the cable name, and the value is a dictionary mapping model textures to their paths
			The mapping dictionnary is optional, if not provided, it will use the default model paths.
			(e.g. {"item_cable":{"0":"item_cable/center","1":"item_cable/pillon","2":"item_cable/glass"}})
	"""
	ns: str = Mem.ctx.project_id
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")
	for cable, textures in cables.items():
		if textures is None:
			textures = {}
		for key, default in ITEM_CABLE_TEXTURES:
			if not textures.get(key):
				textures[key] = f"{cable}/{default}"

		entries: list[JsonDict] = [write_item_cable_variant(cable, textures, i) for i in range(64)]
		Mem.ctx.assets[ns].item_models[cable] = set_json_encoder(ItemModel(model_dispatch(entries)), max_level=3)
		for texture_path in textures.values():
			copy_block_texture(textures_folder, texture_path)

		write_function(BlockFunctions(cable).place_secondary, f"""
# Item cable setup for models, and common itemio cable tag
tag @s add {ns}.cable
tag @s add itemio.cable
function #itemio:calls/cables/init
""")
		write_function(BlockFunctions(cable).destroy, """
# Item cable destruction cleanup
function #itemio:calls/cables/destroy
""")
	write_cable_update(cables, family="itemio", score="itemio.math", tag="itemio:event/cable_update")


def copy_block_texture(textures_folder: str, texture_path: str) -> None:
	""" Copy `<textures_folder>/<texture_path>.png` to the resource pack's block textures, unless missing or already there. """
	ns: str = Mem.ctx.project_id
	src: str = f"{textures_folder}/{texture_path}.png"
	dst: str = f"block/{texture_path}"
	if os.path.exists(src) and (not Mem.ctx.assets[ns].textures.get(dst)):
		Mem.ctx.assets[ns].textures[dst] = texture_mcmeta(src)


def model_dispatch(entries: list[JsonDict]) -> JsonDict:
	""" An item model choosing one of `entries` by the item's custom model data. """
	return {"model": {"type": "minecraft:range_dispatch","property": "minecraft:custom_model_data","entries": entries}}


def write_item_cable_variant(cable: str, textures: dict[str, str], i: int) -> JsonDict:
	""" Write the item cable's model connected on the sides the bits of `i` set, the base model losing the elements of the others.

	Returns:
		The entry of the cable's item model pointing at it.
	"""
	ns: str = Mem.ctx.project_id
	connected: list[str] = [side for index, (side, _) in enumerate(ITEM_CABLE_SIDES) if i & (1 << index)]
	removed: list[str] = [cube for side, cube in ITEM_CABLE_SIDES if side not in connected]
	base_data: JsonDict = stp.json_load(stp.get_root_path(__file__) + "/item_cable_models/cable_base.json")
	base_data["textures"] = {key: f"{ns}:block/{textures[key]}" for key, _ in ITEM_CABLE_TEXTURES}
	base_data["elements"] = [
		element for element in base_data["elements"] if not any(cube in element.get("name", "") for cube in removed)
	]
	variant_name: str = f"variant_{''.join(connected)}" if connected else "no_variant"
	Mem.ctx.assets[ns].models[f"block/{cable}/{variant_name}"] = set_json_encoder(Model(base_data), max_level=3)
	return {"threshold": i, "model": {"type": "minecraft:model", "model": f"{ns}:block/{cable}/{variant_name}"}}


# Setup servo-mechanisms work and visuals
def servo_mechanisms_models(servos: dict[str, dict[str, str] | None]) -> None:
	""" Setup servo mechanisms models and functions for SimplEnergy.

	Args:
		servos: Dictionary of servo mechanisms to setup.
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

	for servo, textures in servos.items():
		textures = textures or {}
		typ: str = textures.get("type", "extract")  # Default to 'extract' if not specified
		register_servo_models(models_path, typ, textures)
		register_servo_textures(textures_folder, typ, textures)
		write_servo_functions(servo, typ)

	# Update the servo model on itemio network changes (delegates to the shared model logic)
	write_function(f"{ns}:calls/itemio/network_update", f"""
# Stop if not {ns} servo
execute unless entity @s[tag={ns}.custom_block,tag={ns}.servo] run return fail

# Apply the model depending on the on/off state and the network connection
function {ns}:utils/servo/update_model
""", tags=["itemio:event/network_update"])

	# Setup the "rotate to toggle on/off" feature
	servo_toggle(servos)


def register_servo_models(models_path: str, typ: str, textures: dict[str, str]) -> None:
	""" The block models of one servo type, default, connected and off, then its item model and the item files of the three. """
	ns: str = Mem.ctx.project_id
	default_texture: str = textures.get("default", f"servo/{typ}_default")
	shown: dict[str, tuple[str, str, str]] = {
		"block": (f"{typ}_block", default_texture, "base_block"),
		"connected": (f"{typ}_connected", textures.get("connected", f"servo/{typ}_connected"), "base_block"),
		"off": (f"{typ}_block", f"servo/{typ}_off", "base_block"),
		"item": (f"{typ}_item", default_texture, "base_item"),
	}
	for state, (source, texture, parent) in shown.items():
		model: JsonDict = stp.json_load(f"{models_path}/{source}.json")
		model["parent"] = f"{ns}:block/servo/{parent}"
		model["textures"] = {"0": f"{ns}:block/{texture}", "particle": f"{ns}:block/{texture}"}
		Mem.ctx.assets[ns].models[f"block/servo/{typ}_{state}"] = set_json_encoder(Model(model), max_level=3)

	for texture in ("block", "connected", "off"):
		model_data = {"model": {"type": "minecraft:model", "model": f"{ns}:block/servo/{typ}_{texture}"}}
		Mem.ctx.assets[ns].item_models[f"servo/{typ}_{texture}"] = set_json_encoder(ItemModel(model_data), max_level=3)


def register_servo_textures(textures_folder: str, typ: str, textures: dict[str, str]) -> None:
	""" Copy one servo type's textures into the resource pack, and darken a gray copy of the default one into its "off" texture. """
	ns: str = Mem.ctx.project_id
	for texture_key in ("default", "connected"):
		copy_block_texture(textures_folder, textures.get(texture_key, f"{typ}_{texture_key}"))

	off_dst: str = f"block/servo/{typ}_off"
	default_src: str = f"{textures_folder}/{textures.get('default', f'{typ}_default')}.png"
	if os.path.exists(default_src) and (not Mem.ctx.assets[ns].textures.get(off_dst)):
		with Image.open(default_src) as base_image:
			rgba: Image.Image = base_image.convert("RGBA")
		r, g, b, a = rgba.split()
		gray = Image.merge("RGB", (r, g, b)).convert("L").point(lambda p: int(p * 0.5))
		Mem.ctx.assets[ns].textures[off_dst] = Texture(Image.merge("RGBA", (gray, gray, gray, a)))


def write_servo_functions(servo: str, typ: str) -> None:
	""" Tag a servo as an itemio one when placed, with its stack and retry limits, and let itemio forget it when destroyed. """
	ns: str = Mem.ctx.project_id
	ns_data: dict[str, int] = Item.from_id(servo).components.get("custom_data", {}).get(ns, {})
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
	write_function(BlockFunctions(servo).destroy, """
# Servo mechanism destruction cleanup
function #itemio:calls/servos/destroy
""")


# Setup the ability to turn servos off and on by rotating (right-clicking) them
def servo_toggle(servos: dict[str, dict[str, str] | None]) -> None:
	""" Setup the functions allowing players to turn servo mechanisms off and on by rotating them.

	Rotating (right-clicking) a servo item frame changes its 'ItemRotation'.
	A vanilla advancement listening to the 'minecraft:player_interacted_with_entity' trigger detects the interaction (so
	nothing runs every tick), then the nearby servos are checked: an odd rotation disables the rotated one (grayed out texture,
	item transfers stopped by removing the 'itemio.servo.extract' / 'itemio.servo.insert' tag),
	an even rotation enables it back to normal. As the check only acts when the parity differs, only the rotated servo toggles.

	Args:
		servos: Same servos dictionary as the one passed to 'servo_mechanisms_models'.
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
					"entity": advancement_entity({
						"minecraft:entity_tags": {"any_of": [f"{ns}.servo"]},
					}),
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
""")  # noqa: E501

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
		f'execute if score @s {ns}.servo_off matches 1 if entity @s[tag={ns}.{servo}] run '
		f'data modify entity @s Item.components."minecraft:item_model" set value "{ns}:servo/{typ}_off"'
		for servo, typ in servo_types.items()
	]
	for servo, typ in servo_types.items():
		for number, texture in ((0, "block"), (1, "connected")):
			model_lines.append(
				f'execute if score @s {ns}.servo_off matches 0 if score @s itemio.math matches {number} '
				f'if entity @s[tag={ns}.{servo}] run '
				f'data modify entity @s Item.components."minecraft:item_model" set value "{ns}:servo/{typ}_{texture}"'
			)
	write_function(f"{ns}:utils/servo/update_model", "\n".join(model_lines) + "\n")
	return

