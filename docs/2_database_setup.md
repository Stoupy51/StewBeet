
# Database setup
The database is the thing where you will define all your custom items and blocks. The main function in [`setup_database.py`](../user/setup_database.py) must return a dictionnary where keys are items ids, and values are a dictionnary that defines the item:
```json
{
    "super_iron_block": {...},
    "super_iron_ore": {...},
    ...
}
```

## 📚 Defining the item
When you are defining an item in your database, there are 4 things to know.<br>
Don't be afraid to miss something, there is a database verification at run time that will point you out some errors you might have done during your setup.<br>
Along with this, if you set up the configuration correctly, a dump of your database will be done at the same moment for you to look up.

### ❗️ Mandatory keys
The value dictionnary must have some key/value pairs to define an item.
1. The `id` key: the value must be a string to a minecraft item like "minecraft:stone". But, if you want your item to not act like a vanilla item, you can use the `CUSTOM_ITEM_VANILLA` constant that will point to an item that can be used in survival mode.
2. The `item_name` key: the value must be a string containing a Text Component such as `'{"text":"My Item"}'`. Prefer using the `add_item_name_and_lore_if_missing()` function that will automatically adds the item_name key based on the item id, ex: "super_iron_block" -> "Super Iron Block".


### 📦 Custom blocks
Dealing with custom blocks in Minecraft vanilla is very hard because of challenges such as placement and destroy detections, vanilla block facade, etc.<br>
To simplify, you will use the `CUSTOM_BLOCK_VANILLA` constant for the `id` key which is basically a furnace (to get facing when placing block)<br>
Alternatively, you should use the `CUSTOM_BLOCK_ALTERNATIVE` constant if your block is placeable on walls (like ladders) or on a player (like flowers and seeds).

When defining a custom block in the database, you must define more key/value pairs such as:
- `VANILLA_BLOCK` constant key: the value must be a dictionnary of 2 key/value pairs to define the block properties when placed, ex: `{"id": "minecraft:iron_block", "apply_facing": False}`
  - the `id` key must lead to a valid vanilla block. Actually, it can be any string that is valid within a /setblock command, like `minecraft:barrel[container=[...]]`
  - the `apply_facing` key must lead to a boolean (true/false). Usually, this is set to true when placing furnaces, barrels, ladders, etc. (every block having a facing property)

If you want to setup a custom ore, the recommendation is to use the `VANILLA_BLOCK_FOR_ORES` constant for the value of the `VANILLA_BLOCK` key.<br>
The reason is that the library will use an optimization trick which also includes fortune and silk touch enchantments support.<br>
Additionnally, the `NO_SILK_TOUCH_DROP` key should lead to an item id you made in the database, see example here:<br>
```json
{
    "super_iron_ore": {
      ...,
      VANILLA_BLOCK: VANILLA_BLOCK_FOR_ORES,
      NO_SILK_TOUCH_DROP: "raw_super_iron"
    },
    ...
}
```


### Recipes


### More special keys


### Utility functions


### Remaining


## 🗞 Conclusion
Thank you for reading.

