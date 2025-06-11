
## 🍲 StewBeet plugins 🌱

Last updated: 2025/06/10

Here are all the available plugins for the StewBeet framework:

| Category | Plugin | Description |
|----------|--------|-------------|
| 🚀 **Core** | [`stewbeet.plugins.initialize`](./initialize.md) | Initializes StewBeet framework, sets up project metadata and pack configurations |
| ✅ **Core** | [`stewbeet.plugins.verify_definitions`](./verify_definitions.md) | Validates item definitions structure and performs consistency checks |
| 🔊 **Resource Pack** | [`stewbeet.plugins.resource_pack.sounds`](./resource_pack.sounds.md) | Processes sound files and generates sounds.json from sounds folder |
| 🎨 **Resource Pack** | [`stewbeet.plugins.resource_pack.item_models`](./resource_pack.item_models.md) | Automatically generates item models from texture patterns |
| 🖼️ **Resource Pack** | [`stewbeet.plugins.resource_pack.check_power_of_2`](./resource_pack.check_power_of_2.md) | Validates that textures use power-of-2 resolutions |
| 🍳 **Recipes** | [`stewbeet.plugins.custom_recipes`](./custom_recipes.md) | Generates vanilla, smithed, furnace and pulverizer recipes for items |
| 📖 **Documentation** | [`stewbeet.plugins.ingame_manual`](./ingame_manual.md) | Creates interactive in-game manual with item documentation and recipes |
| ⚡ **Datapack** | [`stewbeet.plugins.datapack.loading`](./datapack.loading.md) | Sets up datapack loading system with version checking and dependencies |
| 🧱 **Datapack** | [`stewbeet.plugins.datapack.custom_blocks`](./datapack.custom_blocks.md) | Implements custom block placement, destruction and interaction systems |
| 🎁 **Datapack** | [`stewbeet.plugins.datapack.loot_tables`](./datapack.loot_tables.md) | Generates loot tables for all items and creates give-all functionality |
| 📦 **Compatibility** | [`stewbeet.plugins.compatibilities.simpledrawer`](./compatibilities.simpledrawer.md) | Adds SimpleDrawer material compatibility for compacted drawers |
| ⚔️ **Compatibility** | [`stewbeet.plugins.compatibilities.neo_enchant`](./compatibilities.neo_enchant.md) | Provides NeoEnchant veinminer compatibility for custom ores |
| ⏰ **Finalization** | [`stewbeet.plugins.finalyze.custom_blocks_ticking`](./finalyze.custom_blocks_ticking.md) | Sets up custom block ticking and update systems |
| 🏗️ **Finalization** | [`stewbeet.plugins.finalyze.basic_datapack_structure`](./finalyze.basic_datapack_structure.md) | Creates basic datapack timing structure (tick, second, minute functions) |
| 📋 **Finalization** | [`stewbeet.plugins.finalyze.dependencies`](./finalyze.dependencies.md) | Manages external library dependencies and integration |
| 🔍 **Finalization** | [`stewbeet.plugins.finalyze.check_unused_textures`](./finalyze.check_unused_textures.md) | Identifies unused texture files in the resource pack |
| 🌐 **Automation** | [`stewbeet.plugins.auto.lang_file`](./auto.lang_file.md) | Automatically generates language files from text components |
| 📝 **Automation** | [`stewbeet.plugins.auto.headers`](./auto.headers.md) | Adds automatic headers to mcfunction files showing usage context |
| 📦 **Build** | [`stewbeet.plugins.archive`](./archive.md) | Creates zip archives of generated datapacks and resource packs |
| 🔗 **Build** | [`stewbeet.plugins.merge_smithed_weld`](./merge_smithed_weld.md) | Merges datapacks and resource packs with libraries using Smithed Weld |
| 📂 **Build** | [`stewbeet.plugins.copy_to_destination`](./copy_to_destination.md) | Copies generated packs to configured destination folders |
| 🔐 **Build** | [`stewbeet.plugins.compute_sha1`](./compute_sha1.md) | Computes SHA1 hashes for all generated zip files |

