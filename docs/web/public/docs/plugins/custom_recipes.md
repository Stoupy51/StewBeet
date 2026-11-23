
# Recipes

Turns the `recipes` of each item of your definitions into recipe files and functions, so players can craft, smelt, cut or smith your items.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.custom_recipes`, and reads the item definitions with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/custom_recipes/__init__.py)

## Declare a recipe

```python
Item(
  id="super_stone",
  base_item="minecraft:stone",
  recipes=[
    CraftingShapedRecipe(
      category="building",
      shape=["XXX", "XXX", "XXX"],
      ingredients={
        "X": Ingr("minecraft:stone"),
      },
    ),
  ],
)
```

The item is the result, unless the recipe sets `result`. `Ingr("minecraft:stone")` is a vanilla item, `Ingr("steel_ingot")` an item of your project.

## What this plugin writes

An ingredient that is a plain vanilla item gives a vanilla recipe file. An ingredient that is one of your items cannot be in a recipe file, so the recipe goes to a library instead.

- `recipe/<item>.json`: one for each crafting, smelting, blasting, smoking, campfire, stonecutting and smithing recipe whose ingredients are all vanilla items. A second recipe of the item is `<item>_2`.
- `function/utils/get_all_recipes`: gives the player every recipe above.
- `advancement/unlock_recipes`: gives a recipe when the player holds one of its ingredients or its result. It calls `function/advancements/unlock_recipes`.
- `function/calls/smithed_crafter/shapeless_recipes` and `shaped_recipes`: every crafting recipe, tagged for [Smithed Crafter](https://wiki.smithed.dev/libraries/crafter/), which gives the result from the item's loot table. A custom ingredient adds the library to the pack.
- `function/calls/furnace_nbt_recipes/<type>_recipes`: every smelting, blasting and smoking recipe, for [Furnace NBT Recipes](https://github.com/Stoupy51/FurnaceNbtRecipes), with its experience in `recipes_used`. This is how a furnace takes a custom ingredient.
- `function/calls/simplenergy/pulverizer_recipes`: the `PulverizingRecipe` of SimplEnergy's pulverizer.
- `function/calls/stardust/awakened_forge_recipes`: the `AwakenedForgeRecipe` of Stardust Fragment's forge, with a `timer` and a `craft` function for each result.

An item with `remainder` also gets the `use_remainder` component, holding that container.

## Options

Every recipe takes:

| Option | Default | What it does |
|---|---|---|
| `result` | the item | What the recipe gives, as an `Ingr` |
| `result_count` | `1` | How many it gives |
| `category` | `None` | The recipe book tab |
| `group` | `None` | The recipe book group |
| `smithed_crafter_command` | `None` | The command run instead of giving the loot table, for crafting recipes |

Cooking recipes add `experience` (`0.0`) and `cookingtime` in ticks: `200` for smelting, `100` for blasting and smoking. `CampfireCookingRecipe` needs both. On 26.3 and later, blasting and smoking recipe files store twice your `cookingtime`, which the block halves.

## Limits

- A recipe type the plugin does not know raises `Invalid recipe type` when the definition is built.
- A shaped recipe holds at most 3 rows of 3 columns, all rows the same width.
- A stonecutting or smithing recipe with a custom ingredient is skipped, no file and no function.
- A campfire recipe with a custom ingredient is skipped too.
- A furnace recipe adds the Furnace NBT Recipes library to the pack.
- The first ingredient of an awakened forge recipe holds at most 64 items.

## Next steps

- [Definitions](../1_definitions_setup/en.md#recipe-system): every recipe class with its fields.

