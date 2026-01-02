
# 📝 StewBeet Writing to Files Guide

📄 **Example File**: [extensive/src/link.py](../../templates/extensive/src/link.py) 🔗<br>
📄 **Real-world Example**: [SimplEnergy/src/utils/machines.py](https://github.com/Stoupy51/SimplEnergy/blob/main/src/utils/machines.py) 🔗<br>
📄 **Real-world Example**: [StardustFragment/src/utils/remaining.py](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py) 🔗<br>

## 🔗 Dependencies
- **✅ Required**: StewBeet I/O utilities (`from stewbeet import write_function, write_load_file, ...`)
- **📍 Position**: Called after definitions setup, typically in the middle of the pipeline
- **🔄 Integration**: Works with all file types (functions, advancements, tags, etc.)

## 📋 Overview
Writing to files is essential for generating datapacks and resource packs. StewBeet provides three approaches for file writing, each with different use cases and complexity levels. This guide covers static file loading via configuration, native beet API, and StewBeet's streamlined helper functions.

**File writing typically happens in user plugins after definitions are set up but before finalization.**

## 🎯 Purpose
- 📁 Load static files from directories (pre-plugin via `beet.yml`)
- ✍️ Generate dynamic functions, advancements, and tags programmatically
- 🔄 Append, prepend, or overwrite file content
- 📦 Organize datapack logic across multiple files
- 🏷️ Manage function tags and other tag types
- ⏰ Set up clock functions (tick, second, minute)

## 🎨 Three Approaches to Writing Files

### 🗂️ Approach 1: Static File Loading (beet.yml)

The simplest approach - load pre-written files from directories **before any plugins run**.

```yaml
# In beet.yml
data_pack:
    name: "datapack"
    load: ["src"]  # Loads all .mcfunction and .json files from src/

resource_pack:
    name: resource_pack
    load: ["src"]  # Loads all texture, model, and sound files from src/
```

**How it works:**
- Place `.mcfunction` files in `src/data/<namespace>/function/`
- Place `.json` files in `src/data/<namespace>/advancement/`, `src/data/<namespace>/recipe/`, etc.
- Beet automatically loads them into the correct pack locations
- Files are loaded **before** any plugin code runs

**Example structure:**
```
src/
├── data/
│   └── my_namespace/
│       ├── function/
│       │   ├── load.mcfunction
│       │   └── tick.mcfunction
│       ├── advancement/
│       │   └── my_advancement.json
│       └── recipe/
│           └── my_recipe.json
└── assets/
    └── my_namespace/
        └── textures/
            └── item/
                └── my_item.png
```

**✅ Use when:**
- You have static files that don't need dynamic generation
- You're organizing pre-written commands and data
- You want simple, straightforward file structure

**❌ Don't use when:**
- You need to generate content based on definitions
- You need to combine multiple sources of data
- You need conditional file generation

---

### 🔧 Approach 2: Native Beet API

Use beet's native object-oriented API to write files programmatically in plugins.

```python
from beet import Context, Function, Advancement, FunctionTag
from beet.core.utils import JsonDict

def beet_default(ctx: Context):
    # Writing a function
    ctx.data["my_namespace"].functions["my_folder/my_function"] = Function("""
# This is my function
say Hello World!
scoreboard players add @a points 1
""")
    
    # Writing an advancement
    advancement_data: JsonDict = {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": "my_namespace:rewards/give_item"
        }
    }
    ctx.data["my_namespace"].advancements["my_advancement"] = Advancement(advancement_data)
    
    # Writing a function tag
    tag_data: JsonDict = {
        "values": [
            "my_namespace:my_folder/my_function",
            "my_namespace:another_function"
        ]
    }
    ctx.data["my_namespace"].function_tags["minecraft:load"] = FunctionTag(tag_data)
```

**✅ Use when:**
- You need full control over file objects
- You're working with complex nested structures
- You want type safety with beet's object model

**❌ Don't use when:**
- You want simple, quick file writes
- You're dealing with many small functions
- You need automatic path handling

---

### 🚀 Approach 3: StewBeet Helper Functions (Recommended)

StewBeet provides streamlined helper functions that simplify file writing with automatic handling of common patterns.

```python
from stewbeet import write_function, write_load_file, write_tick_file, Mem

def beet_default(ctx: Context):
    ns = ctx.project_id
    
    # Write a simple function
    write_function(f"{ns}:my_folder/my_function", """
# This is my function
say Hello World!
scoreboard players add @a points 1
""")
    
    # Append to load file (runs when datapack loads)
    write_load_file("""
# Initialize scoreboards
scoreboard objectives add points dummy
scoreboard objectives add data dummy
""")
    
    # Append to tick file (runs every game tick)
    write_tick_file("""
# Check for players with high scores
execute as @a[scores={points=100..}] run function my_namespace:rewards/high_score
""")
    
    # Write versioned functions (automatic clock)
    write_versioned_function("second", """
# Runs every second (20 ticks)
execute as @a run title @s actionbar {"score":{"name":"@s","objective":"points"}}
""")
    
    write_versioned_function("minute", """
# Runs every minute (1200 ticks)
say One minute has passed!
""")
```

**✅ Use when:**
- You want simple, readable code
- You need automatic path management
- You're using StewBeet's conventions (versioned functions, load/tick files)
- You want to append/prepend content easily

**❌ Don't use when:**
- You need non-standard file organization
- You're not using StewBeet framework

---

## 📚 StewBeet Helper Functions Reference

### 🏆 Function Writing

#### `write_function()`
Write content to a function file.

```python
def write_function(
    path: str,                      # Function path (e.g., "namespace:folder/function_name")
    content: str,                   # The content to write
    overwrite: bool = False,        # Overwrite instead of appending
    prepend: bool = False,          # Prepend instead of appending
    tags: list[str] | None = None   # Function tags to add (e.g., ["minecraft:load"])
) -> None:
```

**Example:**
```python
write_function(f"{ns}:utils/teleport_spawn", """
# Teleport player to spawn
tp @s 0 64 0
""")
```

---

#### `read_function()`
Read the content of an existing function.

```python
def read_function(
    path: str  # Function path (e.g., "namespace:folder/function_name")
) -> str:
```

**Example:**
```python
existing_content = read_function(f"{ns}:my_function")
modified_content = existing_content.replace("say Hello", "say Goodbye")
write_function(f"{ns}:my_function", modified_content, overwrite=True)
```

---

#### `write_load_file()`
Write content to the main load function (runs when datapack loads).

```python
def write_load_file(
    content: str,                   # The content to write
    overwrite: bool = False,        # Overwrite instead of appending
    prepend: bool = False,          # Prepend instead of appending
    tags: list[str] | None = None   # Additional tags to add
) -> None:
```

**Path:** `namespace:v{version}/load/confirm_load`

**Example:**
```python
# Prepend initialization code (runs first)
write_load_file("""
# Initialize core scoreboards
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)

# Append setup code (runs after prepended content)
write_load_file("""
# Set default values
scoreboard players set #2 data 2
scoreboard players set #100 data 100
""")
```

---

#### `write_tick_file()`
Write content to the main tick function (runs every game tick - 20 times per second).

```python
def write_tick_file(
    content: str,                   # The content to write
    overwrite: bool = False,        # Overwrite instead of appending
    prepend: bool = False,          # Prepend instead of appending
    tags: list[str] | None = None   # Additional tags to add
) -> None:
```

**Path:** `namespace:v{version}/tick`

**Example:**
```python
write_tick_file("""
# Increment timer
scoreboard players add #global_timer data 1

# Reset every minute
execute if score #global_timer data matches 1200.. run scoreboard players set #global_timer data 0
""")
```

---

#### `write_versioned_function()`
Write content to a versioned clock function.

```python
def write_versioned_function(
    path: str,                      # Function path WITHOUT namespace (e.g., "second", "tick_2")
    content: str,                   # The content to write
    overwrite: bool = False,        # Overwrite instead of appending
    prepend: bool = False,          # Prepend instead of appending
    tags: list[str] | None = None   # Additional tags to add
) -> None:
```

**Path:** `namespace:v{version}/{path}`

**Common clock functions:**
| Path | Frequency | Ticks | Description |
|------|-----------|-------|-------------|
| `tick` | Every tick | 1 | Runs with main tick file |
| `tick_2` | Every 2 ticks | 2 | Half-tick speed (10 times/second) |
| `second` | Every second | 20 | Once per second |
| `second_5` | Every 5 seconds | 100 | Good for periodic checks |
| `minute` | Every minute | 1200 | For rare updates |

**Example:**
```python
# Runs every second
write_versioned_function("second", """
# Regenerate health for players with regen effect
execute as @a[nbt={active_effects:[{id:"minecraft:regeneration"}]}] run effect give @s instant_health 1 0 true
""")

# Runs every 5 seconds
write_versioned_function("second_5", """
# Spawn particles at marker entities
execute at @e[type=marker,tag=particle_source] run particle flame ~ ~ ~ 0.5 0.5 0.5 0.01 10
""")

# Runs every minute
write_versioned_function("minute", """
# Clean up old items
kill @e[type=item,nbt={Age:5400s}]
""")
```

---

### 🏅 Advancement Writing

#### `write_advancement()`
Write an advancement file.

```python
def write_advancement(
    path: str,                              # Advancement path (e.g., "namespace:folder/name")
    advancement: Advancement | JsonDict,    # Advancement data or object
    overwrite: bool = False,                # Overwrite instead of merging
    max_level: int = -1                     # JSON nesting depth (-1 = unlimited)
) -> None:
```

**Example:**
```python
# Technical advancement (hidden from players)
write_advancement(f"{ns}:technical/inventory_changed", {
    "criteria": {
        "requirement": {
            "trigger": "minecraft:inventory_changed"
        }
    },
    "rewards": {
        "function": f"{ns}:advancements/check_inventory"
    }
})

# Visible advancement
write_advancement(f"{ns}:story/craft_ruby_sword", {
    "display": {
        "icon": {"id": "minecraft:diamond_sword", "components": {"custom_data": {ns: {"ruby_sword": True}}}},
        "title": {"text": "Legendary Blade", "color": "red"},
        "description": {"text": "Craft a Ruby Sword"},
        "frame": "challenge",
        "show_toast": True,
        "announce_to_chat": True
    },
    "parent": f"{ns}:story/mine_ruby",
    "criteria": {
        "requirement": {
            "trigger": "minecraft:recipe_unlocked",
            "conditions": {
                "recipe": f"{ns}:ruby_sword"
            }
        }
    }
})
```

---

### 🏷️ Tag Writing

#### `write_tag()`
Write a tag file (generic for any tag type).

```python
def write_tag(
    path: str,                                  # Tag path (e.g., "namespace:my_tag")
    tag_type: NamespaceProxy | NamespaceContainer,  # Tag type (e.g., ctx.data.function_tags)
    values: list[Any] | None = None,           # Values to add to the tag
    prepend: bool = False,                      # Prepend instead of appending
    max_level: int | None = None                # JSON nesting depth
) -> None:
```

**Example:**
```python
# Function tags
write_tag(f"{ns}:custom_load", Mem.ctx.data.function_tags, [
    f"{ns}:init/scoreboards",
    f"{ns}:init/teams"
])

# Entity type tags
write_tag(f"{ns}:hostile_mobs", Mem.ctx.data.entity_type_tags, [
    "minecraft:zombie",
    "minecraft:skeleton",
    "minecraft:spider"
])

# Block tags
write_tag(f"{ns}:mineable/pickaxe", Mem.ctx.data.block_tags, [
    f"{ns}:ruby_ore",
    f"{ns}:ruby_block"
])
```

---

#### `write_function_tag()`
Write a function tag (convenience wrapper for `write_tag`).

```python
def write_function_tag(
    path: str,                      # Tag path (e.g., "namespace:my_tag")
    functions: list[Any] | None = None,  # Function paths to add
    prepend: bool = False,          # Prepend instead of appending
    max_level: int | None = None    # JSON nesting depth
) -> None:
```

**Example:**
```python
# Add functions to minecraft:load
write_function_tag("minecraft:load", [
    f"{ns}:load/main"
])

# Add functions to minecraft:tick
write_function_tag("minecraft:tick", [
    f"{ns}:tick/main"
])

# Custom function tag
write_function_tag(f"{ns}:custom_blocks/tick", [
    f"{ns}:custom_blocks/furnace/tick",
    f"{ns}:custom_blocks/machine/tick"
])
```

---

### 🛠️ Utility Functions

#### `super_merge_dict()`
Recursively merge two dictionaries without modifying originals.

```python
def super_merge_dict(
    dict1: JsonDict,  # First dictionary
    dict2: JsonDict   # Second dictionary (overrides dict1)
) -> JsonDict:
```

**Example:**
```python
base_config = {
    "settings": {"power": 100, "speed": 5},
    "enabled": True
}

override_config = {
    "settings": {"power": 150},  # Override power, keep speed
    "debug": True                 # Add new field
}

merged = super_merge_dict(base_config, override_config)
# Result: {"settings": {"power": 150, "speed": 5}, "enabled": True, "debug": True}
```

---

#### `set_json_encoder()`
Set custom JSON encoder for pretty printing.

```python
def set_json_encoder(
    obj: JsonFileT,              # JsonFile object (Advancement, FunctionTag, etc.)
    max_level: int | None = None,  # Max nesting depth (None = unlimited)
    indent: str | int = '\t'      # Indentation character or spaces
) -> JsonFileT:
```

**Example:**
```python
from stewbeet import set_json_encoder
from beet import Advancement

advancement = Advancement({
    "criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}}
})

# Use tabs for indentation (default)
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement)

# Use 2 spaces
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement, indent=2)

# Limit nesting depth
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement, max_level=3)
```

---

#### `convert_to_serializable()`
Convert objects with `to_dict()` method to JSON-serializable forms.

```python
def convert_to_serializable(
    obj: Any  # Object to convert
) -> Any:
```

**Example:**
```python
from stewbeet import Item, convert_to_serializable

item = Item.from_id("ruby_sword")
serializable_data = convert_to_serializable(item)
# Now can be written to JSON
```

---

#### `texture_mcmeta()`
Create a Texture object with mcmeta file if it exists.

```python
def texture_mcmeta(
    source_path: str  # Path to texture file (e.g., "assets/textures/my_texture.png")
) -> Texture:
```

**Example:**
```python
from stewbeet import texture_mcmeta

# Automatically loads my_texture.png.mcmeta if it exists
texture = texture_mcmeta("assets/textures/animated_block.png")
Mem.ctx.assets["my_namespace"].textures["block/animated_block"] = texture
```

---

## 💡 Real-World Examples

### 📦 Example 1: Custom Block Ticking

Generate tick functions for custom blocks with different behaviors.

```python
from stewbeet import write_function, write_versioned_function, Mem

def setup_custom_blocks(ctx: Context):
    ns = ctx.project_id
    
    # Solar panel generates energy during daytime
    write_versioned_function("custom_blocks/solar_panel/second", """
# Check daylight level and generate energy
execute if predicate simplenergy:check_daylight_power run scoreboard players operation @s energy.storage += @s simplenergy.energy_rate
execute if score @s energy.storage > @s energy.max_storage run scoreboard players operation @s energy.storage = @s energy.max_storage
""")
    
    # Electric furnace smelts items using energy
    write_versioned_function("custom_blocks/electric_furnace/second", f"""
# Prevent vanilla cooking
data modify block ~ ~ ~ cooking_total_time set value -200s

# Check if has energy and items
execute if score @s energy.storage matches 20.. if data block ~ ~ ~ Items[{{Slot:0b}}] run function {ns}:custom_blocks/electric_furnace/process
""")
    
    write_function(f"{ns}:custom_blocks/electric_furnace/process", """
# Consume energy
scoreboard players remove @s energy.storage 20

# Cook item (will complete on next check)
data modify block ~ ~ ~ CookTime set value 199s
""")
```

---

### ⚡ Example 2: Machine State Management

Manage machine states with multiple functions.

```python
def setup_machine_states(ctx: Context):
    ns = ctx.project_id
    
    # Main machine tick
    write_function(f"{ns}:machines/processor/tick", f"""
# Check if machine should run
execute if score @s {ns}.power matches 100.. run function {ns}:machines/processor/running
execute unless score @s {ns}.power matches 100.. run function {ns}:machines/processor/idle
""")
    
    # Running state
    write_function(f"{ns}:machines/processor/running", f"""
# Consume power
scoreboard players remove @s {ns}.power 10

# Show running particles
particle electric_spark ~ ~0.5 ~ 0.2 0.2 0.2 0.01 5

# Process items
execute if predicate {ns}:has_input_item run function {ns}:machines/processor/process_item
""")
    
    # Idle state
    write_function(f"{ns}:machines/processor/idle", """
# Show idle particles
particle smoke ~ ~0.5 ~ 0.1 0.1 0.1 0.01 1
""")
    
    # Processing logic
    write_function(f"{ns}:machines/processor/process_item", f"""
# Remove input
item replace block ~ ~ ~ container.0 with air

# Give output
loot spawn ~ ~ ~ loot {ns}:items/processed_material
""")
```

---

### 🎯 Example 3: Advancement Triggers

Set up advancement-based detection system.

```python
def setup_advancement_triggers(ctx: Context):
    ns = ctx.project_id
    
    # Inventory changed trigger
    write_advancement(f"{ns}:technical/inventory_changed", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/check_inventory"
        }
    })
    
    write_function(f"{ns}:advancements/check_inventory", f"""
# Revoke advancement
advancement revoke @s only {ns}:technical/inventory_changed

# Check for custom items
execute if items entity @s container.* *[custom_data~{{{ns}:{{}}}}] run function {ns}:items/handle_custom_item
""", prepend=True)
    
    # Item used trigger (for right-click detection)
    write_advancement(f"{ns}:technical/used_item", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:using_item",
                "conditions": {
                    "item": {
                        "predicates": {
                            "custom_data": {ns: {}}
                        }
                    }
                }
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/item_used"
        }
    })
    
    write_function(f"{ns}:advancements/item_used", f"""
advancement revoke @s only {ns}:technical/used_item
function {ns}:items/right_click_handler
""")
```

---

### 🔄 Example 4: Programmatic Function Generation

Generate multiple similar functions automatically.

```python
def generate_tier_functions(ctx: Context):
    ns = ctx.project_id
    
    # Generate functions for each tier
    tiers = {
        "basic": {"power": 10, "speed": 100, "color": "gray"},
        "advanced": {"power": 25, "speed": 50, "color": "blue"},
        "elite": {"power": 50, "speed": 25, "color": "purple"}
    }
    
    for tier_name, tier_data in tiers.items():
        # Generate upgrade function
        write_function(f"{ns}:machines/{tier_name}/upgrade", f"""
# Set tier stats
scoreboard players set @s {ns}.power {tier_data['power']}
scoreboard players set @s {ns}.speed {tier_data['speed']}

# Show upgrade message
tellraw @s {{"text":"Upgraded to {tier_name.title()} Tier!","color":"{tier_data['color']}"}}
""")
        
        # Generate operation function
        write_function(f"{ns}:machines/{tier_name}/operate", f"""
# Check power requirement
execute if score @s {ns}.energy matches {tier_data['power']}.. run function {ns}:machines/{tier_name}/process

# Show status
title @s actionbar {{"text":"Power: ","color":"gray","extra":[{{"score":{{"name":"@s","objective":"{ns}.energy"}}}}]}}
""")
```

---

### 📊 Example 5: Complex Load Setup

Initialize complete datapack systems on load.

```python
def setup_load_system(ctx: Context):
    ns = ctx.project_id
    
    # Prepend early initialization (runs first)
    write_load_file("""
# Create core scoreboards
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)
    
    # Main initialization
    write_load_file(f"""
# Create game-specific scoreboards
scoreboard objectives add {ns}.energy dummy
scoreboard objectives add {ns}.power dummy
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick

# Set constants
scoreboard players set #2 data 2
scoreboard players set #10 data 10
scoreboard players set #100 data 100
scoreboard players set #1000 data 1000

# Create teams
team add {ns}.green
team add {ns}.gold
team add {ns}.aqua
team modify {ns}.green color green
team modify {ns}.gold color gold
team modify {ns}.aqua color aqua

# Initialize storage
data modify storage {ns}:main config set value {{}}
data modify storage {ns}:main temp set value {{}}
""")
    
    # Load custom modules
    write_load_file(f"""
# Load module systems
function {ns}:modules/energy/load
function {ns}:modules/machines/load
function {ns}:modules/items/load
""")
```

---

### 🎮 Example 6: Right-Click Detection System

Complete right-click detection using custom items.

```python
def setup_right_click_detection(ctx: Context):
    ns = ctx.project_id
    
    # Create detection scoreboard on load
    write_load_file(f"""
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick
""")
    
    # Check for right-clicks every tick
    write_tick_file(f"""
# Detect right-clicks
execute as @a[scores={{{ns}.right_click=1..}}] run function {ns}:items/right_click_handler
""")
    
    # Main right-click handler
    write_function(f"{ns}:items/right_click_handler", f"""
# Reset score
scoreboard players set @s {ns}.right_click 0

# Check which item was used
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{wrench:true}}}}] run function {ns}:items/wrench/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{teleporter:true}}}}] run function {ns}:items/teleporter/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{scanner:true}}}}] run function {ns}:items/scanner/use
""")
    
    # Individual item handlers
    write_function(f"{ns}:items/wrench/use", """
# Rotate the block player is looking at
execute anchored eyes positioned ^ ^ ^1 align xyz positioned ~0.5 ~ ~0.5 as @e[type=item_display,tag=custom_block,distance=..1,limit=1,sort=nearest] run function simplenergy:items/wrench/rotate_block
""")
```

---

### 🌟 Example 7: Growing Crops System

Implement custom growing mechanics.

```python
def setup_growing_system(ctx: Context):
    ns = ctx.project_id
    
    # Check growth every 5 seconds
    write_versioned_function("second_5", f"""
# Update growing crops
execute as @e[type=item_display,tag={ns}.growing_crop] at @s run function {ns}:crops/check_growth
""")
    
    # Growth check function
    write_function(f"{ns}:crops/check_growth", f"""
# Increment growth timer
scoreboard players add @s {ns}.growth_time 5

# Check if fully grown
execute if score @s {ns}.growth_time >= @s {ns}.growth_required run function {ns}:crops/fully_grown

# Visual feedback (random particle)
execute if predicate {ns}:random/0.3 run particle happy_villager ~ ~0.3 ~ 0.2 0.2 0.2 0 1
""")
    
    # Fully grown handler
    write_function(f"{ns}:crops/fully_grown", f"""
# Update model to grown state
data modify entity @s item.components."minecraft:item_model" set value "{ns}:block/crop_grown"

# Add grown tag
tag @s add {ns}.crop_grown
tag @s remove {ns}.growing_crop

# Play sound
playsound minecraft:block.crop.break block @a ~ ~ ~ 1 1.2
""")
    
    # Harvesting
    write_function(f"{ns}:crops/harvest", f"""
# Drop items
loot spawn ~ ~ ~ loot {ns}:crops/harvest_crop

# Remove entity
kill @s

# Play sound
playsound minecraft:block.crop.break block @a ~ ~ ~ 1 0.8
""")
```

---

### 📜 Example 8: Tag Management

Organize functions and entities with tags.

```python
def setup_tags(ctx: Context):
    ns = ctx.project_id
    
    # Add to minecraft:load
    write_function_tag("minecraft:load", [
        f"{ns}:v{ctx.project_version}/load/main"
    ])
    
    # Add to minecraft:tick
    write_function_tag("minecraft:tick", [
        f"{ns}:v{ctx.project_version}/tick"
    ])
    
    # Custom function tags for organization
    write_function_tag(f"{ns}:custom_blocks/tick", [
        f"{ns}:custom_blocks/solar_panel/tick",
        f"{ns}:custom_blocks/electric_furnace/tick",
        f"{ns}:custom_blocks/battery/tick"
    ])
    
    write_function_tag(f"{ns}:machines/process", [
        f"{ns}:machines/crusher/process",
        f"{ns}:machines/smelter/process",
        f"{ns}:machines/assembler/process"
    ])
    
    # Entity type tags
    write_tag("mob_grinder_blacklist", Mem.ctx.data.entity_type_tags, [
        "minecraft:warden",
        "minecraft:ender_dragon",
        "minecraft:wither"
    ])
    
    write_tag("machines", Mem.ctx.data.entity_type_tags, [
        "minecraft:item_display",
        "minecraft:interaction"
    ])
    
    # Block tags
    write_tag(f"minecraft:mineable/pickaxe", Mem.ctx.data.block_tags, [
        f"{ns}:ruby_ore",
        f"{ns}:ruby_block",
        f"{ns}:steel_block"
    ])
    
    write_tag(f"{ns}:machines", Mem.ctx.data.block_tags, [
        "minecraft:furnace",
        "minecraft:barrel",
        "minecraft:dropper"
    ])
```

---

## 🚨 Best Practices

### ✅ Do's

**File Organization:**
- Use meaningful folder structures (e.g., `machines/`, `items/`, `utils/`)
- Group related functions together
- Use versioned paths for datapack updates
- Separate logic into small, reusable functions

**Naming Conventions:**
- Technical advancements: `namespace:technical/trigger_name`
- Visible advancements: `namespace:story/achievement_name`
- Custom blocks: `namespace:custom_blocks/block_name/action`
- Utilities: `namespace:utils/category/function_name`
- Private functions: `namespace:private/function_name`

**Code Quality:**
- Use f-strings for dynamic paths: `f"{ns}:folder/{item}"`
- Use multi-line strings (triple quotes) for command content
- Add descriptive comments in generated functions
- Use `prepend=True` for initialization code in load files

**Performance:**
- Use versioned functions (second, second_5, minute) instead of tick when possible
- Batch operations together in single functions
- Use predicates instead of complex execute conditions
- Avoid unnecessary function calls in tick

**StewBeet Conventions:**
- Always use `Mem.ctx.project_id` for namespace
- Use `write_load_file()` for initialization
- Use `write_versioned_function()` for clock functions
- Call StewBeet helpers instead of direct beet API when available

### ❌ Don'ts

**File Management:**
- Don't hardcode namespace strings (use `ctx.project_id` or `ns` variable)
- Don't mix static files with dynamic generation for the same path
- Don't overwrite files unless intentional
- Don't create circular function calls (infinite loops)

**Code Quality:**
- Don't use `ctx.data["namespace"].functions["path"]` when StewBeet helpers exist
- Don't forget to handle edge cases (empty checks, score limits)
- Don't write monolithic functions (break into smaller pieces)
- Don't duplicate code across multiple functions

**Performance:**
- Don't run expensive operations in tick file
- Don't create functions that call themselves recursively without limits
- Don't use many small functions when one would suffice
- Don't check complex conditions every tick

**Organization:**
- Don't mix different concerns in same function
- Don't use generic names like `temp`, `test`, `function`
- Don't nest folders too deeply (3-4 levels max)
- Don't create files that are never called

---

## 🎯 Complete Example

Here's a complete example combining all approaches:

```python
# src/link.py
from beet import Context
from stewbeet import (
    write_function,
    write_load_file,
    write_tick_file,
    write_versioned_function,
    write_advancement,
    write_function_tag,
    write_tag,
    Mem,
    Item,
)

def beet_default(ctx: Context):
    ns = ctx.project_id
    
    # === LOAD SYSTEM ===
    
    # Early initialization (runs first)
    write_load_file("""
# Core scoreboards
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)
    
    # Main initialization
    write_load_file(f"""
# Game scoreboards
scoreboard objectives add {ns}.energy dummy
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick

# Constants
scoreboard players set #20 data 20
scoreboard players set #100 data 100

# Teams
team add {ns}.green
team modify {ns}.green color green

# Storage
data modify storage {ns}:main config set value {{}}
""")
    
    # === TICK SYSTEM ===
    
    # Main tick
    write_tick_file(f"""
# Right-click detection
execute as @a[scores={{{ns}.right_click=1..}}] run function {ns}:items/right_click_handler

# Custom block updates
execute as @e[type=item_display,tag={ns}.custom_block] at @s run function {ns}:custom_blocks/tick
""")
    
    # === VERSIONED FUNCTIONS (CLOCK) ===
    
    # Every second
    write_versioned_function("second", f"""
# Energy generation
execute as @e[type=item_display,tag={ns}.generator] at @s run function {ns}:machines/generator/generate

# Update displays
execute as @a run title @s actionbar {{"score":{{"name":"@s","objective":"{ns}.energy"}}}}
""")
    
    # Every 5 seconds
    write_versioned_function("second_5", f"""
# Crop growth
execute as @e[type=item_display,tag={ns}.growing] at @s run function {ns}:crops/grow_check

# Cleanup old markers
kill @e[type=marker,tag={ns}.temp,nbt={{Age:100s}}]
""")
    
    # Every minute
    write_versioned_function("minute", """
# Cleanup old items
kill @e[type=item,nbt={Age:5400s}]

# Save statistics
function simplenergy:utils/save_stats
""")
    
    # === CUSTOM FUNCTIONS ===
    
    # Right-click handler
    write_function(f"{ns}:items/right_click_handler", f"""
# Reset score
scoreboard players set @s {ns}.right_click 0

# Check item type
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{wrench:true}}}}] run function {ns}:items/wrench/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{battery:true}}}}] run function {ns}:items/battery/use
""")
    
    # Wrench usage
    write_function(f"{ns}:items/wrench/use", f"""
# Rotate block
execute anchored eyes positioned ^ ^ ^3 align xyz positioned ~0.5 ~ ~0.5 as @e[type=item_display,tag={ns}.custom_block,distance=..1,limit=1] run function {ns}:items/wrench/rotate

# Play sound
playsound minecraft:block.metal.hit player @s ~ ~ ~ 1 1.5
""")
    
    # Generator logic
    write_function(f"{ns}:machines/generator/generate", f"""
# Check fuel
execute unless score @s {ns}.fuel matches 1.. run return 0

# Consume fuel
scoreboard players remove @s {ns}.fuel 1

# Generate energy
scoreboard players add @s {ns}.energy 10

# Cap at max
execute if score @s {ns}.energy > @s {ns}.energy_max run scoreboard players operation @s {ns}.energy = @s {ns}.energy_max

# Particles
particle flame ~ ~0.5 ~ 0.2 0.3 0.2 0.01 5
""")
    
    # === ADVANCEMENTS ===
    
    # Inventory change trigger
    write_advancement(f"{ns}:technical/inventory_changed", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/check_inventory"
        }
    })
    
    write_function(f"{ns}:advancements/check_inventory", f"""
advancement revoke @s only {ns}:technical/inventory_changed
execute if items entity @s container.* *[custom_data~{{{ns}:{{}}}}] run function {ns}:items/detect_custom
""")
    
    # Visible achievement
    ruby_sword = Item.from_id("ruby_sword")
    write_advancement(f"{ns}:story/craft_ruby_sword", {
        "display": {
            "icon": ruby_sword.vanilla_item_components(),
            "title": {"text": "Legendary Blade", "color": "red"},
            "description": {"text": "Craft a Ruby Sword"},
            "frame": "challenge"
        },
        "criteria": {
            "requirement": {
                "trigger": "minecraft:recipe_crafted",
                "conditions": {
                    "recipe_id": f"{ns}:ruby_sword"
                }
            }
        }
    })
    
    # === FUNCTION TAGS ===
    
    # Add to minecraft:load
    write_function_tag("minecraft:load", [
        f"{ns}:v{ctx.project_version}/load/main"
    ])
    
    # Custom function tags
    write_function_tag(f"{ns}:machines/tick", [
        f"{ns}:machines/generator/tick",
        f"{ns}:machines/battery/tick",
        f"{ns}:machines/crusher/tick"
    ])
    
    # === ENTITY/BLOCK TAGS ===
    
    write_tag("machines", Mem.ctx.data.entity_type_tags, [
        "minecraft:item_display",
        "minecraft:interaction"
    ])
    
    write_tag(f"minecraft:mineable/pickaxe", Mem.ctx.data.block_tags, [
        f"{ns}:ruby_ore",
        f"{ns}:steel_block"
    ])
```

---

## 📖 Summary

### **Three Approaches Comparison**

| Approach | Use Case | Complexity | Flexibility |
|----------|----------|------------|-------------|
| **Static Files (beet.yml)** | Pre-written files | ⭐ Simple | ⭐ Low |
| **Native Beet API** | Full control | ⭐⭐⭐ Complex | ⭐⭐⭐ High |
| **StewBeet Helpers** | Dynamic generation | ⭐⭐ Medium | ⭐⭐ Medium-High |

### **When to Use Each**

- 📁 **Static Files**: Configuration files, static recipes, simple functions
- 🔧 **Native Beet API**: Complex nested structures, custom file types, advanced control
- 🚀 **StewBeet Helpers**: Most datapack logic, dynamic functions, standard patterns

### **Key Takeaways**

✅ Start with static files for simple content<br>
✅ Use StewBeet helpers for dynamic datapack logic<br>
✅ Use native beet API only when helpers don't cover your needs<br>
✅ Organize functions into logical folders<br>
✅ Use versioned functions for periodic tasks<br>
✅ Follow naming conventions for consistency<br>

**🎉 Master these file writing approaches to create efficient, maintainable datapacks with StewBeet!**<br>
Check the real-world examples at the top of this page to see these patterns in action! 🚀

