
# Sounds

Turns the `.ogg` files of your sounds folder into sounds a command can play, and writes their `sounds.json`.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.resource_pack.sounds`. It needs `sounds.folder` in the `stewbeet` section of `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/sounds/__init__.py)

## Configure and name your files

```yaml
meta:
  stewbeet:
    sounds:
      folder: assets/sounds
      exclude_patterns: ["debug/*"]
```

Files that end in a number are variants of one sound, and Minecraft picks one at random each time it plays.

```text
dirt_bullet_impact_01.ogg
dirt_bullet_impact_02.ogg
dirt_bullet_impact_03.ogg
fireselect.ogg
```

```mcfunction
playsound simplenergy:dirt_bullet_impact master @s
```

`name_01` and `name1` both group under `name`. A subfolder is part of the name: `guns/shot_1.ogg` plays as `simplenergy:guns/shot`.

## What this plugin writes

- `sounds/<file>.ogg`: each file, its name in lowercase with spaces as `_`.
- `sounds.json`: one event per name, listing its variants. The subtitle is the file name without its trailing number.

A file longer than 10 seconds is set to `stream`, so the game does not load it whole.

## Options

| Option | Default | What it does |
|---|---|---|
| `sounds.folder` | required | The folder scanned for `.ogg` files, subfolders included |
| `sounds.exclude_patterns` | `[]` | Glob patterns, relative to the folder, of files to skip |

## Limits

- Only `.ogg` files are read. A folder with none writes nothing.
- An event name keeps only letters, digits, `.`, `_` and `/`, so `Gun Shot.ogg` plays as `gun_shot`.
- From your own code, `add_sound(ctx, sound, name)` in `stewbeet.core.utils.sounds` adds a sound to the same `sounds.json`.

## Next steps

- [Definitions](../1_definitions_setup/en.md#music-discs): music discs from sound files.

