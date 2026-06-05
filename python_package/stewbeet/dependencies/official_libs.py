
# ruff: noqa: E501, I001
# Imports
from stouputils.typing import JsonDict

def official_lib_used(lib: str) -> bool:
    is_used: bool = OFFICIAL_LIBS[lib]["is_used"]
    OFFICIAL_LIBS[lib]["is_used"] = True
    return is_used

# Each entry has: name, url, is_used, source ("smithed"|"modrinth"|"static")
# Smithed entries can have: version, smithed_id, has_resource_pack
# Modrinth entries can have: modrinth_slug
# Static entries have: static_urls {(mc_ver_tuple, dep_ver_tuple): url}
# Bookshelf modules are merged with source="smithed" (smithed_id derived from bs.X -> bookshelf-X)
OFFICIAL_LIBS: dict[str, JsonDict] = {

    # Smithed API libs
    "smithed.custom_block":	{"name":"Smithed Custom Block",	"url":"https://wiki.smithed.dev/libraries/custom-block/",	"is_used": False, "source":"smithed", "smithed_id":"custom-block"},
    "smithed.crafter":		{"name":"Smithed Crafter",		"url":"https://wiki.smithed.dev/libraries/crafter/",		"is_used": False, "source":"smithed", "smithed_id":"crafter", "has_resource_pack": True},
    "smithed.actionbar":	{"name":"Smithed Actionbar",	"url":"https://wiki.smithed.dev/libraries/actionbar/",		"is_used": False, "source":"smithed", "smithed_id":"actionbar"},
    "realistic_explosion":	{"name":"RealisticExplosion",	"url":"https://github.com/Stoupy51/RealisticExplosion",		"is_used": False, "source":"smithed", "smithed_id":"realistic_explosion"},
    "player_motion":		{"name":"Player Motion API",	"url":"https://github.com/MulverineX/player_motion",        "is_used": False, "source":"smithed", "smithed_id":"player_motion", "no_lantern_load": True},

    # Modrinth API libs
    "itemio":				{"name":"ItemIO",	            "url":"https://github.com/edayot/ItemIO",	                "is_used": False, "source":"modrinth", "modrinth_slug":"itemio"},
    "common_signals":		{"name":"Common Signals",		"url":"https://github.com/Stoupy51/CommonSignals",			"is_used": False, "source":"modrinth", "modrinth_slug":"common_signals"},
    "furnace_nbt_recipes":	{"name":"Furnace NBT Recipes",	"url":"https://github.com/Stoupy51/FurnaceNbtRecipes",		"is_used": False, "source":"modrinth", "modrinth_slug":"furnace_nbt_recipes"},
    "smart_ore_generation":	{"name":"Smart Ore Generation",	"url":"https://github.com/Stoupy51/SmartOreGeneration",		"is_used": False, "source":"modrinth", "modrinth_slug":"smart_ore_generation"},

    # Static URL libs (version resolved from static_urls at download time)
    # "smart_ore_generation":	{"name":"SmartOreGeneration",	"url":"https://github.com/Stoupy51/SmartOreGeneration",			"is_used": False, "source":"static", "static_urls": {
    #         ((1, 21, 7),  (1, 7, 2)): "https://github.com/Stoupy51/SmartOreGeneration/releases/download/v1.7.2/SmartOreGeneration_datapack.zip",
    #     }
    # },

    # Bookshelf modules (resolved via Modrinth API with modrinth_slug)
	"bs.bitwise":           {"name": "Bookshelf Bitwise",       "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-bitwise"},
    "bs.block":             {"name": "Bookshelf Block",         "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-block"},
    "bs.color":             {"name": "Bookshelf Color",         "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-color"},
    "bs.dump":              {"name": "Bookshelf Dump",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-dump"},
    "bs.environment":       {"name": "Bookshelf Environment",   "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-environment"},
    "bs.generation":        {"name": "Bookshelf Generation",    "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-generation"},
    "bs.health":            {"name": "Bookshelf Health",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-health"},
    "bs.hitbox":            {"name": "Bookshelf Hitbox",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-hitbox"},
    "bs.id":                {"name": "Bookshelf Id",            "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-id"},
    "bs.interaction":       {"name": "Bookshelf Interaction",   "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-interaction"},
    "bs.link":              {"name": "Bookshelf Link",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-link"},
    "bs.log":               {"name": "Bookshelf Log",           "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-log"},
    "bs.math":              {"name": "Bookshelf Math",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-math"},
    "bs.move":              {"name": "Bookshelf Move",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-move"},
    "bs.position":          {"name": "Bookshelf Position",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-position"},
    "bs.random":            {"name": "Bookshelf Random",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-random"},
    "bs.raycast":           {"name": "Bookshelf Raycast",       "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-raycast"},
    "bs.schedule":          {"name": "Bookshelf Schedule",      "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-schedule"},
    "bs.sidebar":           {"name": "Bookshelf Sidebar",       "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-sidebar"},
    "bs.spline":            {"name": "Bookshelf Spline",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-spline"},
    "bs.string":            {"name": "Bookshelf String",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-string"},
    "bs.time":              {"name": "Bookshelf Time",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-time"},
    "bs.tree":              {"name": "Bookshelf Tree",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-tree"},
    "bs.vector":            {"name": "Bookshelf Vector",        "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-vector"},
    "bs.view":              {"name": "Bookshelf View",          "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-view"},
    "bs.xp":                {"name": "Bookshelf Xp",            "url": "https://github.com/mcbookshelf/bookshelf/releases", "is_used": False, "source": "modrinth", "modrinth_slug": "bookshelf-xp"}
}

