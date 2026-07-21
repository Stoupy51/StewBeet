
# ruff: noqa: E101
# Imports
from enum import Enum
from typing import cast

import stouputils as stp
from stouputils.typing import JsonDict

from ..__memory__ import Mem

# Constants
SLOTS: dict[str, str] = {
	"helmet": "head",
	"chestplate": "chest",
	"leggings": "legs",
	"boots": "feet",
	"sword": "mainhand",
	"pickaxe": "mainhand",
	"axe": "mainhand",
	"shovel": "mainhand",
	"hoe": "mainhand",
	"spear": "mainhand",
}
INVERSE_SLOTS: dict[str, str] = {v: k for k, v in SLOTS.items()}
UNIQUE_SLOTS_VALUES: list[str] = []	# No sorted(set()) since we want to preserve the current order
for slot in SLOTS.values():
	if slot not in UNIQUE_SLOTS_VALUES:
		UNIQUE_SLOTS_VALUES.append(slot)

class DefaultOre(Enum):
	NETHERITE = "netherite"
	DIAMOND = "diamond"
	IRON = "iron"
	GOLD = "golden"
	CHAINMAIL = "stone"		# Stone tools
	COPPER = "copper"		# Copper added in 1.21.9
	LEATHER = "wooden"		# Wooden tools

class VanillaEquipments(Enum):
	""" Default vanilla equipments values (durability, armor, armor_toughness, knockback_resistance, attack_damage, attack_speed) """
	HELMET			= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 55,		"armor": 1},
						DefaultOre.COPPER:		{"durability": 121,		"armor": 2},
						DefaultOre.CHAINMAIL:	{"durability": 165,		"armor": 2},
						DefaultOre.IRON:		{"durability": 165,		"armor": 2},
						DefaultOre.GOLD:		{"durability": 77,		"armor": 2},
						DefaultOre.DIAMOND:		{"durability": 363,		"armor": 3,	"armor_toughness": 2},
			 			DefaultOre.NETHERITE:	{"durability": 407,		"armor": 3,	"armor_toughness": 3,	"knockback_resistance": 0.1}
					})
	CHESTPLATE		= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 80,		"armor": 3},
						DefaultOre.COPPER:		{"durability": 176,		"armor": 4},
						DefaultOre.CHAINMAIL:	{"durability": 240,		"armor": 5},
						DefaultOre.IRON:		{"durability": 240,		"armor": 6},
						DefaultOre.GOLD:		{"durability": 112,		"armor": 5},
						DefaultOre.DIAMOND: 	{"durability": 528,		"armor": 8,	"armor_toughness": 2},
						DefaultOre.NETHERITE:	{"durability": 592,		"armor": 8,	"armor_toughness": 3,	"knockback_resistance": 0.1}
					})
	LEGGINGS		= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 75,		"armor": 2},
						DefaultOre.COPPER:		{"durability": 165,		"armor": 3},
  						DefaultOre.CHAINMAIL:	{"durability": 225,		"armor": 4},
						DefaultOre.IRON:		{"durability": 225,		"armor": 5},
						DefaultOre.GOLD:		{"durability": 105,		"armor": 3},
						DefaultOre.DIAMOND:		{"durability": 495,		"armor": 6,	"armor_toughness": 2},
						DefaultOre.NETHERITE:	{"durability": 555,		"armor": 6,	"armor_toughness": 3,	"knockback_resistance": 0.1}
					})
	BOOTS			= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 65,		"armor": 1},
						DefaultOre.COPPER:		{"durability": 143,		"armor": 1},
						DefaultOre.CHAINMAIL:	{"durability": 195,		"armor": 1},
						DefaultOre.IRON:		{"durability": 195,		"armor": 2},
						DefaultOre.GOLD:		{"durability": 95,		"armor": 1},
						DefaultOre.DIAMOND:		{"durability": 429,		"armor": 3,	"armor_toughness": 2},
						DefaultOre.NETHERITE:	{"durability": 481,		"armor": 3,	"armor_toughness": 3,	"knockback_resistance": 0.1}
					})
	SWORD			= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 59,		"attack_damage": 4,		"attack_speed": -2.40},
						DefaultOre.COPPER:		{"durability": 190,		"attack_damage": 5,		"attack_speed": -2.40},
						DefaultOre.CHAINMAIL:	{"durability": 131,		"attack_damage": 5,		"attack_speed": -2.40},
						DefaultOre.IRON:		{"durability": 250,		"attack_damage": 6,		"attack_speed": -2.40},
						DefaultOre.GOLD:		{"durability": 32,		"attack_damage": 4,		"attack_speed": -2.40},
						DefaultOre.DIAMOND:		{"durability": 1561,	"attack_damage": 7,		"attack_speed": -2.40},
						DefaultOre.NETHERITE:	{"durability": 2031,	"attack_damage": 8,		"attack_speed": -2.40}
					})
	PICKAXE			= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 59,		"attack_damage": 2,		"attack_speed": -2.8},
						DefaultOre.COPPER:		{"durability": 190,		"attack_damage": 3,		"attack_speed": -2.8},
						DefaultOre.CHAINMAIL:	{"durability": 131,		"attack_damage": 3,		"attack_speed": -2.8},
						DefaultOre.IRON:		{"durability": 250,		"attack_damage": 4,		"attack_speed": -2.8},
						DefaultOre.GOLD:		{"durability": 32,		"attack_damage": 2,		"attack_speed": -2.8},
						DefaultOre.DIAMOND:		{"durability": 1561,	"attack_damage": 5,		"attack_speed": -2.8},
						DefaultOre.NETHERITE:	{"durability": 2031,	"attack_damage": 6,		"attack_speed": -2.8}
					})
	AXE				= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 59,		"attack_damage": 7,		"attack_speed": -3.20},
						DefaultOre.COPPER:		{"durability": 190,		"attack_damage": 9,		"attack_speed": -3.20},
						DefaultOre.CHAINMAIL:	{"durability": 131,		"attack_damage": 9,		"attack_speed": -3.20},
						DefaultOre.IRON:		{"durability": 250,		"attack_damage": 9,		"attack_speed": -3.10},
						DefaultOre.GOLD:		{"durability": 32,		"attack_damage": 7,		"attack_speed": -3.00},
						DefaultOre.DIAMOND:		{"durability": 1561,	"attack_damage": 9,		"attack_speed": -3.00},
						DefaultOre.NETHERITE:	{"durability": 2031,	"attack_damage": 10,	"attack_speed": -3.00}
					})
	SHOVEL			= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 59,		"attack_damage": 2.5,	"attack_speed": -3.00},
						DefaultOre.COPPER:		{"durability": 190,		"attack_damage": 3.5,	"attack_speed": -3.00},
						DefaultOre.CHAINMAIL:	{"durability": 131,		"attack_damage": 3.5,	"attack_speed": -3.00},
						DefaultOre.IRON:		{"durability": 250,		"attack_damage": 4.5,	"attack_speed": -3.00},
						DefaultOre.GOLD:		{"durability": 32,		"attack_damage": 2.5,	"attack_speed": -3.00},
						DefaultOre.DIAMOND:		{"durability": 1561,	"attack_damage": 5.5,	"attack_speed": -3.00},
			 			DefaultOre.NETHERITE:	{"durability": 2031,	"attack_damage": 6.5,	"attack_speed": -3.00}
					})
	HOE				= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 59,		"attack_damage": 1,		"attack_speed": -3.00},
						DefaultOre.COPPER:		{"durability": 190,		"attack_damage": 1,		"attack_speed": -2.00},
						DefaultOre.CHAINMAIL:	{"durability": 131,		"attack_damage": 1,		"attack_speed": -2.00},
						DefaultOre.IRON:		{"durability": 250,		"attack_damage": 1,		"attack_speed": -1.00},
						DefaultOre.GOLD:		{"durability": 32,		"attack_damage": 1,		"attack_speed": -3.00},
						DefaultOre.DIAMOND:		{"durability": 1561,	"attack_damage": 1,		"attack_speed": 0.00},
						DefaultOre.NETHERITE:	{"durability": 2031,	"attack_damage": 1,		"attack_speed": 0.00}
					})
	SPEAR			= cast(dict[DefaultOre, dict[str, float]],
					{	DefaultOre.LEATHER:		{"durability": 59,		"attack_damage": 1,		"attack_speed": -2.462},
						DefaultOre.COPPER:		{"durability": 190,		"attack_damage": 2,		"attack_speed": -2.824},
						DefaultOre.CHAINMAIL:	{"durability": 131,		"attack_damage": 2,		"attack_speed": -2.666},
						DefaultOre.IRON:		{"durability": 250,		"attack_damage": 3,		"attack_speed": -2.947},
						DefaultOre.GOLD:		{"durability": 32,		"attack_damage": 1,		"attack_speed": -2.947},
						DefaultOre.DIAMOND:		{"durability": 1561,	"attack_damage": 4,		"attack_speed": -3.048},
						DefaultOre.NETHERITE:	{"durability": 2031,	"attack_damage": 5,		"attack_speed": -3.130}
					})

class EquipmentsConfig:
	__slots__ = ("attributes", "equivalent_to", "ignore_recipes", "pickaxe_durability")

	def __init__(self, equivalent_to: DefaultOre = DefaultOre.DIAMOND, pickaxe_durability: float | int = 0, attributes: dict[str, float] | None = None, ignore_recipes: bool = False) -> None:
		""" Creates a configuration for equipments (based on the pickaxe)

		Args:
			equivalent_to (DEFAULT_ORE):	The equivalent ore to compare to (ex: DEFAULT_ORE.DIAMOND)
			pickaxe_durability (int):		The pickaxe durability that will be used to calculate the durability of other equipments
			attributes (dict[str, float]):	(optional) Attributes with type "add_value" to add (not override) to the equipment (ex: "attack_damage": 1.0, means 6 attack damage for diamond pickaxe)
				{"attack_damage": 1.0, "armor": 1.0, "mining_efficiency": 1}
				attack_damage and mining_efficiency are always on tools
				armor and armor_toughness is always on armor
			ignore_recipes (bool):			Whether to ignore recipes generation for this material or not

		If you need a specific attribute for a generated item, you should append it afterward.
		"""
		if attributes is None:
			attributes = {}
		self.ignore_recipes: bool = ignore_recipes
		self.equivalent_to: DefaultOre = equivalent_to
		self.pickaxe_durability: int = int(pickaxe_durability if pickaxe_durability > 0 else VanillaEquipments.PICKAXE.value[equivalent_to]["durability"])
		self.attributes: dict[str, float] = attributes
		for key in attributes.keys():
			if "player." in key:
				stp.warning("Since 1.21.3, the 'player.' prefix is no longer written in attributes!!!")
			elif "generic." in key:
				stp.warning("Since 1.21.3, the 'generic.' prefix is no longer written in attributes!!!")
			if "knockback_resistance" in key and attributes[key] >= 1:
				stp.warning(f"You are setting the Knockback Resistance of an equipment to {attributes[key]}. Be aware that Minecraft automatically multiplies it by 10 when applied to an equipment.")

	def getter(self) -> tuple[DefaultOre, int, dict[str, float]]:
		return self.equivalent_to, self.pickaxe_durability, self.attributes

	@stp.simple_cache
	def get_tools_attributes(self) -> dict[str, float]:
		NOT_ON_TOOLS = ["armor", "armor_toughness", "knockback_resistance"]
		return {key: value for key, value in self.attributes.items() if key not in NOT_ON_TOOLS}

	@stp.simple_cache
	def get_armor_attributes(self) -> dict[str, float]:
		NOT_ON_ARMOR = ["attack_damage", "mining_efficiency"]
		return {key: value for key, value in self.attributes.items() if key not in NOT_ON_ARMOR}

	def __str__(self) -> str:
		return f"EquipmentsConfig(equivalent_to={self.equivalent_to}, pickaxe_durability={self.pickaxe_durability}, attributes={self.attributes}, ignore_recipes={self.ignore_recipes})"

	def __repr__(self) -> str:
		return self.__str__()

# UUIDs utils
def format_attributes(attributes: dict[str, float], slot: str, attr_config: dict[str, float] | None = None) -> list[JsonDict]:
	""" Returns generated attribute_modifiers key for an item (adds up attributes and config) """
	# Get attributes from config
	if attr_config is None:
		attr_config = {}
	attribute_modifiers: list[JsonDict] = []
	for attribute_name, value in attr_config.items():

		# We already have a base_attack_damage
		if attribute_name == "attack_damage":
			value -= 1

		# If not durability, we add the base attribute
		if attribute_name != "durability":
			if attribute_name in ["attack_damage", "attack_speed"]:
				attribute_modifiers.append({"type": attribute_name, "amount": value, "operation": "add_value", "slot": slot, "id": f"minecraft:base_{attribute_name}"})
			else:
				attribute_modifiers.append({"type": attribute_name, "amount": value, "operation": "add_value", "slot": slot, "id": f"{Mem.ctx.project_id}:{attribute_name}.{slot}"})

	# For each attribute, add it to the list if not in, else add the value
	for attribute_name, value in attributes.items():
		found = False
		for attribute in attribute_modifiers:
			if attribute["type"] == attribute_name:
				attribute["amount"] += value
				found = True
				break
		if not found:
			attribute_modifiers.append({"type": attribute_name, "amount": value, "operation": "add_value", "slot": slot, "id": f"{Mem.ctx.project_id}:{attribute_name}.{slot}"})

	# Return the list of attributes
	return attribute_modifiers

