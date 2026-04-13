
# ruff: noqa: E501
# Imports
from beet.core.utils import JsonDict
from beet.library import base
from beet.toolchain.config import FormatSpecifier

from ..dependencies.bookshelf import BOOKSHELF_MODULES

# Minecraft version specific constants
MORE_DATA_PACK_FORMATS: dict[tuple[int, ...], FormatSpecifier] = {
	(1, 21): 48,
	(1, 21, 0): 48,
	(1, 21, 1): 48,
	(1, 21, 2): 57,
	(1, 21, 3): 57,
	(1, 21, 4): 61,
	(1, 21, 5): 71,
	(1, 21, 6): 80,
	(1, 21, 7): 81,
	(1, 21, 8): 81,
	(1, 21, 9): (88, 0),
	(1, 21, 10): (88, 0),
	(1, 21, 11): (94, 1),

	# New version numbering system
	(25, 1): 71,			 # 1.21.5
	(25, 1, 0): 71,			 # 1.21.5
	(25, 2): 80,			# 1.21.6
	(25, 2, 0): 80,			# 1.21.6
	(25, 2, 1): 80,			# 1.21.6
	(25, 2, 2): 80,			# 1.21.6
	(25, 3): 81,			 # 1.21.8
	(25, 3, 0): 81,			 # 1.21.8
	(25, 3, 1): 81,			 # 1.21.8
	(25, 4): (94, 1),		# 1.21.11
	(25, 4, 0): (94, 1),	# 1.21.11

	(26, 1): (101, 1),
	(26, 1, 0): (101, 1),
	(26, 1, 1): (101, 1),
	(26, 1, 2): (101, 1),

	(9999, 0, 0): (9999, 0),
}
MORE_ASSETS_PACK_FORMATS: dict[tuple[int, ...], FormatSpecifier] = {
	(1, 21): 34,
	(1, 21, 0): 34,
	(1, 21, 1): 34,
	(1, 21, 2): 42,
	(1, 21, 3): 42,
	(1, 21, 4): 46,
	(1, 21, 5): 55,
	(1, 21, 6): 63,
	(1, 21, 7): 64,
	(1, 21, 8): 64,
	(1, 21, 9): (69, 0),
	(1, 21, 10): (69, 0),
	(1, 21, 11): (75, 0),

	# New version numbering system
	(25, 1): 55,			 # 1.21.5
	(25, 1, 0): 55,			 # 1.21.5
	(25, 2): 63,			 # 1.21.6
	(25, 2, 0): 63,			# 1.21.6
	(25, 2, 1): 63,			# 1.21.6
	(25, 2, 2): 63,			# 1.21.6
	(25, 3): 64,			 # 1.21.8
	(25, 3, 0): 64,			 # 1.21.8
	(25, 3, 1): 64,			 # 1.21.8
	(25, 4): (75, 0),		# 1.21.11
	(25, 4, 0): (75, 0),	# 1.21.11

	(26, 1): (84, 0),
	(26, 1, 0): (84, 0),
	(26, 1, 1): (84, 0),
	(26, 1, 2): (84, 0),

	(9999, 0, 0): (9999, 0),
}
MORE_DATA_VERSIONS: dict[tuple[int, ...], int] = {
	(1, 21): 3953,
	(1, 21, 0): 3953,
	(1, 21, 1): 3955,
	(1, 21, 2): 4080,
	(1, 21, 3): 4082,
	(1, 21, 4): 4189,
	(1, 21, 5): 4325,
	(1, 21, 6): 4435,
	(1, 21, 7): 4438,
	(1, 21, 8): 4440,
	(1, 21, 9): 4554,
	(1, 21, 10): 4556,
	(1, 21, 11): 4669,

	(26, 1): 4786,
	(26, 1, 0): 4786,
	(26, 1, 1): 4788,
	(26, 1, 2): 4790,
}
LATEST_MC_VERSION: str = ".".join(str(x) for x in list(MORE_DATA_VERSIONS.keys())[-1])
base.LATEST_MINECRAFT_VERSION = LATEST_MC_VERSION

# Databases
CATEGORY: str = "manual_category"						# Key for the category, used for recipes and the manual, ex: CATEGORY:"material" or CATEGORY:"equipment"
CUSTOM_BLOCK_VANILLA: str = "minecraft:furnace"			# Vanilla block used as base for custom blocks, must have the "facing" blockstate
CUSTOM_BLOCK_ALTERNATIVE: str = "minecraft:item_frame"	# Same purpose as previous, but useful for blocks that can be placed on walls or on player's position (ex: flowers)
CUSTOM_BLOCK_HEAD: str = "minecraft:player_head"		# Same purpose as previous, but useful for blocks does not have a custom model data
CUSTOM_ITEM_VANILLA: str = "minecraft:command_block"	# Vanilla item used as base for custom items, must not have any survival vanilla behaviour
VANILLA_BLOCK: str = "vanilla_block"					# Key to a vanilla block that will be placed for custom block interaction, value needs to be a dict like {"id":"minecraft:chest[type=single,waterlogged=false]", "block_facing": "player"} or a VanillaBlock instance
NO_SILK_TOUCH_DROP: str = "no_silk_touch_drop"			# Key to no-silk drop data for ores: item id string, deterministic dict-like data (`NoSilkTouchDrop`), or a beet `LootTable`
OVERRIDE_MODEL: str = "override_model"					# Key to a dictionnary that will be used to override the whole model
SMITHED_CRAFTER_COMMAND: str = "smithed_crafter_command"	# Key to a command that will be used in a recipe in the Smithed Crafter library. If not present, the command will be defaulted to a loot table. Ex: {"result":...,SMITHED_CRAFTER_COMMAND: "function your_namespace:calls/smithed_crafter/do_something_else"}
PAINTING_DATA: str = "painting_data"					# Key to a dict that contains the painting data, like {"author":"","title":"","width":1,"height":1} where author and title defaults to beet config values if not given
GROWING_SEED: str = "growing_seed"						# Key to a seed that has multiple growth stages, value needs to be a dict like {"texture_basename":"wheat","stages":8,"seconds":600,"planted_on":"stone","loots":[{"id":"minecraft:wheat_seeds","min_count":1,"max_count":3}]} where loots can be either this format or a loot table path "namespace:blocks/loot_table_name"
WIKI_COMPONENT: str = "wiki_buttons"					# Key to a text component that will be used to generate the wiki button in the manual
RESULT_OF_CRAFTING: str = "result_of_crafting"			# Key to a list of recipes to craft the item, ex: "adamantium": {RESULT_OF_CRAFTING: [...]}
USED_FOR_CRAFTING: str = "used_for_crafting"			# Should not be used unless you are crafting a vanilla item (ex: iyc.chainmail -> chainmail armor)
NOT_COMPONENTS: list[str] = [							# Keys that should not be considered as components. Used for recipes, loot tables, etc.
	"id",
	WIKI_COMPONENT,
	RESULT_OF_CRAFTING,
	USED_FOR_CRAFTING,
	CATEGORY,
	VANILLA_BLOCK,
	NO_SILK_TOUCH_DROP,
	OVERRIDE_MODEL,
	SMITHED_CRAFTER_COMMAND,
	PAINTING_DATA,
	GROWING_SEED,
]

# Technical constants
COMMON_SIGNAL: str = r'custom_data={"common_signals":{"temp":true}}'					# NBT to add to items to mark them as temporary for Common Signals library
COMMON_SIGNAL_HIDDEN: str = r'tooltip_display={"hide_tooltip":true},' + COMMON_SIGNAL	# Same as previous but also hide the tooltip (Useful for GUIs)
FACES: tuple[str, ...] = ("down", "up", "north", "south", "west", "east")						# Faces of a block, used for resource pack and blocks orientation
SIDES: tuple[str, ...] = ("_bottom", "_top", "_front", "_back", "_left", "_right", "_side")	# Sides of a block, used for resource pack
DOWNLOAD_VANILLA_ASSETS_RAW = "https://raw.githubusercontent.com/edayot/renders/renders/resourcepack/assets/minecraft/textures/render"
DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW = "https://raw.githubusercontent.com/edayot/renders/renders-special/resourcepack/assets/minecraft/textures/render"
DOWNLOAD_VANILLA_ASSETS_SOURCE = "https://github.com/edayot/renders/tree/renders/resourcepack/assets/minecraft/textures/render"
CUSTOM_BLOCK_HEAD_CUBE_RADIUS: tuple[int, int, int] = (16, 16, 16)	# Size of the region to check around the player when placing a CUSTOM_BLOCK_HEAD
BLOCKS_WITH_INTERFACES: list[str] = [	# List of blocks that are containers and have an interface
	"minecraft:barrel",
	"minecraft:chest",
	"minecraft:furnace",
	"minecraft:shulker_box",
	"minecraft:dispenser",
	"minecraft:hopper",
	"minecraft:dropper",
	"minecraft:smoker",
	"minecraft:blast_furnace",
	"minecraft:brewing_stand",
	"minecraft:trapped_chest",
	"minecraft:crafter",
]

# Conventions constants
class ConventionTags(list[str]):
	def __init__(self, *args: str):
		if len(args) == 0:
			self.clear()
		elif len(args) == 1 and isinstance(args[0], list):
			self.extend(args[0])
		else:
			self.extend(args)

	@property
	def avoid(self) -> str:
		""" Utility function to generate a string of tags to avoid in an execute command. Example of use: execute as @e[{Conventions.ENTITY_TAGS.avoid}] run function your_namespace:kill_entity """
		return ",".join(f"tag=!{tag}" for tag in self)

class Conventions:
	""" Defines conventions for tags used in datapacks. """
	GLOBAL_KILL = ConventionTags("global.ignore.kill", "global.ignore")
	""" List of tags that prevent entities from being damaged/killed. """
	NO_KILL_TAGS = ConventionTags("smithed.strict", "global.ignore.kill")
	""" List of tags that prevent entities from being killed. """
	ENTITY_TAGS = ConventionTags("smithed.entity", "global.ignore")
	""" List of tags applicable to custom entities. """
	BLOCK_TAGS = ConventionTags("smithed.block", *ENTITY_TAGS)
	""" List of tags applicable to custom blocks. """
	ENTITY_TAGS_NO_KILL = ConventionTags(*ENTITY_TAGS, *NO_KILL_TAGS)
	""" Combined list of entity tags and no kill tags. """
	BLOCK_TAGS_NO_KILL = ConventionTags(*BLOCK_TAGS, *NO_KILL_TAGS)
	""" Combined list of block tags and no kill tags. """

	AVOID_NO_KILL: str = NO_KILL_TAGS.avoid
	""" Deprecated (use Conventions.NO_KILL_TAGS.avoid instead): String of tags to avoid when killing entities. Example of use: execute as @e[{Conventions.AVOID_NO_KILL}] run function your_namespace:kill_entity """
	AVOID_ENTITY_TAGS: str = ENTITY_TAGS.avoid
	""" Deprecated (use Conventions.ENTITY_TAGS.avoid instead): String of tags to avoid when executing an entity command. Example of use: execute as @e[{Conventions.AVOID_ENTITY_TAGS}] run function your_namespace:kill_entity """
	AVOID_BLOCK_TAGS: str = BLOCK_TAGS.avoid
	""" Deprecated (use Conventions.BLOCK_TAGS.avoid instead): String of tags to avoid when executing a block command. Example of use: execute as @e[{Conventions.AVOID_BLOCK_TAGS}] run function your_namespace:kill_entity """
	AVOID_ENTITY_TAGS_NO_KILL: str = ENTITY_TAGS_NO_KILL.avoid
	""" Deprecated (use Conventions.ENTITY_TAGS_NO_KILL.avoid instead): String of tags to avoid when executing an entity command. Example of use: execute as @e[{Conventions.AVOID_ENTITY_TAGS_NO_KILL}] run function your_namespace:kill_entity """
	AVOID_BLOCK_TAGS_NO_KILL: str = BLOCK_TAGS_NO_KILL.avoid
	""" Deprecated (use Conventions.BLOCK_TAGS_NO_KILL.avoid instead): String of tags to avoid when executing a block command. Example of use: execute as @e[{Conventions.AVOID_BLOCK_TAGS_NO_KILL}] run function your_namespace:kill_entity """



# Automatically handled dependencies for supported libs with additional key "is_used" that is True when the lib is found to be used.
def official_lib_used(lib: str) -> bool:
	is_used: bool = OFFICIAL_LIBS[lib]["is_used"]
	OFFICIAL_LIBS[lib]["is_used"] = True
	return is_used

OFFICIAL_LIBS: dict[str, JsonDict] = {
	"common_signals":		{"version":[0, 2, 0],	"name":"Common Signals",					"url":"https://github.com/Stoupy51/CommonSignals",			"is_used": False},
	"smithed.custom_block":	{"version":[0, 7, 1],	"name":"Smithed Custom Block",				"url":"https://wiki.smithed.dev/libraries/custom-block/",	"is_used": False},
	"smithed.crafter":		{"version":[0, 7, 1],	"name":"Smithed Crafter",					"url":"https://wiki.smithed.dev/libraries/crafter/",		"is_used": False},
	"smithed.actionbar":	{"version":[0, 6, 6],	"name":"Smithed Actionbar",					"url":"https://wiki.smithed.dev/libraries/actionbar/",		"is_used": False},
	"furnace_nbt_recipes":	{"version":[1, 10, 1],	"name":"Furnace NBT Recipes",				"url":"https://github.com/Stoupy51/FurnaceNbtRecipes",		"is_used": False},
	"smart_ore_generation":	{"version":[1, 7, 2],	"name":"SmartOreGeneration",				"url":"https://github.com/Stoupy51/SmartOreGeneration",		"is_used": False},
	"realistic_explosion":	{"version":[1, 2, 0],	"name":"RealisticExplosion",				"url":"https://github.com/Stoupy51/RealisticExplosionLibrary",	"is_used": False},
	"itemio":				{"version":[1, 4, 1],	"name":"ItemIO",							"url":"https://github.com/edayot/ItemIO",					"is_used": False},
	**BOOKSHELF_MODULES,
}

