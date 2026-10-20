""" The hidden enchantment of each `RangedWeapon`, and the check giving back what a crossbow loaded instead of its ammunition. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Enchantment, EnchantmentTag
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.items.item import Item
from ....core.utils.io import set_json_encoder, write_advancement, write_function
from ....core.utils.loot_table import entity_type_field, loot_condition, loot_function

# Constants
CROSSBOW_CHARGE_TIME: float = 1.25
""" Seconds a vanilla crossbow takes to load. """

HANDS: dict[str, str] = {"mainhand": "SelectedItem", "offhand": "equipment.offhand"}
""" Player slot of each hand, and where the player's data holds it. """


# Functions
def write_ranged_weapons() -> None:
	""" Write the enchantment of every item with a `ranged_weapon`, a curse so a grindstone keeps it. """
	weapons: list[Item] = [item for item in Mem.definitions.values() if item.ranged_weapon]
	for item in weapons:
		write_enchantment(item)
		if item.ranged_weapon and item.ranged_weapon.ammunition:
			write_ammunition_check(item, item.ranged_weapon.ammunition)
	if weapons:
		curses: EnchantmentTag = Mem.ctx.data.enchantment_tags.setdefault("minecraft:curse", EnchantmentTag({"values": []}))
		curses.data["values"] = stp.unique_list([*curses.data["values"], *(str(item.ranged_weapon_enchantment) for item in weapons)])


def write_enchantment(item: Item) -> None:
	""" The enchantment changing the charge time of the item and the damage of the arrows it shoots. """
	assert item.ranged_weapon
	effects: JsonDict = {}
	if item.ranged_weapon.charge_time is not None:
		added: float = round(item.ranged_weapon.charge_time - CROSSBOW_CHARGE_TIME, 6)
		effects["minecraft:crossbow_charge_time"] = {"type": "minecraft:add", "value": added}
	if item.ranged_weapon.damage_multiplier != 1.0:
		effects["minecraft:damage"] = [{
			"effect": {"type": "minecraft:multiply", "factor": item.ranged_weapon.damage_multiplier},
			"requirements": loot_condition(
				"minecraft:entity_properties", entity="direct_attacker", predicate=entity_type_field("#minecraft:arrows"),
			),
		}]
	no_cost: JsonDict = {"base": 0, "per_level_above_first": 0}
	item.ranged_weapon_enchantment.write(set_json_encoder(Enchantment({
		"description": {"text": item.ranged_weapon.name}, "supported_items": item.base_item, "weight": 1, "max_level": 1,
		"min_cost": no_cost, "max_cost": no_cost, "anvil_cost": 0, "slots": ["mainhand", "offhand"], "effects": effects,
	}), max_level=3))


def write_ammunition_check(item: Item, ammunition: str) -> None:
	""" Whenever the inventory of a player holding this crossbow changes, unload it when it holds anything else than `ammunition`. """
	ns: str = Mem.ctx.project_id
	advancement: str = f"{ns}:ranged_weapon/{item.id}_loaded"
	write_advancement(advancement, {
		"criteria": {"requirement": {"trigger": "minecraft:inventory_changed", "conditions": {"items": [
			{"items": item.base_item, "predicates": {"minecraft:custom_data": {ns: {item.id: True}}}},
		]}}},
		"rewards": {"function": f"{ns}:ranged_weapon/{item.id}/loaded"},
	})
	loaded: str = 'components."minecraft:charged_projectiles"[0]'
	write_function(f"{ns}:ranged_weapon/{item.id}/loaded", f"advancement revoke @s only {advancement}\n" + "".join(
		f"execute if items entity @s weapon.{hand} *[custom_data~{{{ns}:{{{item.id}:true}}}}] if data entity @s {path}.{loaded} "
		f"unless data entity @s {path}.{loaded}.components.\"minecraft:custom_data\".{ns}.{ammunition} "
		f"run function {ns}:ranged_weapon/{item.id}/unload_{hand}\n"
		for hand, path in HANDS.items()
	))
	emptied: JsonDict = loot_function("minecraft:set_components", components={"minecraft:charged_projectiles": []})
	unload: str = stp.json_dump(emptied, max_level=0).strip()
	for hand, path in HANDS.items():
		write_function(f"{ns}:ranged_weapon/{item.id}/unload_{hand}", f"""
# Give back what it loaded, unless the player is in creative where loading costs nothing
execute if entity @s[gamemode=!creative] run summon item ~ ~1 ~ {{Item:{{id:"minecraft:stone"}},Tags:["{ns}.unloaded"],PickupDelay:0s}}
execute if entity @s[gamemode=!creative] run data modify entity @n[type=item,tag={ns}.unloaded] Item set from entity @s {path}.{loaded}
tag @n[type=item,tag={ns}.unloaded] remove {ns}.unloaded
item modify entity @s weapon.{hand} {unload}
""")

