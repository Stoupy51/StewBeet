
# Items and blocks

Declare an item or a block once, in Python. Every build writes its model, loot table, recipes, translations and manual page from that declaration.

You need a project: run the [Quickstart](../quickstart/en.md) first if you have none. Your declarations go in `src/definitions/additions.py`, the file every template keeps for them.

## 1. Add the textures

Put one PNG per item in `assets/textures/`, named after its id. StewBeet finds a texture by its name: `steel_ingot.png` is the texture of the item whose id is `steel_ingot`.

A block takes one texture for every face, or one per face such as `steel_block_top.png` and `steel_block_side.png`. The [texture patterns](../1_definitions_setup/en.md#recognized-texture-patterns) list every suffix StewBeet reads.

## 2. Declare the item

```python title="src/definitions/additions.py"
from stewbeet import *


def main():
	Item(
		id="steel_ingot",
		manual_category="materials",
		components={
			"item_name": "Steel Ingot",
		},
	)
```

Creating the `Item` registers it: there is no list to add it to. `components` takes any Minecraft item component, written without `minecraft:`.

## 3. Add a furnace recipe

A recipe goes in the `recipes` list of the item it makes:

```python
iron = Ingr("minecraft:iron_ingot")
Item(
	id="steel_ingot",
	manual_category="materials",
	components={
		"item_name": "Steel Ingot",
	},
	recipes=[
		SmeltingRecipe(ingredient=iron),
		BlastingRecipe(ingredient=iron),
	],
)
```

A furnace now turns an iron ingot into a steel ingot, and a blast furnace does it twice as fast. `cookingtime` sets the duration in ticks, 200 in a furnace and 100 in a blast furnace by default, and `experience=0.7` gives the experience of a vanilla ore. `SmokingRecipe` takes the same arguments.

## 4. Declare a block

A `Block` is an item that can be placed. Its `vanilla_block` holds its place in the world, so it decides how the block sounds, how long it takes to mine and which tool mines it:

```python
steel = Ingr("steel_ingot")
Block(
	id="steel_block",
	vanilla_block=VanillaBlock(
		id="minecraft:iron_block",
	),
	manual_category="materials",
	components={
		"item_name": "Steel Block",
	},
	recipes=[
		CraftingShapedRecipe(
			shape=["XXX", "XXX", "XXX"],
			ingredients={"X": steel},
		),
	],
)
```

`Ingr("steel_ingot")` is one of your items, `Ingr("minecraft:iron_ingot")` a vanilla one. A recipe makes one of the item it belongs to: set `result_count` for more, or `result=Ingr(...)` to make something else. The [Custom blocks](../plugins/datapack.custom_blocks.md) page lists every file a block gets and every `VanillaBlock` option.

## 5. Build and get them in game

```bash
uv run stewbeet build
```

In your world, run `/reload`, then `/function <namespace>:_give_all` to get every item, or `/loot give @s loot <namespace>:i/steel_block` for one. The namespace is the `id` in your `beet.yml`.

## Where each recipe ends up

| Ingredients | What the build writes |
|---|---|
| Vanilla items only | A recipe file in `data/<namespace>/recipe/` |
| One of your items, crafted | A recipe for the Smithed Crafter library |
| One of your items, cooked | A recipe for the Furnace NBT Recipes library |

Vanilla recipes cannot check custom data, which is why your own items go through a library. The build adds each library to the pack when a recipe needs it.

## Next steps

- [Definitions](../1_definitions_setup/en.md): every field of `Item` and `Block`, and every recipe type.
- [Tutorial, step 7](../0_getting_started/en.md#7-add-a-whole-ore-tier): an ore, its tools and its armour from one material entry.

