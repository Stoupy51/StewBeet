# Writing functions and files

Writing to files is essential for generating datapacks and resource packs. StewBeet provides three approaches for file writing, each with different use cases and complexity levels. This guide covers static file loading via configuration, native beet API, and StewBeet's streamlined helper functions.

**File writing typically happens in user plugins after definitions are set up but before finalization.**

> **Note on Bolt**: [Bolt](https://github.com/mcbeet/beet/tree/beta/packages/bolt) is another way to write datapack functions using Python-like syntax. While it exists and is a great tool, it's not covered in this guide. Check out the [Bolt repository](https://github.com/mcbeet/beet/tree/beta/packages/bolt) to learn more about it.

**Example File**: [extensive/src/link.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py) <br>  
**Real-world Example**: [SimplEnergy/src/utils/machines.py](https://github.com/Stoupy51/SimplEnergy/blob/main/src/utils/machines.py) <br>  
**Real-world Example**: [StardustFragment/src/utils/remaining.py](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py) <br>

- Load static files from directories (pre-plugin via `beet.yml`)
- Generate dynamic functions, advancements, and tags programmatically
- Append, prepend, or overwrite file content
- Organize datapack logic across multiple files
- Manage function tags and other tag types
- Set up clock functions (tick, second, minute)

**Required**: StewBeet I/O utilities (`from stewbeet import write_function, write_load_file, ...`)  
**Position**: Called after definitions setup, typically in the middle of the pipeline  
**Integration**: Works with all file types (functions, advancements, tags, etc.)

## Three Approaches to Writing Files

### Quick Comparison

| Approach | Use Case | Complexity | Flexibility |
|----------|----------|------------|-------------|
| **Static Files (beet.yml)** | Pre-written files | ⭐ Simple | ⭐ Low |
| **Native Beet API** | Full control | ⭐⭐⭐ Complex | ⭐⭐⭐ High |
| **StewBeet Helpers** | Dynamic generation | ⭐⭐ Medium | ⭐⭐ Medium-High |

---

### Approach 1: Static File Loading (beet.yml)

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
├── 📦 data/
│   └── my_namespace/
│       ├── ⚙️ function/
│       │   ├── load.mcfunction
│       │   └── tick.mcfunction
│       ├── 🏆 advancement/
│       │   └── my_advancement.json
│       └── 🍳 recipe/
│           └── my_recipe.json
└── 🎨 assets/
    └── my_namespace/
        └── textures/
            └── item/
                └── my_item.png
```

**What goes where:**
- 📦 **data/** - All datapack content (functions, advancements, recipes, tags, etc.)
- ⚙️ **function/** - Minecraft commands (.mcfunction files)
- 🏆 **advancement/** - Player achievements and technical triggers (.json)
- 🍳 **recipe/** - Crafting, smelting, and other recipes (.json)
- 🎨 **assets/** - All resource pack content (textures, models, sounds)
- 🖼️ **textures/** - PNG image files for items, blocks, etc.
- ...

**✅ Use when:**
- You have static files that don't need dynamic generation
- You're organizing pre-written commands and data
- You want simple, straightforward file structure

**❌ Don't use when:**
- You need to generate content based on definitions
- You need to combine multiple sources of data
- You need conditional file generation

---

### Approach 2: Native Beet API

Use beet's native object-oriented API to write files programmatically in plugins.

```python
from beet import Context, Function, Advancement, FunctionTag
from stouputils.typing import JsonDict

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

### Approach 3: StewBeet Helper Functions (Recommended)

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
    
    # Append to load file (runs when datapack loads: "your_namespace:v{version}/load/confirm_load")
    write_load_file("""
# Initialize scoreboards
scoreboard objectives add points dummy
scoreboard objectives add data dummy
""")
    
    # Append to tick file (runs every game tick: "your_namespace:v{version}/tick")
    write_tick_file("""
# Check for players with high scores
execute as @a[scores={points=100..}] run function my_namespace:rewards/high_score
""")
    
    # Write versioned functions (automatic clock: "your_namespace:v{version}/second", etc.)
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
## Best Practices

### Do's

**File Organization:**
- Use meaningful folder structures (e.g., `machines/`, `items/`, `utils/`)
- Group related functions together
- Separate logic into small, reusable functions

**Code Quality:**
- Use f-strings for dynamic paths: `f"{ns}:folder/{item}"`
- Use multi-line strings (triple quotes) for command content
- Add descriptive comments in generated functions
- Use `prepend=True` for initialization code in files that must run first

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

### Don'ts

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
- Don't nest folders too deeply
- Don't create files that are never called

---
## Summary

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
## Glossary

| Term | Meaning |
|------|---------|
| **Static file loading** | Pre-plugin loading of files declared in `beet.yml` (`data_pack.load` and `resource_pack.load`). |
| **Native Beet API writing** | Creating files through `ctx.data`/`ctx.assets` objects in plugin code. |
| **StewBeet helper writing** | Utility functions like `write_function`, `write_tag`, and related helpers for faster generation. |

## Next steps

- [Helper function reference](reference.md) — every helper and the arguments it takes.
- [Cookbook](cookbook.md) — complete worked examples.
- [Equations](../4_equations/en.md) — build scoreboard arithmetic instead of hand-writing it.
- [Configuring the build](../3_beet_config/en.md) — control when your code runs in the pipeline.
