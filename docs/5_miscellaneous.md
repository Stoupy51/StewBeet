
# 🔧 Miscellaneous Features
This documentation covers various features and examples that didn't really fit in other categories.


## 🗄️ SimpleDrawer's Compacting Drawer
If you're adding custom materials to your datapack, you might want to add compatibility for SimpleDrawer's compacting drawers 🗄️.<br>
By default, the process is handled automatically and will recognize patterns in your recipes to create compacting drawer recipes ✨.<br>
For instance,
- If you have a steel block 🧊, steel ingots ⚔️ and steel nuggets 💎, having recipes that link them,
- It will create a compacting drawer recipe that turns steel ingots into a steel block and steel nuggets into a steel ingot.
- The recipe ratio is by default `1:9:81`, but the program will detect the ratio used in your recipes and use the same one.
- For instance, if you have a `1:4:16` ratio defined in your recipes, it will create a `1:4:16` ratio for the compacting drawer recipe.

In case you don't want this behavior, you can still use `delete_files("simpledrawer/")` during link process to remove the compacting drawer recipes.<br>
They are generated at [`your_namespace:calls/simpledrawer/material`](../build/datapack/data/your_namespace/function/calls/simpledrawer/material.mcfunction) 📁.


## 🔮 SimplEnergy's Pulverizer Items
If you're adding custom materials to your datapack, and you have a dust item, you might want to add compatibility for SimplEnergy's pulverizer 🔮.<br>
By default, the process is handled automatically and will recognize patterns in your recipes to create pulverizer recipes ✨.<br>
For instance,
- If you have raw steel 🔩 (or steel ore) and steel ingots ⚔️,
- It will create a pulverizer recipe that turns raw steel into 2x steel dust 💧.
- Those 2 steel dust can be smelted into one steel ingot each.
- Additionally, you can pulverize 1x steel ingot into 1x steel dust.

In case you don't want this behavior, you can still use `delete_files("simplenergy/")` during link process to remove the pulverizer recipes.<br>
They are generated at [`your_namespace:calls/simplenergy/pulverizer_recipes`](../build/datapack/data/your_namespace/function/calls/simplenergy/pulverizer_recipes.mcfunction) 📁.


## 🔓 Recipe Unlocking
By default, vanilla recipes (ones that don't use custom items in ingredients) will be automatically unlocked for players whenever they discover an ingredient of said recipe.<br>
This behavior can be changed by deleting the advancement [`unlock_recipes.json`](../build/datapack/data/your_namespace/advancement/unlock_recipes.json) along with the reward function [`unlock_recipes.mcfunction`](../build/datapack/data/your_namespace/function/advancements/unlock_recipes.mcfunction) 📁.


## ⏰ Clock Functions for Custom Blocks
When creating custom blocks ⚡, you often need to run functions every tick or at regular intervals ⏰.<br>
For all custom blocks, the program will check if a function named `tick` or `second` is present in the custom block's folder 📁.<br>
If it is, the custom block will be granted additional tags on placement to identify it as a ticking block 🏷️.<br>
Then, proper functions will be created to run the `tick` or `second` code at the right time for each detected custom block 🔄.<br>
For instance,
- If you want an electric furnace to run a function every tick ⚡, you simply add a [`tick.mcfunction`](https://github.com/Stoupy51/SimplEnergy/blob/main/build/datapack/data/simplenergy/function/custom_blocks/electric_furnace/tick.mcfunction) file in the electric furnace's folder 📁.<br>
- Same goes for a `second.mcfunction` file, if you want the custom block to run a function every 20 ticks ⏳.
- The program will do everything else automatically, so you don't have to worry about a thing ✨.


## 📚 Conclusion
You now know how to:
- Create compacting drawer recipes for SimpleDrawer
- Add custom dust items for SimplEnergy's pulverizer
- Control recipe unlocking through advancements
- Set up clock functions for custom blocks

These features will help you create more complex and interactive datapacks!<br>
Thank you for reading 🙌

