
# Live reload

Reloads your datapack in the game after each build, with no `beet link` and no manual `/reload`.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.livereload`, in `require`, and reads the datapack folders of `build_copy_destinations`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/livereload/__init__.py)

## Use it

```yaml
require:
  - "stewbeet.plugins.livereload"

meta:
  stewbeet:
    build_copy_destinations:
      datapack:
        - "C:/mc/saves/world/datapacks"
```

```bash
stewbeet watch
```

Each rebuild copies the datapack, and the game runs `/reload` by itself. The chat shows `livereload - Reloaded`. A project also linked with `beet link` reloads that folder too.

## What this plugin writes

- `livereload`: a small helper datapack dropped into every local datapack destination and the `beet link` folder. It makes the game reload when it appears.
- `livereload.zip`: the same helper, uploaded to each `sftp://` destination.

The previous build's helper is removed first, since the game only reloads when one appears. It is removed again once the reload shows in the client's `logs/latest.log`.

## Options

| Option | Default | What it does |
|---|---|---|
| `build_copy_destinations.datapack` | `[]` | The datapack folders to reload, local paths or `sftp://` URLs |
| `livereload.minecraft` | detected | The folder holding `logs/latest.log` of the client you play on |

The log folder is looked up in this order: `livereload.minecraft`, the `beet link` Minecraft folder, each `resource_pack` destination and its parents, then the first datapack destination and its parents.

For a remote server, point `livereload.minecraft` at your own client, since only your client logs the reload:

```yaml
meta:
  stewbeet:
    livereload:
      minecraft: "C:/Users/you/AppData/Roaming/.minecraft"
    build_copy_destinations:
      datapack:
        - "sftp://user@host/mc/datapacks"
```

SFTP credentials are read as for [Copy to destination](copy_to_destination.md).

## Limits

- No log folder found: the helper is still copied, but a warning says the cleanup is off, and it stays in the destination.
- A missing remote `datapacks` folder warns, and that destination is skipped. A failed upload warns too.
- Every destination gets the helper, local and remote.

