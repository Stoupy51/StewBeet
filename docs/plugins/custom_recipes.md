
# 🍳 stewbeet.plugins.custom_recipes

📄 **Source Code**: [stewbeet/plugins/custom_recipes/__init__.py](../../python_package/src/stewbeet/plugins/custom_recipes/__init__.py) 🔗

## 📋 Overview
The `custom_recipes` plugin generates custom recipes for datapacks based on item definitions.<br>
It supports multiple recipe types including vanilla crafting, smelting, Smithed Crafter recipes,<br>
and specialized recipes for SimplEnergy's pulverizer and furnaces with components.<br>
**(This plugin requires valid item definitions in memory to function properly.)**

## 🎯 Purpose
- 🛠️ Generates vanilla crafting recipes (shapeless, shaped, smelting, blasting, smoking)
- ⚙️ Creates Smithed Crafter custom recipes for advanced crafting systems
- 🔥 Handles furnace recipes with NBT data support
- ⚡ Generates pulverizer recipes for SimplEnergy integration
- 🎁 Creates recipe unlocking systems with advancement triggers
- 📋 Manages ingredient detection and recipe discovery

## 🔗 Dependencies
- **✅ Required**: Item definitions in memory (from user setup code)
- **✅ Required**: StewBeet framework initialization
- **📍 Position**: Should run after item model generation and before datapack finalization<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
# No direct configuration required - recipes are defined in item definitions
# Example item with recipes (json format instead but you get it):
# item_definitions:
#   my_item:
#     recipes:
#       - {type: "shapeless", category: "misc", ingredients: ["minecraft:stick", "minecraft:stone"], ...}
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| *Recipes in definitions* | list | `[]` | Recipe definitions are specified in individual item definitions under the `recipes` key |

## ✨ Features

### 🛠️ Vanilla Recipe Generation
**Supported Types:**
- 🔲 **Shapeless Crafting** - Any arrangement of ingredients [`vanilla.py#L78-L99`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L78-L99)
- 📐 **Shaped Crafting** - Specific pattern-based recipes [`vanilla.py#L101-L128`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L101-L128)
- 🔥 **Smelting** - Furnace, blast furnace, and smoker recipes [`vanilla.py#L130-L151`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L130-L151)
- 🍖 **Cooking** - Campfire and other cooking methods

**Features:**
- ✅ Automatic ingredient validation and conversion [`vanilla.py#L85`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L85)
- 🎁 Recipe unlocking system with advancement triggers [`vanilla.py#L33-L50`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L33-L50)
- 📋 Inventory-based recipe discovery [`vanilla.py#L59-L69`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L59-L69)
- 🔄 Custom item result support [`vanilla.py#L72-L74`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L72-L74)

### ⚙️ Smithed Crafter Integration
- 🛠️ **Shapeless Recipes** - Custom crafting without patterns [`smithed.py#L35-L67`](../../python_package/src/stewbeet/plugins/custom_recipes/smithed.py#L35-L67)
- 📐 **Shaped Recipes** - Pattern-based custom crafting [`smithed.py#L69-L100`](../../python_package/src/stewbeet/plugins/custom_recipes/smithed.py#L69-L100)
- 🎯 **Loot Table Results** - Advanced result generation [`smithed.py#L64`](../../python_package/src/stewbeet/plugins/custom_recipes/smithed.py#L64)
- 📦 **Command Integration** - Custom command execution support [`smithed.py#L62-L64`](../../python_package/src/stewbeet/plugins/custom_recipes/smithed.py#L62-L64)
- 🔧 **Unique Ingredient Handling** - Optimized ingredient processing [`smithed.py#L42-L50`](../../python_package/src/stewbeet/plugins/custom_recipes/smithed.py#L42-L50)

### 🔥 Furnace NBT Recipes
- 🔍 **NBT Data Support** - Custom data preservation during smelting [`furnace.py#L24`](../../python_package/src/stewbeet/plugins/custom_recipes/furnace.py#L24)
- ⚡ **Performance Optimization** - Efficient NBT handling [`furnace.py#L41-L50`](../../python_package/src/stewbeet/plugins/custom_recipes/furnace.py#L41-L50)
- 🎯 **Custom Result Generation** - Loot table integration [`furnace.py#L89-L95`](../../python_package/src/stewbeet/plugins/custom_recipes/furnace.py#L89-L95)
- 🔄 **Multi-type Support** - Furnace, blast furnace, smoker compatibility [`furnace.py#L29`](../../python_package/src/stewbeet/plugins/custom_recipes/furnace.py#L29)

### ⚡ Pulverizer Recipes
- 🏭 **SimplEnergy Integration** - Automatic pulverizer recipe generation [`pulverizer.py#L17-L19`](../../python_package/src/stewbeet/plugins/custom_recipes/pulverizer.py#L17-L19)
- 💎 **Ore Processing** - Dust and fragment generation [`pulverizer.py#L32-L46`](../../python_package/src/stewbeet/plugins/custom_recipes/pulverizer.py#L32-L46)
- 🔧 **Custom Results** - Flexible output configuration [`pulverizer.py#L36-L38`](../../python_package/src/stewbeet/plugins/custom_recipes/pulverizer.py#L36-L38)
- 📊 **Yield Control** - Configurable output quantities [`pulverizer.py#L40`](../../python_package/src/stewbeet/plugins/custom_recipes/pulverizer.py#L40)

### 🎁 Recipe Unlocking System
- 🏆 **Advancement Triggers** - Automatic recipe discovery [`vanilla.py#L46-L53`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L46-L53)
- 📦 **Inventory Detection** - Ingredient-based unlocking [`vanilla.py#L59-L69`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L59-L69)
- 🔄 **Dynamic Updates** - Real-time recipe availability [`vanilla.py#L6-L7`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L6-L7)
- 🎯 **Custom Item Support** - NBT-based custom item detection [`vanilla.py#L76-L77`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L76-L77)

### 📋 Recipe Management
- 🔍 **Ingredient Processing** - Smart ingredient parsing and validation [`vanilla.py#L10`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L10)
- 🏷️ **Category Organization** - Recipe categorization support [`vanilla.py#L87`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L87)
- 🎯 **Result Handling** - Flexible output configuration [`vanilla.py#L102`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L102)
- 📊 **Performance Optimization** - Cached recipe generation [`vanilla.py#L78`](../../python_package/src/stewbeet/plugins/custom_recipes/vanilla.py#L78)

