
# SHA-1 hashes

Writes the SHA-1 of every zip of the build folder to one JSON file, to check a download or tell which pack changed.

It runs in the `basic` template as `stewbeet.plugins.compute_sha1` and in the `extensive` template as `stewbeet.plugins.compute_sha1.silent`, which hides its log output. It needs `output` in `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/compute_sha1/__init__.py)

## What this plugin writes

- `sha1_hashes.json` in the `output` folder: one key per zip, sorted by name, whose value is the SHA-1 in hexadecimal.

```json
{
  "StardustFragment_datapack.zip": "...",
  "StardustFragment_resource_pack.zip": "..."
}
```

Every `.zip` of the folder is hashed, the `_with_libs.zip` ones included.

## Limits

- The plugin hashes what is in the folder when it runs. Put it after [Zip archives](archive.md) and the [Smithed Weld merge](merge_smithed_weld.md) in the `pipeline`, or their zips are missing or out of date.
- A zip left in `output` by an earlier build, such as one from before you renamed the project, is hashed too.

## Next steps

- [Shipping releases automatically](../6_continuous_delivery/en.md): publishing the build.

