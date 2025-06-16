
## 🍲 StewBeet plugins 🌱

Last updated: 2025/06/16

Here are all the available plugins for the StewBeet framework:

| Category | Plugin | Description | Image | Dependency |
|----------|--------|-------------|-------|------------|
| 🚀 **Core** | [`stewbeet.plugins.initialize`](./initialize.md) | Initializes StewBeet framework, sets up project metadata and pack configurations | ![Auto Item Lore](img/initialize.source_lore.jpg) | 🔴 Fully dependent |
| ✅ **Core** | [`stewbeet.plugins.verify_definitions`](./verify_definitions.md) | Validates item definitions structure and performs consistency checks | ![Debug Export](img/verify_definitions.json_dump.jpg) | 🔴 Fully dependent |
| 🔊 **Resource Pack** | [`stewbeet.plugins.resource_pack.sounds`](./resource_pack.sounds.md) | Processes sound files and generates sounds.json from sounds folder | ![Sound Result](img/resource_pack.sounds.result.jpg) | 🟡 Partly dependent |
| 🎨 **Resource Pack** | [`stewbeet.plugins.resource_pack.item_models`](./resource_pack.item_models.md) | Automatically generates item models from texture patterns | ![Pattern Detection](img/resource_pack.item_models.pattern_detection.jpg) | 🟡 Partly dependent |
| 🖼️ **Resource Pack** | [`stewbeet.plugins.resource_pack.check_power_of_2`](./resource_pack.check_power_of_2.md) | Validates that textures use power-of-2 resolutions | ![Texture Warning](img/resource_pack.check_power_of_2.warning.jpg) | 🟢 Independent |
| 🍳 **Recipes** | [`stewbeet.plugins.custom_recipes`](./custom_recipes.md) | Generates vanilla, smithed, furnace and pulverizer recipes for items | ![Smithed Recipe](img/custom_recipes.smithed_recipe.jpg) | 🔴 Fully dependent |
| 📖 **Documentation** | [`stewbeet.plugins.ingame_manual`](./ingame_manual.md) | Creates interactive in-game manual with item documentation and recipes | ![In-Game Manual](https://i.imgur.com/dtuAG99.gif) | 🔴 Fully dependent |
| ⚡ **Datapack** | [`stewbeet.plugins.datapack.loading`](./datapack.loading.md) | Sets up datapack loading system with version checking and dependencies | ![Load messages](img/datapack.loading.load_messages.jpg) | 🟡 Partly dependent |
| 🧱 **Datapack** | [`stewbeet.plugins.datapack.custom_blocks`](./datapack.custom_blocks.md) | Implements custom block placement, destruction and interaction systems | ![Custom blocks stats](img/datapack.custom_blocks.stats.jpg) | 🔴 Fully dependent |
| 🎁 **Datapack** | [`stewbeet.plugins.datapack.loot_tables`](./datapack.loot_tables.md) | Generates loot tables for all items and creates give-all functionality | ![Give all function](img/datapack.loot_tables.give_all.jpg) | 🔴 Fully dependent |
| 📦 **Compatibility** | [`stewbeet.plugins.compatibilities.simpledrawer`](./compatibilities.simpledrawer.md) | Adds SimpleDrawer material compatibility for compacted drawers | ![SimpleDrawer Integration](img/compatibilities.simpledrawer.complete_file_tree.jpg) | 🔴 Fully dependent |
| ⚔️ **Compatibility** | [`stewbeet.plugins.compatibilities.neo_enchant`](./compatibilities.neo_enchant.md) | Provides NeoEnchant veinminer compatibility for custom ores | ![NeoEnchant Veinminer](img/compatibilities.neo_enchant.veinminer.jpg) | 🔴 Fully dependent |
| ⏰ **Finalization** | [`stewbeet.plugins.finalyze.custom_blocks_ticking`](./finalyze.custom_blocks_ticking.md) | Sets up custom block ticking and update systems | ![Custom blocks timers](img/finalyze.custom_blocks_ticking.timers.jpg) | 🔴 Fully dependent |
| 🏗️ **Finalization** | [`stewbeet.plugins.finalyze.basic_datapack_structure`](./finalyze.basic_datapack_structure.md) | Creates basic datapack timing structure (tick, second, minute functions) | ![Datapack timers](img/finalyze.basic_datapack_structure.timers.jpg) | 🟡 Partly dependent |
| 📋 **Finalization** | [`stewbeet.plugins.finalyze.dependencies`](./finalyze.dependencies.md) | Manages external library dependencies and integration | ![In-game dependency errors](img/finalyze.dependencies.ingame_errors.jpg) | 🔴 Fully dependent |
| 🔍 **Finalization** | [`stewbeet.plugins.finalyze.check_unused_textures`](./finalyze.check_unused_textures.md) | Identifies unused texture files in the resource pack | ![Unused textures warning](img/finalyze.check_unused_textures.warnings.jpg) | 🟢 Independent |
| 🌐 **Automation** | [`stewbeet.plugins.auto.lang_file`](./auto.lang_file.md) | Automatically generates language files from text components | ![Automatic Lang File](img/auto.lang_file.en_us_example.jpg) | 🟢 Independent |
| 📝 **Automation** | [`stewbeet.plugins.auto.headers`](./auto.headers.md) | Adds automatic headers to mcfunction files showing usage context | ![Macro Example](img/auto.headers.macro_example.jpg) | 🟢 Independent |
| 📦 **Build** | [`stewbeet.plugins.archive`](./archive.md) | Creates zip archives of generated datapacks and resource packs | ![Output Directory](img/archive.output_directory.jpg) | 🟢 Independent |
| 🔗 **Build** | [`stewbeet.plugins.merge_smithed_weld`](./merge_smithed_weld.md) | Merges datapacks and resource packs with libraries using Smithed Weld | ![Merged Output](img/merged_smithed_weld.output_directory.jpg) | 🟢 Independent |
| 📂 **Build** | [`stewbeet.plugins.copy_to_destination`](./copy_to_destination.md) | Copies generated packs to configured destination folders | ![Copied datapacks](img/copy_to_destination.datapack_destination.jpg) | 🟢 Independent |
| 🔐 **Build** | [`stewbeet.plugins.compute_sha1`](./compute_sha1.md) | Computes SHA1 hashes for all generated zip files | ![Generated sha1 hashes](img/compute_sha1.example.jpg) | 🟢 Independent |

**Dependency Level Legend:**
- 🔴 **Fully dependent**: Requires StewBeet framework definitions and core functionality to operate
- 🟡 **Partly dependent**: Uses some StewBeet features but could be adapted for standalone use  
- 🟢 **Independent**: Can work without StewBeet framework dependencies

