
# 🚀 stewbeet.plugins.initialize

📄 **Source Code**: [stewbeet/plugins/initialize.py](../../python_package/stewbeet/plugins/initialize/__init__.py) 🔗

## 📋 Overview
The `initialize` plugin is the foundation of the StewBeet framework.<br>
It sets up the core infrastructure, initializes project metadata, configures pack.mcmeta files,<br>
and prepares the build environment for all subsequent plugins.<br>
**(All of the other plugins do not always require the `initialize` plugin, check their documentation for details.)**

## 🎯 Purpose
- 🛠️ Initializes the StewBeet framework
- ⚙️ Sets up more project metadata and configurations
- 📦 Configures pack.mcmeta for both datapacks and resource packs
- 📝 Preprocesses project descriptions and few settings
- 🔄 Handles legacy texture naming conversions
- 🏷️ Creates source lore fonts for item identification

## 🔗 Dependencies
- **✅ Required**: None (this is the first plugin in the pipeline)
- **📍 Position**: Must be the first plugin in the beet.yml pipeline<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
description: ""  # or custom description
meta:
  stewbeet:
    source_lore: ""          # or custom text component
    textures_folder: "assets/textures"
    manual:
      name: ""                   # defaults to "{project_name} Manual"
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `description` | TextComponent | `""` | Project description for pack.mcmeta. Defaults to "{project_name} [{project_version}] by {project_author}" |
| `source_lore` | TextComponent | `""` | Lore text for item identification. Defaults [{"text":"ICON"},{"text":" {project_name}","italic":true,"color":"blue"}] |
| `textures_folder` | string | `"assets/textures"` | Path to the textures folder |
| `manual.name` | string | `""` | Name for the in-game manual. Defaults to "{project_name} Manual" |

## ✨ Features

### 🚀 Framework Initialization
- 🛠️ Sets up the StewBeet memory system (`Mem.ctx`) [`#L25`](../../python_package/stewbeet/plugins/initialize/__init__.py#L25)
- 🔄 Converts the context meta to a Box object for easier access [`#L24`](../../python_package/stewbeet/plugins/initialize/__init__.py#L24)
- ⚙️ Initializes core project configurations

### 📦 Pack.mcmeta Generation
Automatically generates pack.mcmeta files for both datapacks and resource packs with: [`#L49-L58`](../../python_package/stewbeet/plugins/initialize/__init__.py#L49-L58)
- ✅ Correct pack format versions
- 📝 Project description
- 🆔 Project ID
- 🔧 Proper JSON encoding

### 📊 Project Metadata Processing
- **📝 Project Description**: Auto-generates if set to "auto" [`#L28-L31`](../../python_package/stewbeet/plugins/initialize/__init__.py#L28-L31)
- **🏷️ Source Lore**: Creates item identification lore [`#L33-L36`](../../python_package/stewbeet/plugins/initialize/__init__.py#L33-L36)
- **📖 Manual Name**: Sets default manual name if not specified [`#L39-L41`](../../python_package/stewbeet/plugins/initialize/__init__.py#L39-L41)

### 🔄 Legacy Support
Handles legacy texture naming conversions for better later compatibility/pattern matching: [`#L65-L93`](../../python_package/stewbeet/plugins/initialize/__init__.py#L65-L93)
- `_off` → (removed) ❌
- `_down` → `_bottom` ⬇️
- `_up` → `_top` ⬆️
- `_north` → `_front` ⬆️
- `_south` → `_back` ⬇️
- `_west` → `_left` ⬅️
- `_east` → `_right` ➡️

### 🎨 Source Lore Font
Creates special fonts for the source lore system used in item identification. [`#L37`](../../python_package/stewbeet/plugins/initialize/__init__.py#L37) [`source_lore_font.py`](../../python_package/stewbeet/plugins/initialize/source_lore_font.py)

