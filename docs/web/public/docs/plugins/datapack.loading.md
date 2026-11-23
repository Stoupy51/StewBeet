
# Load functions

Gives your pack the functions that load it once, check its version against other copies of itself, and put your items in storage.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.datapack.loading`, and needs `version` and `id` in `beet.yml`. The version must read `major.minor.patch`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/loading/__init__.py)

The load is finished by `stewbeet.plugins.finalyze.dependencies`, which runs later in the same pipeline.

## Read your items from storage

Every item of your definitions is in the `<id>:items` storage once the pack has loaded, under `all.<item id>`:

```mcfunction
data get storage simplenergy:items all.pulverizer
```

Components carry the `minecraft:` prefix and the item model comes first.

## What this plugin writes

In `function/v<version>/load/`:

- `enumerate` raises the `#<id>.major`, `#<id>.minor` and `#<id>.patch` scores of `load.status` to this pack's version.
- `resolve` runs `load/main` only when those scores equal this pack's version, so the newest copy of the pack is the one that loads.
- `main` runs `secondary` unless `#<id>.loaded` is already 1.
- `set_items_storage` fills the items storage.

The tags `#<id>:enumerate` and `#<id>:resolve` call `enumerate` and `resolve`.

On load, players with the `convention.debug` tag get `[Loaded <name> v<version>]` in the chat.

For a pack that supports Minecraft 26.3 or newer, the Smithed pack enabled convention: the predicate tag `#<id>:installed` and the context int provider tags `#<id>:major`, `#<id>:minor` and `#<id>:patch`, which other packs read whatever the load order.

It also writes the hidden enchantment of each item with a `ranged_weapon`, and a check that gives back what a crossbow loaded instead of its ammunition.

## Options

| Option | Default | What it does |
|---|---|---|
| `version` | required | `major.minor.patch`, compared with other copies of the pack |
| `id` | required | The namespace of every function and storage written |
| `name` | the `id` | The name shown in the load message |
| `meta.stewbeet.items_storage` | `true` | Fills `<id>:items` on load. `datapack.custom_blocks` and `compatibilities.simpledrawer` read it. Set `false` to skip the function and the storage |

## Limits

- A version that is not `major.minor.patch`, or a missing `id` or `version`, fails the build.
- The items storage holds the definitions as declared at build time. It is not updated while the world runs.
- A pack with many items runs one `data modify` per item on every load, which grows `set_items_storage`.

## Next steps

- [Defining items and blocks](../1_definitions_setup/en.md): where the items stored here are declared.

