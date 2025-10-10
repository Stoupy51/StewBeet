
# Imports
from __future__ import annotations

import os
from collections.abc import Iterable

from beet import ItemModel, Model, Texture
from beet.core.utils import JsonDict
from stouputils.decorators import LogLevels, handle_error, simple_cache
from stouputils.io import super_json_dump, super_json_load
from stouputils.print import error

from ....core.__memory__ import Mem
from ....core.constants import CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA, GROWING_SEED, OVERRIDE_MODEL
from ....core.utils.io import set_json_encoder


class AutoModel:
	""" Class to handle item model processing.

	Attributes:
		item_name       (str):            The name of the item.
		data            (dict):           The parsed JSON data of the item model.
		parent          (str | None):     The parent model of this item model.
		textures        (dict):           The textures used by this item model.
		namespace       (str):            The namespace of the item model.
		block_or_item   (str):            Whether this is a block or item model.
		used_textures   (set[str]):       Set of used textures.
		source_textures (dict[str, str]): Dictionary of source textures.
		ignore_textures (bool):           Whether to ignore texture-related errors.
	"""
	# Class variables
	DEFAULT_PARENT: str = "item/generated"
	def __init__(self, item_name: str, data: JsonDict, source_textures: dict[str, str], ignore_textures: bool = False):
		""" Initialize the AutoModel.

		Args:
			item_name (str): The name of the item.
			data (JsonDict): The item data from the definitions.
			source_textures (dict[str, str]): Dictionary of source textures.
			ignore_textures (bool): Whether to ignore texture-related errors.
		"""
		self.item_name: str = item_name
		self.data: JsonDict = data
		self.ns: str = Mem.ctx.project_id
		self.block_or_item: str = "item"
		self.used_textures: set[str] = set()
		self.source_textures: dict[str, str] = source_textures
		self.ignore_textures: bool = ignore_textures

		# Initialize model data
		self.parent = self.data.get("parent", self.DEFAULT_PARENT)
		self.textures = self.data.get("textures", {})

	@classmethod
	def from_definitions(cls, item_name: str, data: JsonDict, source_textures: dict[str, str], ignore_textures: bool = False) -> AutoModel:
		""" Create an AutoModel from a definitions entry.

		Args:
			item_name (str): The name of the item.
			data (JsonDict): The item data from the definitions.
			source_textures (dict[str, str]): Dictionary of source textures.
			ignore_textures (bool): Whether to ignore textures in the model.

		Returns:
			AutoModel: The created AutoModel instance.
		"""
		return cls(item_name, data, source_textures, ignore_textures)

	@handle_error(exceptions=ValueError, error_log=LogLevels.ERROR_TRACEBACK)
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

	@simple_cache
	def get_same_folder_variants(self, variants: Iterable[str]) -> list[str]:
		""" Get variants that are in the same folder as the item.

		Args:
			variants  (Iterable[str]): Iterable of variant names.

		Returns:
			list[str]: List of variants in the same folder.
		"""
		target_folder_depth: int = self.item_name.count('/')
		same_folder_variants: list[str] = []
		for variant in variants:
			variant_folder_depth: int = variant.count('/')
			if variant_folder_depth == target_folder_depth:
				# Check if all folder parts before the filename are the same
				if target_folder_depth == 0:
					same_folder_variants.append(variant)
				else:
					target_folder: str = '/'.join(self.item_name.split('/')[:-1])
					variant_folder: str = '/'.join(variant.split('/')[:-1])
					if target_folder == variant_folder:
						same_folder_variants.append(variant)
		return same_folder_variants

	def handle_growing_seeds(self) -> None:
		""" Handle growing seeds by adding growth stage models and textures. """
		# Retrieve growing seed data
		growing_seed_data: JsonDict = self.data[GROWING_SEED]
		texture_basename: str = growing_seed_data.get("texture_basename", self.item_name)
		planted_on: str = growing_seed_data["planted_on"]
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
					error(f"Missing texture for growing seed stage: '{stage_texture_name}.png'")
				continue

			# Create model for this stage
			stage_model: JsonDict = {
				"textures": {
					"1": f"block/{planted_on}",
					"2": f"{self.ns}:item/seeds/{stage_texture_name}",
					"particle": f"block/{planted_on}"
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
			Mem.ctx.assets[self.ns].models[f"item/seeds/{stage_texture_name}"] = set_json_encoder(Model(stage_model), max_level=4)
			items_model = {"model": {"type": "minecraft:model", "model": f"{self.ns}:item/seeds/{stage_texture_name}"}}
			Mem.ctx.assets[self.ns].item_models[f"seeds/{stage_texture_name}"] = set_json_encoder(ItemModel(items_model), max_level=4)

			# Add the texture to assets
			mcmeta: JsonDict | None = None
			if os.path.exists(stage_textures[stage_texture_name] + ".mcmeta"):
				mcmeta = super_json_load(stage_textures[stage_texture_name] + ".mcmeta")
			Mem.ctx.assets[self.ns].textures[f"item/seeds/{stage_texture_name}"] = Texture(source_path=stage_textures[stage_texture_name], mcmeta=mcmeta)

	@handle_error(exceptions=ValueError, error_log=LogLevels.ERROR_TRACEBACK)
	def process(self) -> None:
		""" Process the item model. """
		# If the item is a growing seed, handle it
		if GROWING_SEED in self.data:
			self.handle_growing_seeds()

		# If no item model, return
		if not self.data.get("item_model"):
			return

		# If item_model is already processed, return
		if self.data["item_model"] in Mem.ctx.meta["stewbeet"]["rendered_item_models"]:
			return

		# Initialize variables
		if (self.data.get("id") == CUSTOM_BLOCK_VANILLA or
			any((isinstance(x, str) and "block" in x) for x in self.data.get(OVERRIDE_MODEL, {}).values())):
			self.block_or_item = "block"

		overrides: JsonDict = self.data.get(OVERRIDE_MODEL, {})

		# Check if textures should be excluded completely
		exclude_textures: bool = "textures" in overrides and overrides.get("textures") is None

		# Get powered states (if any)
		powered: list[str] = [""]
		for texture_name in self.source_textures:
			if texture_name.startswith(self.item_name) and texture_name.endswith("_on.png"):
				powered = ["", "_on"]

		# Debug
		if False:
			print(self.source_textures)
			print(f"Processing item model: {self.item_name}")
			print(f"Block or item: {self.block_or_item}")
			print(f"Overrides: {overrides}")
			print(f"Powered states: {powered}")

		# Generate its model file(s)
		for on_off in powered:
			content: JsonDict = {}			# Get all variants
			all_variants: list[str] = [
				x.replace(".png", "") for x in self.source_textures
				if os.path.basename(x).startswith(self.item_name)
			]
			# Filter to only include variants in the same folder
			variants: list[str] = self.get_same_folder_variants(all_variants)

			if self.data.get(OVERRIDE_MODEL, None) != {}:
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
								name: str = f"{self.item_name}_slice{i}"
								slice_content: JsonDict = {"parent": f"block/cake_slice{i}", "textures": content["textures"]}
								Mem.ctx.assets[self.ns].models[f"item/{name}{on_off}"] = set_json_encoder(Model(slice_content), max_level=4)

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
						elif not self.data.get(OVERRIDE_MODEL, {}).get("textures"):
							if not self.ignore_textures:
								patterns = super_json_dump({
									"cake": cake,
									"cube_bottom_top": cube_bottom_top,
									"orientable": orientable,
									"cube_column": cube_column
								}, max_level=1)
								raise ValueError(
									f"Block '{self.item_name}' has invalid variants: {variants},\n"
									"consider overriding the model or adding missing textures to match up one of the following patterns:"
									f"\n{patterns}"
								)

				# Else, it's an item
				else:
					# Get parent
					parent = "item/generated"
					data_id: str = self.data["id"]
					if data_id != CUSTOM_ITEM_VANILLA:
						parent = data_id.replace(':', ":item/")

					# Get textures
					if exclude_textures:
						content = {"parent": parent}
					else:
						textures = {"layer0": f"{self.ns}:item/{self.item_name}{on_off}"}
						content = {"parent": parent, "textures": textures}
					data_id = data_id.replace("minecraft:", "")

					# Check for leather armor textures
					if not exclude_textures and data_id.startswith("leather_"):
						content["textures"]["layer1"] = content["textures"]["layer0"]

					# If there is a "_overlay" texture, make it as layer1
					if not exclude_textures and f"{self.item_name}_overlay" in variants:
						content["textures"]["layer1"] = f"{self.ns}:item/{self.item_name}_overlay"

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
									"model": f"{self.ns}:item/{self.item_name}"
								},
								"on_true": {
									"type": "minecraft:range_dispatch",
									"entries": [],
									"fallback": {
										"type": "minecraft:model",
										"model": f"{self.ns}:item/{self.item_name}_pulling_0"
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
									mcmeta: JsonDict | None = None
									if os.path.exists(variant_png + ".mcmeta"):
										mcmeta = super_json_load(variant_png + ".mcmeta")
									Mem.ctx.assets[self.ns].textures[f"item/{variant}"] = Texture(source_path=self.source_textures[variant_png], mcmeta=mcmeta)

								# Add model to assets
								Mem.ctx.assets[self.ns].models[f"item/{self.item_name}_pulling_{i}"] = set_json_encoder(Model(pull_content), max_level=4)

								if i < (len(sorted_pull_variants) - 1):
									pull: float = 0.65 + (0.25 * i)
									model: str = f"{self.ns}:item/{self.item_name}_pulling_{i + 1}"
									items_content["model"]["on_true"]["entries"].append({ # type: ignore
										"model": {
											"type": "minecraft:model",
											"model": model
										},
										"threshold": pull
									})

							# Add the items/bow.json file
							Mem.ctx.assets[self.ns].item_models[self.item_name + on_off] = set_json_encoder(ItemModel(items_content), max_level=4)

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

			# Add used textures (ignore minecraft namespace)
			if content.get("textures"):
				for texture in content["textures"].values():
					if texture.startswith("minecraft:"):
						continue
					self.used_textures.add(texture)

			# Copy used textures
			if not exclude_textures and content.get("textures"):
				for texture in content["textures"].values():
					# Ignore if minecraft namespace
					if texture.startswith("minecraft:"):
						continue

					texture_name = texture.split(":")[-1].split("/")[-1]  # Get just the filename
					texture_name += ".png"
					if texture_name in self.source_textures:
						mcmeta: JsonDict | None = None
						if os.path.exists(self.source_textures[texture_name] + ".mcmeta"):
							mcmeta = super_json_load(self.source_textures[texture_name] + ".mcmeta")
						Mem.ctx.assets[texture] = Texture(source_path=self.source_textures[texture_name], mcmeta=mcmeta)
					else:
						if not self.ignore_textures:
							raise ValueError(f"Texture '{texture_name}' not found in source textures")

			# Remove empty textures
			if exclude_textures or not content.get("textures"):
				if "textures" in content:
					del content["textures"]

			# Add model to assets
			if self.data.get(OVERRIDE_MODEL, None) != {}:
				Mem.ctx.assets[self.ns].models[f"item/{self.item_name}{on_off}"] = set_json_encoder(Model(content), max_level=4)
			Mem.ctx.meta["stewbeet"]["rendered_item_models"].add(self.data["item_model"])

			# Generate the json file required in items/
			if not self.data["id"].endswith("bow"):
				items_model = {"model": {"type": "minecraft:model", "model": f"{self.ns}:item/{self.item_name}{on_off}"}}
				Mem.ctx.assets[self.ns].item_models[self.item_name + on_off] = set_json_encoder(ItemModel(items_model), max_level=4)

