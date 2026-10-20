
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import itertools
import os
from collections.abc import Iterable
from dataclasses import dataclass

import stouputils as stp
from beet import ItemModel, Model, Texture
from stouputils.typing import JsonDict, JsonList

from ....core.__memory__ import Mem
from ....core.cls.items.block import Block
from ....core.cls.items.features import MODEL_MARGIN, STAIRS_SHAPES, GrowingSeed, VanillaBlock
from ....core.cls.items.item import Item
from ....core.cls.resource import Resource
from ....core.constants import CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA
from ....core.utils.io import set_json_encoder, set_model_encoder, texture_mcmeta
from ....core.utils.models import UVLOCK_TURNS, cake_element, flipped, stairs_corner, uv_locked, vanilla_elements, with_margin


# Constants
@dataclass(frozen=True)
class BlockShape:
	""" A vanilla block model a custom block takes when it has a texture for each of its sides. """
	parent: str
	sides: tuple[str, ...]


BLOCK_SHAPES: tuple[BlockShape, ...] = (
	BlockShape(parent="block/cake", sides=("bottom", "side", "top", "inner")),
	BlockShape(parent="block/orientable_with_bottom", sides=("front", "bottom", "side", "top")),
	BlockShape(parent="block/cube_bottom_top", sides=("bottom", "side", "top")),
	BlockShape(parent="block/orientable", sides=("front", "side", "top")),
	BlockShape(parent="block/cube_column", sides=("end", "side")),
)
""" Tried in order, the first whose sides all have a texture winning. """


# Utility function
def to_atlas(texture: str) -> str:
	""" Convert a texture path to its atlas sprite path.

	Args:
		texture: The original texture path.

	Returns:
		str: The converted atlas sprite path.
	"""
	return f"{Mem.ctx.project_id}:atlas/" + "/".join(texture.split("/")[1:])  # Remove 'minecraft:block/' prefix

# Class
class AutoModel:
	""" Class to handle item model processing. """
	__slots__ = {
		"block_or_item":    "Whether this is a block or item model.",
		"ignore_textures":  "Whether to ignore texture-related errors.",
		"ns":               "The namespace of the item model.",
		"obj":              "The item data from the definitions.",
		"parent":           "The parent model of this item model.",
		"source_textures":  "Dictionary of source textures.",
		"textures":         "The textures used by this item model.",
		"used_minecraft_textures": "Set of used Minecraft textures.",
		"used_textures":    "Set of used textures.",
	}

	# Class variables
	DEFAULT_PARENT: str = "item/generated"
	def __init__(self, data: Item, source_textures: dict[str, str], ignore_textures: bool = False):
		""" Initialize the AutoModel.

		Args:
			data:            The item data from the definitions.
			source_textures: Dictionary of source textures.
			ignore_textures: Whether to ignore texture-related errors.
		"""
		self.obj: Item = data
		self.ns: str = Mem.ctx.project_id
		self.block_or_item: str = "item"
		self.used_textures: set[str] = set()
		self.used_minecraft_textures: set[str] = set()
		self.source_textures: dict[str, str] = source_textures
		self.ignore_textures: bool = ignore_textures

		# Initialize model data
		self.parent: str = self.DEFAULT_PARENT
		self.textures: JsonDict = {}

	@classmethod
	def from_definitions(cls, data: Item, source_textures: dict[str, str], ignore_textures: bool = False) -> AutoModel:
		""" Create an AutoModel from a definitions entry.

		Args:
			data:            The item data from the definitions.
			source_textures: Dictionary of source textures.
			ignore_textures: Whether to ignore textures in the model.

		Returns:
			AutoModel: The created AutoModel instance.
		"""
		return cls(data, source_textures, ignore_textures)

	@stp.handle_error(exceptions=ValueError, error_log=stp.LogLevels.ERROR_TRACEBACK)
	def get_powered_texture(self, variants: list[str], side: str, on_off: str) -> str:
		""" Get the powered texture for a given side.

		Args:
			variants: List of texture variants.
			side:     The side to get the texture for.
			on_off:   The power state suffix.

		Returns:
			str: The texture path.
		"""
		if on_off:
			for texture in variants:
				if texture.endswith(side + on_off):
					return texture
		for texture in variants:
			if texture.endswith(side):
				return texture
		if not self.ignore_textures:
			raise ValueError(
				f"Couldn't find texture for side '{side}' in '{variants}', consider adding missing texture or override the model"
			)
		return ""

	def model_in_variants(self, models: Iterable[str], variants: list[str]) -> bool:
		""" Check if all models are in a string of any variant.

		Args:
			models:   List of models to check.
			variants: List of variants to check against.

		Returns:
			bool: True if all models are in variants.
		"""
		def model_matches(model: str, variant: str) -> bool:
			""" Check if model matches in variant with proper word boundary. """
			pattern: str = f"_{model}"
			idx: int = variant.find(pattern)
			if idx == -1:
				return False
			# Check if there's a character after the pattern
			after_idx: int = idx + len(pattern)
			if after_idx < len(variant):
				# Character after pattern should not be alphanumeric
				return not variant[after_idx].isalnum()
			# Pattern is at the end of the string, which is valid
			return True

		return all(any(model_matches(model, x) for x in variants) for model in models)

	@stp.simple_cache(method="str")
	def get_same_folder_variants(self, variants: Iterable[str]) -> list[str]:
		""" Get variants that are in the same folder as the item.

		Args:
			variants: Iterable of variant names.

		Returns:
			list[str]: List of variants in the same folder.
		"""
		target_folder_depth: int = self.obj.id.count('/')
		same_folder_variants: list[str] = []
		for variant in variants:
			variant_folder_depth: int = variant.count('/')
			if variant_folder_depth == target_folder_depth:
				# Check if all folder parts before the filename are the same
				if target_folder_depth == 0:
					same_folder_variants.append(variant)
				else:
					target_folder: str = '/'.join(self.obj.id.split('/')[:-1])
					variant_folder: str = '/'.join(variant.split('/')[:-1])
					if target_folder == variant_folder:
						same_folder_variants.append(variant)
		return same_folder_variants

	def handle_growing_seeds(self) -> None:
		""" Handle growing seeds by adding growth stage models and textures. """
		# Retrieve growing seed data
		if not isinstance(self.obj, Block) or self.obj.growing_seed is None:
			return
		growing_seed_data: GrowingSeed = self.obj.growing_seed
		texture_basename: str = growing_seed_data.texture_basename
		planted_on: str = growing_seed_data.planted_on
		if planted_on == "magma_block":
			planted_on = "magma"

		# Find all stage textures and order them by stage number
		stage_textures: dict[str, str] = dict(sorted({
				k.replace(".png", ""): v for k, v in self.source_textures.items()
				if os.path.basename(k).startswith(f"{texture_basename}_stage_")
			}.items(),
			key=lambda item: int(item[0].split("_")[-1])
		))

		# For each stage, create the model and add the texture
		for i in range(len(stage_textures)):
			stage_texture_name: str = f"{texture_basename}_stage_{i}"
			if stage_texture_name not in stage_textures:
				if not self.ignore_textures:
					stp.error(f"Missing texture for growing seed stage: '{stage_texture_name}.png'")
				continue

			# Create model for this stage
			self.used_minecraft_textures.add(f"minecraft:block/{planted_on}")
			stage_model: JsonDict = {
				"textures": {
					"1": to_atlas(f"minecraft:block/{planted_on}"),
					"2": self.obj.seed_stage_texture(i),
					"particle": to_atlas(f"minecraft:block/{planted_on}")
				},
				"elements": [
					{"name":"seed","from":[0,1,4],"to":[16,17,4],"faces":{"north":{"uv":[0,0,16,16],"texture":"#2"},"south":{"uv":[16,0,0,16],"texture":"#2"}}},
					{"name":"seed","from":[12,1,0],"to":[12,17,16],"faces":{"east":{"uv":[0,0,16,16],"texture":"#2"},"west":{"uv":[16,0,0,16],"texture":"#2"}}},
					{"name":"seed","from":[0,1,12],"to":[16,17,12],"faces":{"north":{"uv":[16,0,0,16],"texture":"#2"},"south":{"uv":[0,0,16,16],"texture":"#2"}}},
					{"name":"seed","from":[4,1,0],"to":[4,17,16],"faces":{"east":{"uv":[16,0,0,16],"texture":"#2"},"west":{"uv":[0,0,16,16],"texture":"#2"}}},
					{"name":"base","from":[0,0,0],"to":[16,1.05,16],"faces":{"north":{"uv":[0,0,16,1],"texture":"#1"},"east":{"uv":[0,0,16,1],"texture":"#1"},"south":{"uv":[0,0,16,1],"texture":"#1"},"west":{"uv":[0,0,16,1],"texture":"#1"},"up":{"uv":[0,0,16,16],"texture":"#1"},"down":{"uv":[0,0,16,16],"texture":"#1"}}}
				]
			}

			# Add the model to assets and create item model
			stage_model_res = self.obj.seed_stage_model(i)
			stage_model_res.write(set_model_encoder(Model(stage_model), max_level=2))
			items_model: JsonDict = {"model": {"type": "minecraft:model", "model": stage_model_res}}
			self.obj.seed_stage_item_model(i).write(set_json_encoder(ItemModel(items_model), max_level=4))

			# Add the texture to assets
			self.obj.seed_stage_texture(i).write(texture_mcmeta(stage_textures[stage_texture_name]))

	def copy_and_register_textures(self, content: JsonDict) -> None:
		""" Copy a model's textures to the assets and register them for atlas handling.

		Args:
			content: The model content whose textures should be processed (may be modified in place).
		"""
		if not content.get("textures"):
			return

		textures_values: list[str] = list(content["textures"].values())
		for texture in textures_values:
			if not texture.startswith("minecraft:"):
				self.copy_texture(texture)

		# Textures from both atlases in one model
		needs_atlas_conversion: bool = len({t.startswith("minecraft:") for t in textures_values}) == 2

		for key, texture in content["textures"].items():
			if texture.startswith("minecraft:"):
				self.used_minecraft_textures.add(texture)
				if needs_atlas_conversion:
					content["textures"][key] = to_atlas(texture)
			else:
				self.used_textures.add(texture)

	def copy_texture(self, texture: str) -> None:
		""" Copy one texture of the project into the assets, found in the source textures by its file name.

		Raises:
			ValueError: When it is not there and `ignore_textures` is off.
		"""
		texture_name: str = texture.split(":")[-1].split("/")[-1] + ".png"
		if texture_name in self.source_textures:
			Mem.ctx.assets[texture] = texture_mcmeta(self.source_textures[texture_name])
		elif not self.ignore_textures:
			raise ValueError(f"Texture '{texture_name}' not found in source textures")

	def handle_hand_model(self, variants: list[str], on_off: str) -> JsonDict:
		""" Generate the in-hand model from the item's hand_model and return the items/ definition
		switching between the regular and in-hand models based on the display context.

		Args:
			variants: List of texture variants of the item.
			on_off:   The power state suffix.

		Returns:
			JsonDict: The content of the items/ definition file.
		"""
		# Copy the hand model content (so the powered loop doesn't mutate the original)
		hand_model: JsonDict = self.obj.hand_model or {}
		content: JsonDict = {k: (v.copy() if isinstance(v, dict) else v) for k, v in hand_model.items()}

		if on_off == "_on":
			switch_on(content.get("textures", {}), variants)
		self.copy_and_register_textures(content)

		# Add the in-hand model to assets
		self.obj.model.suffixed(f"_in_hand{on_off}").write(set_model_encoder(Model(content), max_level=2))

		# Return the items/ definition keeping the regular model for block-like contexts and using the in-hand model otherwise
		return {
			"model": {
				"type": "minecraft:select",
				"cases": [
					{
						"model": {"type": "minecraft:model","model": self.obj.model.suffixed(on_off)},
						"when": self.obj.override_model_contexts or Item.DEFAULT_OVERRIDE_MODEL_CONTEXTS
					}
				],
				"fallback": {"type": "minecraft:model","model": self.obj.model.suffixed(f"_in_hand{on_off}")},
				"property": "minecraft:display_context"
			}
		}

	@stp.handle_error(exceptions=ValueError, error_log=stp.LogLevels.ERROR_TRACEBACK)
	def process(self) -> set[str]:
		""" Write the item's models, and its items/ definition, for each of its power states.

		Returns:
			Block textures to be added to the items atlas.
		"""
		self.handle_growing_seeds()
		item_model: str | None = self.obj.components.get("item_model")
		if not item_model or item_model in Mem.ctx.meta["stewbeet"]["rendered_item_models"]:
			return set()

		overrides: JsonDict = self.obj.override_model or {}
		if self.obj.base_item == CUSTOM_BLOCK_VANILLA or any(isinstance(x, str) and "block" in x for x in overrides.values()):
			self.block_or_item = "block"
		variants: list[str] = self.get_same_folder_variants(self.own_variants())
		for on_off in self.power_states():
			self.write_power_state(variants, on_off, overrides)
		return self.used_minecraft_textures

	def own_variants(self) -> list[str]:
		""" The source textures named after the item, at most 2 underscores longer than its id.

		The bound keeps `awakened_stardust.png` from claiming `awakened_stardust_furnace_generator_on.png`.
		"""
		count: int = self.obj.id.count("_")
		return [
			x.replace(".png", "") for x in self.source_textures
			if x.startswith(self.obj.id) and abs(x.count("_") - count) <= 2
		]

	def power_states(self) -> list[str]:
		""" The suffixes to write a model for, `_on` first when the item has a texture ending in `_on`.

		The plain items definition written after it then finds the `_on` model a lit host shows.
		"""
		count: int = self.obj.id.count("_")
		powered: bool = any(
			name.startswith(self.obj.id) and name.endswith("_on.png") and abs(name.count("_") - count) <= 2
			for name in self.source_textures
		)
		return ["_on", ""] if powered else [""]

	def write_power_state(self, variants: list[str], on_off: str, overrides: JsonDict) -> None:
		""" Write the model and the items/ definition of one power state, `on_off` being "" or "_on". """
		exclude_textures: bool = excludes_textures(overrides)
		content: JsonDict = {}
		if self.obj.override_model != {}:
			make_content = self.block_content if self.block_or_item == "block" else self.item_content
			content = make_content(variants, on_off, overrides)
		content.update({
			key: value.copy() if isinstance(value, dict) else value
			for key, value in overrides.items() if key != "textures" or value is not None
		})

		if not exclude_textures and on_off == "_on":
			switch_on(content.get("textures", {}), variants)
		if (exclude_textures or not content.get("textures")) and "textures" in content:
			del content["textures"]
		self.copy_and_register_textures(content)

		if self.obj.override_model != {}:
			self.write_displayed_elements(content, on_off)
			self.obj.model.suffixed(on_off).write(set_model_encoder(Model(content), max_level=2))
		Mem.ctx.meta["stewbeet"]["rendered_item_models"].add(self.obj.components["item_model"])
		if not self.obj.base_item.endswith("bow"):
			definition: JsonDict = self.items_definition(variants, on_off)
			definition["model"] = self.host_state_select(definition["model"], on_off)
			self.obj.generated_item_model.suffixed(on_off).write(set_json_encoder(ItemModel(definition), max_level=4))

	def margin_scale(self) -> float:
		""" The scale the elements of the model grow by when a display shows it in a host, 1.0 for none. """
		if not isinstance(self.obj, Block) or self.block_or_item != "block":
			return 1.0
		vanilla: VanillaBlock | None = self.obj.vanilla_block
		return MODEL_MARGIN if vanilla is None else vanilla.margin if vanilla.id else 1.0

	def write_displayed_elements(self, content: JsonDict, on_off: str) -> None:
		""" Grow the elements of the model, and write the copies of it a block shows turned by `uvlock`, flipped by `half`,
		or as the corner its stairs host makes.
		"""
		block: Block | None = self.obj if isinstance(self.obj, Block) and self.block_or_item == "block" else None
		elements: JsonList | None = displayed_elements(content) if block else None
		if block is None or elements is None:
			return
		scale: float = self.margin_scale()
		if scale != 1.0:
			content["elements"] = [with_margin(element, scale) for element in elements]

		for y, upper, corner in displayed_variants(block.vanilla_block, on_off):
			suffix: str = on_off + (f"_y{y}" if y else "") + ("_up" if upper else "")
			copy: Resource[Model] = block.model.suffixed((f"_{corner}" if corner else "") + suffix)
			copy_elements: JsonList = displayed_copy(elements, y, upper, corner, scale)
			copy.write(set_model_encoder(Model({"parent": block.model.suffixed(on_off), "elements": copy_elements}), max_level=2))
			if not corner:
				model: JsonDict = {"type": "minecraft:model", "model": copy}
				definition: JsonDict = {"model": self.host_state_select(model, suffix)}
				block.generated_item_model.suffixed(suffix).write(set_json_encoder(ItemModel(definition), max_level=5))

	def host_state_select(self, model: JsonDict, suffix: str) -> JsonDict:
		""" `model`, or a select showing the copy of it drawn for the host state the display's custom_model_data string names.

		`datapack.custom_blocks` keeps that string on the state of `VanillaBlock.host_states` the host is in.
		"""
		vanilla: VanillaBlock | None = self.obj.vanilla_block if isinstance(self.obj, Block) else None
		cases: JsonList = [
			{"when": state, "model": {"type": "minecraft:model", "model": copy}}
			for state, state_suffix in (vanilla.host_states if vanilla else {}).items()
			if state_suffix and (copy := self.obj.model.suffixed(state_suffix + suffix)).exists()
		]
		if not cases:
			return model
		return {"type": "minecraft:select", "property": "minecraft:custom_model_data", "index": 0, "cases": cases, "fallback": model}

	def block_content(self, variants: list[str], on_off: str, overrides: JsonDict) -> JsonDict:
		""" A block's model: one texture on every face, or the first of `BLOCK_SHAPES` its textures fill.

		Raises:
			ValueError: When its textures fill no shape, the model overrides none, and `ignore_textures` is off.
		"""
		content: JsonDict = {"parent": "block/cube_all", "textures": {}}
		if excludes_textures(overrides):
			return content
		if len([x for x in variants if "_on" not in x]) == 1:
			content["textures"]["all"] = f"{self.ns}:item/" + self.get_powered_texture(variants, "", on_off)
			return content

		shape: BlockShape | None = self.block_shape(variants, overrides)
		if shape is None:
			return content

		content["parent"] = shape.parent
		for side in shape.sides:
			texture: str = self.get_powered_texture(variants, side, on_off)
			content["textures"][side.replace("inner", "inside")] = f"{self.ns}:item/" + texture
		if shape.parent == "block/cake":
			for i in range(1, 7):
				slice_content: JsonDict = {"parent": f"block/cake_slice{i}", "textures": content["textures"]}
				if self.margin_scale() != 1.0:
					slice_content["elements"] = [with_margin(cake_element(i), self.margin_scale())]
				Resource(Model, f"item/{self.obj.id}_slice{i}{on_off}").write(set_model_encoder(Model(slice_content), max_level=2))
		return content

	def block_shape(self, variants: list[str], overrides: JsonDict) -> BlockShape | None:
		""" The first of `BLOCK_SHAPES` the block's textures fill, None when they fill none.

		Raises:
			ValueError: When they fill none, the model overrides no texture, and `ignore_textures` is off.
		"""
		shape: BlockShape | None = next((shape for shape in BLOCK_SHAPES if self.model_in_variants(shape.sides, variants)), None)
		if shape is None and not overrides.get("textures") and not self.ignore_textures:
			patterns: str = stp.json_dump({s.parent.removeprefix("block/"): list(s.sides) for s in BLOCK_SHAPES}, max_level=1)
			raise ValueError(
				f"Block '{self.obj.id}' has invalid variants: {variants},\n"
				"consider overriding the model or adding missing textures "
				f"to match up one of the following patterns:\n{patterns}"
			)
		return shape

	def item_content(self, variants: list[str], on_off: str, overrides: JsonDict) -> JsonDict:
		""" An item's model: its base item's parent, with a second layer for leather and overlays, and pulling states for a bow. """
		data_id: str = self.obj.base_item
		own_parent: bool = data_id != CUSTOM_ITEM_VANILLA and "elements" not in overrides
		parent: str = data_id.replace(":", ":item/") if own_parent else "item/generated"
		if excludes_textures(overrides):
			return {"parent": parent}

		textures: JsonDict = {"layer0": f"{self.ns}:item/{self.obj.id}{on_off}"}
		data_id = data_id.replace("minecraft:", "")
		if data_id.startswith("leather_"):
			textures["layer1"] = textures["layer0"]
		if f"{self.obj.id}_overlay" in variants:
			textures["layer1"] = f"{self.ns}:item/{self.obj.id}_overlay"
		elif data_id.endswith("bow"):
			self.write_bow_pulling(variants, parent, on_off)
		return {"parent": parent, "textures": textures}

	def write_bow_pulling(self, variants: list[str], parent: str, on_off: str) -> None:
		""" Write a model per `_pulling_<n>` texture, and the items/ definition switching between them as the bow is drawn. """
		pulling: list[str] = sorted((v for v in variants if "_pulling_" in v), key=lambda x: int(x.split("_")[-1]))
		if not pulling:
			return

		crossbow: bool = self.obj.base_item == "minecraft:crossbow"
		entries: JsonList = []
		for i, variant in enumerate(pulling):
			self.write_layer_model(variant, parent, f"_pulling_{i}")
			if i < len(pulling) - 1:
				model: str = f"{self.ns}:item/{self.obj.id}_pulling_{i + 1}"
				threshold: float = round((i + 1) / (len(pulling) - 1), 2) if crossbow else 0.65 + (0.25 * i)
				entries.append({"model": {"type": "minecraft:model", "model": model}, "threshold": threshold})

		drawn: JsonDict = {
			"type": "minecraft:range_dispatch",
			"entries": entries,
			"fallback": {"type": "minecraft:model", "model": f"{self.ns}:item/{self.obj.id}_pulling_0"},
			"property": "minecraft:crossbow/pull" if crossbow else "minecraft:use_duration",
		}
		idle: JsonDict = {"type": "minecraft:model", "model": f"{self.ns}:item/{self.obj.id}"}
		if crossbow:
			idle = {
				"type": "minecraft:select", "property": "minecraft:charge_type", "fallback": idle,
				"cases": [
					{"when": charge, "model": self.charged_model(variants, parent, charge, len(pulling) - 1)}
					for charge in ("arrow", "rocket")
				],
			}
		else:
			drawn["scale"] = 0.05
		items_content: JsonDict = {"model": {
			"type": "minecraft:condition", "property": "minecraft:using_item", "on_false": idle, "on_true": drawn,
		}}
		self.obj.generated_item_model.suffixed(on_off).write(set_json_encoder(ItemModel(items_content), max_level=4))

	def write_layer_model(self, variant: str, parent: str, suffix: str) -> None:
		""" Copy the texture `variant` and write the model showing it, the item's model with `suffix`. """
		if f"{variant}.png" in self.source_textures:
			Resource(Texture, f"item/{variant}").write(texture_mcmeta(self.source_textures[f"{variant}.png"]))
		content: JsonDict = {"parent": parent, "textures": {"layer0": f"{self.ns}:item/{variant}"}}
		self.obj.model.suffixed(suffix).write(set_model_encoder(Model(content), max_level=2))

	def charged_model(self, variants: list[str], parent: str, charge: str, last_pulling: int) -> JsonDict:
		""" The model of a crossbow loaded with an arrow or a rocket, from its `_arrow` or `_firework` texture, else its drawn one. """
		variant: str = f"{self.obj.id}_{'arrow' if charge == 'arrow' else 'firework'}"
		if variant not in variants:
			return {"type": "minecraft:model", "model": self.obj.model.suffixed(f"_pulling_{last_pulling}")}
		self.write_layer_model(variant, parent, variant.removeprefix(self.obj.id))
		return {"type": "minecraft:model", "model": self.obj.model.suffixed(variant.removeprefix(self.obj.id))}

	def items_definition(self, variants: list[str], on_off: str) -> JsonDict:
		""" The items/ definition: the hand model's switch, a spear's in-hand switch, or the model alone. """
		if self.obj.hand_model:
			return self.handle_hand_model(variants, on_off)
		if self.obj.id.endswith("_spear") and f"{self.obj.id}_in_hand.png" in self.source_textures:
			return self.spear_definition(on_off)
		return {"model": {"type": "minecraft:model", "model": self.obj.model.suffixed(on_off)}}

	def spear_definition(self, on_off: str) -> JsonDict:
		""" Write a spear's in-hand model and texture, and return the items/ definition showing it outside the GUI. """
		items_model: JsonDict = {
			"model": {
				"type": "minecraft:select",
				"cases": [
					{
						"model": {"type": "minecraft:model","model": self.obj.model.suffixed(on_off)},
						"when": ["gui","ground","fixed","on_shelf"]
					}
				],
				"fallback": {"type": "minecraft:model","model": self.obj.model.suffixed(f"_in_hand{on_off}")},
				"property": "minecraft:display_context"
			},
			"swap_animation_scale": 1.95
		}
		in_hand_content: JsonDict = {
			"parent": "item/spear_in_hand",
			"textures": {"layer0": self.obj.texture.suffixed(f"_in_hand{on_off}")},
		}
		self.obj.model.suffixed(f"_in_hand{on_off}").write(set_model_encoder(Model(in_hand_content), max_level=2))

		in_hand_texture: str = f"{self.obj.id}_in_hand{on_off}.png"
		if in_hand_texture in self.source_textures:
			self.obj.texture.suffixed(f"_in_hand{on_off}").write(texture_mcmeta(self.source_textures[in_hand_texture]))
		elif not on_off:
			self.obj.texture.suffixed("_in_hand").write(texture_mcmeta(self.source_textures[f"{self.obj.id}_in_hand.png"]))
		return items_model


def displayed_elements(model: JsonDict) -> JsonList | None:
	""" The elements a model draws: its own, its first parent's in the pack, or those of a cube or cake vanilla parent. """
	while "elements" not in model:
		parent: str | None = model.get("parent")
		pack_model: Model | None = Mem.ctx.assets.models.get(parent if ":" in parent else f"minecraft:{parent}") if parent else None
		if pack_model is None:
			return vanilla_elements(parent) if parent else None
		model = pack_model.data
	return model["elements"]


def displayed_variants(vanilla: VanillaBlock | None, on_off: str) -> list[tuple[int, bool, str]]:
	""" The turn, half and stairs corner of each copy of the model a display shows, all but the model itself.

	The corners of a turn and half come before its plain copy, so the items definition written with that copy finds them.
	"""
	if vanilla is None:
		return []
	turns: list[int] = [0, *UVLOCK_TURNS.values()] if vanilla.uvlock else [0]
	halves: tuple[bool, ...] = (False, True) if vanilla.half else (False,)
	corners: tuple[str, ...] = (*STAIRS_SHAPES[1:], "") if vanilla.base_id.endswith("_stairs") and not on_off else ("",)
	return [(y, upper, corner) for y, upper, corner in itertools.product(turns, halves, corners) if y or upper or corner]


def displayed_copy(elements: JsonList, y: int, upper: bool, corner: str, scale: float) -> JsonList:
	""" The elements cut into a stairs `corner` unless empty, turned `y` degrees, flipped on the upper half, grown by `scale`. """
	shape: JsonList = [uv_locked(element, 0, y) for element in (stairs_corner(elements, corner) if corner else elements)]
	return [with_margin(flipped(element) if upper else element, scale) for element in shape]


def excludes_textures(overrides: JsonDict) -> bool:
	""" Whether the model overrides set `textures` to None, which leaves the model without any. """
	return "textures" in overrides and overrides["textures"] is None


def switch_on(textures: JsonDict, variants: list[str]) -> None:
	""" Point each texture at its `_on` variant where the item has one. """
	for key, texture in textures.items():
		if (texture.split("/")[-1] + "_on") in variants:
			textures[key] = texture + "_on"

