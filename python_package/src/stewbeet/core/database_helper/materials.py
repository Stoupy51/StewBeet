
# ruff: noqa: B008, E501
# Imports
from pathlib import Path

from beet import Equipment
from stouputils.decorators import handle_error
from stouputils.io import clean_path, relative_path, super_copy, super_json_dump
from stouputils.print import error

from ..__memory__ import Mem, assert_ctx
from ..constants import CATEGORY, CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA, NO_SILK_TOUCH_DROP, PULVERIZING, RESULT_OF_CRAFTING, USED_FOR_CRAFTING, VANILLA_BLOCK, VANILLA_BLOCK_FOR_ORES
from ..ingredients import ingr_repr
from .equipments import SLOTS, EquipmentsConfig, VanillaEquipments, format_attributes


# Generate everything related to the ore
@handle_error
def generate_everything_about_this_material(
	material: str = "adamantium_fragment",
	equipments_config: EquipmentsConfig|None = None
) -> None:
	""" Generate everything related to the ore (armor, tools, weapons, ore, and ingredients (raw, nuggets, blocks)).
		The function will try to find textures in the assets folder to each item
		And return a list of generated items if you want to do something with it.
	Args:
		material			(str):					The ore/material to generate everything about (ex: "adamantium_fragment", "steel_ingot", "minecraft:emerald", "minecraft:copper_ingot", "awakened_stardust!")
													When the material ends with "!", the material base will be the material without the "!"
		equipments_config	(EquipmentsConfig):	The base multiplier to apply
	"""
	# Assertions
	assert_ctx("meta.stewbeet.textures_folder")
	textures_folder: str = clean_path(Mem.ctx.meta.stewbeet.textures_folder)

	# Prepare constants
	textures: dict[str, str] = {
		clean_path(str(p)).split("/")[-1]: relative_path(p, textures_folder)
		for p in Path(textures_folder).rglob("*.png")
	}
	if equipments_config:
		durability_factor = equipments_config.pickaxe_durability / VanillaEquipments.PICKAXE.value[equipments_config.equivalent_to]["durability"]

	# Main ingredient constant
	if '_' in material and not material.endswith("!"):
		material_base = "_".join(material.split(":")[-1].split("_")[:-1])			# Get the base material name (ex: "adamantium" from "adamantium_fragment")
	else:
		if material.endswith("!"):	# Remove the "!" if present
			material = material[:-1]
		material_base = material.split(":")[-1]										# Get the base material name (ex: "adamantium" from "adamantium_fragment")
	main_ingredient = ingr_repr(material, Mem.ctx.project_id) 						# Get the main ingredient for recipes

	# Placeables (ore, deepslate_ore, block, raw_block)
	for block in [f"{material_base}_block", f"{material_base}_ore", f"deepslate_{material_base}_ore", f"raw_{material_base}_block"]:
		if block + ".png" not in textures:
			continue
		if block not in Mem.database:
			Mem.database[block] = {}
		Mem.database[block]["id"] = CUSTOM_BLOCK_VANILLA		# Item for placing custom block
		Mem.database[block][CATEGORY] = "material"				# Category
		Mem.database[block]["custom_data"] = {"smithed":{}}		# Smithed convention
		Mem.database[block]["custom_data"]["smithed"]["dict"] = {"block": {material_base: True}}
		is_there_raw_material = f"raw_{material_base}.png" in textures
		if block.endswith("ore"):
			Mem.database[block][VANILLA_BLOCK] = VANILLA_BLOCK_FOR_ORES	# Placeholder for the base block (required for custom ores)
			Mem.database[block]["custom_data"]["smithed"]["dict"]["ore"] = {material_base: True}
			if is_there_raw_material:
				Mem.database[block][NO_SILK_TOUCH_DROP] = f"raw_{material_base}"			# Drop without silk touch (raw_steel is an item in the database)
			else:
				Mem.database[block][NO_SILK_TOUCH_DROP] = material
		if block.endswith("block"):
			if block.startswith("raw") and is_there_raw_material:
				Mem.database[block][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"group":material_base,"category":"misc","shape":["XXX","XXX","XXX"],"ingredients":{"X":ingr_repr(f"raw_{material_base}", Mem.ctx.project_id)}}]
			else:
				Mem.database[block][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"group":material_base,"category":"misc","shape":["XXX","XXX","XXX"],"ingredients":{"X":main_ingredient}}]
		pass


	## Armor equipment entity (top layer and leggings)
	# Define the resource pack namespace and initialize model data
	namespace_rp: str = f"{Mem.ctx.output_directory}/resource_pack/assets/{Mem.ctx.project_id}"
	model_data: dict = {"layers": {}}

	# Helper function to handle armor layer textures and model data
	def handle_armor_layer(layer_num: int, gear_types: list[str], humanoid_type: str) -> bool:
		# Get the layer texture file name
		layer_file: str = f"{material_base}_layer_{layer_num}.png"

		# Check if we have both the layer texture and at least one gear texture
		if any(f"{material_base}_{gear}.png" in textures for gear in gear_types) and layer_file in textures:

			# Define source and destination paths for texture copying
			source: str = f"{textures_folder}/{textures[layer_file]}"
			destination: str = f"{namespace_rp}/textures/entity/equipment/{humanoid_type}/{textures[layer_file]}"

			# Copy the texture file
			super_copy(source, destination)

			# Add the layer to the model data
			model_data["layers"][humanoid_type] = [{"texture": f"{Mem.ctx.project_id}:{textures[layer_file].replace('.png', '')}"}]
			return True
		return False

	# Process top and bottom armor layers
	top_layer: bool = handle_armor_layer(1, ["helmet", "chestplate"], "humanoid")
	bottom_layer: bool = handle_armor_layer(2, ["leggings", "boots"], "humanoid_leggings")

	# Create equipment asset if any layers were processed
	if top_layer or bottom_layer:
		Mem.ctx.assets[f"{Mem.ctx.project_id}:{material_base}"] = Equipment(super_json_dump(model_data))


	## Armor (helmet, chestplate, leggings, boots)
	for gear in ["helmet", "chestplate", "leggings", "boots"]:
		armor = material_base + "_" + gear
		if armor + ".png" not in textures:
			continue
		if armor not in Mem.database:
			Mem.database[armor] = {}
		Mem.database[armor]["id"] = f"minecraft:leather_{gear}"		# Leather armor by default
		Mem.database[armor][CATEGORY] = "equipment"					# Category
		Mem.database[armor]["custom_data"] = {"smithed":{}}			# Smithed convention
		Mem.database[armor]["custom_data"]["smithed"]["dict"] = {"armor": {material_base: True, gear: True}}
		gear_config = {}
		if gear == "helmet":
			Mem.database[armor][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["XXX","X X"],"ingredients":{"X": main_ingredient}}]
			gear_config = VanillaEquipments.HELMET.value[equipments_config.equivalent_to]
			Mem.database[armor]["max_damage"] = int(gear_config["durability"] * durability_factor)
			if top_layer:
				Mem.database[armor]["equippable"] = {"slot":"head", "asset_id":f"{Mem.ctx.project_id}:{material_base}"}
		elif gear == "chestplate":
			Mem.database[armor][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["X X","XXX","XXX"],"ingredients":{"X": main_ingredient}}]
			gear_config = VanillaEquipments.CHESTPLATE.value[equipments_config.equivalent_to]
			Mem.database[armor]["max_damage"] = int(gear_config["durability"] * durability_factor)
			if top_layer:
				Mem.database[armor]["equippable"] = {"slot":"chest", "asset_id":f"{Mem.ctx.project_id}:{material_base}"}
		elif gear == "leggings":
			Mem.database[armor][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["XXX","X X","X X"],"ingredients":{"X": main_ingredient}}]
			gear_config = VanillaEquipments.LEGGINGS.value[equipments_config.equivalent_to]
			Mem.database[armor]["max_damage"] = int(gear_config["durability"] * durability_factor)
			if bottom_layer:
				Mem.database[armor]["equippable"] = {"slot":"legs", "asset_id":f"{Mem.ctx.project_id}:{material_base}"}
		elif gear == "boots":
			Mem.database[armor][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["X X","X X"],"ingredients":{"X": main_ingredient}}]
			gear_config = VanillaEquipments.BOOTS.value[equipments_config.equivalent_to]
			Mem.database[armor]["max_damage"] = int(gear_config["durability"] * durability_factor)
			if bottom_layer:
				Mem.database[armor]["equippable"] = {"slot":"feet", "asset_id":f"{Mem.ctx.project_id}:{material_base}"}
		Mem.database[armor]["attribute_modifiers"] = format_attributes(equipments_config.get_armor_attributes(), SLOTS[gear], gear_config)

	# Tools (sword, pickaxe, axe, shovel, hoe)
	for gear in ["sword", "pickaxe", "axe", "shovel", "hoe"]:
		tool = material_base + "_" + gear
		if tool + ".png" not in textures:
			continue
		if tool not in Mem.database:
			Mem.database[tool] = {}
		Mem.database[tool]["id"] = f"minecraft:{equipments_config.equivalent_to.value}_{gear}"		# Vanilla tool, ex: iron_sword, wooden_hoe
		Mem.database[tool][CATEGORY] = "equipment"
		Mem.database[tool]["custom_data"] = {"smithed":{}}
		Mem.database[tool]["custom_data"]["smithed"]["dict"] = {"tools": {material_base: True, gear: True}}
		tools_ingr = {"X": main_ingredient, "S": ingr_repr("minecraft:stick")}
		gear_config = {}
		if gear == "sword":
			gear_config = VanillaEquipments.SWORD.value[equipments_config.equivalent_to]
			Mem.database[tool]["max_damage"] = int(gear_config["durability"] * durability_factor)
			Mem.database[tool][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["X","X","S"],"ingredients": tools_ingr}]
		elif gear == "pickaxe":
			gear_config = VanillaEquipments.PICKAXE.value[equipments_config.equivalent_to]
			Mem.database[tool]["max_damage"] = int(gear_config["durability"] * durability_factor)
			Mem.database[tool][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["XXX"," S "," S "],"ingredients": tools_ingr}]
		elif gear == "axe":
			gear_config = VanillaEquipments.AXE.value[equipments_config.equivalent_to]
			Mem.database[tool]["max_damage"] = int(gear_config["durability"] * durability_factor)
			Mem.database[tool][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["XX","XS"," S"],"ingredients": tools_ingr}]
		elif gear == "shovel":
			gear_config = VanillaEquipments.SHOVEL.value[equipments_config.equivalent_to]
			Mem.database[tool]["max_damage"] = int(gear_config["durability"] * durability_factor)
			Mem.database[tool][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["X","S","S"],"ingredients": tools_ingr}]
		elif gear == "hoe":
			gear_config = VanillaEquipments.HOE.value[equipments_config.equivalent_to]
			Mem.database[tool]["max_damage"] = int(gear_config["durability"] * durability_factor)
			Mem.database[tool][RESULT_OF_CRAFTING] = [{"type":"crafting_shaped","result_count":1,"category":"equipment","shape":["XX"," S"," S"],"ingredients": tools_ingr}]
		Mem.database[tool]["attribute_modifiers"] = format_attributes(equipments_config.get_tools_attributes(), SLOTS[gear], gear_config)
		if gear == "sword": # Remove the mining_efficiency attribute from swords
			Mem.database[tool]["attribute_modifiers"] = [am for am in Mem.database[tool]["attribute_modifiers"] if am["type"] != "mining_efficiency"]
	pass

	## Ingredients (ingot, nugget, raw, and other)
	for item in [material_base, f"{material_base}_ingot", f"{material_base}_nugget", f"raw_{material_base}", f"{material_base}_fragment", f"{material_base}_dust", f"{material_base}_stick", f"{material_base}_rod"]:
		if item + ".png" not in textures:
			continue
		if item not in Mem.database:
			Mem.database[item] = {}
		item_type = item.replace(f"{material_base}_", "").replace(f"_{material_base}", "")
		Mem.database[item]["id"] = CUSTOM_ITEM_VANILLA		# Custom item
		Mem.database[item][CATEGORY] = "material"			# Category
		Mem.database[item]["custom_data"] = {"smithed":{}}	# Smithed convention
		Mem.database[item]["custom_data"]["smithed"]["dict"] = {item_type: {material_base: True}}

		# Recipes
		Mem.database[item][RESULT_OF_CRAFTING] = Mem.database[item].get(RESULT_OF_CRAFTING, [])
		Mem.database[item][USED_FOR_CRAFTING] = Mem.database[item].get(USED_FOR_CRAFTING, [])
		if item.endswith("ingot") or item.endswith("fragment") or item == material_base:
			if f"{material_base}_block.png" in textures:
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"crafting_shapeless","result_count":9,"category":"misc","group":material_base,"ingredients":[ingr_repr(f"{material_base}_block", Mem.ctx.project_id)]})
			if f"{material_base}_nugget.png" in textures:
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"crafting_shaped","result_count":1,"category":"misc","group":material_base,"shape":["XXX","XXX","XXX"],"ingredients":{"X":ingr_repr(f"{material_base}_nugget", Mem.ctx.project_id)}})
			if f"raw_{material_base}.png" in textures:
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"smelting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":200,"ingredient":ingr_repr(f"raw_{material_base}", Mem.ctx.project_id)})
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"blasting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":100,"ingredient":ingr_repr(f"raw_{material_base}", Mem.ctx.project_id)})
			if f"{material_base}_dust.png" in textures:
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"smelting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":200,"ingredient":ingr_repr(f"{material_base}_dust", Mem.ctx.project_id)})
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"blasting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":100,"ingredient":ingr_repr(f"{material_base}_dust", Mem.ctx.project_id)})
			if f"{material_base}_ore.png" in textures:
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"smelting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":200,"ingredient":ingr_repr(f"{material_base}_ore", Mem.ctx.project_id)})
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"blasting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":100,"ingredient":ingr_repr(f"{material_base}_ore", Mem.ctx.project_id)})
			if f"deepslate_{material_base}_ore.png" in textures:
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"smelting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":200,"ingredient":ingr_repr(f"deepslate_{material_base}_ore", Mem.ctx.project_id)})
				Mem.database[item][RESULT_OF_CRAFTING].append({"type":"blasting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":100,"ingredient":ingr_repr(f"deepslate_{material_base}_ore", Mem.ctx.project_id)})
		if item.endswith("dust"):
			Mem.database[item][USED_FOR_CRAFTING].append({"type":"smelting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":200,"ingredient":ingr_repr(item, Mem.ctx.project_id),"result":main_ingredient})
			Mem.database[item][USED_FOR_CRAFTING].append({"type":"blasting","result_count":1,"category":"misc","group":material_base,"experience":0.8,"cookingtime":100,"ingredient":ingr_repr(item, Mem.ctx.project_id),"result":main_ingredient})
			Mem.database[item][RESULT_OF_CRAFTING].append({"type":PULVERIZING,"result_count":1,"category":"misc","group":material_base,"ingredient":main_ingredient})
			for pulv_ingr in [f"raw_{material_base}",f"{material_base}_ore",f"deepslate_{material_base}_ore"]:
				if f"{pulv_ingr}.png" in textures:
					Mem.database[item][RESULT_OF_CRAFTING].append({"type":PULVERIZING,"result_count":2,"category":"misc","group":material_base,"ingredient":ingr_repr(pulv_ingr, Mem.ctx.project_id)})
		if item.endswith("nugget"):
			Mem.database[item][RESULT_OF_CRAFTING].insert(0, {"type":"crafting_shapeless","result_count":9,"category":"misc","group":material_base,"ingredients":[main_ingredient]})
			for gear in SLOTS.keys():
				if f"{material_base}_{gear}.png" in textures:
					Mem.database[item][RESULT_OF_CRAFTING].append({"type":"smelting","result_count":1,"category":"equipment","experience":0.8,"cookingtime":200,"ingredient":ingr_repr(f"{material_base}_{gear}", Mem.ctx.project_id)})
		if item.endswith("stick"):
			Mem.database[item][RESULT_OF_CRAFTING].append({"type":"crafting_shaped","result_count":4,"category":"misc","shape":["X","X"],"ingredients":{"X":main_ingredient}})
		if item.endswith("rod"):
			Mem.database[item][RESULT_OF_CRAFTING].append({"type":"crafting_shaped","result_count":1,"category":"misc","shape":["X","X","X"],"ingredients":{"X":main_ingredient}})
		pass


# Generate everything about these ores
def generate_everything_about_these_materials(ores: dict[str, EquipmentsConfig|None]) -> None:
	""" Uses function 'generate_everything_about_this_material' for each ore in the ores dictionary.
	Args:
		ores		(dict[str, EquipmentsConfig|None]):	The ores to apply.
	"""
	for material, ore_config in ores.items():
		generate_everything_about_this_material(material, ore_config)


# Add recipes for dust
def add_recipes_for_dust(material: str, pulverize: list[str|dict], smelt_to: dict) -> None:
	""" Add recipes for dust (pulverize and smelt). If dust isn't found in the database, it will be added automagically.

	All items in the pulverize list will be pulverized to get 2 times the dust.

	If the item is a string, their ingr_repr will be used as "minecraft:{item}"

	Args:
		material	(str):				The material to add dust recipes for, ex: "copper" will add recipes for "copper_dust".
		pulverize	(list[str|dict]):	The list of items to pulverize to get 2 times the dust, ex: ["raw_copper", "copper_ore", "deepslate_copper_ore", ingr_repr("custom_copper", "some_namespace")]
		smelt_to	(dict):				The ingredient representation of the result of smelting the dust, ex: ingr_repr("minecraft:copper_ingot")}
	"""
	# Assertions
	assert_ctx("meta.stewbeet.textures_folder")
	textures_folder: str = clean_path(Mem.ctx.meta.stewbeet.textures_folder)

	# Prepare constants
	textures_set: set[str] = {clean_path(str(p)).split("/")[-1] for p in Path(textures_folder).rglob("*.png")}
	dust: str = material + "_dust"
	if f"{dust}.png" not in textures_set:
		error(f"Error during dust recipe generation: texture '{dust}.png' not found (required for '{material}' dust)")
		return

	# Add dust to the database if not found
	if dust not in Mem.database:
		Mem.database[dust] = {"id": CUSTOM_ITEM_VANILLA, CATEGORY: "material"}

	# Add smelting and blasting recipes
	ingredient: dict = ingr_repr(dust, Mem.ctx.project_id)
	Mem.database[dust][USED_FOR_CRAFTING] = Mem.database[dust].get(USED_FOR_CRAFTING, [])
	Mem.database[dust][USED_FOR_CRAFTING].append({"type":"smelting","result_count":1,"category":"misc","group":material,"experience":0.8,"cookingtime":200,"ingredient":ingredient, "result":smelt_to})
	Mem.database[dust][USED_FOR_CRAFTING].append({"type":"blasting","result_count":1,"category":"misc","group":material,"experience":0.8,"cookingtime":100,"ingredient":ingredient, "result":smelt_to})

	# Add reverse recipe
	Mem.database[dust][RESULT_OF_CRAFTING] = Mem.database[dust].get(RESULT_OF_CRAFTING, [])
	Mem.database[dust][RESULT_OF_CRAFTING].append({"type":PULVERIZING,"result_count":1,"category":"misc","group":material,"ingredient":smelt_to})

	# Add pulverizing recipes
	for item in pulverize:
		pulv_ingr = item if isinstance(item, dict) else ingr_repr(f"minecraft:{item}")
		Mem.database[dust][RESULT_OF_CRAFTING].append({"type":PULVERIZING,"result_count":2,"category":"misc","group":material,"ingredient":pulv_ingr})
	return

# Add recipes for all dusts
def add_recipes_for_all_dusts(dusts_configs: dict[str, tuple[list[str|dict],dict]]) -> None:
	""" Add recipes for all dusts in the dusts_configs dictionary using the add_recipes_for_dust function.

	Args:
		dusts_configs	(dict[str, tuple[list[str|dict],dict]]):	The dusts to add recipes for, ex:

	```py
	{
		"copper": (
			["raw_copper", "copper_ore", "deepslate_copper_ore", ingr_repr("custom_copper", "some_namespace")],
			ingr_repr("minecraft:copper_ingot")
		)
	}
	```
	"""
	for dust, (pulverize, smelt_to) in dusts_configs.items():
		add_recipes_for_dust(dust, pulverize, smelt_to)

