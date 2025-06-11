
# 📖 stewbeet.plugins.ingame_manual

📄 **Source Code**: [stewbeet/plugins/ingame_manual/__init__.py](../../python_package/src/stewbeet/plugins/ingame_manual/__init__.py) 🔗

## 📋 Overview
The `ingame_manual` plugin generates an interactive in-game manual/guide book for Minecraft datapacks.<br>
It creates a comprehensive documentation system with item information, crafting recipes, and navigation.<br>
The manual features clickable pages, hover effects, and high-resolution item displays.<br>
**(This plugin requires the `initialize` plugin and item definitions in memory to function properly.)**

![In-game Manual Example](https://i.imgur.com/dtuAG99.gif)

## 🎯 Purpose
- 📖 Creates interactive in-game manual with item documentation
- 🍳 Displays crafting recipes with visual representations
- 🖼️ Generates high-resolution item renders and textures
- 🏷️ Organizes items by categories with navigation
- 🎨 Provides customizable manual assets and fonts
- 🔗 Links related items with clickable page navigation

## 🔗 Dependencies
- **✅ Required**: `stewbeet.plugins.initialize` (for project metadata and configurations)
- **📊 Data**: Requires item definitions in memory (`Mem.definitions`)
- **📍 Position**: Should be placed after definition setup and before finalization plugins<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
meta:
  stewbeet:
    cache_path: "manual_cache"
    high_resolution: true
    debug_mode: false
    manual_overrides: "assets/manual_overrides"
    cache_assets: true
    cache_pages: false
    json_dump_path: "manual_cache/content.json"
    name: ""
    max_items_per_row: 5
    max_rows_per_page: 5
    opengl_resolution: 256
    first_page_text: [{"text":"Modify in beet.yml the text that will be shown in this first manual page", "color":"#505050"}]
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cache_path` | string | **Required** | Directory for storing cached manual assets and fonts |
| `high_resolution` | boolean | `true` | Enables high-resolution crafting displays and item renders |
| `debug_mode` | boolean | `false` | Shows debug grids and uses debug textures for development |
| `manual_overrides` | string | `"assets/manual_overrides"` | Path to directory containing custom manual assets |
| `cache_assets` | boolean | `true` | Enables caching of Minecraft assets and item renders |
| `cache_pages` | boolean | `false` | Enables caching of manual content and page data |
| `json_dump_path` | string | `""` | Path for manual debug dump (JSON format) |
| `name` | string | `""` | Manual title. Defaults to "{project_name} Manual" |
| `max_items_per_row` | integer | `5` | Maximum items per row in category pages (max: 6) |
| `max_rows_per_page` | integer | `5` | Maximum rows per page in category pages (max: 6) |
| `opengl_resolution` | integer | `256` | Resolution for OpenGL renders (recommended: 256x256) |
| `first_page_text` | TextComponent | `""` | Custom text component for the manual's first page |

## ✨ Features

### 📖 Manual Generation
- 📚 **Written Book Creation** - Generates complete written book with navigation [`__init__.py#L15-L20`](../../python_package/src/stewbeet/plugins/ingame_manual/__init__.py#L15-L20)
- 🏷️ **Category Organization** - Groups items by category with dedicated pages [`main.py#L169-L188`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L169-L188)
- 🔄 **Page Management** - Handles page numbering and cross-references [`main.py#L202-L226`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L202-L226)
- 📝 **Content Optimization** - Optimizes book content for performance [`main.py#L588-L590`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L588-L590)

### 🎨 Visual Components
- 🖼️ **High-Resolution Displays** - Advanced item rendering system [`main.py#L260-L275`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L260-L275)
- 🎯 **Custom Fonts** - Specialized font system for manual elements [`main.py#L603-L626`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L603-L626)
- 🖌️ **Image Processing** - Texture generation and manipulation [`iso_renders.py#L86-L117`](../../python_package/src/stewbeet/plugins/ingame_manual/iso_renders.py#L86-L117)
- 🎨 **Asset Management** - Custom manual assets and overrides [`main.py#L83-L95`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L83-L95)

### 🍳 Recipe Integration
- 📐 **Shaped Crafting** - Visual representation of shaped recipes [`other_utils.py#L25-L35`](../../python_package/src/stewbeet/plugins/ingame_manual/other_utils.py#L25-L35)
- 🔲 **Shapeless Crafting** - Organized display of shapeless recipes [`other_utils.py#L37-L47`](../../python_package/src/stewbeet/plugins/ingame_manual/other_utils.py#L37-L47)
- 🔥 **Furnace Recipes** - Smelting and cooking recipe displays [`shared_import.py#L43-L46`](../../python_package/src/stewbeet/plugins/ingame_manual/shared_import.py#L43-L46)
- ⚡ **Special Recipes** - Support for custom recipe types [`other_utils.py#L49-L55`](../../python_package/src/stewbeet/plugins/ingame_manual/other_utils.py#L49-L55)

### 🔗 Interactive Features
- 🖱️ **Clickable Navigation** - Page linking and category browsing [`book_components.py#L94-L107`](../../python_package/src/stewbeet/plugins/ingame_manual/book_components.py#L94-L107)
- 💬 **Hover Effects** - Item information on hover [`text_components.py#L8-L16`](../../python_package/src/stewbeet/plugins/ingame_manual/text_components.py#L8-L16)
- 📄 **Wiki Integration** - Item wiki components and descriptions [`main.py#L349-L366`](../../python_package/src/stewbeet/plugins/ingame_manual/main.py#L349-L366)
- 🔍 **Smart Filtering** - Recipe type filtering and organization [`other_utils.py#L57-L70`](../../python_package/src/stewbeet/plugins/ingame_manual/other_utils.py#L57-L70) 

