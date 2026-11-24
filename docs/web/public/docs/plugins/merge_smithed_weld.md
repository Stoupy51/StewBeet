
# Smithed Weld merge

Merges your pack with the libraries it needs into one `_with_libs.zip` per pack type, ready to publish or to drop in a world.

The `basic` template runs `stewbeet.plugins.merge_smithed_weld` and the `extensive` template runs its two halves, `stewbeet.plugins.merge_smithed_weld.datapack` and `stewbeet.plugins.merge_smithed_weld.resource_pack`. It reads the zips of [Zip archives](archive.md). [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/merge_smithed_weld/__init__.py)

## Choose what gets merged

Welding costs seconds on every build. List only the pack types you ship:

```yaml
pipeline:
  - stewbeet.plugins.archive
  - stewbeet.plugins.merge_smithed_weld.datapack
```

The plain entry merges both, like listing the two halves.

## What this plugin writes

In the `output` folder:

- `StardustFragment_datapack_with_libs.zip`: your datapack, the zips of `libs/datapack/`, then the [official libraries](../5_dependencies/en.md#official-libraries) your functions use.
- `StardustFragment_resource_pack_with_libs.zip`: the same for the resource pack, with `libs/resource_pack/`.

Smithed Weld resolves the files two packs both provide. Your own pack comes last, so its `pack.mcmeta` and `pack.png` win. When a merge has the same sources as the last build, the zip on disk is kept as it is.

## Options

Set in `meta.stewbeet`.

| Option | Default | What it does |
|---|---|---|
| `libs_folder` | `"libs"` | The folder holding `datapack/*.zip` and `resource_pack/*.zip` |
| `libs_exclude_patterns` | `[]` | Glob patterns, relative to `libs_folder`, of library zips to leave out, such as `"resource_pack/*ARAM*.zip"` |

An excluded zip is left out of the whole build: it is not merged and not copied to a destination.

## Limits

- A pack type needs your own zip and at least one library. With nothing to merge, the build warns `No datapacks or libs to merge` and writes no `_with_libs.zip`.
- A pack type that no entry in the `pipeline` merges has its `_with_libs.zip` deleted from `output`. A leftover zip from an older build would otherwise be hashed and uploaded as if it were current.
- When a weld fails, the build prints the error and the `_with_libs.zip` is the one from the last good build.
- The merged resource pack drops the `__smithed__` entry of its language files, which would stop Minecraft from loading the language.

## Next steps

- [Using datapack libraries](../5_dependencies/en.md): how official libraries are detected and downloaded.
- [Configuring the build](../3_beet_config/en.md#metastewbeet): `meta.stewbeet`.

