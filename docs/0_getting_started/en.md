
# 🚀 Getting Started with StewBeet

Welcome to **StewBeet**! 🎉 This comprehensive guide will take you from complete beginner to creating your first Minecraft datapack using the StewBeet framework. Whether you're new to datapack development or coming from vanilla datapacks, this guide has everything you need to get started.

## 📋 What You'll Learn

By the end of this guide, you'll be able to:
- ✅ Install and set up StewBeet on your computer
- 🎯 Choose the right template for your project
- ⚙️ Configure your first StewBeet project
- 🔨 Build and test your datapack
- 📝 Add your first custom items and blocks
- 🎮 Load your datapack in Minecraft

## 🎯 What is StewBeet?

StewBeet is a powerful **automation framework** for creating Minecraft datapacks. Think of it as a smart assistant that:

- 🤖 **Automates repetitive tasks** - No more manually creating models, textures, or function files
- 📦 **Generates resource packs** - Automatically creates all the visual assets your datapack needs
- 📚 **Integrates libraries** - Works seamlessly with popular datapack libraries like Smithed
- 📖 **Creates documentation** - Generates in-game manuals and function headers
- 🔧 **Handles complexity** - Manages dependencies, versioning, and compatibility automatically

Instead of writing hundreds of files manually, you define what you want and StewBeet creates everything for you!

## 🛠️ Prerequisites

Before we start, make sure you have:

### ✅ Required Software
- **Python 3.14** 🐍 - [Download from python.org](https://www.python.org/downloads/)
- **Text Editor or IDE** 📝 - We recommend [VS Code](https://code.visualstudio.com/) with Python extension pack and the [StewBeet extension](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet)
- **Minecraft Java Edition** 🎮 - For testing your datapacks

### 🔍 Check Your Python Installation
Open a terminal/command prompt and run:
```bash
python --version
```
You should see something like `Python 3.14.3` or higher. If not, install Python first.

## 📦 Step 1: Install StewBeet

Open your terminal/command prompt and run:

```bash
pip install stewbeet
```

This installs StewBeet along with all its dependencies (beet, bolt, mecha, and more). The installation might take a few minutes.

### ✅ Verify Installation
Check that StewBeet is installed correctly:
```bash
stewbeet --version
```

## 🎯 Step 2: Choose Your Template

StewBeet provides three templates to get you started.<br>
**We strongly recommend the Basic Template** for beginners:

### 📋 Template Comparison

| Template | Best For | Features | Complexity |
|----------|----------|----------|------------|
| **🔹 Minimal** | Learning beet basics | Core beet functionality only | ⭐ Beginner |
| **⭐ Basic** | **Most users** | Full StewBeet features, clean setup | ⭐⭐ Intermediate |
| **🌟 Extensive** | Advanced users | All features + examples | ⭐⭐⭐ Advanced |

### 🎯 Why Choose Basic Template?

The **Basic Template** is perfect because it:
- ✅ Includes **all StewBeet features** but with clean, empty configuration
- 📝 Has **detailed comments** explaining every option
- 🎯 Provides a **solid foundation** without overwhelming examples
- 🔧 Is **easily customizable** for your specific needs

## 📁 Step 3: Create Your Project

### 🎯 Initialize a New Project

1. **Create** a new folder for your project (e.g., `C:/MyDatapacks/AwesomeOres/`)
2. **Open the folder in VS Code**:
   - Right-click the folder → "Open with Code"
   - Or launch VS Code and use File → Open Folder
3. **Open a terminal in VS Code**:
   - Use Terminal → New Terminal from the menu
   - The terminal will automatically open in your project folder
4. **Run the init command**:
   ```bash
   stewbeet init basic
   ```

This will automatically create all the necessary files and folders for your project!

Your project structure will look like this:
```bash
AwesomeOres/
├── 📁 .beet_cache/              # Build cache (auto-generated)
├── 📁 build/                    # Output folder (auto-generated)
├── 📁 assets/                   # Assets folder (important for textures and sounds)
├── 📁 src/                      # Your source code
│   ├── 📁 data/                 # Datapack functions and data
│   │   └── 📁 basic_template/  # Your namespace (rename this!)
│   ├── 📁 definitions/          # Definition modules
│   │   ├── 📄 additions.py      # Additional custom definitions
│   │   └── 📄 ores.py           # Ore equipment configurations
│   ├── 📄 link.py               # User code for linking features
│   └── 📄 setup_definitions.py  # Main definitions setup
├── 📁 assets/                   # Your textures and sounds
├── 📄 .gitignore                # Git ignore file
├── 📄 beet.yml                  # Main configuration file
└── 📄 definitions_debug.json    # Debug definitions file
```

## ⚙️ Step 4: Configure Your Project

Open `beet.yml` in your text editor. This is your main configuration file. Let's customize it:

### 🎯 Basic Project Settings

These are the minimum metadata fields that identify your pack and are reused by generated files, packaging, and in-game presentation.

```yaml
# Project identifier - MUST match your namespace in src/data/
id: "awesome_ores"

# Project name for display
name: "Awesome Ores"

# Your name (shows up in pack.mcmeta and item lore)
author: "YourName"

# Version using semantic versioning
version: "1.0.0"

# Brief description
description: "My first StewBeet datapack with custom ores!"
```

### 🎯 Important Notes:
- **ID**: Use lowercase, underscores only, no spaces (e.g., `awesome_ores`)
- **Name**: Can have spaces and special characters (e.g., `"Awesome Ores & Gems"`)
- **Version**: Follow [semantic versioning](https://semver.org/) (major.minor.patch)

## 🔨 Step 5: Build Your First Project

Let's test that everything works:

### ⚡ Open Terminal in Project Folder & Run Your First Build

🖥️ Open Terminal in Project Folder and run `stewbeet` or `stewbeet build`

You should see output like:
```bash
Building project...

[WARNING 19:05:57] Error during generate_custom_records(): (FileNotFoundError) [WinError 3] The system cannot find the path specified: 'assets/records' 
[DEBUG 19:05:58] Mem.definitions exported to 'definitions_debug.json' 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.sounds': 0.070ms (69900ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.item_models': 0.246ms (245700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.check_power_of_2': 0.250ms (249700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.custom_recipes': 0.021ms (20700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.custom_paintings': 0.007ms (7400ns) 
[WARNING 19:05:58] Database is empty, skipping manual generation. 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.ingame_manual': 0.075ms (74600ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.loading': 0.150ms (150300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.custom_blocks': 0.108ms (108200ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.loot_tables': 0.187ms (187300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.sorters': 0.031ms (31300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compatibilities.simpledrawer': 0.003ms (2700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compatibilities.neo_enchant': 0.003ms (2800ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking': 0.045ms (45100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.basic_datapack_structure': 0.062ms (61600ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.dependencies': 0.875ms (874900ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.check_unused_textures': 0.125ms (124800ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.last_final': 0.154ms (154500ns) 
Generating lang file: 100%|████████████████████████████████████████████████| 21/21 [4481.78it/s, 00:00<00:00]
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.auto.lang_file': 73.613ms (73613100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.auto.headers': 0.561ms (561000ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.archive': 23.592ms (23592200ns) 
[WARNING 19:05:58] No datapacks or libs to merge for build\AwesomeOres_datapack_with_libs.zip. Skipping weld. 
[WARNING 19:05:58] No resource packs or libs to merge for build\AwesomeOres_resource_pack_with_libs.zip. Skipping weld. 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.merge_smithed_weld': 0.593ms (593100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.copy_to_destination': 0.007ms (7300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compute_sha1': 25.546ms (25546400ns) 
[DEBUG 19:05:58] Total execution time: 0.56934s 
Done!
```

### 🎯 Check the Results

Look in your `build/` folder. You should see:
- 📁 `datapack/` - Your generated datapack
- 📁 `resource_pack/` - Your generated resource pack
- 📦 `AwesomeOres_datapack.zip` - Ready-to-use datapack
- 📦 `AwesomeOres_resource_pack.zip` - Ready-to-use resource pack
- 📄 `sha1_hashes.json` - May be useful for server admins

**Congratulations!** 🎉 You've successfully built your first StewBeet project!

## 🎮 Step 6: Test in Minecraft

### 📦 Install the Datapack

#### ⚡ Option 1: Automatic Copying (Recommended)

Configure StewBeet to automatically copy files to your Minecraft folders by editing `beet.yml`:

```yaml
meta:
  stewbeet:
    build_copy_destinations:
      datapack: ["C:/Users/YourName/AppData/Roaming/.minecraft/saves/YourWorldName/datapacks"]
      resource_pack: ["C:/Users/YourName/AppData/Roaming/.minecraft/resourcepacks"]
```

Replace the paths with your actual Minecraft folders. Now when you run `stewbeet`, files are automatically copied!

#### 📋 Option 2: Manual Copying

1. **Open Minecraft** and create a new world (or open an existing one)
2. **Copy** `build/AwesomeOres_datapack.zip` to your world's datapacks folder:
   - Windows: `%appdata%\.minecraft\saves\[WorldName]\datapacks\`
   - Mac: `~/Library/Application Support/minecraft/saves/[WorldName]/datapacks/`
3. **Copy** `build/AwesomeOres_resource_pack.zip` to your resource packs folder:
   - Windows: `%appdata%\.minecraft\resourcepacks\`
   - Mac: `~/Library/Application Support/minecraft/resourcepacks/`

### 🔧 Enable in Game

1. **In Minecraft**, type `/reload` in chat
2. Go to **Options** → **Resource Packs** and enable your resource pack
3. Test the basic functionality with `/function awesome_ores:path/to/a/random/function/i/guess` (if you didn't remove the example function in `src/data/awesome_ores/function/`)

## 📝 Step 7: Add Your First Custom Item

Now let's add a custom item to see StewBeet's power in action!

### 🖼️ Add a Texture

1. Create the folder structure: `assets/textures/`
2. Add a 16x16 PNG texture file, for example: [`ruby.png`](./ruby.png)
3. Your structure should be: `assets/textures/ruby.png`

### 🎯 Define the Item

Open `src/definitions/additions.py` and add the definition for your new item:

```python
# Imports
from stewbeet import *


# Main entry point
def main():

    # Add items to the definitions
    Mem.definitions["ruby"] = Item(
        id="ruby",
        components={
            "lore": [{"text":"A precious red gemstone","color":"gray","italic":False}]
        }
    )

    # See extensive_template/src/definitions/additions.py for examples
    pass
```

### 🔨 Build and Test

1. Run `stewbeet` in your terminal and wait for it to finish (first time rendering item models may take a bit longer)
2. Reload your world with `/reload`
3. Get your item with `/loot give @s loot awesome_ores:i/ruby` or `/function awesome_ores:_give_all`

**Amazing!** 🎉 StewBeet automatically:
- ✅ Created the item model and reference
- ✅ Added it to the resource pack
- ✅ Created proper item components
- ✅ Added it to the manual (if enabled)

## 🎯 Step 8: Add Your First Custom Block

Let's create a custom block:

### 🖼️ Add Block Textures

Add these textures to `assets/textures/`:
- [`ruby_ore.png`](./ruby_ore.png) - The main texture
- [`ruby_sword.png`](./ruby_sword.png) - A sword texture
- [`ruby_chestplate.png`](./ruby_chestplate.png) - A ruby chestplate texture
- [`ruby_layer_1.png`](./ruby_layer_1.png) - A layer texture for the top layer (it's how Minecraft handles custom armors)
- [`ruby_layer_2.png`](./ruby_layer_2.png) - A layer texture for the bottom layer

### 🎯 Configure the Block

For simplicity, we'll use the `ORES_CONFIGS` section in `src/definitions/ores.py`:

```python
# Imports
from stewbeet import *


# Main entry point
def main():

    # Configuration to generate everything about a material
    ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
        "ruby": EquipmentsConfig(
            # This ruby is equivalent to diamond,
            equivalent_to = DefaultOre.DIAMOND,

            # But, has more durability (1.2 times more)
            pickaxe_durability = 1.2 * VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]["durability"],

            # And, does 1 more damage per hit (mainhand), and has 0.5 more armor, and mines 20% faster (pickaxe)
            attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
        ),
    }

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    generate_everything_about_these_materials(ORES_CONFIGS)
    return
```

### 🔨 Build and Test

1. Run `stewbeet`, wait for it to finish
2. Reload in Minecraft
3. Get your block with `/loot give @s awesome_ores:i/ruby_ore`
4. Place it in the world - it's a fully functional custom block!

StewBeet automatically:
- ✅ Created block models with proper faces
- ✅ Set up placement and breaking mechanics
- ✅ Added mining properties (requires pickaxe, drops, etc.)
- ✅ Integrated with Smithed Custom Blocks library
- ✅ Added fortune and silk touch support

## 📖 Step 9: Check Your In-Game Manual

One of StewBeet's coolest features is the automatic manual generation.<br>
First, make sure to restart your world since ingame-manual require a server restart (minecraft dialogs system), and then:

1. In Minecraft, press "G" (quick action keybind) or run `/loot give @s loot awesome_ores:i/manual` if you started with the Extensive Template
2. Open the book to see your **automatically generated manual**
3. It includes all your items, recipes, and crafting information!

## 🎯 Step 10: Understanding the Configuration

Let's explore some key configuration options in `beet.yml`:

### 📁 Important Folders

These paths define where StewBeet reads source assets and where it copies generated outputs for testing.

```yaml
meta:
  stewbeet:
    # Directory containing all project textures
    textures_folder: "assets/textures"

    # Directory containing all custom sounds
    sounds_folder: "assets/sounds"

    # Directory containing all jukebox records
    records_folder: "assets/records"

    # Directory containing libraries that will be copied to the build destination, and merged using Smithed Weld if enabled.
    libs_folder: "libs"

    # Optional list of destination paths where generated files will be copied
    build_copy_destinations:
      datapack: ["C:/Users/YourName/AppData/Roaming/.minecraft/saves/YourWorldName/datapacks"]
      resource_pack: ["C:/Users/YourName/AppData/Roaming/.minecraft/resourcepacks"]
```

### 🔧 Plugin Pipeline

The `pipeline` section controls what StewBeet does:

```yaml
# Plugins to run first
require:
    - "stewbeet"  # Equivalent to "stewbeet.plugins.initialize"
    - "bolt"      # Initialize bolt

# A list of strings representing "plugins".
# - These plugins will execute after the pack is loaded (all src/data and src/assets contents are loaded first)
pipeline:
    - "src.setup_definitions"                           # Your User code for defining items/blocks
    - "stewbeet.plugins.resource_pack.sounds"           # Generate sound files
    - "stewbeet.plugins.resource_pack.item_models"      # Generate item models
    - "stewbeet.plugins.resource_pack.check_power_of_2" # Verify texture dimensions
    - "stewbeet.plugins.custom_recipes"                 # Generate custom recipes
    - "stewbeet.plugins.custom_paintings"               # Generate custom paintings
    - "stewbeet.plugins.ingame_manual"                  # Generate in-game manual
    - "stewbeet.plugins.datapack.loading"               # Set up load/tick functions
    - "stewbeet.plugins.datapack.custom_blocks"         # Set up block mechanics
    - "stewbeet.plugins.datapack.loot_tables"           # Generate loot tables
    - "stewbeet.plugins.datapack.sorters"               # Set up item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"   # SimpleDrawer compatibility
    - "stewbeet.plugins.compatibilities.neo_enchant"    # NeoEnchant compatibility
    - "src.link"                                        # User code for linking features
    - "mecha"                                           # Bolt/Mecha compilation
    - "stewbeet.plugins.finalyze.custom_blocks_ticking" # Finalize block ticking
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # Structure finalization
    - "stewbeet.plugins.finalyze.dependencies"          # Dependency checks
    - "stewbeet.plugins.finalyze.check_unused_textures" # Find unused textures
    - "stewbeet.plugins.finalyze.last_final"            # Final cleanup
    - "stewbeet.plugins.auto.lang_file"                 # Generate language files
    - "stewbeet.plugins.auto.headers"                   # Generate function headers
    - "stewbeet.plugins.archive"                        # Create zip files
    - "stewbeet.plugins.merge_smithed_weld"             # Merge with Smithed Weld
    - "stewbeet.plugins.copy_to_destination"            # Copy to configured paths
    - "stewbeet.plugins.compute_sha1"                   # Compute file hashes
```

## 🚀 Next Steps

Congratulations! You now have a working StewBeet project. Here's what to explore next:

For more in-depth guides and advanced features, check out the **📖 [Documentation](https://stewbeet.paralya.fr/documentation)** with comprehensive guides and references.

### 🎯 Try These Features

1. **Add more items** with different textures and properties
2. **Create armor sets** using the equipment configuration
3. **Add custom recipes** in the recipe definitions
4. **Set up automatic copying** to your Minecraft folders
5. **Explore the extensive template** for advanced examples

### 🌟 Advanced Configuration

Once comfortable, explore these powerful features:

- **🔄 Auto-generation** of ores, tools, and armor sets
- **📦 Library integration** with Smithed, Bookshelf, and more
- **🎨 Custom model overrides** for special items
- **📝 Function generation** with proper headers
- **🌐 Internationalization** with automatic language files

## 🤝 Get Help

Need assistance? Here are your best resources:

- **📖 [Documentation](https://stewbeet.paralya.fr/documentation)** - Comprehensive guides and references
- **💬 [Discord Server](https://discord.gg/anxzu6rA9F)** - Active community support
- **🐛 [GitHub Issues](https://github.com/Stoupy51/StewBeet/issues)** - Bug reports and feature requests

## 🎉 Conclusion

You've successfully:
- ✅ Installed StewBeet
- ✅ Set up your first project
- ✅ Created custom items and blocks
- ✅ Built and tested in Minecraft
- ✅ Explored key configuration options

StewBeet is incredibly powerful, and you've only scratched the surface! The framework will save you hundreds of hours of manual work while creating professional-quality datapacks.

**Happy datapack development!** 🚀

---

*💡 **Pro Tip**: Start small, experiment often, and don't hesitate to ask for help in the Discord community. The StewBeet developers and users are very friendly and helpful!*

