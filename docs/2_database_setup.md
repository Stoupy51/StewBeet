
# 🗃️ Database setup
The database is the thing where you will define all your custom items and blocks. The main function in [`setup_database.py`](../user/setup_database.py) must return a dictionnary where keys are items ids, and values are a dictionnary that defines the item:
```json
{
    "steel_block": {...},
    "steel_ore": {...},
    ...
}
```

## 📚 Defining the item
When you are defining an item in your database, there are many things to know.<br>
Don't be afraid to miss something, there is a database verification 🛡️ at run time that will point you out some errors you might have done during your setup.<br>
Along with this, if you set up the configuration correctly, a [dump](../database_debug.json) of your database will be done at the same moment for you to review 📊.<br>


### ❗️ Mandatory keys
The value dictionnary must have some key/value pairs to define an item.
1. The `id` key: the value must be a string to a minecraft item like "minecraft:stone". But, if you want your item to not act like a vanilla item, you can use the `CUSTOM_ITEM_VANILLA` constant that will point to an item that can be used in survival mode.
2. The `item_name` key: the value must be a string containing a Text Component such as `'{"text":"My Item"}'`. Prefer using the `add_item_name_and_lore_if_missing()` function that will automatically adds the item_name key based on the item id, ex: "steel_block" -> "Steel Block".


### 📦 Custom blocks
Dealing with custom blocks in Minecraft vanilla is very hard because of challenges such as placement and destroy detections, vanilla block facade, etc.<br>
To simplify, you will use the `CUSTOM_BLOCK_VANILLA` constant for the `id` key which is basically a furnace (to get facing when placing block)<br>
Alternatively, you should use the `CUSTOM_BLOCK_ALTERNATIVE` constant if your block is placeable on walls (like ladders) or on a player (like flowers and seeds).

When defining a custom block in the database, you must define more key/value pairs such as:
- `VANILLA_BLOCK` constant key: the value must be a dictionnary of 2 key/value pairs to define the block properties when placed, ex: `{"id": "minecraft:iron_block", "apply_facing": False}`
  - the `id` key must lead to a valid vanilla block. Actually, it can be any string that is valid within a /setblock command, like `minecraft:barrel[container=[...]]`
  - the `apply_facing` key must lead to a boolean (true/false). Usually, this is set to true when placing furnaces, barrels, ladders, etc. (every block having a facing property)

If you want to setup a custom ore, the recommendation is to use the `VANILLA_BLOCK_FOR_ORES` constant for the value of the `VANILLA_BLOCK` key.<br>
The reason is that the package will use an optimization trick ⚒️ which also includes fortune and silk touch enchantments support.<br>
Additionnally, the `NO_SILK_TOUCH_DROP` key should lead to an item id you made in the database, see example here or in the [`database setup`](../user/setup_database.py):<br>
```json
{
    "steel_ore": {
      ...,
      VANILLA_BLOCK: VANILLA_BLOCK_FOR_ORES,
      NO_SILK_TOUCH_DROP: "raw_steel"
    },
    ...
}
```


### 🍳 Recipes
The recipes in the database must be defined the same way as [vanilla recipes](https://misode.github.io/recipe/) but with little changes.<br>
An utility function `ingr_repr()` is available to "encode" ingredients or result of a recipe to a dictionnary.<br>
If you want the representation of a vanilla item, you will write `ingr_repr("minecraft:stone")` for example.<br>
Alternatively, if you want the representation of a custom item you made, use the function like this: `ingr_repr("steel_ingot", NAMESPACE)` where the namespace is the one you put in the [`config.py`](../config.py) file.<br>
The reason of this format is to bring NBT crafting 🧪 as simple as possible, don't need to worry everything will be automatic.

You have two ways of writing recipes in the database:
1. The `RESULT_OF_CRAFTING` key should lead to a list of recipes where the result is by default the item where you are writing recipes for (so the result key is omitted).
2. The `USED_FOR_CRAFTING` key should also lead to a list of recipes but the result is mandatory. I strongly recommend you not using this key but `RESULT_OF_CRAFTING` instead whenever it is possible, the reason is to keep consistency 🔁 within your recipes.

Not all recipe types are recognized, only crafting table and all smelting types are recognized along with custom type `PULVERIZING` (from SimplEnergy).<br>
Meaning that you should use the [`link.py`](../user/link.py) script to write missing recipes yourself or use the [`merge`](../merge/) folder 🔗.

Now, let's imagine a super diamond made of 8 diamonds and a steel ingot, we also want the super diamond to uncraft to 5 diamond block, then you will write something like this in the database setup:
```py
database["super_diamond"] = {
	...

	RESULT_OF_CRAFTING: [
		{"type":"crafting_shaped","result_count":1,"group":"super_diamond","category":"misc","shape":["XXX","XIX","XXX"],"ingredients": {"X": ingr_repr("minecraft:diamond"), "I":ingr_repr("steel_ingot", NAMESPACE)}},
	],

  USED_FOR_CRAFTING: [
    {"type":"crafting_shapeless","result_count":5,"group":"super_diamond","category":"misc","ingredients":[ingr_repr("super_diamond", NAMESPACE)], "result":ingr_repr("minecraft:diamond_block")},
  ],
}
```

### 💫 More special keys
A few more keys are available for the database setup:
- `CATEGORY`: Leading to a simple string, the category is used to organize the manual 📖. If an item doesn't have a category, a warning message will be shown in console during build process and the item won't show up in the in-game manual.
- `OVERRIDE_MODEL`: Since the build process will automatically try to recognize textures patterns, it might fail or you want to put a custom model 🧰 to your item. This is why you can override parts or everything in the generated model by bringing the model in the value of this key. For instance, [SimplEnergy's Electric Brewing Stand](https://github.com/Stoupy51/SimplEnergy/blob/main/user/database/additions.py) use it.
- `SMITHED_CRAFTER_COMMAND`: Crafts with custom ingredients are not possible in vanilla, so we use the Smithed Crafter library to handle that. By default, the build process will automatically generate loot tables 🗃️ for recipes and use them for the smithed crafter. You can override the loot table command by using this key **__in the recipe definition__** to run whatever you want, such as running a function instead of a loot table. For instance, [Armored-Elytra](https://github.com/e-psi-lon/Armored-Elytra/blob/main/user/setup_database.py#L22) use it.


### 🔑 The other keys
You may want to add other [components](https://minecraft.wiki/w/Data_component_format) such as food, durability, dyed color, etc.
Those are automatically recognized, you don't need to put them in a "components" key for an item:
```json
"steel_helmet": {
  // Mandatory keys:
  "id": "minecraft:leather_helmet",

  // Automatically recognized components of the item:
  "custom_data": {"smithed": {"dict": {"armor": {"steel": true,"helmet": true}},"ignore": {"functionality": true,"crafting": true}},"your_namespace": {"steel_helmet": true}},
  "dyed_color": {"rgb": 4605510,"show_in_tooltip": false},
  "max_damage": 495,
  "attribute_modifiers": [{"type": "armor","amount": 2.5,"operation": "add_value","slot": "head","id": "your_namespace:armor.head"}],
  "custom_model_data": 30008,
  "item_name": "{'text': 'Steel Helmet', 'italic': false, 'color': 'white'}",
  "lore": ["{'text': 'Template', 'italic': true, 'color': 'blue'}"]
},
```


### 🛠️ Utility functions
Within the `database_helper` import, multiple functions are present to help you complete your database.<br>
This section will not detail function parameters but will just enumerate them, check the template for use cases.
- `generate_everything_about_these_materials()`: 🧪 Will seek for every item related to the given materials such as armor, tool, nugget, etc.
- `add_recipes_for_all_dusts()`: ⚙️ Add recipes for dusts using special compatiblity with SimplEnergy's pulverizer.
- `generate_custom_records()`: 🎶 Will seek for every .ogg file in the [records folder](../assets/records/) and add them to the database.
- `deterministic_custom_model_data()`: 📜 Uses the [`cmd_cache.json`](../cmd_cache.json) file to give custom model data to every item in the database.
- `add_item_name_and_lore_if_missing()`: 🧻 Adds item name and lore components for every item in the database if missing.
- `add_private_custom_data_for_namespace()`: 🔍 Adds a custom data component to easily identify the item with commands.
- `add_smithed_ignore_vanilla_behaviours_convention()`: 🚫 As the name implies, adds custom data for a Smithed convention.


## 📚 Conclusion
As there are many things to cover when setting up the database, you probably don't need to know everything for your project. The important thing is to know where you can find information, come back here when you'll need it!<br>
Thank you for reading 🙌.

