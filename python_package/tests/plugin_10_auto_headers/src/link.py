
# Imports
from beet import Context

from stewbeet import *


# Main entry point
def beet_default(ctx: Context):
	ns: str = ctx.project_id

	# Root function that calls a helper
	write_function(f"{ns}:root", f"""
say Starting root
function {ns}:helper/do_work
say Root done
""")

	# Helper function called by root, which calls another helper
	write_function(f"{ns}:helper/do_work", f"""
say Doing work
function {ns}:helper/log_result
scoreboard players add #count {ns}.data 1
""")

	# Leaf function with no outgoing calls
	write_function(f"{ns}:helper/log_result", f"""
say Work complete
tellraw @a [{{"text":"count: "}},{{"score":{{"name":"#count","objective":"{ns}.data"}}}}]
""")

	# Reachable ONLY from a dialog button: no mcfunction, tag, or advancement calls it.
	# Without the dialog pass in FunctionAnalyzer this would be reported as "@within ???".
	write_function(f"{ns}:menu_from_dialog", "say Opened from a dialog button")

	ctx.data[ns].dialogs["config"] = Dialog({
		"type": "minecraft:multi_action",
		"title": {"text": "Test"},
		"actions": [
			{"label": {"text": "Open"}, "action": {"type": "run_command", "command": f"/function {ns}:menu_from_dialog"}},
		],
	})

	# Reachable only through a placeholder in a macro call path
	write_function(f"{ns}:perks/apply", f"$function {ns}:perks/apply/$(perk_id)")
	write_function(f"{ns}:perks/apply/juggernog", "say Juggernog")

	# Reachable only as a function id handed to a macro
	write_function(f"{ns}:give_via_function", "$function $(give_function)")
	write_function(f"{ns}:box", f'function {ns}:give_via_function {{give_function:"{ns}:give/weapon"}}')
	write_function(f"{ns}:give/weapon", "say Weapon")

	# Reachable only from an enchantment effect
	write_function(f"{ns}:on_attack", "say Attack")
	ctx.data[ns].enchantments["left_click"] = Enchantment({
		"description": "", "supported_items": "#minecraft:swords", "weight": 1, "max_level": 1,
		"min_cost": {"base": 1, "per_level_above_first": 0}, "max_cost": {"base": 1, "per_level_above_first": 0},
		"anvil_cost": 0, "slots": ["mainhand"],
		"effects": {"minecraft:post_attack": [{"enchanted": "attacker", "affected": "attacker",
			"effect": {"type": "minecraft:run_function", "function": f"{ns}:on_attack"}}]},
	})

	# Uncalled: public outside the versioned folder, dead inside it
	write_function(f"{ns}:config", "say Config")
	write_versioned_function("dead", "say Dead")

