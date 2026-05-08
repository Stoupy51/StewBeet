
# 🔧 StewBeet Definitions Setup Guide

## 📖 Definitions
- **Definitions Setup**: The user plugin responsible for creating and enriching `Mem.definitions`.
- **Definition**: A typed object entry (`Item`, `Block`, `Painting`, etc.) used by downstream StewBeet plugins.
- **Mem.definitions**: Global registry where all definitions are stored and shared through the pipeline.

## 🧪 Examples
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
<img src="./additions.jpg">

## 🎯 Purpose
- 🛠️ Define custom items, blocks, and equipment using Python classes
- ⚙️ Configure automatic material generation (ores, ingots, tools, armor)
- 📦 Set up crafting recipes with typed classes
- 🔗 Establish relationships between items and their uses
- 🏷️ Configure item names, lore, and categories
- 🎨 Link items to their texture and model assets

## ⚙️ Configuration

### 🎯 Basic Setup Structure
This structure defines the lifecycle of your definitions plugin: generate content, normalize metadata, run required post-processing, and optionally export debug data.

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

Definition of the `Item` class properties:

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

Example using the `Item` class:

```python
from stewbeet import Item, Ingr, CraftingShapedRecipe, WikiButton

item = Item(
    id="magic_sword",                           # Required: unique identifier
    base_item="minecraft:iron_sword",           # Base Minecraft item (default: CUSTOM_ITEM_VANILLA)
    manual_category="equipment",                # Category for the manual
    recipes=[                                   # List of Recipe objects
        CraftingShapedRecipe(
            category="equipment",
            shape=["X", "X", "Y"],
            ingredients={"X": Ingr("minecraft:amethyst_shard"), "Y": Ingr("minecraft:stick")}
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
        "enchantments": {"minecraft:sharpness": 5},
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

### 🧱 Block Class

Custom blocks extend the `Item` class with block-specific properties:

```python
from stewbeet import Block, VanillaBlock, CraftingShapedRecipe, SmeltingRecipe, Ingr

block = Block(
    id="super_stone",
    vanilla_block=VanillaBlock(id="minecraft:cobblestone"),
    manual_category="blocks",
    recipes=[
        # Could have been shapeless, but just for example:
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
        # Item name, lore, and container will be auto-generated if missing
    }
)
```

#### **VanillaBlock Configuration**

`VanillaBlock` defines the vanilla block state StewBeet uses as the runtime anchor for your custom block behavior.

```python
@dataclass
class VanillaBlock:
    id: str                                          # Base vanilla block (e.g., "minecraft:cobblestone")
    contents: bool = False                           # For blocks using item frames without vanilla block
    block_facing: Literal[False, "player"] = False   # Rotate placed block based on player facing
    visual_facing: Literal["none", "player", "item_frame"] = "none"  # Visual entity orientation source
```

#### **NoSilkTouchDrop Configuration**

Defines custom drops when the block is broken without silk touch:

```python
@dataclass
class NoSilkTouchDrop:
    id: str                     # Item ID to drop (e.g., "raw_simplunium")
    count: dict | int = 1       # Drop count: int or {"min": 1, "max": 3}
```
```python
# Example usage
block = Block(
    id="simplunium_ore",
    vanilla_block=VanillaBlockForOres,
    no_silk_touch_drop=NoSilkTouchDrop(id="raw_simplunium", count={"min": 2, "max": 4})
)

# Or shorthand
block = Block(
    id="simplunium_ore",
    vanilla_block=VanillaBlockForOres,
    no_silk_touch_drop="raw_simplunium"  # Defaults to count=1
)

# Or dynamic drops with a direct beet LootTable
block = Block(
    id="simplunium_ore",
    vanilla_block=VanillaBlockForOres,
    no_silk_touch_drop=LootTable({
        "pools": [{
            "rolls": 1,
            "entries": [
                {"type": "minecraft:item", "name": "minecraft:raw_iron", "weight": 3},
                {"type": "minecraft:item", "name": "minecraft:iron_nugget", "weight": 7}
            ]
        }]
    })
)
```

#### **GrowingSeed Configuration**

For seeds that grow over time (like Stardust Seed from [Stardust Fragment](https://github.com/Stoupy51/StardustFragment)):

```python
@dataclass
class GrowingSeedLoot:
    id: str                     # Item ID to drop
    rolls: JsonDict | int = 1   # Roll definition or count
    fortune: JsonDict | None = None  # Fortune modifier

@dataclass
class GrowingSeed:
    texture_basename: str       # Base texture name (e.g., "stardust")
    seconds: int                # Growth time in seconds
    planted_on: str             # Block to plant on (e.g., "diamond_block")
    loots: list[GrowingSeedLoot] | str  # Loot list or loot table path
```
```python
# Example usage
seed = Block(
    id="stardust_seed",
    vanilla_block=VanillaBlock(id="minecraft:wheat"),
    no_silk_touch_drop=NoSilkTouchDrop(id="stardust_fragment", count=1),
    growing_seed=GrowingSeed(
        texture_basename="stardust",
        seconds=480,  # 8 minutes
        planted_on="diamond_block",
        loots=[
            GrowingSeedLoot(
                id="stardust_fragment",
                rolls={"type": "minecraft:uniform", "min": 3, "max": 9},
                fortune={"extra": 0, "probability": 0.5}
            )
        ]
    )
)
```

#### **`on_place` — Custom Placement Commands**

An optional string of Minecraft commands appended to `{ns}:custom_blocks/{id}/place_secondary`, executed **as the item display (or item frame) entity** right after the block is fully set up:

```python
block = Block(
    id="my_machine",
    vanilla_block=VanillaBlock(id="minecraft:furnace"),
    on_place="tag @s add my_ns.active\nscoreboard players set @s my_ns.energy 0"
)

# Multi-line strings work too
block = Block(
    id="stardust_seed",
    vanilla_block=VanillaBlock(id="minecraft:wheat"),
    on_place=(
        "tag @s add my_ns.seed\n"
        "scoreboard players add @s my_ns.growth_time 0"
    )
)
```

> **Note**: Commands run as the item_display entity, not the player. Use `execute as @p[tag={ns}.placer]` if you need to target the placing player.

#### **BlockAlternative and BlockHead**

Alternative block types for special placement methods:

```python
from stewbeet import BlockAlternative, BlockHead

# Using item frames (e.g., for machinery with no vanilla block)
servo = BlockAlternative(
    id="servo_inserter",
    vanilla_block=VanillaBlock(contents=True),  # No vanilla block, just item frame
    manual_category="machines"
)

# Using player heads (for custom heads)
custom_head = BlockHead(
    id="stoupy_head",
    vanilla_block=VanillaBlock(id="minecraft:player_head[profile={name:\"Stoupy51\"}]"),
    manual_category="decorations"
)
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
        width=2,                                        # Width in blocks
        height=2                                        # Height in blocks
    )
)
```

## 🍳 Recipe System

### 📋 Recipe Classes

StewBeet provides typed recipe classes for all Minecraft recipe types:

#### **⚔️ Crafting Shaped Recipe**
Use a shaped recipe when slot position matters; the `shape` maps symbols to ingredients and controls exact crafting layout.

```python
from stewbeet import CraftingShapedRecipe, Ingr

recipe = CraftingShapedRecipe(
    result_count=1,                            # Number of items produced
    group="tools",                             # Recipe book grouping
    category="equipment",                      # Recipe book category
    shape=["X X", " Y ", "X X"],               # 3x3 pattern
    ingredients={
        "X": Ingr("minecraft:iron_ingot"),
        "Y": Ingr("minecraft:stick")
    }
)
```

#### **🎯 Crafting Shapeless Recipe**
Use a shapeless recipe when only ingredient presence matters, regardless of placement order in the crafting grid.

```python
recipe = CraftingShapelessRecipe(
    result_count=4,
    category="building_blocks",
    ingredients=[Ingr("minecraft:oak_wood"), Ingr("minecraft:oak_log"),
                 Ingr("minecraft:oak_log"), Ingr("minecraft:oak_wood")]
    # Can also use: ingredients=(2*[Ingr("minecraft:oak_wood")] + 2*[Ingr("minecraft:oak_log"])
)
```

#### **🔥 Smelting Recipe**
Smelting recipes model furnace-like transformations with controlled time, XP reward, and one input-to-output conversion.

```python
recipe = SmeltingRecipe(
    result_count=1,
    cookingtime=200,        # Ticks (200 = 10 seconds)
    experience=0.7,
    category="misc",
    ingredient=Ingr("ruby_ore"),
    result=Ingr("ruby")
)
```

#### **⚡ Other Recipe Types**
StewBeet exposes typed wrappers for specialized vanilla recipe systems so each mechanic can be configured explicitly.

```python
# Blasting Furnace (faster smelting)
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
Ingr("tin_ingot", ns="mechanization")
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
                "mining_efficiency": 2               # +20% mining speed for tools
            }
        ),
        "minecraft:stone": None,    # Auto-detect from textures (e.g., stone_stick, stone_rod, etc.)
    }
    
    # Generates: steel_ingot, steel_pickaxe, steel_axe, steel_shovel, 
    # steel_sword, steel_hoe, steel_helmet, steel_chestplate, 
    # steel_leggings, steel_boots, steel_block, raw_steel, raw_steel_block, etc.
    generate_everything_about_these_materials(ORES_CONFIGS)
    
    # Configure custom blocks after generation
    # ⚠️ We use Block.from_id() to access existing definitions and modify them
    Block.from_id("steel_block").vanilla_block = VanillaBlock(id="minecraft:iron_block")
    Block.from_id("raw_steel_block").vanilla_block = VanillaBlock(id="minecraft:raw_iron_block")
```

### 🧪 Equipment Configuration

`EquipmentsConfig` controls how generated material families inherit base stats and how custom modifiers are applied across tools and armor.

```python
class EquipmentsConfig:
    equivalent_to: DefaultOre                   # Base material (WOOD, STONE, GOLD, IRON, DIAMOND, NETHERITE, COPPER, CHAINMAIL, LEATHER)
    pickaxe_durability: float | int = 0         # Custom durability (0 = use vanilla equivalent)
    attributes: dict[str, float] | None = None  # Stat modifiers to ADD (not override)
    ignore_recipes: bool = False                # Skip automatic recipe generation
```

**Common attribute modifiers:**
- `"attack_damage": 1.0` → +1 attack damage for weapons (e.g., diamond pickaxe: 5 → 6)
- `"armor": 0.5` → +0.5 armor for each armor piece
- `"armor_toughness": 1.0` → +1 armor toughness for armor pieces
- `"mining_efficiency": 2` → +20% mining speed for tools
- `"knockback_resistance": 0.1` → +0.1 knockback resistance (applied to armor only)

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

Music disc generation maps `.ogg` assets to definitions so sounds, items, and references stay synchronized automatically.

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

These helpers finalize definitions so generated output remains consistent, namespaced correctly, and ready for downstream plugins.

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

Common categories for manual organization (but it's always up to you!):

| Category | Description |
|----------|-------------|
| `"materials"` | Raw materials, ingots, gems |
| `"equipment"` | Tools, weapons, armor |
| `"blocks"` | Building blocks, decorative blocks |
| `"miscellaneous"` | Other items, special items |
| `"food"` | Consumable items |
| `"decorations"` | Paintings, decorative items |

## ✨ Advanced Features

### 🎨 Texture Integration
Items automatically detect textures by name from `assets/textures/`:
- `steel_ingot.png` → `steel_ingot` item
- `steel_pickaxe.png` → `steel_pickaxe` tool
- `steel_block.png` → `steel_block` custom block

### 🔗 Accessing Existing Items

`Item.from_id` lets you fetch and mutate previously declared definitions, enabling staged configuration without re-creating objects.

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

### 🎨 Complex Model Examples

#### **Recognized Texture Patterns**

StewBeet automatically recognizes texture patterns and generates appropriate models:

**Block Patterns:**
- **`cube_all`**: Single texture (e.g., `my_block.png`)
- **`cake`**: bottom, side, top, inner (e.g., `my_cake_bottom.png`, `my_cake_side.png`, `my_cake_top.png`, `my_cake_inner.png`)
- **`orientable_with_bottom`**: front, bottom, side, top (e.g., `furnace_front.png`, `furnace_bottom.png`, `furnace_side.png`, `furnace_top.png`)
- **`cube_bottom_top`**: bottom, side, top (e.g., `barrel_bottom.png`, `barrel_side.png`, `barrel_top.png`)
- **`orientable`**: front, side, top (e.g., `dropper_front.png`, `dropper_side.png`, `dropper_top.png`)
- **`cube_column`**: end, side (e.g., `pillar_end.png`, `pillar_side.png`)

**Item Patterns:**
- **`leather_armor`**: Items starting with `leather_` automatically use layer1 for overlay coloring
- **`overlay`**: Items with `_overlay` texture (e.g., `my_item.png` + `my_item_overlay.png` → layer0 + layer1)
- **`bow_pulling`**: Bow items with `_pulling_0`, `_pulling_1`, `_pulling_2`, etc. (sorted numerically)
- **`spear_in_hand`**: Spears ending with `_spear` + `_in_hand` texture variant (uses display context switching)

**Powered States:**
- Any block/item can have `_on` variants (e.g., `furnace_front.png` + `furnace_front_on.png`)
- StewBeet automatically generates both states if `_on` textures are detected

#### **Multiple States (On/Off, Facing)**

Example from SimplEnergy's Electric Furnace with on/off states and directional facing:

```python
from stewbeet import Block, VanillaBlock, CraftingShapedRecipe, Ingr

# Create the electric furnace block
electric_furnace = Block(
    id="electric_furnace",
    vanilla_block=VanillaBlock(
        id="minecraft:furnace",
        block_facing="player"  # Enables directional variants (north, east, south, west)
    ),
    manual_category="energy",
    recipes=[
        CraftingShapedRecipe(
            category="misc",
            shape=["LLL", "LML", "III"],
            ingredients={
                "L": Ingr("minecraft:lapis_lazuli"),
                "M": Ingr("machine_block"),
                "I": Ingr("minecraft:iron_block")
            }
        )
    ],
    components={
        "item_name": {"text": "Electric Furnace", "color": "aqua"},
        "custom_data": {"energy": {"usage": 20, "max_storage": 1600}}
    }
)

# StewBeet automatically detects block model patterns from texture names:
# Required textures: electric_furnace_front.png, electric_furnace_side.png, electric_furnace_top.png, electric_furnace_bottom.png
# Optional for on state: electric_furnace_front_on.png (other sides can also have _on variants)
# Pattern recognized: "orientable_with_bottom" (front, side, top, bottom)
# Other supported patterns: "orientable" (front, side, top), "cube_bottom_top" (bottom, side, top), "cube_column" (end, side)
```

#### **Animated Item Models (Bow Pulling)**

Example with bow pulling animations:

```python
from stewbeet import Item, Ingr, CraftingShapedRecipe

custom_bow = Item(
    id="super_bow",
    base_item="minecraft:bow",
    manual_category="equipment",
    recipes=[
        CraftingShapedRecipe(
            category="equipment",
            shape=[" XY", "X Y", " XY"],
            ingredients={"X": Ingr("minecraft:stick"), "Y": Ingr("minecraft:string")}
        )
    ],
    components={
        "item_name": {"text": "Super Bow", "color": "gold"},
        "max_damage": 500
    }
)

# StewBeet auto-generates pulling animation models and item_model JSON files:
# Required textures in assets/textures/item/:
# - super_bow.png (base bow texture)
# - super_bow_pulling_0.png (slightly pulled)
# - super_bow_pulling_1.png (half pulled)  
# - super_bow_pulling_2.png (fully pulled)
# 
# Generated files:
# - assets/models/item/super_bow_pulling_0.json, super_bow_pulling_1.json, super_bow_pulling_2.json
# - assets/items/super_bow.json (with condition and range_dispatch for pull states)
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

