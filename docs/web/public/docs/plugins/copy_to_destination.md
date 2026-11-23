
# Copy to destination

Copies the built packs into your game folders or onto a server after every build, so the game always runs the latest one.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.copy_to_destination`. It does nothing until `build_copy_destinations` is set. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/copy_to_destination/__init__.py)

## Set the destinations

```yaml
meta:
  stewbeet:
    build_copy_destinations:
      datapack:
        - "D:/world/datapacks"
        - "sftp://bob@host/dp"
      resource_pack:
        - "D:/minecraft/resourcepacks"
```

A local folder must already exist, or the build warns and skips it.

For `sftp://user@host/path`, the password comes from the URL (`sftp://user:password@host/path`), then from `~/stewbeet/credentials.yml`. Without a password, the local SSH keys and agent are tried.

```yaml
sftp:
  bob@host:
    password: "..."
```

## What this plugin writes

In every `datapack` destination:

- `StardustFragment_datapack.zip`: your datapack, without its libraries.
- Each zip of `libs/datapack/`, under its own name.
- Each official library your functions use, as `<library>.zip`.

In every `resource_pack` destination:

- `StardustFragment_resource_pack_with_libs.zip` when the [Smithed Weld merge](merge_smithed_weld.md) wrote it, else `StardustFragment_resource_pack.zip`.

## Options

Set in `meta.stewbeet`.

| Option | Default | What it does |
|---|---|---|
| `build_copy_destinations.datapack` | `[]` | Folders or `sftp://` URLs that receive the datapack and its libraries |
| `build_copy_destinations.resource_pack` | `[]` | Folders or `sftp://` URLs that receive the resource pack |
| `libs_folder` | `"libs"` | Where the library zips are read from |
| `libs_exclude_patterns` | `[]` | Library zips to leave out, see the [Smithed Weld merge](merge_smithed_weld.md#options) |

## Limits

- A local file is deleted, then copied. When the game holds it, the copy retries 10 times, one second apart.
- Two destinations that lead to the same folder, through a link for instance, receive the file once.
- A file already on an SFTP server with the same SHA-1 and size as the last upload is not sent again.
- A remote folder that does not exist is never created: the build warns and skips it.
- The libraries inside `libs/resource_pack/` are not copied alone. They reach a resource pack destination only through the merged pack.

## Next steps

- [Configuring the build](../3_beet_config/en.md#build_copy_destinations): the key in context.
- [Live reload](livereload.md): reloads the game when a build lands in these folders.

