
# ruff: noqa: E501, I001
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from stouputils.typing import JsonDict

def official_lib_used(lib: str) -> bool:
	is_used: bool = OFFICIAL_LIBS[lib]["is_used"]
	OFFICIAL_LIBS[lib]["is_used"] = True
	return is_used

def detection_markers(project_id: str) -> dict[str, str]:
	""" Map every text marker to the library it proves the use of, skipping the pack being built.

	Args:
		project_id (str): Project id of the pack being built, so a library never detects itself.
	Returns:
		dict[str, str]: Marker to look for in function sources, mapped to its library namespace.
	Examples:
		>>> detection_markers("my_pack")["#bs.math:"]
		'bs.math'
		>>> "#bs.math:" in detection_markers("bookshelf")
		False
	"""
	return {
		data["detect"]: lib_ns
		for lib_ns, data in OFFICIAL_LIBS.items()
		if "detect" in data and project_id not in (lib_ns, data.get("detect_ns", lib_ns))
	}

# Each entry has: name, url, is_used, source ("smithed"|"modrinth"|"static")
# Smithed entries can have: version, smithed_id, has_resource_pack
# Modrinth entries can have: modrinth_slug
# Static entries have: static_urls {(mc_ver_tuple, dep_ver_tuple): url}
# "detect" is the marker whose presence in a function source auto-enables the library, "detect_ns" being the project id shipping it when it differs from the key
OFFICIAL_LIBS: dict[str, JsonDict] = {

	# Smithed API libs
	"smithed.custom_block": {"name":"Smithed Custom Block",   "url":"https://wiki.smithed.dev/libraries/custom-block/",   "is_used": False, "source":"smithed", "smithed_id":"custom-block"},
	"smithed.crafter":      {"name":"Smithed Crafter",        "url":"https://wiki.smithed.dev/libraries/crafter/",        "is_used": False, "source":"smithed", "smithed_id":"crafter", "has_resource_pack": True},
	"smithed.actionbar":    {"name":"Smithed Actionbar",      "url":"https://wiki.smithed.dev/libraries/actionbar/",      "is_used": False, "source":"smithed", "smithed_id":"actionbar", "detect": "smithed.actionbar"},
	"realistic_explosion":  {"name":"RealisticExplosion",     "url":"https://github.com/Stoupy51/RealisticExplosion",     "is_used": False, "source":"smithed", "smithed_id":"realistic_explosion", "detect": "realistic_explosion"},
	"player_motion":        {"name":"Player Motion API",      "url":"https://github.com/MulverineX/player_motion",        "is_used": False, "source":"smithed", "smithed_id":"player_motion", "no_lantern_load": True, "detect": "player_motion"},

	# Modrinth API libs
	"itemio":               {"name":"ItemIO",                 "url":"https://github.com/edayot/ItemIO",                   "is_used": False, "source":"modrinth", "modrinth_slug":"itemio", "detect": "itemio"},
	"common_signals":       {"name":"Common Signals",         "url":"https://github.com/Stoupy51/CommonSignals",          "is_used": False, "source":"modrinth", "modrinth_slug":"common_signals", "detect": "common_signals"},
	"furnace_nbt_recipes":  {"name":"Furnace NBT Recipes",    "url":"https://github.com/Stoupy51/FurnaceNbtRecipes",      "is_used": False, "source":"modrinth", "modrinth_slug":"furnace_nbt_recipes", "detect": "furnace_nbt_recipes"},
	"smart_ore_generation": {"name":"Smart Ore Generation",   "url":"https://github.com/Stoupy51/SmartOreGeneration",     "is_used": False, "source":"modrinth", "modrinth_slug":"smart_ore_generation"},
	"cinemalya":            {"name":"Cinemalya",              "url":"https://github.com/Stoupy51/Cinemalya",              "is_used": False, "source":"modrinth", "modrinth_slug":"cinemalya", "detect": "cinemalya"},

	# Static URL libs (version resolved from static_urls at download time)
	# "smart_ore_generation":   {"name":"SmartOreGeneration",   "url":"https://github.com/Stoupy51/SmartOreGeneration",         "is_used": False, "source":"static", "static_urls": {
	#         ((1, 21, 7),  (1, 7, 2)): "https://github.com/Stoupy51/SmartOreGeneration/releases/download/v1.7.2/SmartOreGeneration_datapack.zip",
	#     }
	# },

	# Bookshelf modules (resolved via Modrinth API with modrinth_slug)
	"bs.bitwise":           {"name": "Bookshelf Bitwise",     "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-bitwise",     "detect": "#bs.bitwise:",     "detect_ns": "bookshelf"},
	"bs.block":             {"name": "Bookshelf Block",       "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-block",       "detect": "#bs.block:",       "detect_ns": "bookshelf"},
	"bs.color":             {"name": "Bookshelf Color",       "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-color",       "detect": "#bs.color:",       "detect_ns": "bookshelf"},
	"bs.dump":              {"name": "Bookshelf Dump",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-dump",        "detect": "#bs.dump:",        "detect_ns": "bookshelf"},
	"bs.environment":       {"name": "Bookshelf Environment", "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-environment", "detect": "#bs.environment:", "detect_ns": "bookshelf"},
	"bs.generation":        {"name": "Bookshelf Generation",  "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-generation",  "detect": "#bs.generation:",  "detect_ns": "bookshelf"},
	"bs.health":            {"name": "Bookshelf Health",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-health",      "detect": "#bs.health:",      "detect_ns": "bookshelf"},
	"bs.hitbox":            {"name": "Bookshelf Hitbox",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-hitbox",      "detect": "#bs.hitbox:",      "detect_ns": "bookshelf"},
	"bs.id":                {"name": "Bookshelf Id",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-id",          "detect": "#bs.id:",          "detect_ns": "bookshelf"},
	"bs.interaction":       {"name": "Bookshelf Interaction", "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-interaction", "detect": "#bs.interaction:", "detect_ns": "bookshelf"},
	"bs.link":              {"name": "Bookshelf Link",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-link",        "detect": "#bs.link:",        "detect_ns": "bookshelf"},
	"bs.log":               {"name": "Bookshelf Log",         "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-log",         "detect": "#bs.log:",         "detect_ns": "bookshelf"},
	"bs.math":              {"name": "Bookshelf Math",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-math",        "detect": "#bs.math:",        "detect_ns": "bookshelf"},
	"bs.move":              {"name": "Bookshelf Move",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-move",        "detect": "#bs.move:",        "detect_ns": "bookshelf"},
	"bs.position":          {"name": "Bookshelf Position",    "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-position",    "detect": "#bs.position:",    "detect_ns": "bookshelf"},
	"bs.random":            {"name": "Bookshelf Random",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-random",      "detect": "#bs.random:",      "detect_ns": "bookshelf"},
	"bs.raycast":           {"name": "Bookshelf Raycast",     "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-raycast",     "detect": "#bs.raycast:",     "detect_ns": "bookshelf"},
	"bs.schedule":          {"name": "Bookshelf Schedule",    "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-schedule",    "detect": "#bs.schedule:",    "detect_ns": "bookshelf"},
	"bs.sidebar":           {"name": "Bookshelf Sidebar",     "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-sidebar",     "detect": "#bs.sidebar:",     "detect_ns": "bookshelf"},
	"bs.spline":            {"name": "Bookshelf Spline",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-spline",      "detect": "#bs.spline:",      "detect_ns": "bookshelf"},
	"bs.string":            {"name": "Bookshelf String",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-string",      "detect": "#bs.string:",      "detect_ns": "bookshelf"},
	"bs.time":              {"name": "Bookshelf Time",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-time",        "detect": "#bs.time:",        "detect_ns": "bookshelf"},
	"bs.tree":              {"name": "Bookshelf Tree",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-tree",        "detect": "#bs.tree:",        "detect_ns": "bookshelf"},
	"bs.vector":            {"name": "Bookshelf Vector",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-vector",      "detect": "#bs.vector:",      "detect_ns": "bookshelf"},
	"bs.view":              {"name": "Bookshelf View",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-view",        "detect": "#bs.view:",        "detect_ns": "bookshelf"},
	"bs.xp":                {"name": "Bookshelf Xp",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-xp",          "detect": "#bs.xp:",          "detect_ns": "bookshelf"}

	# Gamemode 4 libs: #TODO
}

