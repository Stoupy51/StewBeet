
# 🔄 Migration Guide
This guide will help you migrate your project to use Python Datapack in a few simple steps.

## 🔧 Prerequisites
Before migrating your project, make sure you have:
- 🐍 Python 3.12 or higher installed.
- 📦 A working datapack that you want to migrate.
- 📚 Understood the [project structure](./1_project_structure.md) with the guide.


## 📦 Fast Migration Steps
1. 📥 Clone or download this template repository.
2. 📋 Move your datapack and resource pack files into the [`merge` folder](../merge).
3. ⚙️ Configure your [`config.py`](../config.py) with your project details.
4. 🚀 Run `build.py` and check the generated files in the [`build` folder](../build).

⚠️ Note that by doing this, you will not use efficiently the Python Datapack features (custom items, blocks, etc.).<br>
I recommend you read the next section "Advanced Migration Steps" for a better migration.

### 🚨 Important Notes
Be aware that the [tick and load](../build/datapack/data/your_namespace/function/v1.21.615/tick.mcfunction) functions will probably not match your existing ones,<br>
so you will have to either:
- 🗑️ Remove them and write your own logic in `user/link.py`
- 🔄 Change their paths in the merge folder to match the generated ones


## 🔍 Advanced Migration Steps

### 🖼️ Setting Up the Assets Folder
In this section, we will setup the assets folder and move your textures to it.

As [1_project_structure.md](./1_project_structure.md) explains, the assets are located in the `assets` folder.<br>
Here is the structure of the assets folder, and what you need to do:

```bash
assets/
├── textures/       # Item and block textures 
├── sounds/         # Custom sounds
├── original_icon.png   # Your datapack icon
```

1. **Move Textures** 🖼️: Move all your item and block textures to the `assets/textures/` folder. Ensure textures follow basic naming conventions:
   - Item textures should match their item IDs (e.g., "ruby_sword" would be `ruby_sword.png`) 🗡️
   - Block textures should use suffixes like `_top`, `_bottom`, `_front`, etc. (e.g., "iron_furnace" would be `iron_furnace_top.png`, `iron_furnace_bottom.png`, `iron_furnace_front.png`, `iron_furnace_side.png`) 📦
   - The system will automatically convert suffixes like `_up` to `_top`, `_down` to `_bottom`, etc. in case you used them before. ✨

2. **Add Pack Icon** 🎨: If you have a custom icon, place it as `assets/original_icon.png` and it will be used for both datapack and resource pack (and more like the generated Manual).

3. **Sound Files** 🔊: Place any custom sound files (`.ogg`) in the `assets/sounds/` folder. The system will automatically create the necessary sound definitions for them.

### Custom Items and Blocks Database Setup 🛠️

1. **Understanding the Database Structure** 📊: The core of Python Datapack is the database system in `user/database.py`. This is where you define all your custom items and blocks.

2. **Basic Database Structure** 📝: Each item in the database is a dictionary entry with properties that define its behavior:
   - Use the `id` key to specify the base vanilla item (like `minecraft:command_block` for items) 🔑
   - For custom blocks, use `CUSTOM_BLOCK_VANILLA` constant as the ID 🧱
   - Define your item's appearance with `item_model` and other visual properties ✨
   - Use `CATEGORY` for organizing items in the manual 📚

3. **Custom Blocks** 🧱: For blocks that players can place in the world:
   - Use the `VANILLA_BLOCK` property to specify what block should be placed when your item is used 🏗️
   - Configure block interactions and behaviors through custom functions 🔄
   - Add additional properties like drops for mining with or without silk touch 💎

4. **Material Generation** ⚒️: For materials (like ores, ingots, tools, and armor):
   - Use the `generate_everything_about_this_material` helper function to create complete material sets 🔨
   - This automatically creates items, blocks, crafting recipes, and textures relationships ✨

5. **Recipes** 📜: To define how items can be crafted:
   - Use the `RESULT_OF_CRAFTING` key to specify crafting recipes 🍳
   - Define shaped or shapeless recipes with ingredients using helper functions 🧩
   - Support for furnace recipes and other crafting types 🔥

### Avoiding Conflicts Between Merge Files and Generated Files ⚠️

1. **Versioned Function Structure** 🔢: Python Datapack creates functions with version numbers in the path (e.g., `v1.21.615/tick.mcfunction`). When migrating:

   - **Option 1** ❌: Modify your merge folder structure to match the versioned paths (bad practice since you'll have to update it every time you update the project version)
   - **Option 2** ✅: Create custom calls in `user/link.py` to connect versioned functions with your existing ones (recommended)

2. **Understanding Function Generation** 🔄: Python Datapack automatically generates various functions:
   - Load and tick functions ⏱️
   - Custom block placement and interaction functions 🧱
   - Recipe unlock functions 🔓
   - Consider reviewing these generated functions to avoid duplications or conflicts 🔍

3. **Working with Legacy Code** 📜: If you have existing functionality:
   - Add/Modify function calls to connect the generated system with your existing functions 🔗
   - Gradually migrate features to use Python Datapack's native capabilities 📈

4. **Incremental Migration** 🚶‍♂️: Consider migrating your datapack in phases:
   - Start with basic structure and essential files 🏗️
   - Then add custom items and blocks 🧰
   - Finally implement more complex features like manual pages and custom block behaviors 🌟


## 🎯 Next Steps
After migrating:
1. Test in Minecraft to ensure everything works
2. Start using Python Datapack's features to enhance your datapack!


## 📚 Conclusion
You now know how to:
- Migrate an existing project to use Python Datapack
- Handle potential conflicts with tick/load functions
- Start enhancing your project with Python Datapack features

Migration can seem daunting at first, but Python Datapack makes it as simple as possible! 🎉<br>
The benefits of using Python Datapack will quickly become apparent as you explore its features.

Thank you for reading 🙌

