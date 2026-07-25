
# 🚀 stewbeet.plugins.initialize

📄 **Source Code**: [`stewbeet/plugins/initialize/__init__.py`](../../python_package/stewbeet/plugins/initialize/__init__.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/initialize/source_lore_font.py`](../../python_package/stewbeet/plugins/initialize/source_lore_font.py) 🔗<br>

## 🔗 Dependencies
- **✅ Required**: None (this is the first plugin in the pipeline)
- **📍 Position**: Must be the first plugin in the beet.yml pipeline<br>
(see [`basic/beet.yml`](../../templates/basic/beet.yml) for an example)

## 📋 Overview
The `initialize` plugin is the foundation of the StewBeet framework.<br>
It sets up the core infrastructure, initializes project metadata, configures pack.mcmeta files,<br>
and prepares the build environment for all subsequent plugins.

### <u>Some Features Showcase</u>

**Automatic Item Lore (If not configured) for item definitions**<br>
<img src="img/initialize.source_lore.jpg" style="width: min(540px, 100%)">

**Automatic pack.mcmeta + Automatic description (If not configured)**<br>
<img src="img/initialize.pack_mcmeta.jpg" style="width: min(540px, 100%)">

**Legacy Texture Naming Conversion**<br>
<img src="img/initialize.legacy_texture_naming.jpg" style="width: min(540px, 100%)">


## 🎯 Purpose
- 🛠️ Initializes the StewBeet framework
- ⚙️ Sets up more project metadata and configurations
- 📦 Configures pack.mcmeta for both datapacks and resource packs
- 📝 Preprocesses project descriptions and few settings
- 🔄 Handles legacy texture naming conversions
- 🏷️ Creates source lore fonts for item identification

## ⚙️ Configuration

### 🎯 Basic Example Configuration
```yaml
name: "SimplEnergy"
version: "2.0.2"

pipeline:
  - stewbeet.plugins.initialize  # must be the first plugin
  - ...  # other plugins follow

description: ""  # or custom description
meta:
  stewbeet:
    source_lore: ""          # or custom text component
    source_lore_color: "auto"  # or "#55FFFF" / "gold" / [85, 255, 255] / false
    textures_folder: "assets/textures"
    manual:
      name: ""                   # defaults to "{project_name} Manual"
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `description` | TextComponent | `""` | Project description for pack.mcmeta. Defaults to "{project_name} [{project_version}] by {project_author}" |
| `source_lore` | TextComponent | `""` | Lore text for item identification. Defaults to the logo glyph followed by the project name, both rendered with the generated `{project_id}:tooltip` font |
| `source_lore_color` | string \| list \| false | `"auto"` | Color of the tooltip font. `"auto"` derives it from `pack.png`, any Pillow color (`"#55FFFF"`, `"gold"`, `[85, 255, 255]`) forces it, `false` keeps the packaged gold |
| `textures_folder` | string | `"assets/textures"` | Path to the textures folder |
| `manual.name` | string | `""` | Name for the in-game manual. Defaults to "{project_name} Manual" |

## ✨ Features

### 🚀 Framework Initialization
- 🛠️ Sets up the StewBeet memory system (`Mem.ctx`)
- 🔄 Converts the context meta to a Box object for easier access
- ⚙️ Initializes core project configurations

### 📦 Pack.mcmeta Generation
Automatically generates pack.mcmeta files for both datapacks and resource packs with:
- ✅ Correct pack format versions
- 📝 Project description
- 🆔 Project ID
- 🔧 Proper JSON encoding

### 📊 Project Metadata Processing
- **📝 Project Description**: Auto-generates if set to "auto"
- **🏷️ Source Lore**: Creates item identification lore
- **📖 Manual Name**: Sets default manual name if not specified

### 🏷️ Source Lore Tooltip Font
When `source_lore` is `"auto"` (or unset), items get a branded lore line rendered with a font
generated in your namespace, `{project_id}:tooltip`:

| Provider | Texture | Role |
|----------|---------|------|
| `space` | – | Provides the 2px spacer glyph `뀁` between the logo and the name |
| `bitmap` | `{project_id}:font/tooltip.png` | 8×8 pixel character atlas (printable ASCII + CP437 extras) used to draw the project name |
| `bitmap` | `{project_id}:tooltip/tooltip.png` | The `ꀁ` glyph showing your `pack.png` logo (skipped when the project has no logo) |

The font (and the lore) is only generated when at least one item definition actually carries the
source lore, so a project that overrides every lore pays nothing for it.

**🎨 Automatic recoloring**<br>
The packaged atlas ships in gold. By default (`source_lore_color: "auto"`) StewBeet picks the
dominant color of your `pack.png` — ignoring transparent, gray and dark pixels — then rotates the
atlas hues onto it. Rotating instead of flattening keeps the vertical gradient of the glyphs, so the
result still looks hand-made rather than a single flat color.

```yaml
meta:
  stewbeet:
    source_lore_color: "auto"        # derive from pack.png (default)
    # source_lore_color: "#55FFFF"   # force a color (anything Pillow parses: hex, "gold", "rgb(...)")
    # source_lore_color: [85, 255, 255]
    # source_lore_color: false       # keep the packaged gold, no recolor at all
```

**🖌️ Bringing your own atlas**<br>
Drop a `tooltip.png` next to your `pack.png` (i.e. `assets/tooltip.png`, or `src/tooltip.png`) and it
replaces the packaged atlas verbatim — never recolored, since you already chose its colors. It must
keep the same 16×16 grid layout of 8×8 glyphs.

### 🖼️ Pack Icon Management
Automatically handles pack.png icon distribution:
- 🔍 Searches for pack.png next to the beet project directory (`src/pack.png`, `assets/pack.png`, then `*pack.png`)
- 📦 Copies pack.png to both datapack and resource pack outputs
- 🎨 Uses `PngFile` for proper beet integration
- ✅ Ensures consistent branding across both pack types

### 🔄 Legacy Support
Handles legacy texture naming conversions for better later compatibility/pattern matching:
- `_off` -> (removed) ❌
- `_down` -> `_bottom` ⬇️
- `_up` -> `_top` ⬆️
- `_north` -> `_front` ⬆️
- `_south` -> `_back` ⬇️
- `_west` -> `_left` ⬅️
- `_east` -> `_right` ➡️

