
# 🔧 StewBeet Definitions Setup Guide

📄 **Example File**: [extensive/src/setup_definitions.py](../../templates/extensive/src/setup_definitions.py) 🔗<br>
📄 **Real-world Example**: [SimplEnergy/src/definitions/setup_main.py](https://github.com/Stoupy51/SimplEnergy/blob/main/src/definitions/setup_main.py) 🔗<br>

## 🔗 Dependencies
- **✅ Required**: StewBeet framework (`from stewbeet import *`)
- **✅ Required**: Beet context (`from beet import Context`)
- **📍 Position**: Must be called early in the pipeline before other plugins that depend on definitions
- **🔄 Integration**: Works with all StewBeet plugins that process item definitions

## 📋 Overview
Item definitions are the heart of the StewBeet framework. They define custom items, blocks, equipment, recipes, and their properties using modern Python classes. The definitions setup creates a comprehensive database of all custom content that subsequent plugins use to generate datapacks and resource packs.

**This is typically the first user-created plugin in the pipeline (after `stewbeet.plugins.initialize`).**

### <u>Some Features Showcase</u>

**Item definitions from the Extensive Template:**<br>
<img src="img/definitions_setup.extensive_template.jpg">

## 🎯 Purpose
- 🛠️ Define custom items, blocks, and equipment using Python classes
- ⚙️ Configure automatic material generation (ores, ingots, tools, armor)
- 📦 Set up crafting recipes with typed classes
- 🔗 Establish relationships between items and their uses
- 🏷️ Configure item names, lore, and categories
- 🎨 Link items to their texture and model assets

## ⚙️ Configuration

### 🎯 Basic Setup Structure
```python
from beet import Context
from stewbeet import *

# Import your definition modules
from .definitions.additions import main as main_additions
from .definitions.ores import main as main_ores

def beet_default(ctx: Context):
    # 1. Generate materials and equipment
    main_ores()
    
    # 2. Generate custom records
    generate_custom_records("auto")
    
    # 3. Add custom items, blocks, paintings
    main_additions()
    
    # 4. Set missing categories
    for item in Mem.definitions.keys():
        obj = Item.from_id(item)
        if not obj.manual_category:
            obj.manual_category = "miscellaneous"
    
    # 5. Final adjustments (REQUIRED!)
    add_item_model_component(black_list=["excluded_items"])
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
    set_manual_components(white_list=["item_name", "lore", "custom_name", "damage", "max_damage"])
    
    # 6. Debug export (optional)
    export_all_definitions_to_json(f"{Mem.ctx.directory}/definitions_debug.json")
```

## 📚 Core Concepts

### 🔩 The Mem.definitions Database
All item definitions are stored in `Mem.definitions`, a global dictionary that gets populated when you create `Item`, `Block`, or `Painting` instances:

```python
# Creating an item automatically registers it
item = Item(id="my_item", base_item="minecraft:iron_ingot")

# Access it from anywhere
same_item = Item.from_id("my_item")
assert item is same_item  # They're the same object!

# Check the underlying dictionary
assert "my_item" in Mem.definitions
```

### 🏗️ Item Class

The modern way to define items using the `Item` class:

```python
from stewbeet import Item, Ingr, CraftingShapedRecipe, WikiButton

item = Item(
    id="magic_sword",                           # Required: unique identifier
    base_item="minecraft:iron_sword",            # Base Minecraft item (default: CUSTOM_ITEM_VANILLA)
    manual_category="combat",                    # Category for the manual
    recipes=[                                   # List of Recipe objects
        CraftingShapedRecipe(
            category="equipment",
            shape=["X", "X", "Y"],
            ingredients={"X": Ingr("diamond"), "Y": Ingr("stick")}
        )
    ],
    override_model=None,                        # Override auto-generated model
    hand_model=None,                            # Special hand-held model
    wiki_buttons=[                              # Manual documentation buttons
        WikiButton({"text": "A powerful sword", "color": "gold"})
    ],
    components={                                # Minecraft item components
        "item_name": {"text": "Magic Sword", "color": "gold"},
        "lore": [{"text": "Deals extra damage", "color": "gray"}],
        "max_damage": 500,
        "enchantments": {"levels": {"minecraft:sharpness": 5}},
        "attribute_modifiers": [
            {
                "type": "minecraft:attack_damage",
                "amount": 8,
                "operation": "add_value",
                "slot": "mainhand",
                "id": "minecraft:base_attack_damage"
            }
        ]
    }
)
```

#### **Item Properties**

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | **Required**: Unique identifier (e.g., `"magic_sword"`) |
| `base_item` | `str` | Base Minecraft item (default: `CUSTOM_ITEM_VANILLA`) |
| `manual_category` | `str \| None` | Category for in-game manual organization |
| `recipes` | `list[RecipeBase]` | List of recipe objects that create this item |
| `override_model` | `JsonDict \| None` | Override auto-generated item model |
| `hand_model` | `JsonDict \| None` | Special model when held in hand |
| `wiki_buttons` | `list[WikiButton] \| TextComponent \| None` | Manual documentation |
| `components` | `JsonDict` | Minecraft item components (without `minecraft:` prefix) |

### 🧱 Block Class

Custom blocks extend the `Item` class with block-specific properties:

```python
from stewbeet import Block, VanillaBlock, CraftingShapedRecipe, Ingr

block = Block(
    id="super_stone",
    vanilla_block=VanillaBlock(
        id="minecraft:cobblestone",
        apply_facing=False              # Whether block has directional states
    ),
    manual_category="blocks",
    recipes=[
        CraftingShapedRecipe(
            category="blocks",
            shape=["XXX", "XXX", "XXX"],
            ingredients={"X": Ingr("minecraft:stone")}
        ),
        # Multiple recipe types supported
        SmeltingRecipe(
            experience=0.1,
            cookingtime=200,
            category="blocks",
            ingredient=Ingr("super_stone"),
            result=Ingr("minecraft:diamond")
        )
    ],
    components={
        "item_name": {"text": "Super Stone", "color": "aqua"}
    }
)
```

#### **VanillaBlock Configuration**

```python
@dataclass
class VanillaBlock:
    id: str                     # Base vanilla block (e.g., "minecraft:cobblestone")
    apply_facing: bool = False  # Enable directional variants (north, east, south, west)
```

### 🎨 Painting Class

Custom paintings for decoration:

```python
from stewbeet import Painting, PaintingData

painting = Painting(
    id="stewbeet_painting",
    manual_category="decorations",
    painting_data=PaintingData(
        texture="stewbeet_painting_2x2",                # Texture file name (without .png)
        author={"text": "Stoupy", "color": "yellow"},   # Defaults to ctx.project_author
        title={"text": "Da' Icon", "color": "gray"},    # Defaults to item name
        width=2,                                         # Width in blocks
        height=2                                         # Height in blocks
    )
)
```

## 🍳 Recipe System

### 📋 Recipe Classes

StewBeet provides typed recipe classes for all Minecraft recipe types:

#### **⚔️ Crafting Shaped Recipe**
```python
from stewbeet import CraftingShapedRecipe, Ingr

recipe = CraftingShapedRecipe(
    result_count=1,                             # Number of items produced
    group="tools",                              # Recipe book grouping
    category="equipment",                       # Recipe book category
    shape=["X X", " Y ", "X X"],               # 3x3 pattern
    ingredients={
        "X": Ingr("minecraft:iron_ingot"),
        "Y": Ingr("stick")
    }
)
```

#### **🎯 Crafting Shapeless Recipe**
```python
recipe = CraftingShapelessRecipe(
    result_count=4,
    category="building_blocks",
    ingredients=[Ingr("minecraft:oak_log")]
    # Can also use: ingredients=4*[Ingr("something")]
)
```

#### **🔥 Smelting Recipe**
```python
recipe = SmeltingRecipe(
    result_count=1,
    cookingtime=200,        # Ticks (200 = 10 seconds)
    experience=0.7,
    category="misc",
    ingredient=Ingr("minecraft:iron_ore"),
    result=Ingr("minecraft:iron_ingot")
)
```

#### **⚡ Other Recipe Types**
```python
# Blasting (faster smelting)
BlastingRecipe(cookingtime=100, experience=0.7, ...)

# Smoking (for food)
SmokingRecipe(cookingtime=100, experience=0.35, ...)

# Campfire
CampfireCookingRecipe(cookingtime=600, experience=0.35, ...)

# Stonecutting
StonecuttingRecipe(result_count=1, ingredient=Ingr(...), result=Ingr(...))

# Smithing Transform
SmithingTransformRecipe(template=Ingr(...), base=Ingr(...), addition=Ingr(...), result=Ingr(...))

# Smithing Trim
SmithingTrimRecipe(template=Ingr(...), base=Ingr(...), addition=Ingr(...))
```

### 🔄 Ingredient Helper

The `Ingr` function creates ingredient specifications:

```python
from stewbeet import Ingr

# Local namespace item
Ingr("steel_ingot")
# Result: {"custom_data": {"your_namespace": {"steel_ingot": True}}}

# Minecraft item
Ingr("minecraft:iron_ingot")
# Result: {"id": "minecraft:iron_ingot"}

# External datapack item
Ingr("tin_ingot", namespace="mechanization")
# Result: {"custom_data": {"mechanization": {"tin_ingot": True}}}

# Use in recipes
recipe = CraftingShapedRecipe(
    shape=["XXX", "XYX", "XXX"],
    ingredients={
        "X": Ingr("steel_ingot"),
        "Y": Ingr("minecraft:diamond")
    }
)
```

## 🛠️ Material Generation

### ⚒️ Automatic Equipment Generation

Generate complete material sets automatically:

```python
# In src/definitions/ores.py
from stewbeet import *

def main():
    ORES_CONFIGS: dict[str, EquipmentsConfig | None] = {
        "steel_ingot": EquipmentsConfig(
            equivalent_to=DefaultOre.IRON,          # Base material stats
            pickaxe_durability=3 * VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"],
            attributes={
                "attack_damage": 1,                  # +1 damage for weapons
                "armor": 0.5,                        # +0.5 armor for armor pieces  
                "mining_efficiency": 0.2             # +20% mining speed for tools
            }
        ),
        "minecraft:stone": None,    # Auto-detect from textures
    }
    
    # Generates: steel_ingot, steel_pickaxe, steel_axe, steel_shovel, 
    # steel_sword, steel_hoe, steel_helmet, steel_chestplate, 
    # steel_leggings, steel_boots, steel_block, raw_steel, raw_steel_block, etc.
    generate_everything_about_these_materials(ORES_CONFIGS)
    
    # Configure custom blocks after generation
    Block.from_id("steel_block").vanilla_block = VanillaBlock(
        id="minecraft:iron_block",
        apply_facing=False
    )
    Block.from_id("raw_steel_block").vanilla_block = VanillaBlock(
        id="minecraft:raw_iron_block",
        apply_facing=False
    )
```

### 🧪 Equipment Configuration

```python
@dataclass
class EquipmentsConfig:
    equivalent_to: DefaultOre               # Base material (WOOD, STONE, GOLD, IRON, DIAMOND, NETHERITE)
    pickaxe_durability: int | None = None  # Custom durability (affects all tools/armor)
    attributes: dict[str, float] = {}       # Stat modifiers
```

## 📖 Documentation Integration

### 📝 Wiki Buttons

Add interactive documentation for the in-game manual:

```python
from stewbeet import Item, WikiButton

item = Item.from_id("steel_ingot")  # Get existing item
item.wiki_buttons = [
    WikiButton([
        {"text": "Steel is a stronger variant of iron.\n"},
        {"text": "It provides better durability.", "color": "yellow"}
    ]),
    WikiButton({"text": "This is another button.", "color": "aqua"})
]
```

### 📚 Manual Item

Create a recipe for the in-game manual:

```python
Item(
    id="manual",
    manual_category="miscellaneous",
    recipes=[
        # Craft with book + steel ingot
        CraftingShapelessRecipe(
            category="misc",
            ingredients=[Ingr("minecraft:book"), Ingr("steel_ingot")]
        ),
        # Update manual by crafting it again
        CraftingShapelessRecipe(
            category="misc",
            ingredients=[Ingr("manual")]
        )
    ],
    components={
        "item_name": Mem.ctx.meta.get("stewbeet", {}).get("manual", {}).get("name") or "Manual"
    }
)
```

## 🎵 Audio Content

### 🎶 Custom Music Discs

```python
# Auto-generate from assets/records/*.ogg files
generate_custom_records("auto")

# Or specify manually
generate_custom_records({
    "my_disc": "My Custom Music.ogg",
    "battle_theme": "Epic Battle Music.ogg"
})
```

## 🔧 Utility Functions

### 🧰 Essential Helper Functions

```python
# Generate item models for all defined items
add_item_model_component(black_list=["excluded_items"])

# Add default names and lore where missing
add_item_name_and_lore_if_missing()

# Add namespace detection data (REQUIRED!)
add_private_custom_data_for_namespace()

# Add Smithed convention data
add_smithed_ignore_vanilla_behaviours_convention()

# Configure manual hover components
set_manual_components(white_list=["item_name", "lore", "custom_name", "damage", "max_damage"])

# Export definitions for debugging
export_all_definitions_to_json(f"{Mem.ctx.directory}/definitions_debug.json")
```

## 🏷️ Item Categories

Common categories for manual organization:

| Category | Description |
|----------|-------------|
| `"materials"` | Raw materials, ingots, gems |
| `"equipment"` | Tools, weapons, armor |
| `"blocks"` | Building blocks, decorative blocks |
| `"miscellaneous"` | Other items, special items |
| `"food"` | Consumable items |
| `"decorations"` | Paintings, decorative items |

## ⚙️ Special Constants

📄 **Source Code**: [stewbeet/core/constants.py](../../python_package/stewbeet/core/constants.py) 🔗

| Constant | Usage |
|----------|-------|
| `CUSTOM_ITEM_VANILLA` | Default base item for custom items (`"minecraft:command_block"`) |
| `CUSTOM_BLOCK_VANILLA` | Base for custom blocks (`"minecraft:furnace"`) |
| `CUSTOM_BLOCK_ALTERNATIVE` | Alternative custom block (`"minecraft:item_frame"`) |
| `CUSTOM_BLOCK_HEAD` | Custom block using player heads (`"minecraft:player_head"`) |

## ✨ Advanced Features

### 🎨 Texture Integration
Items automatically detect textures by name from `assets/textures/`:
- `steel_ingot.png` → `steel_ingot` item
- `steel_pickaxe.png` → `steel_pickaxe` tool
- `steel_block.png` → `steel_block` custom block

### 🔗 Accessing Existing Items

```python
# Get an existing item
item = Item.from_id("my_item")

# Modify it
item.manual_category = "materials"
item.wiki_buttons = [WikiButton({"text": "New info!"})]

# Add a recipe
item.recipes.append(CraftingShapelessRecipe(
    category="misc",
    ingredients=[Ingr("something")]
))
```

## 🚨 Best Practices

### ✅ Do's
- Use `Item`, `Block`, `Painting` classes for clean, typed definitions
- Use `Ingr()` for all ingredient references
- Call final adjustment functions at the end of `beet_default()`
- Organize definitions into separate modules (like `ores.py`, `additions.py`)
- Use meaningful categories for manual organization
- Set `vanilla_block` for custom blocks after generation

### ❌ Don'ts
- Don't modify `Mem.definitions` directly (use classes instead)
- Don't use raw dictionaries for ingredients (use `Ingr()`)
- Don't forget to call final adjustment functions
- Don't skip `vanilla_block` configuration for custom blocks

## 🎯 Complete Example

```python
# src/setup_definitions.py
from beet import Context
from stewbeet import *

from .definitions.additions import main as main_additions
from .definitions.ores import main as main_ores

def beet_default(ctx: Context):
    # 1. Generate materials
    main_ores()
    
    # 2. Generate records
    generate_custom_records("auto")
    
    # 3. Add custom items
    main_additions()
    
    # 4. Set missing categories
    for item_id in Mem.definitions.keys():
        obj = Item.from_id(item_id)
        if not obj.manual_category:
            obj.manual_category = "miscellaneous"
    
    # 5. Final adjustments (REQUIRED!)
    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
    set_manual_components(white_list=["item_name", "lore", "custom_name", "damage", "max_damage"])
    
    # 6. Debug export
    export_all_definitions_to_json(f"{Mem.ctx.directory}/definitions_debug.json")
```

**🎉 This modern approach creates clean, type-safe item definitions that integrate seamlessly with all StewBeet plugins!**<br>
Check the real-world examples at the top of this page to see how it works in practice! 🚀

