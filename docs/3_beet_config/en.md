
# ⚙️ Beet & StewBeet Configuration Guide

📄 **Example File**: [extensive/beet.yml](../../templates/extensive/beet.yml) 🔗<br>
📄 **Real-world Example**: [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml) 🔗<br>
📄 **Real-world Example**: [LifeSteal/beet.yml](https://github.com/Stoupy51/LifeSteal/blob/main/beet.yml) 🔗<br>

## 🔗 Configuration File Formats
- **Supported formats**: `beet.yml`, `beet.yaml`, `beet.json`, or `pyproject.toml`
- **📍 Location**: Project root directory
- **🔄 Integration**: Controls entire build process and plugin pipeline

## 📋 Overview
The configuration file is the heart of your StewBeet project. It defines everything from basic project metadata to complex plugin pipelines and custom settings. This guide uses YAML format (`beet.yml`) for examples, but all options work with JSON or pyproject.toml as well.

**The configuration file is read at the start of every build and determines how your entire project is processed.**

## 🎯 Purpose
- 🏷️ Define project identity (name, version, author)
- 📂 Configure directory structure and build output
- 🔌 Manage dependencies and required plugins
- 📦 Set up datapack and resource pack loading
- ⚙️ Control plugin execution pipeline
- 🎨 Customize StewBeet-specific features
- 📚 Configure in-game manual generation
- 🔄 Set up automatic file copying for testing

## 📚 Table of Contents

- [Basic Project Configuration](#basic-project-configuration)
- [Directory Settings](#directory-settings)
- [Dependencies](#dependencies)
- [Pack Configuration](#pack-configuration)
- [Pipeline](#pipeline)
- [Meta Configuration](#meta-configuration)
  - [Minecraft Support](#minecraft-support)
  - [Model Resolver](#model-resolver)
  - [Mecha](#mecha)
  - [StewBeet Settings](#stewbeet-settings)

---

## 🎨 Basic Project Configuration

### 🆔 Project Identifier
```yaml
id: "_your_namespace"
```
Used for namespacing functions, tags, and storage. Must be lowercase with underscores only.

### 📛 Project Name
```yaml
name: "Extensive Template"
```
Displayed in pack.mcmeta, item lore, and in-game messages.

### 👤 Author
```yaml
author: "Stoupy51"
author: "Player1, Player2, Player3"  # Multiple authors
```
Displayed in pack.mcmeta. Supports multiple names separated by `", "`.<br>
**🎁 Special feature:** Players with matching in-game names automatically receive the `convention.debug` tag for development tools.

### 🔢 Version
```yaml
version: "3.0.0"
```
Semantic versioning (`major.minor.patch`) used for dependency validation and versioned function paths.

### 🎮 Minecraft Version
```yaml
minecraft: "1.21.11"
```
Determines available commands and resources. Omit to use latest version.

---

## 📂 Directory Settings

### 📁 Base Directory & Output
```yaml
directory: "."
output: "build"
```
Base directory for relative paths. Output defines where generated packs are saved.

### 🚫 Ignore Patterns
```yaml
ignore: ["build", "manual_cache", "definitions_debug.json"]
```
Files/patterns ignored by `beet watch` to prevent infinite rebuild loops and speed up watching

---

## 🔌 Dependencies

```yaml
require:
    - "stewbeet"
    - "bolt"
```
Python packages/modules required for your project. Listed packages are imported before processing, making their plugins available in the pipeline.

Common dependencies:
- `stewbeet` - StewBeet framework (required)
- `bolt` - Python-like function syntax
- `beet.contrib.vanilla` - Vanilla data generators
- `mecha` - Command preprocessor (usually auto-loaded)

---

## 📦 Pack Configuration

### 📊 Data Pack
```yaml
data_pack:
    name: "datapack"
    load: ["src"]
```
Loads `.mcfunction` files and JSON from `src/data/your_namespace/` into the datapack.

### 🎨 Resource Pack
```yaml
resource_pack:
    name: "resource_pack"
    load: ["src"]
```
Loads assets from `src/assets/` into the resource pack.

---

## ⚡ Pipeline

The pipeline defines the order of plugins executed after packs are loaded. Each plugin processes your project in sequence:

```yaml
pipeline:
    - "src.setup_definitions"                              # 🎨 User setup code
    - "stewbeet.plugins.resource_pack.sounds"              # 🔊 Process custom sounds
    - "stewbeet.plugins.resource_pack.item_models"         # 🎁 Generate item models
    - "stewbeet.plugins.resource_pack.check_power_of_2"    # ✅ Validate texture dimensions
    - "stewbeet.plugins.custom_recipes"                    # 🍳 Generate custom recipes
    - "stewbeet.plugins.custom_paintings"                  # 🖼️ Process custom paintings
    - "stewbeet.plugins.ingame_manual"                     # 📚 Generate in-game manual
    - "stewbeet.plugins.datapack.loading"                  # 🚀 Setup datapack loading
    - "stewbeet.plugins.datapack.custom_blocks"            # 🧱 Process custom blocks
    - "stewbeet.plugins.datapack.loot_tables"              # 🎁 Generate loot tables
    - "stewbeet.plugins.datapack.sorters"                  # 📋 Setup item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"      # 🗄️ SimpleDrawer compatibility
    - "stewbeet.plugins.compatibilities.neo_enchant"       # ✨ NeoEnchant compatibility
    - "src.link"                                           # 🔗 User linking code
    - "mecha"                                              # 🔧 Mecha paired with Bolt
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"    # ⏰ Setup block ticking
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # 🏗️ Create basic structure
    - "stewbeet.plugins.finalyze.dependencies"             # 📦 Handle dependencies
    - "stewbeet.plugins.finalyze.check_unused_textures"    # 🔍 Find unused textures
    - "stewbeet.plugins.finalyze.last_final"               # 🎯 Final cleanup
    - "stewbeet.plugins.auto.lang_file"                    # 🌐 Auto-generate lang files
    - "stewbeet.plugins.auto.headers"                      # 📄 Add file headers
    - "stewbeet.plugins.archive"                           # 🗜️ Create ZIP archives
    - "stewbeet.plugins.merge_smithed_weld"                # 🔀 Merge Smithed Weld libs
    - "stewbeet.plugins.copy_to_destination"               # 📁 Copy to game folders
    - "stewbeet.plugins.compute_sha1"                      # #️⃣ Compute file hashes
```

### 📋 Pipeline Stages Explained

**🎨 Phase 1: Setup** - Define items, blocks, recipes for StewBeet plugins to use
```yaml
- "src.setup_definitions"
```

**🎨 Phase 2: Resource Pack** - Generate models and sounds
```yaml
- "stewbeet.plugins.resource_pack.sounds"
- "stewbeet.plugins.resource_pack.item_models"
- "stewbeet.plugins.resource_pack.check_power_of_2"
```

**🍳 Phase 3: Content** - Recipes, paintings, manual
```yaml
- "stewbeet.plugins.custom_recipes"
- "stewbeet.plugins.custom_paintings"
- "stewbeet.plugins.ingame_manual"
```

**⚙️ Phase 4: Datapack Core** - Loading, blocks, loot tables
```yaml
- "stewbeet.plugins.datapack.loading"
- "stewbeet.plugins.datapack.custom_blocks"
- "stewbeet.plugins.datapack.loot_tables"
```

**🔗 Phase 5: User Code** - Your custom functions
```yaml
- "src.link"
```

**🔧 Phase 6: Compilation** - Mecha/Bolt processing
```yaml
- "mecha"
```

**🎯 Phase 7: Finalization** - Clock functions, dependencies
```yaml
- "stewbeet.plugins.finalyze.custom_blocks_ticking"
- "stewbeet.plugins.finalyze.basic_datapack_structure"
- "stewbeet.plugins.finalyze.dependencies"
```

**📦 Phase 8: Packaging** - ZIPs, copying, hashing
```yaml
- "stewbeet.plugins.auto.lang_file"
- "stewbeet.plugins.archive"
- "stewbeet.plugins.copy_to_destination"
```

### 💡 Pipeline Tips

**✅ DO:**
- Keep the recommended order
- Place user code at strategic points

**❌ DON'T:**
- Put `mecha` before your code
- Skip finalization plugins

---

## 🎛️ Meta Configuration

### 🎮 Minecraft Support
```yaml
mc_supports: ["1.21.11", "26.1-snapshot-1", "infinite"]
```
Declares version compatibility for platform uploads (Modrinth, Smithed). Use `"infinite"` for forward compatibility.<br>
(Influences supported formats in `pack.mcmeta`)

### 🗄️ Model Resolver
```yaml
model_resolver:
    use_cache: true
```
Caches resolved item models (80-90% faster builds). Stored in `.beet_cache/model_resolver/`.

### 🔧 Mecha
```yaml
mecha:
    multiline: true
    formatting: preserve
```
**`multiline: true`** - Enables multi-line command syntax:
```mcfunction
execute
    as @a[scores={health=1..10}]
    at @s
    run function my_namespace:fn
```

**`formatting: preserve`** - Keeps your original formatting style.

---

### ⚙️ StewBeet Settings

#### 📁 Directory Paths
```yaml
stewbeet:
    textures_folder: "assets/textures"
    sounds_folder: "assets/sounds"
    records_folder: "assets/records"
    libs_folder: "libs"
```

#### 🚀 Build Copy Destinations
```yaml
build_copy_destinations:
    datapack: ["D:/latest_snapshot/world/datapacks"]
    resource_pack: ["D:/minecraft/snapshot/resourcepacks"]
```
Automatically copies packs after building. Perfect with `beet watch` for live testing.

#### 🏷️ Custom Item Lore
```yaml
source_lore: "auto" # TextComponents format
```
Appended to custom items lore, `"auto"` defaults to project icon + name.

#### 📦 Load Dependencies
```yaml
load_dependencies:
    "energy":
        version: [1, 8, 0]
        name: "DatapackEnergy"
        url: "https://github.com/ICY105/DatapackEnergy"
```
**Runtime dependency checking** - Validates dependencies on datapack load, shows error messages with download links if missing/outdated.

**⚠️ Requirement:** Only works with datapacks following the [LanternLoad](https://github.com/LanternMC/load) convention.

---

#### 📚 In-Game Manual Configuration

```yaml
manual:
    debug_mode: false
    manual_overrides: "assets/manual_overrides"
    high_resolution: true
    cache_path: "manual_cache"
    cache_assets: true
    cache_pages: false
    name: ""
    max_items_per_row: 5
    max_rows_per_page: 5
    first_page_text: [{"text":"...", "color":"#505050"}]
    showcase_image: 3
    use_dialog: 1
```

**Auto-generated interactive documentation** showing custom items, recipes, and navigation.

**🐛 Debug & Development:**
- `debug_mode: true` - Shows grid overlay for layout debugging

**🎨 Customization:**
- `manual_overrides: "assets/manual_overrides"` - Override default manual assets by placing files with matching names. See [available assets](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/plugins/ingame_manual/assets) for the complete list of overridable files
- `name: ""` - Manual title (empty = auto-generated from project name)
- `first_page_text: [...]` - Welcome message using text components

**💾 Caching:**
- `cache_path: "manual_cache"` - Where to store cache files
- `cache_assets: true` - Cache MC textures/models (90% faster builds)
- `cache_pages: false` - Cache all pages (recommended to false for small projects)

**📐 Layout:**
- `max_items_per_row: 5` - Items per row (1-6)
- `max_rows_per_page: 5` - Rows per page (1-7)
- Default grid: 5×5 = 25 items/page

**📸 Showcase Images:**
- `0` - Disabled
- `1` - Manual items only
- `2` - All custom items
- `3` - Both (recommended)

**💬 Display Mode:**
- `0` - Book only (legacy, no server restart needed)
- `1` - Book opening dialog (recommended, requires server restart)
- `2` - Dialog only (requires server restart)

**Example welcome text:**
```yaml
first_page_text: [{"text":"The following manual will guide you through recipes and energy statistics about devices.", "color": "#505050"}]
```

---

## 💡 Tips and Best Practices

1. 🆔 **Unique namespace** - Use unique `id` to avoid conflicts
2. 🔢 **Semantic versioning** - Follow `major.minor.patch` format
3. 🔀 **Pipeline order** - Place user code at `setup_definitions` and `link`
4. ⚡ **Enable caching** - `cache_assets` and `use_cache` for faster builds
5. 🧪 **Auto-testing** - Set `build_copy_destinations`
6. 📦 **Document dependencies** - Always specify in `load_dependencies`

---

## 📝 Example: Minimal Configuration

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

---

**Need help?** Join the [Discord community](https://discord.gg/anxzu6rA9F)!

