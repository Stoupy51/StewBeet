
# ruff: noqa: E501, I001
# Imports
from stouputils.typing import JsonDict

from .bookshelf import BOOKSHELF_MODULES

def official_lib_used(lib: str) -> bool:
    is_used: bool = OFFICIAL_LIBS[lib]["is_used"]
    OFFICIAL_LIBS[lib]["is_used"] = True
    return is_used

# Each entry has: name, url, is_used, source ("smithed"|"modrinth"|"static")
# Smithed entries can have: version, smithed_id, has_resource_pack
# Modrinth entries can have: modrinth_slug
# Static entries have: static_urls {(mc_ver_tuple, dep_ver_tuple): url}
# Bookshelf modules are merged with source="smithed" (smithed_id derived from bs.X → bookshelf-X)
OFFICIAL_LIBS: dict[str, JsonDict] = {

    # Smithed API libs
    "smithed.custom_block":	{"version":[0, 7, 1], "name":"Smithed Custom Block",	"url":"https://wiki.smithed.dev/libraries/custom-block/",	"is_used": False, "source":"smithed", "smithed_id":"custom-block"},
    "smithed.crafter":		{"version":[0, 7, 1], "name":"Smithed Crafter",			"url":"https://wiki.smithed.dev/libraries/crafter/",		"is_used": False, "source":"smithed", "smithed_id":"crafter", "has_resource_pack": True},
    "smithed.actionbar":	{"version":[0, 6, 6], "name":"Smithed Actionbar",		"url":"https://wiki.smithed.dev/libraries/actionbar/",		"is_used": False, "source":"smithed", "smithed_id":"actionbar"},

    # Modrinth API libs
    "itemio":				{"name":"ItemIO",	"url":"https://github.com/edayot/ItemIO",	"is_used": False, "source":"modrinth", "modrinth_slug":"itemio"},

    # Static URL libs (version resolved from static_urls at download time)
    "common_signals":		{"name":"Common Signals",		"url":"https://github.com/Stoupy51/CommonSignals",				"is_used": False, "source":"static", "static_urls": {
            ((1, 21, 7),  (0, 2, 0)): "https://github.com/Stoupy51/CommonSignals/releases/download/v0.2.0/CommonSignals_datapack.zip",
        }
    },
    "furnace_nbt_recipes":	{"name":"Furnace NBT Recipes",	"url":"https://github.com/Stoupy51/FurnaceNbtRecipes",			"is_used": False, "source":"static", "static_urls": {
            ((1, 21, 8),  (1, 10, 1)): "https://github.com/Stoupy51/FurnaceNbtRecipes/releases/download/v1.10.1/FurnaceNbtRecipes_datapack.zip",
        }
    },
    "smart_ore_generation":	{"name":"SmartOreGeneration",	"url":"https://github.com/Stoupy51/SmartOreGeneration",			"is_used": False, "source":"static", "static_urls": {
            ((1, 21, 7),  (1, 7, 2)): "https://github.com/Stoupy51/SmartOreGeneration/releases/download/v1.7.2/SmartOreGeneration_datapack.zip",
        }
    },
    "realistic_explosion":	{"name":"RealisticExplosion",	"url":"https://github.com/Stoupy51/RealisticExplosionLibrary",	"is_used": False, "source":"static", "static_urls": {
            ((1, 21, 11), (1, 2, 0)): "https://github.com/Stoupy51/RealisticExplosionLibrary/releases/download/v1.2.0/RealisticExplosion_datapack.zip",
        }
    },

    # Bookshelf modules (auto-generated, resolved via Smithed API with bs.X → bookshelf-X)
    **{k: {**v, "source": "smithed"} for k, v in BOOKSHELF_MODULES.items()},
}

