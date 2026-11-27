
# Tutorial: build your first datapack

In this tutorial you create a StewBeet project, build it, load it in Minecraft, then add a custom item and a full ruby ore tier with a working custom block. It takes about 20 minutes. Already have a datapack? [Migrate it](../9_migration/en.md) instead.

You need three things:

- **uv**, [the Python package manager from Astral](https://docs.astral.sh/uv/). It installs Python for you, so it is the only thing on this list you set up by hand.
- **A text editor.** [VS Code](https://code.visualstudio.com/) with the Python extension pack and the [StewBeet extension](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) gives you completion inside your commands.
- **Minecraft Java Edition**, to test the result.

You do not install Python yourself. StewBeet needs 3.14, every template says so in its `pyproject.toml`, and uv downloads a matching version the first time you build.

## 1. Install uv

```powershell tab="Windows"
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash tab="macOS and Linux"
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Other ways to install it (winget, Homebrew, pipx, a standalone binary) are listed on the [uv installation page](https://docs.astral.sh/uv/getting-started/installation/).

Close and reopen your terminal, then check that uv is on your PATH:

```bash
uv --version
```

> Already have Python 3.14 and prefer pip? `pip install stewbeet` works too, and every `uv run stewbeet ...` below becomes plain `stewbeet ...`. The rest of the tutorial is identical.

## 2. Create the project

StewBeet ships three templates. This tutorial uses **Basic**: every plugin is configured and commented, and there is no example content to delete.

| Template | For | What you get |
|----------|-----|--------------|
| Minimal | Learning beet on its own | One StewBeet plugin, nothing else |
| **Basic** | **Most projects** | Every plugin, commented, no example content |
| Extensive | Reading real examples | Every feature, with working items, ores and a manual |

1. Create a folder for the project, for example `C:/MyDatapacks/AwesomeOres/`.
2. Open it in VS Code (right-click the folder and pick "Open with Code", or File, Open Folder).
3. Open a terminal with Terminal, New Terminal. It starts in the project folder.
4. Run:

   ```bash
   uvx stewbeet init basic
   ```

`uvx` downloads StewBeet, runs it once and discards the copy, so nothing is installed globally. The folder looks like this:

```bash
AwesomeOres/
├── .beet_cache/              # Build cache (generated)
├── build/                    # Output folder (generated)
├── .venv/                    # Project environment (created by uv on the first build)
├── assets/                   # Your textures and sounds
│   └── pack.png              # The icon of both packs
├── src/                      # Your source code
│   ├── data/                 # Datapack functions and data
│   │   └── basic_template/   # Your namespace (rename this)
│   ├── definitions/          # Definition modules
│   │   ├── additions.py      # Custom items and blocks
│   │   └── ores.py           # Ore and equipment tiers
│   ├── link.py               # Code that runs after the definitions
│   └── setup_definitions.py  # Entry point for the definitions
├── .gitignore
├── pyproject.toml            # Python dependencies (StewBeet and anything you add)
├── beet.yml                  # Main configuration file
└── definitions_debug.json    # What your definitions produced, for debugging
```

### What `pyproject.toml` does

It makes the project self-contained:

```toml
[project]
name = "template"
version = "0.0.1"
requires-python = ">=3.14"
dependencies = [
	"stewbeet>=3.18.2",
]

[tool.uv]
package = false
```

`requires-python` tells uv which interpreter to fetch.

To use another library in your definitions (`requests`, `pillow`), run `uv add requests`. It lands in this file, in your `.venv`, and in the lock file your collaborators reuse.

## 3. Name your pack

Open `beet.yml`. These fields identify the pack and are reused in `pack.mcmeta`, item lore, archive names and the manual:

```yaml
# Project identifier used for namespacing functions and tags. Should align with the namespace in the source folder.
id: "awesome_ores"

# Project name that will be used in messages, item lore, etc.
name: "Awesome Ores"

# Author(s) name(s) displayed in pack.mcmeta
author: "YourName"

# Project version in semantic versioning format
version: "1.0.0"

# Pack description for pack.mcmeta. Defaults to "{name} [{version}] by {author}" if empty.
description: ""
```

| Field | Rule | Example |
|-------|------|---------|
| `id` | Lowercase and underscores, no spaces. Should match the folder in `src/data/` | `awesome_ores` |
| `name` | Free text | `"Awesome Ores & Gems"` |
| `version` | [Semantic versioning](https://semver.org/), major.minor.patch | `1.0.0` |

Rename `src/data/basic_template/` to `src/data/awesome_ores/` so it matches `id`.

## 4. Build it

In the terminal, run `uv run stewbeet` (or `uv run stewbeet build`, which is the same).

The first run does the setup: uv reads `pyproject.toml`, downloads Python 3.14 if it is missing, creates `.venv/` and installs StewBeet. Later runs start building immediately.

The build prints the time each plugin took. An empty project also prints a few warnings, such as one saying the manual has nothing to list yet.

`build/` contains:

| Path | What it is |
|------|------------|
| `datapack/` | The generated datapack, unzipped |
| `resource_pack/` | The generated resource pack, unzipped |
| `AwesomeOres_datapack.zip` | The datapack, ready to drop into a world |
| `AwesomeOres_resource_pack.zip` | The resource pack, ready to enable |
| `sha1_hashes.json` | Hashes of the archives, for server admins |

## 5. Load it in Minecraft

The fastest loop is to let every build copy the packs into your game. Add this under `meta.stewbeet` in `beet.yml`, with your own paths:

```yaml
build_copy_destinations:
  datapack: ["C:/Users/YourName/AppData/Roaming/.minecraft/saves/YourWorldName/datapacks"]
  resource_pack: ["C:/Users/YourName/AppData/Roaming/.minecraft/resourcepacks"]
```

With this set, `uv run stewbeet` copies both packs after each build.

To copy them by hand instead:

1. Copy `build/AwesomeOres_datapack.zip` into the world's datapacks folder:
   - Windows: `%appdata%\.minecraft\saves\[WorldName]\datapacks\`
   - macOS: `~/Library/Application Support/minecraft/saves/[WorldName]/datapacks/`
2. Copy `build/AwesomeOres_resource_pack.zip` into the resource packs folder:
   - Windows: `%appdata%\.minecraft\resourcepacks\`
   - macOS: `~/Library/Application Support/minecraft/resourcepacks/`

Then, in game:

1. Run `/reload`. The load message written by `src/link.py` appears in the chat.
2. Enable the resource pack in Options, Resource Packs.
3. Run `/function awesome_ores:path/to/a/random/function/i/guess`. It prints "Hello world!", from the function `src/link.py` writes.

## 6. Add a custom item

1. Create `assets/textures/` and put a 16x16 PNG in it, for example [`ruby.png`](./ruby.png), so the file is `assets/textures/ruby.png`.
2. Open `src/definitions/additions.py` and declare the item. The `id` matches the texture name, which is how StewBeet finds it:

```python
# Imports
from stewbeet import *  # type: ignore


# Main entry point
def main():

	# Add items to the definitions
	Item(
		id="ruby",
		manual_category="material",
		components={
			"lore": [{"text":"A precious red gemstone","color":"gray","italic":False}]
		}
	)
```

3. Run `uv run stewbeet`.
4. In game, run `/reload`, then `/loot give @s loot awesome_ores:i/ruby` or `/function awesome_ores:_give_all`.

From that one declaration, StewBeet wrote the item model, added the texture to the resource pack, built the item components, and listed the item in the manual under its `manual_category`.

## 7. Add a whole ore tier

Put these textures in `assets/textures/`:

| File | Used for |
|------|----------|
| [`ruby_ore.png`](./ruby_ore.png) | The ore block |
| [`ruby_sword.png`](./ruby_sword.png) | The sword |
| [`ruby_chestplate.png`](./ruby_chestplate.png) | The chestplate item |
| [`ruby_layer_1.png`](./ruby_layer_1.png) | Worn armour, top layer (how Minecraft draws custom armour) |
| [`ruby_layer_2.png`](./ruby_layer_2.png) | Worn armour, bottom layer, drawn on leggings (read only when a `ruby_leggings.png` exists) |

Open `src/definitions/ores.py` and describe the material. Everything StewBeet finds in the textures folder under the `ruby` prefix is registered from this entry:

```python
# Imports
from stewbeet import *  # type: ignore


# Main entry point
def main():

	# Configuration to generate everything about a material
	ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
		"ruby": EquipmentsConfig(
			# This ruby is equivalent to diamond,
			equivalent_to = DefaultOre.DIAMOND,

			# But, has more durability (1.2 times more)
			pickaxe_durability = 1.2 * VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]["durability"],

			# And, does 1 more damage per hit (mainhand), has 0.5 more armor, and adds 0.2 to the mining efficiency attribute of tools
			attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
		),
	}

	# Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
	generate_everything_about_these_materials(ORES_CONFIGS)
```

`src/setup_definitions.py` runs `ores.py` before `additions.py`. With a `ruby.png` in the textures folder, the `ruby` item comes from the material, so an `Item(id="ruby", ...)` in `additions.py` is ignored: an item already in the definitions is not replaced. Set the lore on the existing item instead:

```python
Item.from_id("ruby").components["lore"] = [{"text":"A precious red gemstone","color":"gray","italic":False}]
```

Build, `/reload`, then run `/loot give @s loot awesome_ores:i/ruby_ore` and place the block. It is a working custom block: StewBeet wrote its model, its placement and breaking logic and its drops, and wired it to the Smithed Custom Block library. Without Silk Touch it drops a ruby, with Silk Touch the ore itself. The sword and the chestplate get crafting recipes made from rubies.

## 8. Open the in-game manual

The manual uses Minecraft's dialog system, which only picks up new dialogs on a server restart, so leave and rejoin the world first. Then press G (the quick action keybind), or run `/loot give @s loot awesome_ores:i/manual` if you started from the Extensive template.

The manual lists your items with their recipes, drawn from your definitions.

## What is in `beet.yml`

`beet.yml` has two parts to know before you go further.

The folders StewBeet reads from, under `meta.stewbeet`:

```yaml
# Directory containing all project textures
textures_folder: "assets/textures"
# Directory containing all custom sounds
sounds:
    folder: "assets/sounds"
    # Optional: glob patterns to exclude from processing
    exclude_patterns: ["some_sub_folder/*"]
# Directory containing all jukebox records
records_folder: "assets/records"
# Directory containing libraries that will be copied to the build destination, and merged using Smithed Weld if enabled.
libs_folder: "libs"
# Optional: glob patterns (relative to libs_folder) of library archives to leave out of the build
libs_exclude_patterns: []
```

The `pipeline` lists every step of the build in order. Each `stewbeet.plugins` line is one plugin, and removing a line turns its feature off. [How StewBeet fits with beet](../how_it_fits/en.md) explains how `require` and `pipeline` work together, and every option is described in [Configuring the build](../3_beet_config/en.md).

## Next steps

- [Items and blocks](../items_and_blocks/en.md): add recipes and a placeable block to an item.
- [Defining items and blocks](../1_definitions_setup/en.md): every field an `Item` or a `Block` accepts, recipes included.
- The [Extensive template](https://github.com/Stoupy51/StewBeet/tree/main/templates/extensive/src) is a complete project to read.

Stuck? Ask on [Discord](https://discord.gg/anxzu6rA9F) or open a [GitHub issue](https://github.com/Stoupy51/StewBeet/issues).

