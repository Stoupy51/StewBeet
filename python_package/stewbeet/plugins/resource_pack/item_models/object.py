
# Imports
from __future__ import annotations

import os

from beet import ItemModel, Model, Texture
from beet.core.utils import JsonDict
from stouputils.io import super_json_dump, super_json_load
from stouputils.print import error

from ....core.__memory__ import Mem
from ....core.constants import CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA, OVERRIDE_MODEL


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
	def __init__(self, item_name: str, data: dict, source_textures: dict[str, str], ignore_textures: bool = False):
		""" Initialize the AutoModel.

		Args:
			item_name (str): The name of the item.
			data (dict): The item data from the definitions.
			source_textures (dict[str, str]): Dictionary of source textures.
			ignore_textures (bool): Whether to ignore texture-related errors.
		"""
		self.item_name: str = item_name
		self.data: dict = data
		self.namespace: str = Mem.ctx.project_id
		self.block_or_item: str = "item"
		self.used_textures: set[str] = set()
		self.source_textures: dict[str, str] = source_textures
		self.ignore_textures: bool = ignore_textures

		# Initialize model data
		self.parent = self.data.get("parent", self.DEFAULT_PARENT)
		self.textures = self.data.get("textures", {})

	@classmethod
	def from_definitions(cls, item_name: str, data: dict, source_textures: dict[str, str], ignore_textures: bool = False) -> AutoModel:
		""" Create an AutoModel from a definitions entry.

		Args:
			item_name (str): The name of the item.
			data (dict): The item data from the definitions.
			source_textures (dict[str, str]): Dictionary of source textures.
			ignore_textures (bool): Whether to ignore textures in the model.

		Returns:
			AutoModel: The created AutoModel instance.
		"""
		return cls(item_name, data, source_textures, ignore_textures)

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
			error(f"Couldn't find texture for side '{side}' in '{variants}', consider adding missing texture or override the model")
		return ""

	def model_in_variants(self, models: list[str], variants: list[str]) -> bool:
		""" Check if all models are in a string of any variant.

		Args:
			models (list[str]): List of models to check.
			variants (list[str]): List of variants to check against.

		Returns:
			bool: True if all models are in variants.
		"""
		return all(any(model in x for x in variants) for model in models)

	def process(self) -> None:
		""" Process the item model. """
		# If no item model, return
		if not self.data.get("item_model"):
			return

		# Initialize variables
		if (self.data.get("id") == CUSTOM_BLOCK_VANILLA or
			any((isinstance(x, str) and "block" in x) for x in self.data.get(OVERRIDE_MODEL, {}).values())):
			self.block_or_item = "block"

		overrides: dict = self.data.get(OVERRIDE_MODEL, {})

		# Get powered states (if any)
		powered = [""]
		on_textures = []
		for texture_name in self.source_textures:
			if texture_name.startswith(self.item_name) and texture_name.endswith("_on.png"):
				powered = ["", "_on"]
				on_textures.append(texture_name)

		# Debug
		if False:
			print(self.source_textures)
			print(f"Processing item model: {self.item_name}")
			print(f"Block or item: {self.block_or_item}")
			print(f"Overrides: {overrides}")
			print(f"Powered states: {powered}")
			print(f"On textures: {on_textures}")

		# Generate its model file(s)
		for on_off in powered:
			content: dict = {}

			# Get all variants
			variants: list[str] = [
				x.replace(".png", "") for x in self.source_textures
				if "gui/" not in x and x.startswith(self.item_name)
			]

			if self.data.get(OVERRIDE_MODEL, None) != {}:
				# If it's a block
				if self.block_or_item == "block":
					# Get parent
					content = {"parent": "block/cube_all", "textures": {}}

					# Check in which variants state we are
					variants_without_on = [x for x in variants if "_on" not in x]
					if len(variants_without_on) == 1:
						content["textures"]["all"] = f"{self.namespace}:item/" + self.get_powered_texture(variants, "", on_off)
					else:
						# Prepare models to check
						cake = ["bottom", "side", "top", "inner"]
						cube_bottom_top = ["bottom", "side", "top"]
						orientable = ["front", "side", "top"]
						cube_column = ["end", "side"]						# Check cake model
						if self.model_in_variants(cake, variants):
							content["parent"] = "block/cake"
							for side in cake:
								texture_key = side.replace("inner", "inside")
								texture_path = f"{self.namespace}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][texture_key] = texture_path

							# Generate 6 models for each cake slice
							for i in range(1, 7):
								name: str = f"{self.item_name}_slice{i}"
								slice_content = {"parent": f"block/cake_slice{i}", "textures": content["textures"]}
								Mem.ctx.assets[f"{self.namespace}:item/{name}{on_off}"] = Model(super_json_dump(slice_content, max_level=4))						# Check cube_bottom_top model
						elif self.model_in_variants(cube_bottom_top, variants):
							content["parent"] = "block/cube_bottom_top"
							for side in cube_bottom_top:
								texture_path = f"{self.namespace}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][side] = texture_path						# Check orientable model
						elif self.model_in_variants(orientable, variants):
							content["parent"] = "block/orientable"
							for side in orientable:
								texture_path = f"{self.namespace}:item/" + self.get_powered_texture(variants, side, on_off)
								content["textures"][side] = texture_path						# Check cube_column model
						elif self.model_in_variants(cube_column, variants):
							content["parent"] = "block/cube_column"
							for side in cube_column:
								texture_path = f"{self.namespace}:item/" + self.get_powered_texture(variants, side, on_off)
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
								error(
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
					textures = {"layer0": f"{self.namespace}:item/{self.item_name}{on_off}"}
					content = {"parent": parent, "textures": textures}
					data_id = data_id.replace("minecraft:", "")

					# Check for leather armor textures
					if data_id.startswith("leather_"):
						textures["layer1"] = textures["layer0"]

					# Check for bow pulling textures
					elif data_id.endswith("bow"):
						sorted_pull_variants: list[str] = sorted(
							[v for v in variants if "_pulling_" in v],
							key=lambda x: int(x.split("_")[-1])
						)
						items_content: dict = {}
						if sorted_pull_variants:
							items_content["model"] = {
								"type": "minecraft:condition",
								"on_false": {
									"type": "minecraft:model",
									"model": f"{self.namespace}:item/{self.item_name}"
								},
								"on_true": {
									"type": "minecraft:range_dispatch",
									"entries": [],
									"fallback": {
										"type": "minecraft:model",
										"model": f"{self.namespace}:item/{self.item_name}_pulling_0"
									},
									"property": "minecraft:use_duration",
									"scale": 0.05
								},
								"property": "minecraft:using_item"
							}

							# Add override for each pulling state
							for i, variant in enumerate(sorted_pull_variants):
								pull_content: dict = {"parent": parent, "textures": {"layer0": f"{self.namespace}:item/{variant}"}}
								# Add texture to assets
								if variant + ".png" in self.source_textures:
									Mem.ctx.assets[f"{self.namespace}:item/{variant}"] = Texture(source_path=self.source_textures[variant + ".png"])
								# Add model to assets
								Mem.ctx.assets[f"{self.namespace}:item/{self.item_name}_pulling_{i}"] = Model(super_json_dump(pull_content, max_level=4))

								if i < (len(sorted_pull_variants) - 1):
									pull: float = 0.65 + (0.25 * i)
									model: str = f"{self.namespace}:item/{self.item_name}_pulling_{i + 1}"
									items_content["model"]["on_true"]["entries"].append({
										"model": {
											"type": "minecraft:model",
											"model": model
										},
										"threshold": pull
									})

							# Add the items/bow.json file
							im: ItemModel = ItemModel(items_content)
							im.encoder = lambda x: super_json_dump(x, max_level=4)  # Use custom encoder to avoid beet's default encoder
							Mem.ctx.assets[f"{self.namespace}:{self.item_name}{on_off}"] = im

			# Add overrides
			for key, value in overrides.items():
				content[key] = value

			# If powered, check if the on state is in the variants and add it
			if on_off == "_on":
				for key, texture in content.get("textures", {}).items():
					texture: str
					if (texture.split("/")[-1] + on_off) in variants:
						content["textures"][key] = texture + on_off

			# Add used textures (ignore minecraft namespace)
			if content.get("textures"):
				for texture in content["textures"].values():
					if texture.startswith("minecraft:"):
						continue
					self.used_textures.add(texture)			# Copy used textures
			if content.get("textures"):
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
							error(f"Texture '{texture_name}' not found in source textures")

			# Add model to assets
			if self.data.get(OVERRIDE_MODEL, None) != {}:
				m: Model = Model(content)
				m.encoder = lambda x: super_json_dump(x, max_level=4)  # Use custom encoder to avoid beet's default encoder
				Mem.ctx.assets[f"{self.namespace}:item/{self.item_name}{on_off}"] = m
			Mem.ctx.meta["stewbeet"]["rendered_item_models"].add(self.data["item_model"])

			# Generate the json file required in items/
			if not self.data["id"].endswith("bow"):
				items_model = {"model": {"type": "minecraft:model", "model": f"{self.namespace}:item/{self.item_name}{on_off}"}}
				im: ItemModel = ItemModel(items_model)
				im.encoder = lambda x: super_json_dump(x, max_level=4)  # Use custom encoder to avoid beet's default encoder
				Mem.ctx.assets[f"{self.namespace}:{self.item_name}{on_off}"] = im

