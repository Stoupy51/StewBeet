
# 🎨 stewbeet.plugins.resource_pack.item_models

📄 **Source Code**: [stewbeet/plugins/resource_pack/item_models/__init__.py](../../python_package/stewbeet/plugins/resource_pack/item_models/__init__.py) 🔗

## 📋 Overview
The `item_models` plugin automatically generates item and block models for custom items defined in the StewBeet framework.<br>
It intelligently processes textures, handles powered states, generates specialized models for different block types,<br>
and creates the necessary item model files for Minecraft resource packs.<br>
**(This plugin requires item definitions in memory and the `textures_folder` configuration.)**

## 🎯 Purpose
- 🧊 Generates block models with automatic pattern detection (cube, cake, orientable, etc.)
- 🗡️ Creates item models with proper texture layering and parent inheritance
- ⚡ Handles powered states for blocks (_on variants)
- 🏹 Supports specialized models (bow pulling animations, leather armor overlays)
- 🖼️ Automatically processes and copies textures from source folders
- 📄 Generates both `items/*.json` files and `models/[item|block]/*.json` files
- 🎯 Tracks rendered models to prevent duplicates

## 🔗 Dependencies
- **✅ Required**: Item definitions in memory (from user setup code)
- **✅ Required**: `textures_folder` configuration in meta.stewbeet
- **📍 Position**: Should run after verification plugins and before finalization<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
meta:
  stewbeet:
    textures_folder: "assets/textures"  # Path to textures directory
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `textures_folder` | string | `"assets/textures"` | Path to the directory containing texture files. Must be set in `meta.stewbeet.textures_folder` |

## ✨ Features

### 🧊 Block Model Generation
Automatically detects texture patterns and generates appropriate block models:

**🍰 Cake Model** (requires: bottom, side, top, inner textures) [`#L157-L168`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L157-L168)
- Creates main cake model with proper texture mapping
- Generates 6 slice models for each cake state
- Maps `inner` texture to `inside` in model

**🔲 Cube Bottom Top** (requires: bottom, side, top textures) [`#L170-L174`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L170-L174)
- Uses `block/cube_bottom_top` parent
- Perfect for blocks with different top/bottom faces

**⬆️ Orientable Model** (requires: front, side, top textures) [`#L176-L180`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L176-L180)
- Uses `block/orientable` parent
- Ideal for directional blocks like furnaces

**📦 Cube Column** (requires: end, side textures) [`#L182-L186`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L182-L186)
- Uses `block/cube_column` parent
- Great for pillar-like blocks

### 🗡️ Item Model Generation
- 📋 Uses appropriate parent models based on item type [`#L202-L206`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L202-L206)
- 🛡️ Handles leather armor with layer1 overlays [`#L213-L214`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L213-L214)
- 🏹 Creates bow pulling animations with range dispatch [`#L216-L245`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L216-L245)
- ⚡ Supports powered state variants

### ⚡ Powered State Support
- 🔍 Automatically detects `_on` texture variants [`#L113-L118`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L113-L118)
- 🔄 Generates separate models for powered/unpowered states [`#L125`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L125)
- 🎯 Handles texture switching for powered blocks [`#L273-L276`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L273-L276)

### 🖼️ Texture Processing
- 📁 Recursively scans textures folder for .png files [`#L30-L33`](../../python_package/stewbeet/plugins/resource_pack/item_models/__init__.py#L30-L33)
- 📋 Creates texture mappings for model generation
- 🔄 Copies textures to resource pack assets [`#L293-L295`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L293-L295)
- 📝 Supports .mcmeta animation files [`#L296-L297`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L296-L297)
- 🚫 Handles missing texture validation [`#L299-L300`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L299-L300)

### 🏹 Specialized Model Types
**Bow Models:** [`#L216-L245`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L216-L245)
- 🎯 Detects pulling texture variants (`_pulling_0`, `_pulling_1`, etc.)
- 📊 Creates range dispatch system for use duration
- 🔄 Generates conditional models for bow states

**Leather Armor:** [`#L213-L214`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L213-L214)
- 🎨 Automatically adds layer1 texture for color overlays
- 🛡️ Maintains compatibility with vanilla dyeing system

### 📄 Item Component Files
- 🆔 Generates items/{item_name}.json files [`#L313-L316`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L313-L316)
- 🎯 Creates model references for item components
- 🔧 Uses custom JSON encoder for proper formatting [`#L315`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L315)
- 🏹 Handles special cases like bow animations [`#L312`](../../python_package/stewbeet/plugins/resource_pack/item_models/object.py#L312)
