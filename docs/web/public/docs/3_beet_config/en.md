
# Configuring the build

The options of the beet configuration file that StewBeet reads, and what it does with each. The file is read at the start of every build.

If beet, bolt and mecha are new names to you, [How StewBeet fits with beet](../how_it_fits/en.md) says who makes what.

The examples use YAML (`beet.yml`). Every option works the same in `beet.yaml`, `beet.json` or `pyproject.toml`. The file lives at the project root.

Complete files to read alongside this page:

- [extensive/beet.yml](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/beet.yml), the template that uses every feature
- [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml), a published pack
- [LifeSteal/beet.yml](https://github.com/Stoupy51/LifeSteal/blob/main/beet.yml), a published pack

## Project identity

### `id`

The namespace root of generated functions, tags and storage keys. Lowercase and underscores only.

```yaml
id: "_your_namespace"
```

### `name`

The human-readable name, shown in `pack.mcmeta`, item lore and in-game messages.

```yaml
name: "Extensive Template"
```

### `author`

One or more creators, shown in `pack.mcmeta`. Separate several names with `", "`.

```yaml
author: "Stoupy51"
author: "Player1, Player2, Player3"  # Multiple authors
```

Players whose in-game name matches an author automatically receive the `convention.debug` tag, which unlocks development tools.

### `version`

Semantic version (`major.minor.patch`), used for dependency checks and versioned function paths.

```yaml
version: "3.0.0"
```

### `minecraft`

The target game version, which decides the available commands and resource formats. Omit it to target the latest version.

```yaml
minecraft: "26.3"
```

## Directories

### `directory` and `output`

`directory` is the base for relative paths. `output` is where the built packs are written.

```yaml
directory: "."
output: "build"
```

### `ignore`

Files and patterns the watcher ignores, which prevents rebuild loops and speeds up `stewbeet watch`.

```yaml
ignore: ["build", "iso_renders", "manual_content.json", "definitions_debug.json", "external_definitions.json"]
```

## `require`

Python packages imported before the build, which makes their plugins available to the pipeline.

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.livereload"
    - "stewbeet.plugins.source_maps"
    - "bolt"
```

| Package | Role |
|---------|------|
| `stewbeet` | The framework (required) |
| `stewbeet.plugins.livereload` | Reloads the game after each build, see [livereload](../plugins/livereload.md) |
| `stewbeet.plugins.source_maps` | Records which line of your code wrote each function, see [source_maps](../plugins/source_maps.md) |
| `bolt` | Python-like syntax inside functions |

## Packs

### `data_pack`

Loads `.mcfunction` and JSON files from `src/data/your_namespace/` into the datapack.

```yaml
data_pack:
    name: "datapack"
    load: ["src"]
```

### `resource_pack`

Loads assets from `src/assets/` into the resource pack.

```yaml
resource_pack:
    name: "resource_pack"
    load: ["src"]
```

## `pipeline`

The plugins that run after the packs are loaded, in order. Each one works on the result of the previous one:

```yaml
pipeline:
    - "src.setup_definitions"                              # User setup code
    - "stewbeet.plugins.resource_pack.sounds"              # Process custom sounds
    - "stewbeet.plugins.resource_pack.item_models"         # Generate item models
    - "stewbeet.plugins.resource_pack.check_power_of_2"    # Validate texture dimensions
    - "stewbeet.plugins.custom_recipes"                    # Generate custom recipes
    - "stewbeet.plugins.custom_paintings"                  # Process custom paintings
    - "stewbeet.plugins.ingame_manual"                     # Generate in-game manual
    - "stewbeet.plugins.datapack.loading"                  # Setup datapack loading
    - "stewbeet.plugins.datapack.custom_blocks"            # Process custom blocks
    - "stewbeet.plugins.datapack.loot_tables"              # Generate loot tables
    - "stewbeet.plugins.datapack.sorters"                  # Setup item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"      # SimpleDrawer compatibility
    - "stewbeet.plugins.compatibilities.neo_enchant"       # NeoEnchant compatibility
    - "src.link"                                           # User linking code
    - "mecha"                                              # Mecha paired with Bolt
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"    # Setup block ticking
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # Create basic structure
    - "stewbeet.plugins.finalyze.dependencies"             # Handle dependencies
    - "stewbeet.plugins.finalyze.unload"                   # Write the unload functions
    - "stewbeet.plugins.finalyze.last_final"               # Final cleanup
    - "stewbeet.plugins.auto.scoreboard_constants"         # Initialize the #<number> constants
    - "stewbeet.plugins.auto.lang_file"                    # Auto-generate lang files
    - "stewbeet.plugins.auto.text_renders"                 # Turn "render" keys into item glyphs
    - "stewbeet.plugins.auto.headers"                      # Add file headers
    - "stewbeet.plugins.source_maps.emit"                  # Write the source maps
    - "stewbeet.plugins.check_unused_textures"             # Find unused textures
    - "stewbeet.plugins.archive"                           # Create ZIP archives
    - "stewbeet.plugins.merge_smithed_weld.datapack"       # Merge Smithed Weld libs into the datapack
    - "stewbeet.plugins.merge_smithed_weld.resource_pack"  # Merge Smithed Weld libs into the resource pack
    - "stewbeet.plugins.copy_to_destination"               # Copy to game folders
    - "stewbeet.plugins.compute_sha1"                      # Compute file hashes
```

Adding `.silent` to the name of a StewBeet plugin, as in `stewbeet.plugins.datapack.loading.silent`, hides its console output. The templates do it for the plugins that print the most.

The order follows eight phases:

| Phase | Plugins | What happens |
|-------|---------|--------------|
| 1. Setup | `src.setup_definitions` | Your code declares items, blocks and recipes |
| 2. Resource pack | `resource_pack.sounds`, `resource_pack.item_models`, `resource_pack.check_power_of_2` | Models and sounds are generated |
| 3. Content | `custom_recipes`, `custom_paintings`, `ingame_manual` | Recipes, paintings and the manual |
| 4. Datapack core | `datapack.loading`, `datapack.custom_blocks`, `datapack.loot_tables`, `datapack.sorters`, `compatibilities.simpledrawer`, `compatibilities.neo_enchant` | Loading, blocks, loot tables, sorters and compatibilities |
| 5. User code | `src.link` | Your functions, which can use everything above |
| 6. Compilation | `mecha` | Bolt and mecha compile every function |
| 7. Finalisation | `finalyze.custom_blocks_ticking`, `finalyze.basic_datapack_structure`, `finalyze.dependencies`, `finalyze.unload`, `finalyze.last_final` | Tick functions, dependency checks, unload functions |
| 8. Packaging | `auto.scoreboard_constants`, `auto.lang_file`, `auto.text_renders`, `auto.headers`, `source_maps.emit`, `check_unused_textures`, `archive`, `merge_smithed_weld`, `copy_to_destination`, `compute_sha1` | Constants, lang file, archives, libraries, copies, hashes |

Keep the order of the templates. Your code goes in `setup_definitions` and `link`, `mecha` comes after `link`, and the finalisation plugins read the functions it compiled, so they stay after it.

## `meta`

### `mc_supports`

The versions declared to Modrinth and Smithed on upload. `"infinite"` declares forward compatibility. It also sets the supported formats written to `pack.mcmeta`, and its lowest release is the Minecraft version the load check asks for.

```yaml
mc_supports: ["26.3", "infinite"]
```

### `model_resolver`

Configures the renderer that draws the item images. `use_cache` reuses the dynamic textures it extracts, instead of extracting them again on every build.

```yaml
model_resolver:
    use_cache: true
```

### `mecha`

How commands are parsed and formatted during compilation.

```yaml
mecha:
    multiline: true
    formatting: preserve
```

`multiline: true` accepts commands split over several lines:

```mcfunction
execute
    as @a[scores={health=1..10}]
    at @s
    run function my_namespace:fn
```

`formatting: preserve` keeps your own formatting in the output.

Leave `version` unset. Mecha then parses with the command tree of your `minecraft` version, and the build warns when `meta.mecha.version` is older than it.

## `meta.stewbeet`

### Source folders

Where StewBeet reads textures, sounds, jukebox records and libraries.

```yaml
stewbeet:
    textures_folder: "assets/textures"
    sounds:
        folder: "assets/sounds"
        exclude_patterns: ["some_sub_folder/*"]
    records_folder: "assets/records"
    libs_folder: "libs"
    libs_exclude_patterns: []
```

`sounds.exclude_patterns` and `libs_exclude_patterns` are glob patterns of files to leave out. The `libs_exclude_patterns` ones are relative to `libs_folder`.

### `build_copy_destinations`

Folders the packs are copied to after each build. Combined with `stewbeet watch`, the game always has the latest build.

```yaml
build_copy_destinations:
    datapack: ["D:/latest_snapshot/world/datapacks"]
    resource_pack: ["D:/minecraft/snapshot/resourcepacks"]
```

A destination can also be an `sftp://user@host/path` URL. The password comes from the URL or from the `sftp` entry of `~/stewbeet/credentials.yml`.

### `source_lore` and `source_lore_color`

A line appended to the lore of every custom item. `"auto"` is the project name, drawn with the generated `{id}:tooltip` font and preceded by the project icon when a `pack.png` exists.

```yaml
source_lore: "auto" # TextComponents format
source_lore_color: "auto" # "auto" | any color | false
```

`source_lore_color` sets that font's colour. `"auto"` takes the dominant colour of your `pack.png`, any Pillow colour forces it (`"#55FFFF"`, `"gold"`, `[85, 255, 255]`), and `false` keeps the packaged gold. An `assets/tooltip.png` placed next to `pack.png` replaces the character atlas entirely and is never recoloured.

A source lore is a plain text component, so it also accepts the `render` key of the [`auto.text_renders`](../plugins/auto.text_renders.md) plugin, to show an item image next to the project name:

```yaml
source_lore: [{"text":"ICON"}, " ", {"text":"Extensive Template", "color":"white", "italic":false, "font":"_your_namespace:tooltip"}, " ", {"render":"steel_ingot", "height":10}]
```

### `iso_renders_path` and `text_renders`

Where the per-item PNGs live, and how the `render` key of text components is drawn.

```yaml
iso_renders_path: "iso_renders"
text_renders:
    default_height: 16
    default_resolution: 0
    font: "renders"
    # allow_oversized: true   # unset asks once in the terminal, and remembers the answer
```

`iso_renders_path` holds one PNG per item, as `<folder>/<namespace>/<item>.png`. Project items are rendered from their model, `minecraft:` items are downloaded, and items from other packs are the ones you put there yourself. It is shared by [`ingame_manual`](../7_ingame_manual/en.md) and [`auto.text_renders`](../plugins/auto.text_renders.md), so an item is only rendered once.

`default_height` is the on-screen height of a glyph in pixels, and `default_resolution` the height its texture is stored at (`0` keeps each image untouched). A picture larger than the 256x256 that fits in one glyph is cut into a grid of glyphs joined with negative spacing, at the cost of one texture per tile. The first build that meets one asks in the terminal and remembers the answer in `.beet_cache`. `allow_oversized` answers up front, and `false` shrinks such renders to a single glyph.

### `load_dependencies`

Datapacks checked when your pack loads. A missing or outdated one prints an error in chat with a download link.

```yaml
load_dependencies:
    "energy":
        version: [1, 8, 0]
        name: "DatapackEnergy"
        url: "https://github.com/ICY105/DatapackEnergy"
```

This only works with datapacks that follow the [LanternLoad](https://github.com/LanternMC/load) convention. Adding `source` and an id downloads the library too, see [Using datapack libraries](../5_dependencies/en.md#custom-load_dependencies).

### `items_storage`

On by default: the load function fills the `<namespace>:items` storage with every item of the project. Set `items_storage: false` to skip it.

### `manual`

Rendering, layout and interaction of the generated in-game manual.

```yaml
manual:
    debug_mode: false
    manual_overrides: "assets/manual_overrides"
    high_resolution: true
    cache_assets: true
    json_dump_path: "manual_content.json"
    name: ""
    max_items_per_row: 5
    max_rows_per_page: 5
    first_page_text: [{"text":"...", "color":"#505050"}]
    showcase_image: 3
    item_layout: "craft"
    item_box_gap: 4
    use_dialog: 1
```

| Option | Effect |
|--------|--------|
| `debug_mode` | `true` draws a grid overlay to debug the layout |
| `manual_overrides` | Folder of files that replace the default manual assets by name. See the [overridable assets](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/plugins/ingame_manual/assets) |
| `high_resolution` | Renders item images at high resolution |
| `cache_assets` | Keeps the Minecraft textures and item renders that already exist instead of making them again |
| `json_dump_path` | Writes the rendered pages to this file, for debugging |
| `name` | Manual title, under 32 characters. Empty means generated from the project name |
| `max_items_per_row` | Items per row, up to 6 |
| `max_rows_per_page` | Rows per page, up to 7. The default grid is 5x5, so 25 items a page |
| `first_page_text` | Welcome text, as text components |
| `showcase_image` | `0` off, `1` manual items only, `2` all custom items, `3` both (recommended) |
| `item_layout` | What an item page shows: `"craft"`, `"item"` (the item in its box) or `"item+craft"` (the box left of the recipe) |
| `item_box_gap` | Pixels between the box and the recipe of `"item+craft"`, negative to draw the recipe over the box |
| `use_dialog` | `1` dialog plus a `manual` item that opens it (recommended), `2` dialog only |

Generated glyph images are cached in beet's `.beet_cache` folder. Item renders live in `iso_renders_path`, above.

Example welcome text:

```yaml
first_page_text: [{"text":"The following manual will guide you through recipes and energy statistics about devices.", "color": "#505050"}]
```

## Minimal configuration

A beet project that only uses the `auto.headers` plugin:

```yaml
# Path to a folder for beet to output
output: "build"

# A list of importable plugin strings
require:
    - "bolt"

# Takes a nested pack config
data_pack:
    name: "datapack"
    load: ["src"]

pipeline:
    - "mecha"
    - "stewbeet.plugins.auto.headers"
```

## Next steps

- [All plugins](../plugins/README.md): what each pipeline stage does.
- [Using datapack libraries](../5_dependencies/en.md): declare and auto-download dependencies.
- [In-game manual](../7_ingame_manual/en.md): the pages and hooks behind the `manual` options.

Questions go to the [Discord community](https://discord.gg/anxzu6rA9F).

