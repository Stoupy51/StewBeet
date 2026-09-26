# Tutorial: build your first datapack

In this tutorial you create a StewBeet project, build it, load it in Minecraft, then add a custom item and a full ruby ore tier with a working custom block. It takes about 20 minutes. Already have a datapack? [Migrate it](../9_migration/en.md) instead.

You need three things:

- **uv**, [the Python package manager from Astral](https://docs.astral.sh/uv/). It installs Python for you, so it is the only thing on this list you set up by hand.
- **A text editor.** [VS Code](https://code.visualstudio.com/) with the Python extension pack and the [StewBeet extension](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) gives you completion inside your commands.
- **Minecraft Java Edition**, to test the result.

You do not install Python yourself. StewBeet needs 3.14, every template says so in its `pyproject.toml`, and uv downloads a matching version the first time you build.

## 1. Install uv

Run the line for your system:

```powershell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS and Linux
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

`uvx` downloads StewBeet, runs it once and discards the copy, so nothing is installed globally. The folder now looks like this:

```bash
AwesomeOres/
├── .beet_cache/              # Build cache (generated)
├── build/                    # Output folder (generated)
├── .venv/                    # Project environment (created by uv on the first build)
├── assets/                   # Your textures and sounds
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
	"smithed",
	"stewbeet>=3.9.3",
]

[tool.uv]
package = false

[tool.uv.sources]
smithed = { git = "https://github.com/Stoupy51/smithed-python.git" }
```

`requires-python` tells uv which interpreter to fetch.

The `[tool.uv.sources]` section is temporary: the `smithed` release on PyPI mixes Pydantic V1 and V2 models, which makes Smithed Weld merging fail on recent Python. Drop that section and the `smithed` dependency once it is fixed upstream.

To use another library in your definitions (`requests`, `pillow`), run `uv add requests`. It lands in this file, in your `.venv`, and in the lock file your collaborators reuse.

## 3. Name your pack

Open `beet.yml`. These fields identify the pack and are reused in `pack.mcmeta`, item lore, archive names and the manual:

```yaml
# Project identifier - MUST match your namespace in src/data/
id: "awesome_ores"

# Project name for display
name: "Awesome Ores"

# Your name (shows up in pack.mcmeta and item lore)
author: "YourName"

# Version using semantic versioning
version: "1.0.0"

# Brief description
description: "My first StewBeet datapack with custom ores!"
```

| Field | Rule | Example |
|-------|------|---------|
| `id` | Lowercase and underscores, no spaces. Must match the folder in `src/data/` | `awesome_ores` |
| `name` | Free text | `"Awesome Ores & Gems"` |
| `version` | [Semantic versioning](https://semver.org/), major.minor.patch | `1.0.0` |

Rename `src/data/basic_template/` to `src/data/awesome_ores/` so it matches `id`.

## 4. Build it

In the terminal, run `uv run stewbeet` (or `uv run stewbeet build`, which is the same).

The first run does the setup: uv reads `pyproject.toml`, downloads Python 3.14 if it is missing, creates `.venv/` and installs StewBeet. It takes about a minute. Later runs start building immediately.

The output looks like this. The warnings are expected on an empty project:

```bash
Building project...

[WARNING 19:05:57] Error during generate_custom_records(): (FileNotFoundError) [WinError 3] The system cannot find the path specified: 'assets/records' 
[DEBUG 19:05:58] Mem.definitions exported to 'definitions_debug.json' 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.sounds': 0.070ms (69900ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.item_models': 0.246ms (245700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.check_power_of_2': 0.250ms (249700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.custom_recipes': 0.021ms (20700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.custom_paintings': 0.007ms (7400ns) 
[WARNING 19:05:58] Database is empty, skipping manual generation. 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.ingame_manual': 0.075ms (74600ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.loading': 0.150ms (150300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.custom_blocks': 0.108ms (108200ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.loot_tables': 0.187ms (187300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.sorters': 0.031ms (31300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compatibilities.simpledrawer': 0.003ms (2700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compatibilities.neo_enchant': 0.003ms (2800ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking': 0.045ms (45100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.basic_datapack_structure': 0.062ms (61600ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.dependencies': 0.875ms (874900ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.check_unused_textures': 0.125ms (124800ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.last_final': 0.154ms (154500ns) 
Generating lang file: 100%|████████████████████████████████████████████████| 21/21 [4481.78it/s, 00:00<00:00]
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.auto.lang_file': 73.613ms (73613100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.auto.headers': 0.561ms (561000ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.archive': 23.592ms (23592200ns) 
[WARNING 19:05:58] No datapacks or libs to merge for build\AwesomeOres_datapack_with_libs.zip. Skipping weld. 
[WARNING 19:05:58] No resource packs or libs to merge for build\AwesomeOres_resource_pack_with_libs.zip. Skipping weld. 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.merge_smithed_weld': 0.593ms (593100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.copy_to_destination': 0.007ms (7300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compute_sha1': 25.546ms (25546400ns) 
[DEBUG 19:05:58] Total execution time: 0.56934s 
Done!
```

`build/` now contains:

| Path | What it is |
|------|------------|
| `datapack/` | The generated datapack, unzipped |
| `resource_pack/` | The generated resource pack, unzipped |
| `AwesomeOres_datapack.zip` | The datapack, ready to drop into a world |
| `AwesomeOres_resource_pack.zip` | The resource pack, ready to enable |
| `sha1_hashes.json` | Hashes of the archives, for server admins |

## 5. Load it in Minecraft

The fastest loop is to let every build copy the packs into your game. Add this to `beet.yml`, with your own paths:

```yaml
meta:
  stewbeet:
    build_copy_destinations:
      datapack: ["C:/Users/YourName/AppData/Roaming/.minecraft/saves/YourWorldName/datapacks"]
      resource_pack: ["C:/Users/YourName/AppData/Roaming/.minecraft/resourcepacks"]
```

From now on, `uv run stewbeet` copies both packs after each build.

To copy them by hand instead:

1. Copy `build/AwesomeOres_datapack.zip` into the world's datapacks folder:
   - Windows: `%appdata%\.minecraft\saves\[WorldName]\datapacks\`
   - macOS: `~/Library/Application Support/minecraft/saves/[WorldName]/datapacks/`
2. Copy `build/AwesomeOres_resource_pack.zip` into the resource packs folder:
   - Windows: `%appdata%\.minecraft\resourcepacks\`
   - macOS: `~/Library/Application Support/minecraft/resourcepacks/`

Then, in game:

1. Run `/reload`.
2. Enable the resource pack in Options, Resource Packs.
3. If you kept the example function in `src/data/awesome_ores/function/`, run it with `/function awesome_ores:path/to/a/random/function/i/guess`.

## 6. Add a custom item

1. Create `assets/textures/` and put a 16x16 PNG in it, for example [`ruby.png`](./ruby.png), so the file is `assets/textures/ruby.png`.
2. Open `src/definitions/additions.py` and declare the item. The `id` matches the texture name, which is how StewBeet finds it:

```python
# Imports
from stewbeet import *


# Main entry point
def main():

    # Add items to the definitions
    Mem.definitions["ruby"] = Item(
        id="ruby",
        components={
            "lore": [{"text":"A precious red gemstone","color":"gray","italic":False}]
        }
    )

    # See extensive_template/src/definitions/additions.py for examples
    pass
```

3. Run `uv run stewbeet`. The first build that renders item models takes a little longer.
4. In game, run `/reload`, then `/loot give @s loot awesome_ores:i/ruby` or `/function awesome_ores:_give_all`.

From that one declaration, StewBeet wrote the item model and its reference, added the texture to the resource pack, built the item components, and added a manual page.

## 7. Add a whole ore tier

Put these textures in `assets/textures/`:

| File | Used for |
|------|----------|
| [`ruby_ore.png`](./ruby_ore.png) | The ore block |
| [`ruby_sword.png`](./ruby_sword.png) | The sword |
| [`ruby_chestplate.png`](./ruby_chestplate.png) | The chestplate item |
| [`ruby_layer_1.png`](./ruby_layer_1.png) | Worn armour, top layer (how Minecraft draws custom armour) |
| [`ruby_layer_2.png`](./ruby_layer_2.png) | Worn armour, bottom layer |

Open `src/definitions/ores.py` and describe the material. Everything StewBeet finds in the textures folder under the `ruby` prefix is registered from this entry:

```python
# Imports
from stewbeet import *


# Main entry point
def main():

    # Configuration to generate everything about a material
    ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
        "ruby": EquipmentsConfig(
            # This ruby is equivalent to diamond,
            equivalent_to = DefaultOre.DIAMOND,

            # But, has more durability (1.2 times more)
            pickaxe_durability = 1.2 * VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]["durability"],

            # And, does 1 more damage per hit (mainhand), and has 0.5 more armor, and mines 20% faster (pickaxe)
            attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
        ),
    }

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    generate_everything_about_these_materials(ORES_CONFIGS)
    return
```

Build, `/reload`, then run `/loot give @s loot awesome_ores:i/ruby_ore` and place the block. It is a working custom block: StewBeet wrote its model, its placement and breaking logic, its drops and mining requirements, its Fortune and Silk Touch behaviour, and wired it to the Smithed Custom Blocks library.

## 8. Open the in-game manual

The manual uses Minecraft's dialog system, which only picks up new dialogs on a server restart, so leave and rejoin the world first. Then press G (the quick action keybind), or run `/loot give @s loot awesome_ores:i/manual` if you started from the Extensive template.

The manual lists your items with their recipes, drawn from the definitions you just wrote.

## What is in `beet.yml`

You have now used the whole loop. Two more parts of `beet.yml` are worth knowing before you go further.

The folders StewBeet reads from, and where it copies the result:

```yaml
meta:
  stewbeet:
    # Directory containing all project textures
    textures_folder: "assets/textures"

    # Directory containing all custom sounds
    sounds_folder: "assets/sounds"

    # Directory containing all jukebox records
    records_folder: "assets/records"

    # Directory containing libraries that will be copied to the build destination, and merged using Smithed Weld if enabled.
    libs_folder: "libs"

    # Optional: glob patterns (relative to libs_folder) of library archives to leave out of the build
    libs_exclude_patterns: []

    # Optional list of destination paths where generated files will be copied
    build_copy_destinations:
      datapack: ["C:/Users/YourName/AppData/Roaming/.minecraft/saves/YourWorldName/datapacks"]
      resource_pack: ["C:/Users/YourName/AppData/Roaming/.minecraft/resourcepacks"]
```

The pipeline, which lists every step of the build in order. Remove a line to turn a feature off:

```yaml
# Plugins to run first
require:
    - "stewbeet"  # Equivalent to "stewbeet.plugins.initialize"
    - "bolt"      # Initialize bolt

# A list of strings representing "plugins".
# - These plugins will execute after the pack is loaded (all src/data and src/assets contents are loaded first)
pipeline:
    - "src.setup_definitions"                           # Your User code for defining items/blocks
    - "stewbeet.plugins.resource_pack.sounds"           # Generate sound files
    - "stewbeet.plugins.resource_pack.item_models"      # Generate item models
    - "stewbeet.plugins.resource_pack.check_power_of_2" # Verify texture dimensions
    - "stewbeet.plugins.custom_recipes"                 # Generate custom recipes
    - "stewbeet.plugins.custom_paintings"               # Generate custom paintings
    - "stewbeet.plugins.ingame_manual"                  # Generate in-game manual
    - "stewbeet.plugins.datapack.loading"               # Set up load/tick functions
    - "stewbeet.plugins.datapack.custom_blocks"         # Set up block mechanics
    - "stewbeet.plugins.datapack.loot_tables"           # Generate loot tables
    - "stewbeet.plugins.datapack.sorters"               # Set up item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"   # SimpleDrawer compatibility
    - "stewbeet.plugins.compatibilities.neo_enchant"    # NeoEnchant compatibility
    - "src.link"                                        # User code for linking features
    - "mecha"                                           # Bolt/Mecha compilation
    - "stewbeet.plugins.finalyze.custom_blocks_ticking" # Finalize block ticking
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # Structure finalization
    - "stewbeet.plugins.finalyze.dependencies"          # Dependency checks
    - "stewbeet.plugins.finalyze.check_unused_textures" # Find unused textures
    - "stewbeet.plugins.finalyze.last_final"            # Final cleanup
    - "stewbeet.plugins.auto.lang_file"                 # Generate language files
    - "stewbeet.plugins.auto.headers"                   # Generate function headers
    - "stewbeet.plugins.archive"                        # Create zip files
    - "stewbeet.plugins.merge_smithed_weld"             # Merge with Smithed Weld
    - "stewbeet.plugins.copy_to_destination"            # Copy to configured paths
    - "stewbeet.plugins.compute_sha1"                   # Compute file hashes
```

Every option is described in [Configuring the build](../3_beet_config/en.md).

## Next steps

- [Defining items and blocks](../1_definitions_setup/en.md): every field an `Item` or a `Block` accepts, recipes included.
- [Writing functions and files](../2_writing_to_files/en.md): add your own commands to the pack.
- [Using datapack libraries](../5_dependencies/en.md): Smithed, Bookshelf and the version checks StewBeet writes for you.
- The [Extensive template](https://github.com/Stoupy51/StewBeet/tree/main/templates/extensive/src) is a complete project to read.

Stuck? Ask on [Discord](https://discord.gg/anxzu6rA9F) or open a [GitHub issue](https://github.com/Stoupy51/StewBeet/issues).
