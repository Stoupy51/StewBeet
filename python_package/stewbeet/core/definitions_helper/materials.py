
# ruff: noqa: E501
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import stouputils as stp
from beet import Equipment, Texture
from stouputils.typing import JsonDict

from ..__memory__ import Mem
from ..cls.block import VANILLA_BLOCK_FOR_ORES, Block
from ..cls.ingredients import Ingr
from ..cls.item import Item
from ..cls.recipe import BlastingRecipe, CraftingShapedRecipe, CraftingShapelessRecipe, PulverizingRecipe, RecipeBase, SmeltingRecipe
from ..constants import CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA
from .equipments import SLOTS, EquipmentsConfig, VanillaEquipments, format_attributes


# Constants
@dataclass(frozen=True)
class Gear:
	""" An armor piece or a tool: its crafting shape, and the vanilla equipment its stats scale from. """
	name: str
	shape: tuple[str, ...]
	vanilla: VanillaEquipments


ARMOR: tuple[Gear, ...] = (
	Gear(name="helmet",     shape=("XXX", "X X"),        vanilla=VanillaEquipments.HELMET),
	Gear(name="chestplate", shape=("X X", "XXX", "XXX"), vanilla=VanillaEquipments.CHESTPLATE),
	Gear(name="leggings",   shape=("XXX", "X X", "X X"), vanilla=VanillaEquipments.LEGGINGS),
	Gear(name="boots",      shape=("X X", "X X"),        vanilla=VanillaEquipments.BOOTS),
)
""" Armor pieces, `X` being the material. """

TOOLS: tuple[Gear, ...] = (
	Gear(name="sword",   shape=("X", "X", "S"),         vanilla=VanillaEquipments.SWORD),
	Gear(name="pickaxe", shape=("XXX", " S ", " S "),   vanilla=VanillaEquipments.PICKAXE),
	Gear(name="axe",     shape=("XX", "XS", " S"),      vanilla=VanillaEquipments.AXE),
	Gear(name="shovel",  shape=("X", "S", "S"),         vanilla=VanillaEquipments.SHOVEL),
	Gear(name="hoe",     shape=("XX", " S", " S"),      vanilla=VanillaEquipments.HOE),
	Gear(name="spear",   shape=("  X", " S ", "S  "),   vanilla=VanillaEquipments.SPEAR),
)
""" Tools, `X` being the material and `S` a stick. """

ARMOR_MATERIALS: dict[str, str] = {"stone": "chainmail", "wooden": "leather"}
""" The vanilla armor of a tier whose armor is not named after it. """


# Classes
@dataclass(frozen=True)
class Material:
	""" A material being generated: its names, the textures found for it, and how its equipment is configured. """
	name: str
	""" The material item, `minecraft:emerald` or `steel_ingot`, without the `!` suffix. """
	base: str
	""" What every generated item is named after, `steel` for `steel_ingot`. """
	main: Ingr
	textures: dict[str, str]
	textures_folder: str
	config: EquipmentsConfig | None
	ignore_recipes: bool
	durability_factor: float
	""" Durability of this material's equipment relative to the vanilla tier it is equivalent to. """

	@classmethod
	def of(cls, material: str, config: EquipmentsConfig | None, ignore_recipes: bool, textures_folder: str) -> Self:
		""" A material from its name: the base is cut before the last `_`, or is the whole name when it ends with `!`. """
		if '_' in material and not material.endswith("!"):
			base: str = "_".join(material.split(":")[-1].split("_")[:-1])
		else:
			material = material.removesuffix("!")
			base = material.split(":")[-1]
		durability_factor: float = 1.0
		if config:
			durability_factor = config.pickaxe_durability / VanillaEquipments.PICKAXE.value[config.equivalent_to]["durability"]
		return cls(
			name=material,
			base=base,
			main=Ingr(material),
			textures={
				stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
				for p in sorted(Path(textures_folder).rglob("*.png"), key=str)
			},
			textures_folder=textures_folder,
			config=config,
			ignore_recipes=ignore_recipes or (config is not None and config.ignore_recipes),
			durability_factor=durability_factor,
		)

	def has(self, name: str) -> bool:
		""" Whether a texture named `<name>.png` exists, which is what decides that an item is generated. """
		return f"{name}.png" in self.textures

	def smelt_and_blast(self, ingredient: Ingr, result: Ingr | None = None) -> list[RecipeBase]:
		""" A smelting recipe and the twice faster blasting one, `result` defaulting to the item the recipe is put on. """
		return [
			SmeltingRecipe(result_count=1, category="misc", group=self.base, experience=0.8, cookingtime=200, ingredient=ingredient, result=result),
			BlastingRecipe(result_count=1, category="misc", group=self.base, experience=0.8, cookingtime=100, ingredient=ingredient, result=result),
		]


# Functions
@stp.handle_error
def generate_everything_about_this_material(
	material: str = "adamantium_fragment",
	equipments_config: EquipmentsConfig|None = None,
	ignore_recipes: bool = False
) -> None:
	""" Generate everything related to the ore (armor, tools, weapons, ore, and ingredients (raw, nuggets, blocks)).

	The function will try to find textures in the assets folder to each item
	And return a list of generated items if you want to do something with it.

	Args:
		material:          The ore/material to generate everything about (ex: "adamantium_fragment", "steel_ingot", "minecraft:emerald", "minecraft:copper_ingot", "awakened_stardust!")
													When the material ends with "!", the material base will be the material without the "!"
		equipments_config: The base multiplier to apply
		ignore_recipes:    If True, no recipes will be added in the definitions.
	"""
	textures_folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert textures_folder != "", "Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. Please set a directory path in project configuration."
	m: Material = Material.of(material, equipments_config, ignore_recipes, textures_folder)
	base: str = m.base

	for item in (base, f"{base}_fragment", f"{base}_ingot", f"{base}_nugget", f"raw_{base}", f"{base}_dust", f"{base}_stick", f"{base}_rod"):
		if m.has(item):
			write_ingredient(m, item)
	for block in (f"{base}_block", f"{base}_ore", f"deepslate_{base}_ore", f"raw_{base}_block"):
		if m.has(block):
			write_placeable(m, block)

	top_layer, bottom_layer = write_equipment_asset(m)
	if equipments_config is not None:
		for gear in ARMOR:
			if m.has(f"{base}_{gear.name}"):
				write_armor(m, equipments_config, gear, layer_drawn=bottom_layer if gear.name == "leggings" else top_layer)
	for gear in TOOLS:
		if m.has(f"{base}_{gear.name}"):
			write_tool(m, gear)


def write_ingredient(m: Material, item: str) -> None:
	""" Define an ingredient of the material (ingot, nugget, raw, dust, stick...) and the recipes making it. """
	obj: Item = Item.from_id(item, strict=False)
	item_type: str = item.replace(f"{m.base}_", "").replace(f"_{m.base}", "")
	obj.base_item = CUSTOM_ITEM_VANILLA
	obj.manual_category = "material"
	obj.components["custom_data"] = {"smithed": {"dict": {item_type: {m.base: True}}}}
	if m.ignore_recipes:
		return
	if item.endswith("nugget"):
		obj.recipes.insert(0, CraftingShapelessRecipe(result_count=9, category="misc", group=m.base, ingredients=[m.main]))
	obj.recipes.extend(ingredient_recipes(m, item))


def ingredient_recipes(m: Material, item: str) -> list[RecipeBase]:
	""" The recipes making an ingredient, from the other forms of the material that have a texture. """
	base: str = m.base
	recipes: list[RecipeBase] = []
	if item.endswith(("ingot", "fragment")) or item == base:
		recipes += refined_recipes(m)
	if item.startswith("raw_") and m.has(f"raw_{base}_block"):
		recipes.append(CraftingShapelessRecipe(result_count=9, category="misc", group=base, ingredients=[Ingr(f"raw_{base}_block")]))
	if item.endswith("dust"):
		recipes += dust_recipes(m, item)
	if item.endswith("nugget"):
		recipes += [
			SmeltingRecipe(result_count=1, category="equipment", experience=0.8, cookingtime=200, ingredient=Ingr(f"{base}_{gear}"))
			for gear in SLOTS if m.has(f"{base}_{gear}")
		]
	if item.endswith("stick"):
		recipes.append(CraftingShapedRecipe(result_count=4, category="misc", shape=["X","X"], ingredients={"X":m.main}))
	if item.endswith("rod"):
		recipes.append(CraftingShapedRecipe(result_count=1, category="misc", shape=["X","X","X"], ingredients={"X":m.main}))
	return recipes


def refined_recipes(m: Material) -> list[RecipeBase]:
	""" The recipes making the refined material: out of its block and its nuggets, and by smelting its raw form, dust or ores. """
	base: str = m.base
	recipes: list[RecipeBase] = []
	if m.has(f"{base}_block"):
		recipes.append(CraftingShapelessRecipe(result_count=9, category="misc", group=base, ingredients=[Ingr(f"{base}_block")]))
	if m.has(f"{base}_nugget"):
		recipes.append(CraftingShapedRecipe(result_count=1, category="misc", group=base, shape=["XXX","XXX","XXX"], ingredients={"X":Ingr(f"{base}_nugget")}))
	for source in (f"raw_{base}", f"{base}_dust", f"{base}_ore", f"deepslate_{base}_ore"):
		if m.has(source):
			recipes += m.smelt_and_blast(Ingr(source))
	return recipes


def dust_recipes(m: Material, dust: str) -> list[RecipeBase]:
	""" The recipes around the dust: smelting it back into the material, and pulverizing the material, its raw form and its ores. """
	base: str = m.base
	return [
		*m.smelt_and_blast(Ingr(dust), result=m.main),
		PulverizingRecipe(result_count=1, category="misc", group=base, ingredient=m.main),
		*(
			PulverizingRecipe(result_count=2, category="misc", group=base, ingredient=Ingr(source))
			for source in (f"raw_{base}", f"{base}_ore", f"deepslate_{base}_ore") if m.has(source)
		),
	]


def write_placeable(m: Material, block: str) -> None:
	""" Define a block of the material: its storage block, raw block or ores, which drop the raw material without silk touch. """
	obj: Block = Block.from_id(block, strict=False)
	obj.base_item = CUSTOM_BLOCK_VANILLA
	obj.manual_category = "material"
	obj.components["custom_data"] = {"smithed": {"dict": {"block": {m.base: True}}}}
	has_raw: bool = m.has(f"raw_{m.base}")
	if block.endswith("ore"):
		obj.vanilla_block = VANILLA_BLOCK_FOR_ORES
		obj.components["custom_data"]["smithed"]["dict"]["ore"] = {m.base: True}
		obj.no_silk_touch_drop = f"raw_{m.base}" if has_raw else m.name
	if block.endswith("block") and not m.ignore_recipes:
		ingredient: Ingr = Ingr(f"raw_{m.base}") if block.startswith("raw") and has_raw else m.main
		obj.recipes.append(CraftingShapedRecipe(result_count=1, group=m.base, category="misc", shape=["XXX","XXX","XXX"], ingredients={"X":ingredient}))


def write_equipment_asset(m: Material) -> tuple[bool, bool]:
	""" The equipment asset drawing the material's armor on a player, from its `_layer_1` and `_layer_2` textures.

	Returns:
		Whether the top layer and the leggings layer were found.
	"""
	model_data: JsonDict = {"layers": {}}
	top_layer: bool = copy_armor_layer(m, model_data, 1, ("helmet", "chestplate", "boots"), "humanoid")
	bottom_layer: bool = copy_armor_layer(m, model_data, 2, ("leggings",), "humanoid_leggings")
	if top_layer or bottom_layer:
		Mem.ctx.assets[f"{Mem.ctx.project_id}:{m.base}"] = Equipment(stp.json_dump(model_data))
	return top_layer, bottom_layer


def copy_armor_layer(m: Material, model_data: JsonDict, layer_num: int, gear_types: tuple[str, ...], humanoid_type: str) -> bool:
	""" Copy one layer texture into the assets and add it to `model_data`, when it and one of the pieces it draws exist. """
	layer_file: str = f"{m.base}_layer_{layer_num}.png"
	if layer_file not in m.textures or not any(m.has(f"{m.base}_{gear}") for gear in gear_types):
		return False
	source: str = stp.relative_path(os.path.splitext(m.textures[layer_file])[0], m.textures_folder)
	destination: str = f"entity/equipment/{humanoid_type}/{source}"
	Mem.ctx.assets[Mem.ctx.project_id].textures[destination] = Texture(source_path=m.textures[layer_file])
	model_data["layers"][humanoid_type] = [{"texture": f"{Mem.ctx.project_id}:{source}"}]
	return True


def write_armor(m: Material, config: EquipmentsConfig, gear: Gear, layer_drawn: bool) -> None:
	""" Define an armor piece, wearable with the material's look when the layer drawing it exists. """
	obj: Item = Item.from_id(f"{m.base}_{gear.name}", strict=False)
	equivalent_to: str = ARMOR_MATERIALS.get(config.equivalent_to.value, config.equivalent_to.value)
	obj.base_item = f"minecraft:{equivalent_to}_{gear.name}"
	obj.manual_category = "equipment"
	obj.components["custom_data"] = {"smithed": {"dict": {"armor": {m.base: True, gear.name: True}}}}
	if not m.ignore_recipes:
		obj.recipes.append(CraftingShapedRecipe(result_count=1,category="equipment",shape=list(gear.shape),ingredients={"X": m.main},manual_priority=0))
	gear_config: JsonDict = gear.vanilla.value[config.equivalent_to]
	obj.components["max_damage"] = int(gear_config["durability"] * m.durability_factor)
	if layer_drawn:
		obj.components["equippable"] = {"slot":SLOTS[gear.name], "asset_id":f"{Mem.ctx.project_id}:{m.base}"}
	obj.components["attribute_modifiers"] = format_attributes(config.get_armor_attributes(), SLOTS[gear.name], gear_config)


def write_tool(m: Material, gear: Gear) -> None:
	""" Define a tool, mining like the vanilla tier the material is configured to equal. """
	obj: Item = Item.from_id(f"{m.base}_{gear.name}", strict=False)
	if m.config:
		obj.base_item = f"minecraft:{m.config.equivalent_to.value}_{gear.name}"
	obj.manual_category = "equipment"
	obj.components["custom_data"] = {"smithed": {"dict": {"tools": {m.base: True, gear.name: True}}}}
	gear_config: JsonDict = {}
	if m.config:
		gear_config = gear.vanilla.value[m.config.equivalent_to]
		obj.components["max_damage"] = int(gear_config["durability"] * m.durability_factor)
	if not m.ignore_recipes:
		tools_ingr: dict[str, Ingr] = {"X": m.main, "S": Ingr("minecraft:stick")}
		obj.recipes.append(CraftingShapedRecipe(result_count=1,category="equipment",shape=list(gear.shape),ingredients=tools_ingr,manual_priority=0))
	if m.config:
		obj.components["attribute_modifiers"] = format_attributes(m.config.get_tools_attributes(), SLOTS[gear.name], gear_config)
	# A weapon mines nothing
	if gear.name in ("sword", "spear"):
		obj.components["attribute_modifiers"] = [am for am in obj.components["attribute_modifiers"] if am["type"] != "mining_efficiency"]


# Generate everything about these ores
def generate_everything_about_these_materials(ores: dict[str, EquipmentsConfig|None], ignore_recipes: bool = False) -> None:
	""" Uses function 'generate_everything_about_this_material' for each ore in the ores dictionary.

	Args:
		ores:           The ores to apply.
			The ore/material (key) to generate everything about (ex: "adamantium_fragment", "steel_ingot", "minecraft:emerald", "minecraft:copper_ingot", "awakened_stardust!")
			When the material ends with "!", the material base will be the material without the "!", else we try to cut before the last "_".
		ignore_recipes: If True, no recipes will be added in the definitions.
	"""
	for material, ore_config in ores.items():
		generate_everything_about_this_material(material, ore_config, ignore_recipes=ignore_recipes)


# Add recipes for dust
def add_recipes_for_dust(material: str, pulverize: list[str | JsonDict], smelt_to: Ingr) -> None:
	""" Add recipes for dust (pulverize and smelt). If dust isn't found in the definitions, it will be added automagically.

	All items in the pulverize list will be pulverized to get 2 times the dust.

	If the item is a string, their Ingr will be used as "minecraft:{item}"

	Args:
		material:  The material to add dust recipes for, ex: "copper" will add recipes for "copper_dust".
		pulverize: The list of items to pulverize to get 2 times the dust, ex: ["raw_copper", "copper_ore", "deepslate_copper_ore", Ingr("custom_copper", "some_namespace")]
		smelt_to:  The ingredient representation of the result of smelting the dust, ex: Ingr("minecraft:copper_ingot")}
	"""
	# Assertions
	textures_folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert textures_folder != "", "Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. Please set a directory path in project configuration."

	# Prepare constants
	textures_set: set[str] = {stp.clean_path(str(p)).split("/")[-1] for p in Path(textures_folder).rglob("*.png")}
	dust: str = material + "_dust"
	if f"{dust}.png" not in textures_set:
		stp.error(f"Error during dust recipe generation: texture '{dust}.png' not found (required for '{material}' dust)")
		return

	# Add dust to the definitions if not found
	obj = Item.from_id(dust, strict=False)  # Ensure the item is created in the definitions
	obj.base_item = CUSTOM_ITEM_VANILLA
	obj.manual_category = "material"
	obj.components["custom_data"] = {"smithed":{}}
	obj.components["custom_data"]["smithed"]["dict"] = {"dust": {material: True}}

	# Add smelting and blasting recipes
	ingredient: JsonDict = Ingr(dust)
	obj.recipes.append(SmeltingRecipe(result_count=1,category="misc",group=material,experience=0.8,cookingtime=200,ingredient=ingredient, result=smelt_to))
	obj.recipes.append(BlastingRecipe(result_count=1,category="misc",group=material,experience=0.8,cookingtime=100,ingredient=ingredient, result=smelt_to))

	# Add reverse recipe
	obj.recipes.append(PulverizingRecipe(result_count=1,category="misc",group=material,ingredient=smelt_to))

	# Add pulverizing recipes
	for item in pulverize:
		pulv_ingr = Ingr(item) if isinstance(item, dict) else Ingr(f"minecraft:{item}")
		obj.recipes.append(PulverizingRecipe(result_count=2,category="misc",group=material,ingredient=pulv_ingr))
	return

# Add recipes for all dusts
def add_recipes_for_all_dusts(dusts_configs: dict[str, tuple[list[str | JsonDict], Ingr]]) -> None:
	""" Add recipes for all dusts in the dusts_configs dictionary using the add_recipes_for_dust function.

	Args:
		dusts_configs: The dusts to add recipes for.

	.. code-block:: python

		{
			"copper": (
				["raw_copper", "copper_ore", "deepslate_copper_ore", Ingr("custom_copper", "some_namespace")],
				Ingr("minecraft:copper_ingot")
			)
		}
	"""
	for dust, (pulverize, smelt_to) in dusts_configs.items():
		add_recipes_for_dust(dust, pulverize, smelt_to)

