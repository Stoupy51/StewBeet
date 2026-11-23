
# Source maps

Writes a `.mcfunction.map` file beside each generated function, so an editor or [Sniffer](https://github.com/mcbookshelf/sniffer) can jump from a command to the Python line that wrote it.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.source_maps`, with `stewbeet.plugins.source_maps.emit` in the pipeline. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/source_maps/__init__.py)

## Use it

Both go in `beet.yml`:

```yaml
require:
  - "stewbeet"
  - "stewbeet.plugins.source_maps"

pipeline:
  # after the plugins writing functions
  - "stewbeet.plugins.source_maps.emit"
  - "stewbeet.plugins.archive"
```

`source_maps` records the writes, so it comes in `require` before anything writes a function. `emit` writes the maps, after the last plugin that rewrites functions and before the one that zips the pack.

For one build without editing `beet.yml`: `beet -s "require[]=stewbeet.plugins.source_maps" build`.

A bolt or mecha project with no StewBeet call in it needs `source_maps` alone, in `require`.

## What this plugin writes

For each function with a known origin, `<name>.mcfunction.map`, a Source Map v3 file next to the function. The function is not changed.

```json
{
  "version": 3,
  "file": "root.mcfunction",
  "sources": ["src/link.py"],
  "names": [],
  "mappings": "AAKA;AACA;AACA"
}
```

`sources` are paths from the project root. There is no `sourcesContent` and no `sourceRoot`, so the editor reads your files from disk.

Functions mecha compiled also carry `x_stewbeet_bolt` and `x_stewbeet_opaque`, fields that other consumers ignore.

## What is mapped

- Your own `write_function` calls and the lines they build, including a command built in a loop.
- What mecha compiled: a `.bolt` module, or a `.mcfunction` holding bolt.
- What a plugin generates from one of your declarations, mapped to that `Block(...)` or `Item(...)` call. This covers `datapack.custom_blocks` and the recipe functions of `custom_recipes` (smithed, furnace, pulverizer, awakened forge).

Everything else a plugin generates stays unmapped, as do functions written once for the whole pack (`custom_blocks/get_rotation`) and definitions loaded from JSON or `external_definitions`. A map never points inside StewBeet, beet, bolt, mecha or stouputils.

## Limits

- Without `source_maps` in `require`, no map is written. A build that captured nothing warns.
- Without `emit` in the pipeline, the maps are written at the very end of the build. When a plugin that packages the pack already ran (`archive`, `merge_smithed_weld`, `copy_to_destination`, `compute_sha1`), a warning says it did not see them.
- `archive` writes the maps itself before zipping, so the zip and the build folder carry the same files.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): the calls this plugin records.

