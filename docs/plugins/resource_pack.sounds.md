
# 🔊 stewbeet.plugins.resource_pack.sounds

📄 **Source Code**: [stewbeet/plugins/resource_pack/sounds/__init__.py](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py) 🔗

## 📋 Overview
The `sounds` plugin automatically processes sound files and generates the sounds.json configuration for Minecraft resource packs.<br>
It intelligently groups numbered sound variants and handles multithreading for optimal performance.<br>
**(This plugin requires the `sounds_folder` configuration to be set in meta.stewbeet.)**

## 🎯 Purpose
- 🎵 Processes sound files from a designated sounds folder
- 🔢 Groups numbered sound variants (e.g., sound_01.ogg, sound_02.ogg)
- 📄 Generates sounds.json configuration automatically
- ⚡ Utilizes multithreading for efficient file handling
- 🏷️ Creates appropriate subtitles for sound identification

## 🔗 Dependencies
- **✅ Required**: `sounds_folder` configuration in meta.stewbeet
- **📍 Position**: Should run after initialization and before other resource pack plugins<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)
- **📂 Assets**: Requires a sounds folder with audio files

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
meta:
  stewbeet:
    sounds_folder: "assets/sounds"  # Path to sounds directory
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sounds_folder` | string | **Required** | Path to the directory containing sound files. Must be set in `meta.stewbeet.sounds_folder` |

## ✨ Features

### 🎵 Sound File Processing
- 📁 Recursively scans the sounds folder for audio files [`#L40-L41`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L40-L41)
- ✅ Only supports `.ogg` file format [`#L42`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L42)
- 🧹 Sanitizes filenames (removes spaces, converts to lowercase) [`#L59`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L59)
- 📝 Creates Sound objects with proper source paths and subtitles [`#L81-L84`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L81-L84)

### 🔢 Numbered Variant Grouping
Automatically groups sound variants with numbered suffixes: [`#L62-L68`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L62-L68)
- `dirt_bullet_impact_01.ogg` 🎯
- `dirt_bullet_impact_02.ogg` 🎯  
- `dirt_bullet_impact_03.ogg` 🎯

These become variants of the sound `dirt_bullet_impact` in sounds.json.

**Supported numbering patterns:**
- `name_01`, `name_02`, etc. (with underscore)
- `name1`, `name2`, etc. (without underscore)

### 📄 Sounds.json Generation
- 🔧 Automatically creates or updates sounds.json [`#L87`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L87) [`add_sound`](../../python_package/src/stewbeet/core/utils/sounds.py#L22-L25)
- 🏷️ Generates subtitles based on sound names [`#L84`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L84)
- 🎛️ Preserves sound properties (volume, pitch, weight, etc.) [`sounds.py#L34-L44`](../../python_package/src/stewbeet/core/utils/sounds.py#L34-L44)
- 📍 Uses project namespace for sound references [`sounds.py#L15-L17`](../../python_package/src/stewbeet/core/utils/sounds.py#L15-L17)

### ⚡ Multithreading Processing
- 🚀 Processes multiple sound files simultaneously [`#L71`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L71)
- 🔧 Automatically optimizes worker count based on file quantity (max 32) [`#L71`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L71)
- ⏱️ Includes execution time measurement for performance monitoring [`#L16`](../../python_package/src/stewbeet/plugins/resource_pack/sounds/__init__.py#L16)

