
# Everything you don't need to think about

A datapack is mostly paperwork: tags that start it, scores that compare versions, a model file for each item, a pack.mcmeta that matches the game, a zip a release can use. StewBeet writes all of it from your definitions and your `beet.yml`. This page lists it by area, with a link to the plugin behind each item.

## Loading and ticking

- Your pack gets the load sequence of the Lantern Load convention: the `minecraft:load` tag, the `load:` tags other packs hook into, and a `load.status` objective reset at every `/reload`. The load tags of your libraries run before yours.
- Two copies of the same pack in one world do not both load. Each copy raises the `#<id>.major`, `#<id>.minor` and `#<id>.patch` scores to its own version, and only the copy that reads back its own version loads. The functions sit under `<id>:v<version>/`, so versions never overwrite each other's files. See [Load functions](../plugins/datapack.loading.md).
- The load function cannot run twice, and the `tick` function only runs once the pack has loaded.
- Players whose name is in `author` get the `convention.debug` tag, and receive `[Loaded <name> v<version>]` in the chat when the pack loads.
- For a pack that supports Minecraft 26.3 or newer, other packs can detect yours through the Smithed tags `#<id>:installed`, `#<id>:major`, `#<id>:minor` and `#<id>:patch`.
- Every item of your definitions is put in the `<id>:items` storage on load.
- A function named `tick`, `tick_2`, `second`, `second_5` or `minute` gets its timer. The tick function counts one score per timer and calls the function when the threshold is reached. See [Tick, second and minute functions](../plugins/finalyze.basic_datapack_structure.md).
- A custom block that has a `second` or `tick` function in its folder gets the tag, the counter and the dispatcher that run it for every placed copy, and a line in the stats function. See [Block ticking](../plugins/finalyze.custom_blocks_ticking.md).
- Every `#<n> <id>.data` constant your functions use is set on load. You write the number where you need it. See [Scoreboard constants](../plugins/auto.scoreboard_constants.md).
- An `unload` function is built by reading your functions: it removes each scoreboard objective you add, removes each field of an `<id>:` storage you modify, kills the entities you summon with a custom tag or UUID, and clears your items from players. It also calls the `unload` function of a library when its archive has one.

## Files from one definition

- An item defined once gets its model, its `items/` definition and its texture in the resource pack, found by file name in your textures folder. A block takes the right parent model from the sides it finds (`_front`, `_top`, `_side`), a bow its pulling states, a lit machine its `_on` model. See [Item models](../plugins/resource_pack.item_models.md).
- Textures dropped at the top of the textures folder are renamed on disk to the names the models look for: lowercase, `_up` becomes `_top`, `_north` becomes `_front`, and so on. The build warns for each rename.
- The same item gets a loot table, one more for each count a recipe gives, a creative inventory tab for the [Unjank](https://github.com/Smithed-MC/unjank) mod, and a `_give_all` function that gives chests holding every item, 27 to a chest. See [Loot tables](../plugins/datapack.loot_tables.md).
- The four setup calls of the templates fill the rest of an item: its `item_model`, its name from its id, your pack's lore, a `custom_data` entry under your namespace, and the Smithed ignore flags.
- Plain text becomes translatable text. Each `{"text": "..."}` in a file of your datapack turns into a `translate` component with the text as its fallback, and `en_us.json` is written with the keys. The key is the project id plus the text, and two different texts that would share a key get a numeric suffix. See [Lang file](../plugins/auto.lang_file.md).
- Your sound files become `sounds.json`. Files that differ by a trailing number are grouped as variants of one event, each variant gets its subtitle, and a sound longer than 10 seconds is streamed. See [Sounds](../plugins/resource_pack.sounds.md).
- A `render` key in a text component is replaced by a glyph of that item, drawn by a font the build generates. See [Item images in text](../plugins/auto.text_renders.md).
- Each function gets a header saying which functions, tags or advancements call it and in what context, and which macro arguments it takes. See [Function headers](../plugins/auto.headers.md).
- Your `pack.png` is copied into the datapack and the resource pack.

## Versions

- Both packs get the pack format of the Minecraft version in `beet.yml`, including versions beet does not know yet.
- `pack.mcmeta` is written for you: format, `min_format` and `max_format` where the game reads them, `supported_formats` for older ones, the description from your name, version and author, and your project id.
- The first and last entries of [`mc_supports`](../3_beet_config/en.md#mc_supports) set the range of formats, and `"infinite"` stands for the latest known version.
- Overlays agree on their format keys, since the game refuses a pack.mcmeta whose overlays disagree.
- The lowest release in `mc_supports` becomes the game version the pack asks for. On an older game, the pack prints a red error in chat instead of half working.

## Libraries

- Your functions are scanned for the markers of the official libraries, such as Smithed Custom Block or a Bookshelf module. Each one found is downloaded for your Minecraft version from Smithed or Modrinth, kept in the beet cache, and added to the load tags. [Datapack libraries](../5_dependencies/en.md) lists them.
- For each library, and each one you declare under `load_dependencies`, the pack compares the library's version scores with the one it was built against. A missing or outdated library prints a clickable line with its name, the version needed and a link. See [Library version checks](../plugins/finalyze.dependencies.md).

## Output

- Both packs are zipped as `<Name>_datapack.zip` and `<Name>_resource_pack.zip`, where `<Name>` is your project name without spaces. Every entry carries the date of the last commit of your `beet.yml` (a fixed date outside git), text entries use Unix line endings, and an unchanged entry is copied from the previous zip. The same sources give the same zip on any machine. See [Zip archives](../plugins/archive.md).
- Each pack can be merged with your libraries into a `_with_libs.zip`. A `_with_libs.zip` of a pack type your pipeline does not weld is moved out of the output, so a release never picks up a stale one. See [Smithed Weld merge](../plugins/merge_smithed_weld.md).
- `sha1_hashes.json` lists the SHA1 of every zip. See [SHA-1 hashes](../plugins/compute_sha1.md).
- The zips go to every folder of `build_copy_destinations`, local or over SFTP. A remote file that already holds the same bytes is not uploaded again. See [Copy to destination](../plugins/copy_to_destination.md).

## Checks

The build warns or fails where the game would stay silent.

- A texture that is not a power of 2 in `item/` or `block/` is listed with its size. See [Texture size check](../plugins/resource_pack.check_power_of_2.md).
- A texture file that no JSON file of the resource pack references is listed. See [Unused textures](../plugins/check_unused_textures.md).
- A function line that starts with `$` without a macro, or a line that uses `$(name)` without the leading `$`, is reported with its function and line number, since the game would run neither as written.
- An item id that contains `:` is warned about and stripped of its namespace.
- A texture a model needs and the folder lacks, or a block whose textures fit no shape, is logged as an error naming the missing file.
- A project `version` that is not `major.minor.patch`, or a missing `id`, `name`, `version` or `author`, stops the build before anything is written.

## Next steps

- [Plugins](../plugins/README.md): the whole pipeline, with what each plugin writes and how to configure it.
- [Datapack libraries](../5_dependencies/en.md): the libraries the build downloads and checks for you.
- [Publishing releases](../6_continuous_delivery/en.md): sending the zips to GitHub, Modrinth and Smithed.

