
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
- **Python 3.12 or higher** 🐍 - [Download from python.org](https://www.python.org/downloads/)
- **Text Editor or IDE** 📝 - We recommend [VS Code](https://code.visualstudio.com/) with Python extension
- **Minecraft Java Edition** 🎮 - For testing your datapacks

### 🔍 Check Your Python Installation
Open a terminal/command prompt and run:
```bash
python --version
```
You should see something like `Python 3.12.0` or higher. If not, install Python first.

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

StewBeet provides three templates to get you started. **We strongly recommend the Basic Template** for beginners:

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

### 🔽 Download the Basic Template

1. **Download** the [basic template zip file](../templates/basic_template.zip)
2. **Extract** it to a folder where you want to work (e.g., `C:\MyDatapacks\MyFirstPack\`)
3. **Rename** the folder to your project name (e.g., `AwesomeOres`)

Your project structure should look like this:
```
AwesomeOres/
├── 📁 .beet_cache/          # Build cache (auto-generated)
├── 📁 build/               # Output folder (auto-generated)
├── 📁 src/                 # Your source code
│   ├── 📁 data/           # Datapack functions and data
│   ├── 📄 link.py         # User code for linking features
│   └── 📄 setup_definitions.py  # Define your items/blocks here
├── 📄 .gitignore          # Git ignore file
└── 📄 beet.yml            # Main configuration file
```

## ⚙️ Step 4: Configure Your Project

Open `beet.yml` in your text editor. This is your main configuration file. Let's customize it:

### 🎯 Basic Project Settings

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

### 📁 Create Your Namespace Folder

1. Navigate to `src/data/`
2. Create a folder with **exactly the same name** as your `id` in beet.yml
3. If your ID is `awesome_ores`, create: `src/data/awesome_ores/`

## 🔨 Step 5: Build Your First Project

Let's test that everything works:

### 🖥️ Open Terminal in Project Folder

1. **Windows**: Shift + Right-click in your project folder → "Open PowerShell window here"
2. **Mac/Linux**: Open terminal and navigate to your project folder using `cd`

### ⚡ Run Your First Build

```bash
stewbeet
```

You should see output like:
```bash
Building project...

[PROGRESS 19:49:31] Execution time of 'stewbeet.plugins.initialize': 1.256ms (1256000ns) 
[INFO  19:49:31] No errors found in the definitions during verification 
[PROGRESS 19:49:31] Execution time of 'stewbeet.plugins.verify_definitions': 0.098ms (98400ns) 
[PROGRESS 19:49:31] Execution time of 'stewbeet.plugins.resource_pack.sounds': 0.056ms (55700ns) 
[PROGRESS 19:49:31] Execution time of 'stewbeet.plugins.resource_pack.item_models': 0.157ms (156700ns)      
[PROGRESS 19:49:31] Execution time of 'stewbeet.plugins.resource_pack.check_power_of_2': 0.228ms (228400ns) 
[PROGRESS 19:49:31] Execution time of 'stewbeet.plugins.custom_recipes': 0.013ms (12500ns) 
[WARNING 19:49:32] Database is empty, skipping manual generation. 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.ingame_manual': 0.159ms (159400ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.datapack.loading': 0.208ms (208100ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.datapack.custom_blocks': 0.003ms (3400ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.datapack.loot_tables': 0.273ms (273100ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.compatibilities.simpledrawer': 0.002ms (1900ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.compatibilities.neo_enchant': 0.003ms (2500ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking': 0.013ms (12900ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.finalyze.basic_datapack_structure': 0.049ms (48600ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.finalyze.dependencies': 0.910ms (910100ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.finalyze.check_unused_textures': 0.095ms (94500ns) 
Generating lang file: 100%|██████████████████████████████████| 14/14 [27922.14it/s, 00:00<00:00]
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.auto.lang_file': 33.317ms (33316900ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.auto.headers': 0.256ms (255600ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.archive': 23.990ms (23989600ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.merge_smithed_weld': 0.12550s 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.copy_to_destination': 0.015ms (15400ns) 
[PROGRESS 19:49:32] Execution time of 'stewbeet.plugins.compute_sha1': 83.104ms (83103700ns) 
Done!
```

### 🎯 Check the Results

Look in your `build/` folder. You should see:
- 📁 `datapack/` - Your generated datapack
- 📁 `resource_pack/` - Your generated resource pack
- 📦 `awesome_ores_datapack.zip` - Ready-to-use datapack
- 📦 `awesome_ores_resource_pack.zip` - Ready-to-use resource pack

**Congratulations!** 🎉 You've successfully built your first StewBeet project!

## 🎮 Step 6: Test in Minecraft

### 📦 Install the Datapack

1. **Open Minecraft** and create a new world (or open an existing one)
2. **Copy** `build/awesome_ores_datapack.zip` to your world's datapacks folder:
   - Windows: `%appdata%\.minecraft\saves\[WorldName]\datapacks\`
   - Mac: `~/Library/Application Support/minecraft/saves/[WorldName]/datapacks/`
3. **Copy** `build/awesome_ores_resource_pack.zip` to your resource packs folder:
   - Windows: `%appdata%\.minecraft\resourcepacks\`
   - Mac: `~/Library/Application Support/minecraft/resourcepacks/`

### 🔧 Enable in Game

1. **In Minecraft**, type `/reload` in chat
2. Go to **Options** → **Resource Packs** and enable your resource pack
3. Test the basic functionality with `/function awesome_ores:_give_all` (if available)

## 📝 Step 7: Add Your First Custom Item

Now let's add a custom item to see StewBeet's power in action!

### 🖼️ Add a Texture

1. Create the folder structure: `assets/textures/`
2. Add a 16x16 PNG texture file, for example: `ruby.png`
3. Your structure should be: `assets/textures/ruby.png`

### 🎯 Define the Item

Open `src/setup_definitions.py` and add after the existing comments:

```python
# Add items to the definitions
Mem.database["ruby"] = {"id": core.CUSTOM_ITEM_VANILLA, "lore":["A precious red gemstone"]}
```

### 🔨 Build and Test

1. Run `stewbeet` in your terminal
2. Reload your world with `/reload`
3. Get your item with `/loot give @s loot awesome_ores:i/ruby`

**Amazing!** 🎉 StewBeet automatically:
- ✅ Created the item model
- ✅ Generated the custom model data
- ✅ Added it to the resource pack
- ✅ Created proper item components
- ✅ Added it to the manual (if enabled)

## 🎯 Step 8: Add Your First Custom Block

Let's create a custom block:

### 🖼️ Add Block Textures

Add these textures to `assets/textures/blocks/`:
- `ruby_ore.png` - The main texture
- `ruby_sword.png` - A sword texture
- `ruby_chestplate.png` - A ruby chestplate texture
- `ruby_layer_1.png` - A layer texture for the top layer (it's how Minecraft handles custom armors)

### 🎯 Configure the Block

In your `ORES_CONFIGS` section in `setup_definitions.py`:

```python
ORES_CONFIGS: dict[str, core.EquipmentsConfig|None] = {
    "ruby": core.EquipmentsConfig(
        # This ruby is equivalent to diamond,
        equivalent_to = core.DefaultOre.DIAMOND,

        # But, has more durability (1.2 times more)
        pickaxe_durability = 1.2 * core.VanillaEquipments.PICKAXE.value[core.DefaultOre.DIAMOND]["durability"],

        # And, does 1 more damage per hit (mainhand), and has 0.5 more armor, and mines 20% faster (pickaxe)
        attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
    ),
}
```

### 🔨 Build and Test

1. Run `stewbeet`
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

One of StewBeet's coolest features is the automatic manual generation:

1. In Minecraft, run: `/loot give @s loot awesome_ores:i/manual`
2. Open the book to see your **automatically generated manual**
3. It includes all your items, recipes, and crafting information!

## 🎯 Step 10: Understanding the Configuration

Let's explore some key configuration options in `beet.yml`:

### 📁 Important Folders

```yaml
meta:
  stewbeet:
    # Where your textures are stored
    textures_folder: "assets/textures"
    
    # Where your sounds are stored  
    sounds_folder: "assets/sounds"
    
    # Where external libraries go
    libs_folder: "libs"
    
    # Where to copy finished packs
    build_copy_destinations:
      datapack: 
        - "C:/Users/YourName/.minecraft/saves/TestWorld/datapacks"
      resource_pack:
        - "C:/Users/YourName/.minecraft/resourcepacks"
```

### 🔧 Plugin Pipeline

The `pipeline` section controls what StewBeet does:

```yaml
pipeline:
    - "stewbeet.plugins.initialize"           # Set up framework
    - "src.setup_definitions"                 # Your item/block definitions  
    - "stewbeet.plugins.resource_pack.item_models"  # Generate models
    - "stewbeet.plugins.datapack.custom_blocks"     # Set up block mechanics
    - "stewbeet.plugins.auto.lang_file"             # Generate language files
    - "stewbeet.plugins.archive"                    # Create zip files
    # ... and many more!
```

## 🚀 Next Steps

Congratulations! You now have a working StewBeet project. Here's what to explore next:

### 📚 Learn More Features

(NOT UPDATED FOR NOW)
- **🔧 [Project Structure](1_project_structure.md)** - Understand the folder organization
- **🗄️ [Database Setup](2_database_setup.md)** - Advanced item and block definitions  
- **✍️ [Writing to Files](3_writing_to_files.md)** - Custom functions and data
- **🔗 [External Dependencies](4_external_dependencies.md)** - Using libraries
- **⚔️ [Adding a Sword](specific_guides/adding_a_sword.md)** - Practical example

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

- **📖 [Documentation](README.md)** - Comprehensive guides and references
- **💬 [Discord Server](https://discord.gg/anxzu6rA9F)** - Active community support
- **🐛 [GitHub Issues](https://github.com/Stoupy51/stewbeet/issues)** - Bug reports and feature requests
- **🎥 [YouTube Tutorial]()** - Soon

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

