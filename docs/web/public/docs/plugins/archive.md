
# Zip archives

Zips your datapack and your resource pack into the build folder, with the same bytes on every machine for the same sources.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.archive`, and needs `output` in `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/archive/__init__.py)

## What this plugin writes

In the `output` folder, for a project named `Stardust Fragment`:

- `StardustFragment_datapack.zip`: the datapack. The name is the project name with its spaces removed.
- `StardustFragment_resource_pack.zip`: the resource pack.

Both zips are written in parallel, and each entry follows the same rules:

- Its date is the date of the last git commit of `beet.yml`, in UTC, so every clone dates it the same. Outside a git repository the date is the one of the beet cache folder, and when that is missing, 2025-01-01.
- A text file (`.json`, `.mcfunction`, `.mcmeta`, `.properties`, `.lang`, `.md` and a few more) is stored with Unix line endings, even when you build on Windows.
- An entry whose content is unchanged since the previous build is copied still compressed, which keeps a rebuild fast.
- `pack.png` is replaced by the project icon, when your project has one.

When source maps are on, their files are added to the packs before they are zipped, so the plugin needs no `source_maps.emit` entry before it.

## Limits

- Everything that reads the zips (the [Smithed Weld merge](merge_smithed_weld.md), the [copy to destination](copy_to_destination.md), the [SHA-1 hashes](compute_sha1.md)) must come after it in the `pipeline`.
- A zip locked by another program, such as a game reading the file, is retried 10 times, 0.5 seconds apart. After that the build reports the error.
- `stewbeet.plugins.archive.silent` runs the same plugin and hides its log output.

## Next steps

- [Configuring the build](../3_beet_config/en.md#pipeline): where a plugin sits in the `pipeline`.

