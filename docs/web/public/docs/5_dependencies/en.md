# Using datapack libraries

StewBeet's dependency system has two layers: **official libraries** auto-detected from function usage (no config), and **custom `load_dependencies`** declared in `beet.yml`. Both are auto-downloaded at build time and get runtime scoreboard version checks with clickable in-game error messages.

**Config Reference**: [extensive/beet.yml](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/beet.yml) <br>  
**Real-world Example**: [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml) <br>  
**Source Code**: [stewbeet/plugins/finalyze/dependencies/__init__.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/finalyze/dependencies/__init__.py) <br>

- Auto-detect and download official libraries: no configuration needed
- Declare custom dependencies in `beet.yml` with `load_dependencies`
- Generate runtime version checks and Minecraft version compatibility checks
- Provide clickable in-game error messages when dependencies are missing

**Required**: `stewbeet.plugins.finalyze.dependencies` in pipeline  
**Required**: `stewbeet.plugins.datapack.loading` must run before  
**Position**: Must be placed **after** all user functions have been written (scans them to auto-detect libraries)

## Official Libraries (Auto-detected)

The plugin automatically scans all datapack functions during build and marks a library as used when its namespace appears. **No configuration required**: just use the library in your functions.

### Detection Logic
- **Modrinth / static libs** (`furnace_nbt_recipes`, `common_signals`, `realistic_explosion`, `itemio`, `smithed.actionbar`): detected when their namespace string appears in any function.
- **Bookshelf modules** (`bs.*`): detected when a tag call `#bs.X:...` appears in any function.

### Supported Official Libraries

**Smithed**

| Key | Name | URL |
|-----|------|-----|
| `smithed.custom_block` | Smithed Custom Block | [wiki.smithed.dev](https://wiki.smithed.dev/libraries/custom-block/) |
| `smithed.crafter` | Smithed Crafter | [wiki.smithed.dev](https://wiki.smithed.dev/libraries/crafter/) |
| `smithed.actionbar` | Smithed Actionbar | [wiki.smithed.dev](https://wiki.smithed.dev/libraries/actionbar/) |
| `realistic_explosion` | RealisticExplosion | [github.com/Stoupy51/RealisticExplosion](https://github.com/Stoupy51/RealisticExplosion) |

**Modrinth**

| Key | Name | URL |
|-----|------|-----|
| `itemio` | ItemIO | [github.com/edayot/ItemIO](https://github.com/edayot/ItemIO) |
| `common_signals` | Common Signals | [github.com/Stoupy51/CommonSignals](https://github.com/Stoupy51/CommonSignals) |
| `furnace_nbt_recipes` | Furnace NBT Recipes | [github.com/Stoupy51/FurnaceNbtRecipes](https://github.com/Stoupy51/FurnaceNbtRecipes) |
| `smart_ore_generation` | Smart Ore Generation | [github.com/Stoupy51/SmartOreGeneration](https://github.com/Stoupy51/SmartOreGeneration) |

**Bookshelf modules**: all `bs.*` modules are supported (e.g. `bs.math`, `bs.block`, `bs.raycast`, ...). See the [official Bookshelf releases](https://github.com/mcbookshelf/bookshelf/releases) for the full list.

> **Note**: `smart_ore_generation` also receives automatic function tag wiring: if your datapack contains `calls/smart_ore_generation/generate_ores`, `denied_dimensions`, or `post_generation` functions, they are wired into the corresponding `smart_ore_generation:v1/signals/` tags automatically.

### Generating custom ores with `CustomOreGeneration`

`CustomOreGeneration` writes those `generate_ores` functions for you, and using it pulls in `smart_ore_generation`. The library scans 96x96 regions around players and starts each vein at a random position next to air, so ores end up where players can find them.

```python
from stewbeet import CustomOreGeneration

CustomOreGeneration.all_with_config({
    "steel_ore": [
        # Common veins, from y=0 to y=50
        CustomOreGeneration(dimensions=["minecraft:overworld"], minimum_height=0, maximum_height=50, veins_per_region=1.2),
        # Extra veins in badlands only, replacing terracotta that has terracotta above it
        CustomOreGeneration(
            dimensions=["minecraft:overworld"],
            minimum_height=60,
            maximum_height=120,
            veins_per_region=2,
            provider=["#minecraft:terracotta"],
            vein_conditions=["if biome ~ ~ ~ #minecraft:is_badlands"],
            block_conditions=["if block ~ ~1 ~ #minecraft:terracotta"],
        ),
    ],
    "deepslate_steel_ore": [
        CustomOreGeneration(dimensions=["minecraft:overworld"], maximum_height=0, veins_per_region=1.2),
    ],
})
```

Call it from a plugin that runs after the custom blocks exist, like `src/link.py` in the [extensive template](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py). Keys are custom block ids (or `Block` objects), and an ore with several configurations gets one vein function per configuration.

| Field | Default | Meaning |
|-------|---------|---------|
| `dimensions` | required | Dimensions to generate in, ex: `["minecraft:overworld", "stardust:cavern"]` |
| `minimum_height` | `None` | Lowest y of a vein, `None` for the bottom of the overworld |
| `maximum_height` | `70` | Highest y of a vein |
| `veins_per_region` | `4` | Veins per region, the decimal part being a chance: `1.2` is one vein plus a 20% chance of a second |
| `vein_size_logic` | `0.4` | Vein size: `0.0` is a single block, `0.4` a small vein, `1.0` a large one |
| `provider` | overworld carver replaceables | Block, block tag, or list of them, that the ore replaces |
| `vein_conditions` | `[]` | Conditions checked once at the start of the vein, cancelling all of it |
| `block_conditions` | `[]` | Conditions checked at every block of the vein |
| `placer_command` | place the custom block | Execute subcommands ending with `run ...`, placing one ore at `~ ~ ~` |

Conditions are `execute` subcommands starting with `if ` or `unless `, and all of them must hold. Use `vein_conditions` for what is the same across a vein, like a biome (`if biome ~ ~ ~ #minecraft:is_badlands`), and `block_conditions` for what depends on each block, like its neighbours (`if block ~ ~-1 ~ minecraft:deepslate`). To only replace some blocks, set `provider` instead of adding a block condition.

When both `x_ore` and `deepslate_x_ore` are defined, the default placer keeps `x_ore` off deepslate and `deepslate_x_ore` off stone.

---

## Custom `load_dependencies`

Use `load_dependencies` in `beet.yml` to declare libraries that should be downloaded **and** version-checked at runtime. Three source types are supported.

### Configuration Structure

```yaml
meta:
  stewbeet:
    load_dependencies:
      # --- Smithed API (latest MC-compatible version auto-fetched) ---
      "smithed.crafter":
        name: "Smithed Crafter"
        url: "https://wiki.smithed.dev/libraries/crafter/"
        source: "smithed"
        smithed_id: "crafter"
        has_resource_pack: true   # optional, default false

      # --- Modrinth API (latest release for the current MC version auto-fetched) ---
      "itemio":
        name: "ItemIO"
        url: "https://github.com/edayot/ItemIO"
        source: "modrinth"
        modrinth_slug: "itemio"

      # --- Static URL (version pinned, zip downloaded from given URL per MC version) ---
      "common_signals":
        version: [0, 2, 0]
        name: "Common Signals"
        url: "https://github.com/Stoupy51/CommonSignals"
        source: "static"
        static_urls:
          "((1, 21, 7), (0, 2, 0))": "https://github.com/Stoupy51/CommonSignals/releases/download/v0.2.0/CommonSignals_datapack.zip"
```

> **Tip**: The key (e.g. `"smithed.crafter"`) becomes the dependency namespace used in the runtime scoreboard version check (score `#smithed.crafter.major load.status`).

### Source Types

| `source` | Extra required fields | Behavior |
|----------|-----------------------|----------|
| `"smithed"` | `smithed_id` | Fetches the latest MC-compatible version from the Smithed API |
| `"modrinth"` | `modrinth_slug` | Fetches the latest release for the current MC version from Modrinth |
| `"static"` | `static_urls` | Downloads the pinned zip URL for the best matching `((mc_ver), (dep_ver))` key |

### Configuration Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✅ | `str` | Display name shown in runtime error messages |
| `url` | ✅ | `str` | Clickable link shown when the dependency is missing |
| `source` | ✅ | `str` | Download method: `"smithed"`, `"modrinth"`, or `"static"` |
| `smithed_id` | Smithed only | `str` | Smithed pack ID used to query the API |
| `has_resource_pack` | Smithed only | `bool` | Whether to also download the resource pack (default: `false`) |
| `modrinth_slug` | Modrinth only | `str` | Modrinth project slug used to query the API |
| `static_urls` | Static only | `dict` | Maps `"((mc_ver), (dep_ver))"` string keys to download URLs |
| `version` | Static only | `list[int]` | Resolved automatically from `static_urls` at build time |

### Real-world Example: SimplEnergy

[SimplEnergy](https://github.com/Stoupy51/SimplEnergy) uses a single Smithed dependency:

```yaml
# Excerpt from SimplEnergy/beet.yml
meta:
  stewbeet:
    load_dependencies:
      energy:
        name: "DatapackEnergy"
        url: "https://github.com/ICY105/DatapackEnergy"
        source: "smithed"
        smithed_id: "energy"
```

At build time, StewBeet fetches the latest `DatapackEnergy` version compatible with the configured Minecraft version and merges it into the output automatically.

---

## Runtime Behaviour

When the world loads, the generated functions run in this sequence:

1. Lantern Load triggers each dependency's `#dep:load` tag so libraries publish their version scores to `load.status`.
2. **`check_dependencies`**: sets `#dependency_error ns.data` flag if any version score is too old.
3. **`valid_dependencies`**: waits for a player entity, reads `DataVersion` to verify the Minecraft version (against the minimum from `mc_supports`), then sends `tellraw @a` with clickable error links if anything fails. Calls `confirm_load` only when all checks pass.

**In-game error messages when dependencies are missing:**<br>
<img src="../plugins/img/finalyze.dependencies.ingame_errors.jpg">

**Generated `check_dependencies` function:**<br>
<img src="../plugins/img/finalyze.dependencies.check_function.jpg">

---

## Generated Files

| File | Type | Description |
|------|------|-------------|
| `minecraft:load` tag | Tag | Entry point: triggers `#load:_private/load` |
| `load:load` tag | Tag | Points to `#ns:load` |
| `ns:load` tag | Tag | Calls `[#ns:enumerate, #ns:resolve]` |
| `ns:enumerate` tag | Tag | Prepended with `#ns:dependencies` |
| `ns:dependencies` tag | Tag | Lists `#dep:load` for every dependency |
| `load:_private/init` | Function | Resets the `load.status` scoreboard |
| `ns:vX.Y.Z/load/secondary` | Function | Registers `ns.data` scoreboard, calls check/valid |
| `ns:vX.Y.Z/load/check_dependencies` | Function | Sets `#dependency_error` via scoreboard version checks |
| `ns:vX.Y.Z/load/valid_dependencies` | Function | Waits for player, checks `DataVersion`, shows errors |
| `ns:vX.Y.Z/load/confirm_load` | Function | Called only when all checks pass |
| `ns:vX.Y.Z/load/tick_verification` | Function | Routes tick function only when the correct version is loaded |

## Glossary

| Term | Meaning |
|------|---------|
| **`load_dependencies`** | A `beet.yml` metadata dict where you declare external libraries to auto-download and version-check at runtime. |
| **Source type** | How to resolve and download a library: `"smithed"` (Smithed API), `"modrinth"` (Modrinth API), or `"static"` (pinned zip URL per MC version). |
| **Official library** | A pre-registered library in StewBeet's `OFFICIAL_LIBS` registry, detected automatically from function usage: no configuration needed. |
| **Lantern Load** | A community standard for datapack loading order; StewBeet sets it up automatically. |
| **`DataVersion`** | An entity NBT field used to detect the current Minecraft version at runtime; compared against the minimum from `mc_supports`. |

## Next steps

- [finalyze.dependencies](../plugins/finalyze.dependencies.md): the plugin that performs the checks.
- [Configuring the build](../3_beet_config/en.md): where load_dependencies is declared.
- [Shipping releases](../6_continuous_delivery/en.md): shipping a pack that depends on libraries.
