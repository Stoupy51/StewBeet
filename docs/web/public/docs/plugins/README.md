
# Plugins

Each line of a project's `pipeline` in `beet.yml` is one plugin: it reads your definitions and the packs beet holds, and writes the files they need. This page lists them by what they write.

## Turn a plugin on or off

The `basic` and `extensive` templates run every plugin below. Take a plugin you do not need out of the list, and the next build writes none of its files. The `minimal` template runs only [Function headers](auto.headers.md).

```yaml
pipeline:
    - "src.setup_definitions"
    - "stewbeet.plugins.resource_pack.item_models"
    - "stewbeet.plugins.custom_recipes.silent"
    - "stewbeet.plugins.datapack.custom_blocks"
    - "mecha"
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"
```

- Order matters: a plugin sees the files of the ones before it. The `finalyze` plugins run after `mecha`, once every function exists.
- Add `.silent` to any StewBeet plugin to hide what it prints during the build.
- [Live reload](livereload.md) goes under `require`, since it acts on the whole build. [Source maps](source_maps.md) goes there too, with its `source_maps.emit` step near the end of the `pipeline`.

[How StewBeet fits with beet](../how_it_fits/en.md) explains `require` and `pipeline`, and the [beet.yml reference](../3_beet_config/en.md) lists every option.

## Items and blocks

- [Custom blocks](datapack.custom_blocks.md): makes every `Block` of your definitions placeable.
- [Block ticking](finalyze.custom_blocks_ticking.md): runs a function of your block on every placed copy, each tick, second or minute.
- [Loot tables](datapack.loot_tables.md): a loot table for each item, and a function giving every item in chests.
- [Paintings](custom_paintings.md): turns each `Painting` into a variant players can place.
- [In-game manual](../7_ingame_manual/en.md): a book listing your items and their recipes.

## Recipes

- [Recipes](custom_recipes.md): turns the `recipes` of each item into recipe files and functions, to craft, smelt, cut or smith it.

## Resource pack

- [Item models](resource_pack.item_models.md): the model and `items/` definition of each item and block, from a texture named after it.
- [Sounds](resource_pack.sounds.md): turns the `.ogg` files of your sounds folder into sounds and their `sounds.json`.
- [Texture size check](resource_pack.check_power_of_2.md): warns about textures whose sides are not powers of 2.
- [Unused textures](check_unused_textures.md): warns about textures nothing uses.

## Text and translations

- [Lang file](auto.lang_file.md): moves the text of your commands and loot tables into `lang/en_us.json`.
- [Item images in text](auto.text_renders.md): lets a text component show the picture of an item.

## Functions

- [Load functions](datapack.loading.md): loads your pack once, checks its version against other copies of itself.
- [Tick, second and minute functions](finalyze.basic_datapack_structure.md): runs `tick_2`, `second`, `second_5` and `minute` at their interval.
- [Scoreboard constants](auto.scoreboard_constants.md): declares every number you use as a score holder.
- [List sorting](datapack.sorters.md): functions that sort a list in a storage.
- [Function headers](auto.headers.md): a comment at the top of each function saying what calls it and with which macro arguments.

## Zips and copies

- [Zip archives](archive.md): zips both packs, with the same bytes on every machine.
- [Smithed Weld merge](merge_smithed_weld.md): one `_with_libs.zip` per pack type, libraries included.
- [SHA-1 hashes](compute_sha1.md): the SHA-1 of every zip in one JSON file.
- [Copy to destination](copy_to_destination.md): copies the built packs into your game folders or onto a server.

## Development

- [Project setup](initialize.md): `pack.mcmeta` for both packs and a source lore line on every item.
- [Live reload](livereload.md): reloads your datapack in the game after each build.
- [Source maps](source_maps.md): links every generated command to the Python line that wrote it.

## Compatibility

- [Library version checks](finalyze.dependencies.md): refuses to load when a library or the Minecraft version is too old.
- [SimpleDrawer](compatibilities.simpledrawer.md): compacting drawers for your ingots, nuggets and blocks.
- [NeoEnchant](compatibilities.neo_enchant.md): Veinminer mines your custom ores.

