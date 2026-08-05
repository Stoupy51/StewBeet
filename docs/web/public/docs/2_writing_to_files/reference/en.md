# Helper function reference

Every helper StewBeet adds on top of beet for writing datapack files, with the arguments each
one takes.

**See also** [Writing functions and files](../en.md) for choosing between the three approaches,
and [the cookbook](../cookbook/en.md) for worked examples.

### Function Writing

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
""", tags=[f"{ns}:tp_spawn"])
```
Function will be written to `data/your_namespace/functions/utils/teleport_spawn.mcfunction`, and added to the `your_namespace:tp_spawn` function tag.

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

#### Prefer Resource accessors over hardcoded paths

Whenever the path belongs to a definition, take it from the `Item`/`Block` instead of retyping the convention.
A `Resource` is a string, so it drops straight into any of these functions:

```python
furnace = Block.from_id("electric_furnace")

# ❌ Hardcoded — silently breaks if the convention ever changes
write_function(f"{ns}:custom_blocks/electric_furnace/tick", "...")

# ✅ Derived from the definition
write_function(furnace.functions.tick, "...")

# ✅ Equivalent, without the definition lookup (BlockFunctions builds the same paths)
write_function(BlockFunctions("electric_furnace").tick, "...")

# ✅ Appending to a function that already exists? Grab the beet Function via .obj:
furnace.functions.place_secondary.obj.append("tag @s add my_ns.active")
# (raises KeyError if the function hasn't been generated yet — a loud failure
#  instead of your commands silently landing before the block setup)

# Works the same for loot tables, models, textures, advancements
write_function(f"{ns}:give_furnace", f"loot give @s loot {furnace.loot_table}")
```

See [Resource Locations](../../1_definitions_setup/en.md#-resource-locations) for the full list of accessors.

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

**Common clock functions:** (other names will not be automatically called by default)
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

### Advancement Writing

#### `write_advancement()`
Write an advancement file.

```python
def write_advancement(
    path: str,                              # Advancement path (e.g., "namespace:folder/name")
    advancement: Advancement | JsonDict,    # Advancement data or object
    overwrite: bool = False,                # Overwrite instead of merging
    max_level: int = -1                     # JSON indentation depth (-1 = unlimited)
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
        "icon": {"id": "minecraft:diamond_sword", "components": {"item_model": f"{ns}:ruby_sword"}},
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

### Tag Writing

#### `write_tag()`
Write a tag file (generic for any tag type).

```python
def write_tag(
    path: str,                                  # Tag path (e.g., "namespace:my_tag")
    tag_type: NamespaceProxy | NamespaceContainer,  # Tag type (e.g., ctx.data.function_tags)
    values: list[Any] | None = None,           # Values to add to the tag
    prepend: bool = False,                      # Prepend instead of appending
    max_level: int | None = None                # JSON indentation depth
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
    "stone",
    "emerald_block"
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
    max_level: int | None = None    # JSON indentation depth
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

### Utility Functions

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
    max_level: int | None = None,  # Max indentation depth (None = unlimited)
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

# Limit indentation depth
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

# Automatically loads animated_block.png.mcmeta if it exists
texture = texture_mcmeta("assets/textures/animated_block.png")
Mem.ctx.assets["my_namespace"].textures["block/animated_block"] = texture
```

---

## Next steps

- [Writing functions and files](../en.md) — which approach to reach for, and why.
- [Cookbook](../cookbook/en.md) — these helpers used in complete, working files.
- [Equations](../../4_equations/en.md) — build scoreboard arithmetic to embed in what you write.
