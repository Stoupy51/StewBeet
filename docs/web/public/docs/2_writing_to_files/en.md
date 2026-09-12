# Writing functions and files

Writing to files is essential for generating datapacks and resource packs. StewBeet provides four approaches for file writing, each with different use cases and complexity levels. This guide covers static file loading via configuration, the native beet API, StewBeet's streamlined helper functions, and Bolt.

**File writing typically happens in user plugins after definitions are set up but before finalization.**

> **Write all of this with the commands checked as you type.** Every approach below ends with commands inside a Python string, inside a `.bolt` module, or both. The [StewBeet extension for VSCode](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) reads them as what they are: completion, errors, ctrl+click, and a link from each block to the function your build wrote from it. See [Editor support](../8_editor/en.md).

<video src="/vscode_extension.mp4" controls loop muted playsinline preload="auto">
</video>

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

## Four Approaches to Writing Files

### Quick Comparison

| Approach | Use Case | Complexity | Flexibility |
|----------|----------|------------|-------------|
| **Static Files (beet.yml)** | Pre-written files | ⭐ Simple | ⭐ Low |
| **Native Beet API** | Full control | ⭐⭐⭐ Complex | ⭐⭐⭐ High |
| **StewBeet Helpers** | Dynamic generation | ⭐⭐ Medium | ⭐⭐ Medium-High |
| **Bolt** | Commands as syntax | ⭐⭐⭐ Complex | ⭐⭐⭐ High |

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

### Approach 4: Bolt

[Bolt](https://github.com/mcbeet/beet/tree/main/packages/bolt) is mecha's scripting layer, and it inverts the three approaches above.
Instead of Python writing a string that happens to hold commands, the commands are the syntax: in a `.bolt` file, `item = 3` is Python and `item modify entity @s weapon.mainhand set value ...` is a command, at the same indentation, in the same scope.

All of it runs at build time. Nothing Python reaches the datapack.

```yaml
# In beet.yml
require:
    - "stewbeet"
    - "bolt"

pipeline:
    - "mecha"       # bolt needs mecha to compile what it produced

meta:
    bolt:
        entrypoint: "*"     # let any function file use bolt, not only modules
```

Two kinds of file:

- **Modules**, `.bolt` under `data/<namespace>/module/`. Importable, and they write a function only where they ask for one.
- **Function files**, `.mcfunction` covered by `entrypoint`. The file *is* one function, written in bolt.

#### Writing a function

```python
# src/data/voltaic/module/gui.bolt
MACHINES = ["pulverizer", "furnace", "smelter"]

for machine in MACHINES:
    function f"voltaic:gui/{machine}/open":
        playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
        data modify entity @s equipment.head set from storage voltaic:gui Icon
        tag @s add voltaic.watching
```

Three functions out of one loop. The f-string is the path, and the indented block is the body.

A path is a value like any other, so it can be named, imported and passed around. Two shorthands keep the namespace out of it:

| Written  | Resolves to                                               |
|----------|-----------------------------------------------------------|
| `./load` | `<namespace>:<module path>/load`                           |
| `~/init` | A child of the function being written at that point        |

```python
SERVER_LOAD = ./load

prepend function_tag minecraft:load {"values": [SERVER_LOAD]}

function SERVER_LOAD:
    forceload add 0 0
    scoreboard objectives add voltaic.energy dummy
```

#### Nesting and implicit execute

An `execute` that ends in a colon writes its own function and the call that reaches it:

```python
execute as @a[tag=voltaic.using] at @s:
    particle minecraft:electric_spark ~ ~1 ~
    playsound minecraft:block.beacon.ambient block @s ~ ~ ~ 0.4 2.0
```

Conditions read as conditions, with `if`, `else` and the `run return` shapes folded in:

```python
if score @s voltaic.energy matches 1..:
    scoreboard players remove @s voltaic.energy 1
else:
    function voltaic:machines/shutdown
```

#### Adding to a function another module owns

```python
from voltaic:core import SERVER_LOAD

append function SERVER_LOAD:
    team add builder "Builder"
    team modify builder color black
```

`function`, `append function` and `prepend function` are the three ways a module contributes to a path.
Several modules can append to the same load function without knowing about each other, which is what makes one file per feature work.

#### It is Python, so the whole language is there

Imports take a resource location where Python takes a dotted path:

```python
from lib:helpers import ticks            # a module in another namespace
from ./items import team_flag            # a sibling module
from dataclasses import dataclass        # plain Python, from your environment
from functools import cache
```

Classes and decorators work, and a method can write functions:

```python
from functools import cached_property

class Gui:
    """ One machine's interface, opened by right clicking it. """

    def __init__(self, machine):
        self.path = f"voltaic:gui/{machine}"

    @cached_property
    def open(self):
        function f"{self.path}/open":
            playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
            tag @s add voltaic.watching
        return f"{self.path}/open"


gui = Gui("pulverizer")
function voltaic:gui/pulverizer/tick:
    execute as @a[tag=voltaic.using] run function gui.open
```

`cached_property` is doing real work there: the function is written the first time something asks for its path, and never twice.

JSON files are literals, with Python values dropped straight into them:

```python
ON_KILL = ./on_kill

advancement ON_KILL {
    "criteria": {"kill": {"trigger": "minecraft:player_killed_entity"}},
    "rewards": {"function": ON_KILL}
}

function ON_KILL:
    advancement revoke @s only ON_KILL
```

#### Scoreboards and storage as variables

[`bolt_expressions`](https://github.com/mcbeet/bolt-expressions) (`pip install bolt-expressions`, then add it to `require`) turns arithmetic into the commands that perform it:

```python
from bolt_expressions import Scoreboard, Data

Energy = Scoreboard("voltaic.energy")
Temp = Data.storage("voltaic:temp")

Energy["@s"] -= 20
Energy["#total"] = Energy["@s"] * 3 + Energy["#buffer"]
Temp.display.text = Energy["#total"]
```

Each line compiles to the `scoreboard players operation` sequence it needs, temporaries included.
It is the same job as [Equations](../4_equations/en.md) on the StewBeet side, expressed in the file that uses it.

#### Bolt and StewBeet in the same pack

Nothing forces a choice. A pack can declare its items with `Item(...)`, let the plugins generate recipes and the manual, write most of its logic with `write_function`, and keep one `.bolt` module for the part where the commands are the hard bit.
The [demo pack](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode/demo) the extension records its showcases from is exactly that: one small pack written three ways.

**✅ Use when:**
- The commands are the complicated part, not the data behind them
- You want loops, conditions and classes around commands without an f-string between you and them
- You are doing scoreboard or storage arithmetic and want to read it as arithmetic
- You want nesting (`execute ...:`) instead of hand-splitting functions

**❌ Don't use when:**
- The work is generating many near-identical functions from your definitions. `write_function` in a plugin sees `Mem.definitions` and is the shorter road
- You need a StewBeet plugin to see what you wrote. Plugins run on the pack, and mecha compiles after them
- Your collaborators do not want a second language in the project

#### Two things to set up once

- **Spyglass underlines a `.mcfunction` holding bolt**, because it is not vanilla mcfunction. [`stewbeet.plugins.spyglass`](../plugins/spyglass.md) takes those files off its list, from what the build actually compiled.
- **The [StewBeet extension](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) gives `.bolt` its own language**, with completion and ctrl+click on the commands and a lens per function the module writes. See [Editor support](../8_editor/en.md).

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

### **Four Approaches Comparison**

| Approach | Use Case | Complexity | Flexibility |
|----------|----------|------------|-------------|
| **Static Files (beet.yml)** | Pre-written files | ⭐ Simple | ⭐ Low |
| **Native Beet API** | Full control | ⭐⭐⭐ Complex | ⭐⭐⭐ High |
| **StewBeet Helpers** | Dynamic generation | ⭐⭐ Medium | ⭐⭐ Medium-High |
| **Bolt** | Commands as syntax | ⭐⭐⭐ Complex | ⭐⭐⭐ High |

### **When to Use Each**

- 📁 **Static Files**: Configuration files, static recipes, simple functions
- 🔧 **Native Beet API**: Complex nested structures, custom file types, advanced control
- 🚀 **StewBeet Helpers**: Most datapack logic, dynamic functions, standard patterns
- 🧪 **Bolt**: Command-heavy logic, scoreboard arithmetic, nesting instead of hand-split functions

### **Key Takeaways**

✅ Start with static files for simple content<br>
✅ Use StewBeet helpers for dynamic datapack logic<br>
✅ Use native beet API only when helpers don't cover your needs<br>
✅ Reach for Bolt where the commands, not the data, are the hard part<br>
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
| **Bolt** | Mecha's scripting layer. Python and commands share one syntax, compiled at build time. |
| **Module** | A `.bolt` file under `data/<namespace>/module/`, imported by others and writing functions only where it asks to. |
| **Nesting** | An `execute` or `if` ending in a colon, which mecha turns into its own function and the call reaching it. |

## Next steps

- [Helper function reference](reference/en.md): every helper and the arguments it takes.
- [Editor support](../8_editor/en.md): the extension that checks every block on this page.
- [Cookbook](cookbook/en.md): complete worked examples.
- [Equations](../4_equations/en.md): build scoreboard arithmetic instead of hand-writing it.
- [Configuring the build](../3_beet_config/en.md): control when your code runs in the pipeline.
