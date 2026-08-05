# stewbeet.plugins.resource_pack.sounds

The `sounds` plugin automatically processes sound files and generates the sounds.json configuration for Minecraft resource packs.<br>
It groups numbered sound variants.<br>
**(This plugin requires the `sounds.folder` configuration to be set in meta.stewbeet)**

### <u>Features Showcase</u>

**Example of a sounds folder with .ogg files:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.sounds.folder_example.jpg" style="width: min(480px, 100%)">

**Files are copied to resource pack and sounds.json is created:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.sounds.result.jpg" style="width: min(480px, 100%)">

**Source Code**: [`stewbeet/plugins/resource_pack/sounds/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/sounds/__init__.py) <br>  
**Source Code**: [stewbeet/core/utils/sounds.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/core/utils/sounds.py) <br>


## What it does

- Processes sound files from a designated sounds folder
- Groups numbered sound variants (e.g., sound_01.ogg, sound_02.ogg)
- Generates sounds.json configuration automatically
- Creates appropriate subtitles for sound identification

## Dependencies
- **✅ Required**: `sounds.folder` configuration in meta.stewbeet
- **📍 Position**: Should be able to run anywhere in the pipeline<br>
(see [`basic/beet.yml`](https://github.com/Stoupy51/StewBeet/blob/main/templates/basic/beet.yml) for an example)
- **📂 Assets**: Requires a sounds folder with audio files

## Configuration

### Basic Example Configuration
```yaml
pipeline:
  - ...
  - stewbeet.plugins.resource_pack.sounds
  - ...

meta:
  stewbeet:
    sounds:
      folder: "assets/sounds"             # Path to sounds directory
      exclude_patterns: ["some_folder/*"] # Optional: glob patterns to exclude
```

> **⚠️ Deprecated**: The old `meta.stewbeet.sounds_folder` key is still supported but will emit a warning. Migrate to `meta.stewbeet.sounds.folder`.

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sounds.folder` | string | **Required** | Path to the directory containing sound files. Set in `meta.stewbeet.sounds.folder` |
| `sounds.exclude_patterns` | list[string] | `[]` | Glob patterns (relative to the sounds folder) of files to exclude from processing. E.g. `["some_folder/*", "debug_*.ogg"]` |

## Features

### Sound File Processing
- 📁 Recursively scans the sounds folder for audio files
- ✅ Only supports `.ogg` file format for now
- 🚫 Supports glob-based exclusion via `exclude_patterns`
- 🧹 Sanitizes filenames (removes spaces, converts to lowercase)
- 📝 Creates Sound objects with proper source paths and subtitles

### Numbered Variant Grouping
Automatically groups sound variants with numbered suffixes:
- `dirt_bullet_impact_01.ogg` 🎯
- `dirt_bullet_impact_02.ogg` 🎯  
- `dirt_bullet_impact_03.ogg` 🎯

These become variants of the sound `dirt_bullet_impact` in sounds.json.

**Supported numbering patterns:**
- `name_01`, `name_02`, etc. (with underscore)
- `name1`, `name2`, etc. (without underscore)

### Sounds.json Generation
- 🔧 Automatically creates or updates sounds.json thanks to the `add_sound` function in [`stewbeet.core.utils.sounds`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/core/utils/sounds.py)
- 🏷️ Generates subtitles based on sound names
- 🎛️ Preserves sound properties (volume, pitch, weight, etc.)
- 📍 Uses project namespace for sound references

## Next steps

- [Defining items and blocks](../1_definitions_setup/en.md) — the textures and models this plugin consumes.
- [All plugins](README.md) — the rest of the pipeline, in the order it runs.
- [Configuring the build](../3_beet_config/en.md) — enabling, ordering and configuring plugins.
