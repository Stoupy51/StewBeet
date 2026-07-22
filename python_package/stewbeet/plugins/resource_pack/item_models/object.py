
# Imports
from __future__ import annotations

import os
from collections.abc import Iterable

import stouputils as stp
from beet import ItemModel, Model, Texture
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import Block, GrowingSeed
from ....core.cls.item import Item
from ....core.cls.resource import Resource
from ....core.constants import CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA
from ....core.utils.io import set_json_encoder, set_model_encoder, texture_mcmeta


# Utility function
def to_atlas(texture: str) -> str:
	""" Convert a texture path to its atlas sprite path.

	Args:
		texture (str): The original texture path.

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
			data (Item): The item data from the definitions.
			source_textures (dict[str, str]): Dictionary of source textures.
			ignore_textures (bool): Whether to ignore texture-related errors.
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
			data (Item): The item data from the definitions.
			source_textures (dict[str, str]): Dictionary of source textures.
			ignore_textures (bool): Whether to ignore textures in the model.

		Returns:
			AutoModel: The created AutoModel instance.
		"""
		return cls(data, source_textures, ignore_textures)

	@stp.handle_error(exceptions=ValueError, error_log=stp.LogLevels.ERROR_TRACEBACK)
	def get_powered_texture(self, variants: list[str], side: str, on_off: str) -> str:
		""" Get the powered texture for a given side.

		Args:
			variants (list[str]): List of texture variants.
			side (str): The side to get the texture for.
			on_off (str): The power state suffix.

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
			raise ValueError(f"Couldn't find texture for side '{side}' in '{variants}', consider adding missing texture or override the model")
		return ""

	def model_in_variants(self, models: list[str], variants: list[str]) -> bool:
		""" Check if all models are in a string of any variant.

		Args:
			models (list[str]): List of models to check.
			variants (list[str]): List of variants to check against.

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
			else:
				# Pattern is at the end of the string, which is valid
				return True

		return all(any(model_matches(model, x) for x in variants) for model in models)

	@stp.simple_cache
	def get_same_folder_variants(self, variants: Iterable[str]) -> list[str]:
		""" Get variants that are in the same folder as the item.

		Args:
			variants  (Iterable[str]): Iterable of variant names.

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
			stage_model_res.write(set_model_encoder(Model(stage_model), max_level=4))
			items_model: JsonDict = {"model": {"type": "minecraft:model", "model": stage_model_res}}
			self.obj.seed_stage_item_model(i).write(set_json_encoder(ItemModel(items_model), max_level=4))

			# Add the texture to assets
			self.obj.seed_stage_texture(i).write(texture_mcmeta(stage_textures[stage_texture_name]))

	def copy_and_register_textures(self, content: JsonDict) -> None:
		""" Copy a model's textures to the assets and register them for atlas handling.

		Args:
			content (JsonDict): The model content whose textures should be processed (may be modified in place).
		"""
		if not content.get("textures"):
			return

		# Copy used textures
		for texture in content["textures"].values():
			# Ignore if minecraft namespace
			if texture.startswith("minecraft:"):
				continue

			texture_name = texture.split(":")[-1].split("/")[-1]  # Get just the filename
			texture_name += ".png"
			if texture_name in self.source_textures:
				Mem.ctx.assets[texture] = texture_mcmeta(self.source_textures[texture_name])
			else:
				if not self.ignore_textures:
					raise ValueError(f"Texture '{texture_name}' not found in source textures")

		# Check if there are textures from different atlases
		textures_values: list[str] = list(content["textures"].values())
		has_minecraft: bool = any(t.startswith("minecraft:") for t in textures_values)
		has_custom: bool = any(not t.startswith("minecraft:") for t in textures_values)
		needs_atlas_conversion: bool = has_minecraft and has_custom

		for key, texture in content["textures"].items():
			if texture.startswith("minecraft:"):
				self.used_minecraft_textures.add(texture)
				if needs_atlas_conversion:
					content["textures"][key] = to_atlas(texture)
			else:
				self.used_textures.add(texture)

	def handle_hand_model(self, variants: list[str], on_off: str) -> JsonDict:
		""" Generate the in-hand model from the item's hand_model and return the items/ definition
		switching between the regular and in-hand models based on the display context.

		Args:
			variants (list[str]): List of texture variants of the item.
			on_off   (str):       The power state suffix.

		Returns:
			JsonDict: The content of the items/ definition file.
		"""
		# Copy the hand model content (so the powered loop doesn't mutate the original)
		hand_model: JsonDict = self.obj.hand_model or {}
		content: JsonDict = {k: (v.copy() if isinstance(v, dict) else v) for k, v in hand_model.items()}

		# If powered, check if the on state is in the variants and add it
		if on_off == "_on":
			for key, texture in content.get("textures", {}).items():
				texture: str
				if (texture.split("/")[-1] + on_off) in variants:
					content["textures"][key] = texture + on_off

		# Copy and register used textures
		self.copy_and_register_textures(content)

		# Add the in-hand model to assets
		self.obj.model.suffixed(f"_in_hand{on_off}").write(set_model_encoder(Model(content), max_level=4))

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
		""" Process the item model.

		Returns:
			set[str]: Set of blocks textures to be added to the items atlas.
		"""
		# If the item is a growing seed, handle it
		self.handle_growing_seeds()

		# If no item model, return
		if not self.obj.components.get("item_model"):
			return set()

		# If item_model is already processed, return
		if self.obj.components["item_model"] in Mem.ctx.meta["stewbeet"]["rendered_item_models"]:
			return set()

		# Initialize variables
		overrides: JsonDict = self.obj.override_model or {}
		if (self.obj.base_item == CUSTOM_BLOCK_VANILLA or
			any((isinstance(x, str) and "block" in x) for x in overrides.values())):
			self.block_or_item = "block"


		# Check if textures should be excluded completely
		exclude_textures: bool = "textures" in overrides and overrides.get("textures") is None

		# Get powered states (if any)
		powered: list[str] = [""]
		count: int = self.obj.id.count("_")
		for texture_name in self.source_textures:
			texture_count: int = texture_name.count("_")
			# Only consider textures with similar underscore count to avoid false positives
			if texture_name.startswith(self.obj.id) and texture_name.endswith("_on.png") and abs(texture_count - count) <= 2:
				powered = ["", "_on"]

		# Debug
		if False:
			print(self.source_textures)
			print(f"Processing item model: {self.item_name}")
			print(f"Block or item: {self.block_or_item}")
			print(f"Overrides: {overrides}")
			print(f"Powered states: {powered}")

		all_variants: list[str] = [
			x.replace(".png", "") for x in self.source_textures
			if x.startswith(self.obj.id)
			and abs(x.count("_") - self.obj.id.count("_")) <= 2  # Allow for up to 2 extra underscores. Preventing "awakened_stardust.png" to match "awakened_stardust_furnace_generator_on.png"
		]
		# Filter to only include variants in the same folder
		variants: list[str] = self.get_same_folder_variants(all_variants)

		# Generate its model file(s)
		for on_off in powered:
			content: JsonDict = {}			# Get all variants

			if self.obj.override_model != {}:
				# If it's a block
				if self.block_or_item == "block":
					# Get parent
					content = {"parent": "block/cube_all", "textures": {}}
					# Check in which variants state we are
					variants_without_on = [x for x in variants if "_on" not in x]
					if not exclude_textures and len(variants_without_on) == 1:
						content["textures"]["all"] = f"{self.ns}:item/" + self.get_powered_texture(variants, "", on_off)
					elif not exclude_textures:
						# Prepare models to check
						cake = ["bottom", "side", "top", "inner"]
						orientable_with_bottom = ["front", "bottom", "side", "top"]
						cube_bottom_top = ["bottom", "side", "top"]
						orientable = ["front", "side", "top"]
						cube_column = ["end", "side"]						# Check cake model
						if self.model_in_variants(cake, variants):
							content["parent"] = "block/cake"
							for side in cake:
								texture_key = side.replace("inner", "inside")
								texture_path = f"{self.ns}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][texture_key] = texture_path

							# Generate 6 models for each cake slice
							for i in range(1, 7):
								name: str = f"{self.obj.id}_slice{i}"
								slice_content: JsonDict = {"parent": f"block/cake_slice{i}", "textures": content["textures"]}
								Resource(Model, f"item/{name}{on_off}").write(set_model_encoder(Model(slice_content), max_level=4))

						# Check orientable_with_bottom model
						elif self.model_in_variants(orientable_with_bottom, variants):
							content["parent"] = "block/orientable_with_bottom"
							for side in orientable_with_bottom:
								texture_path = f"{self.ns}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][side] = texture_path

						# Check cube_bottom_top model
						elif self.model_in_variants(cube_bottom_top, variants):
							content["parent"] = "block/cube_bottom_top"
							for side in cube_bottom_top:
								texture_path = f"{self.ns}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][side] = texture_path

						# Check orientable model
						elif self.model_in_variants(orientable, variants):
							content["parent"] = "block/orientable"
							for side in orientable:
								texture_path = f"{self.ns}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][side] = texture_path

						# Check cube_column model
						elif self.model_in_variants(cube_column, variants):
							content["parent"] = "block/cube_column"
							for side in cube_column:
								texture_path = f"{self.ns}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][side] = texture_path

						# Else, if there are no textures override, show error
						elif not overrides.get("textures"):
							if not self.ignore_textures:
								patterns = stp.json_dump({
									"cake": cake,
									"cube_bottom_top": cube_bottom_top,
									"orientable": orientable,
									"cube_column": cube_column
								}, max_level=1)
								raise ValueError(
									f"Block '{self.obj.id}' has invalid variants: {variants},\n"
									"consider overriding the model or adding missing textures to match up one of the following patterns:"
									f"\n{patterns}"
								)

				# Else, it's an item
				else:
					# Get parent
					parent = "item/generated"
					data_id: str = self.obj.base_item
					if data_id != CUSTOM_ITEM_VANILLA and "elements" not in overrides:
						parent = data_id.replace(':', ":item/")

					# Get textures
					if exclude_textures:
						content = {"parent": parent}
					else:
						textures = {"layer0": f"{self.ns}:item/{self.obj.id}{on_off}"}
						content = {"parent": parent, "textures": textures}
					data_id = data_id.replace("minecraft:", "")

					# Check for leather armor textures
					if not exclude_textures and data_id.startswith("leather_"):
						content["textures"]["layer1"] = content["textures"]["layer0"]

					# If there is a "_overlay" texture, make it as layer1
					if not exclude_textures and f"{self.obj.id}_overlay" in variants:
						content["textures"]["layer1"] = f"{self.ns}:item/{self.obj.id}_overlay"

					# Check for bow pulling textures
					elif not exclude_textures and data_id.endswith("bow"):
						sorted_pull_variants: list[str] = sorted(
							[v for v in variants if "_pulling_" in v],
							key=lambda x: int(x.split("_")[-1])
						)
						items_content: JsonDict = {}
						if sorted_pull_variants:
							items_content["model"] = {
								"type": "minecraft:condition",
								"on_false": {
									"type": "minecraft:model",
									"model": f"{self.ns}:item/{self.obj.id}"
								},
								"on_true": {
									"type": "minecraft:range_dispatch",
									"entries": [],
									"fallback": {
										"type": "minecraft:model",
										"model": f"{self.ns}:item/{self.obj.id}_pulling_0"
									},
									"property": "minecraft:use_duration",
									"scale": 0.05
								},
								"property": "minecraft:using_item"
							}

							# Add override for each pulling state
							for i, variant in enumerate(sorted_pull_variants):
								pull_content: JsonDict = {"parent": parent, "textures": {"layer0": f"{self.ns}:item/{variant}"}}

								# Add texture to assets
								variant_png: str = variant + ".png"
								if variant_png in self.source_textures:
									Resource(Texture, f"item/{variant}").write(texture_mcmeta(self.source_textures[variant_png]))

								# Add model to assets
								self.obj.model.suffixed(f"_pulling_{i}").write(set_model_encoder(Model(pull_content), max_level=4))

								if i < (len(sorted_pull_variants) - 1):
									pull: float = 0.65 + (0.25 * i)
									model: str = f"{self.ns}:item/{self.obj.id}_pulling_{i + 1}"
									items_content["model"]["on_true"]["entries"].append({ # type: ignore
										"model": {
											"type": "minecraft:model",
											"model": model
										},
										"threshold": pull
									})

							# Add the items/bow.json file
							self.obj.generated_item_model.suffixed(on_off).write(set_json_encoder(ItemModel(items_content), max_level=4))

			# Add overrides
			for key, value in overrides.items():
				if key == "textures" and value is None:
					# Skip adding textures key if it's explicitly set to None
					continue
				content[key] = value.copy() if isinstance(value, dict) else value

			# If powered, check if the on state is in the variants and add it
			if not exclude_textures and on_off == "_on":
				for key, texture in content.get("textures", {}).items():
					texture: str
					if (texture.split("/")[-1] + on_off) in variants:
						content["textures"][key] = texture + on_off

			# Remove empty textures
			if exclude_textures or not content.get("textures"):
				if "textures" in content:
					del content["textures"]

			# Copy and register used textures
			self.copy_and_register_textures(content)

			# Add model to assets
			if self.obj.override_model != {}:
				self.obj.model.suffixed(on_off).write(set_model_encoder(Model(content), max_level=4))
			Mem.ctx.meta["stewbeet"]["rendered_item_models"].add(self.obj.components["item_model"])

			# Generate the json file required in items/
			if not self.obj.base_item.endswith("bow"):
				# Check if the item has a custom hand model
				if self.obj.hand_model:
					items_model: JsonDict = self.handle_hand_model(variants, on_off)

				# Check if this is a spear with an in_hand variant
				elif self.obj.id.endswith("_spear") and f"{self.obj.id}_in_hand.png" in self.source_textures:
					# Create the special spear model with display context switching
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

					# Create the in_hand model
					in_hand_content: JsonDict = {"parent": "item/spear_in_hand","textures": {"layer0": self.obj.texture.suffixed(f"_in_hand{on_off}")}}

					# Add the in_hand model to assets
					self.obj.model.suffixed(f"_in_hand{on_off}").write(set_model_encoder(Model(in_hand_content), max_level=4))

					# Add the in_hand texture to assets
					in_hand_texture = f"{self.obj.id}_in_hand{on_off}.png"
					if in_hand_texture in self.source_textures:
						self.obj.texture.suffixed(f"_in_hand{on_off}").write(texture_mcmeta(self.source_textures[in_hand_texture]))
					elif f"{self.obj.id}_in_hand.png" in self.source_textures and not on_off:
						self.obj.texture.suffixed("_in_hand").write(texture_mcmeta(self.source_textures[f"{self.obj.id}_in_hand.png"]))
				else:
					# Standard item model
					items_model = {"model": {"type": "minecraft:model", "model": self.obj.model.suffixed(on_off)}}

				self.obj.generated_item_model.suffixed(on_off).write(set_json_encoder(ItemModel(items_model), max_level=4))

		# Return
		return self.used_minecraft_textures

