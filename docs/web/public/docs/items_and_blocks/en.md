
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
		manual_category="material",
		components={
			"item_name": "Steel Ingot",
		},
	)
```

Creating the `Item` registers it: there is no list to add it to. `components` takes any Minecraft item component, written without `minecraft:`. `manual_category` is a free string, and the manual makes one page per exact value: the material generator writes `material` for ingredients and blocks and `equipment` for tools and armor, so `materials` and `material` are two pages.

## 3. Add a furnace recipe

A recipe goes in the `recipes` list of the item it makes:

```python
iron = Ingr("minecraft:iron_ingot")
Item(
	id="steel_ingot",
	manual_category="material",
	components={
		"item_name": "Steel Ingot",
	},
	recipes=[
		SmeltingRecipe(ingredient=iron),
		BlastingRecipe(ingredient=iron),
	],
)
```

A furnace turns an iron ingot into a steel ingot, and a blast furnace does it twice as fast. `cookingtime` sets the duration in ticks, 200 in a furnace and 100 in a blast furnace by default, and `experience=0.7` gives the experience of a vanilla ore. `SmokingRecipe` takes the same arguments.

## 4. Declare a block

A `Block` is an item that can be placed. Its `vanilla_block` holds its place in the world, so it decides how the block sounds, how long it takes to mine and which tool mines it:

```python
steel = Ingr("steel_ingot")
Block(
	id="steel_block",
	vanilla_block=VanillaBlock(
		id="minecraft:iron_block",
	),
	manual_category="material",
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

## Load your definition modules

beet runs the plugins listed under `pipeline` in `beet.yml`, in order. A project lists its definition entry files first, ahead of the plugins that read them:

```yaml title="beet.yml"
pipeline:
    - "src.definitions.setup_main"
    - "src.definitions.setup_external"
```

The entry file imports the other definition modules and calls them. SimplEnergy's `src/definitions/setup_main.py` does it in this order:

```python title="src/definitions/setup_main.py"
def beet_default(ctx: Context) -> None:
	generate_everything_about_these_materials(ORES_CONFIGS)
	add_recipes_for_all_dusts(DUSTS_CONFIGS)
	generate_custom_records("auto")

	material_additions()
	gear_additions()
	energy_additions()
	misc_additions()

	add_item_model_component(black_list = ["simple_cable", "advanced_cable", "elite_cable"])
	add_item_name_and_lore_if_missing()
	add_private_custom_data_for_namespace()
	add_smithed_ignore_vanilla_behaviours_convention()
	set_manual_components(white_list=["item_name", "lore", "custom_name", "attribute_modifiers"])
```

The last five calls complete every definition that exists when they run, so they come after the last module that declares one. Generators come before the modules that adjust what they made, because `Item.from_id` fails on an id nothing has declared yet.

An item with no `manual_category` has no manual page. The template gives the remaining ones `"miscellaneous"` in a loop over `Mem.definitions` before the final calls.

## Generate a whole material tier from one ingot

One entry of a dictionary, and the textures in `assets/textures/` decide what exists. `simplunium_ingot` has the base `simplunium`, so `simplunium_pickaxe.png` makes a pickaxe, `simplunium_helmet.png` a helmet, `raw_simplunium_block.png` a block of raw material:

```python title="src/definitions/additions/gear.py"
SIMPLUNIUM_EQUIPMENTS: EquipmentsConfig = EquipmentsConfig(
	DefaultOre.IRON,
	3 * VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"],
	{"attack_damage": 1, "armor": 0.5, "mining_efficiency": 2},
)
```

```python
generate_everything_about_these_materials({"simplunium_ingot": SIMPLUNIUM_EQUIPMENTS})

Block.from_id("simplunium_block").vanilla_block = VanillaBlock(id="minecraft:iron_block")
Block.from_id("raw_simplunium_block").vanilla_block = VanillaBlock(id="minecraft:raw_iron_block")
```

The tools and armor take the stats of iron, three times its durability, and the attributes added to them. Armor is generated only when a config is given. The generator picks the host of ores, but not of storage blocks, so the lines after the call set them.

## Give a block on and off states, or a facing

A block takes its model from the names of its textures. SimplEnergy's furnace generator has `furnace_generator_front.png`, `furnace_generator_side.png` and `furnace_generator_top.png`, which are the sides of the `orientable` model, and a `furnace_generator_front_on.png` for when it works:

```python
Block(
	id="furnace_generator",
	vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player"),
	manual_category="energy",
)
```

`block_facing="player"` rotates the furnace host as vanilla does, and the model follows it. A texture ending with `_on` makes the build write an `_on` model, which a furnace, smoker or blast furnace host shows while it burns. A block whose textures fill no pattern stops the build and lists the patterns it knows, which are all in [Recognized texture patterns](../1_definitions_setup/en.md#recognized-texture-patterns).

## Add a bow with pull animations

Give an item `minecraft:bow` as its `base_item`, and number the textures of its stages from 0:

```python
Item(
	id="stardust_bow",
	base_item="minecraft:bow",
	manual_category="equipment",
	components={"max_damage": 768},
)
```

With `stardust_bow.png`, `stardust_bow_pulling_0.png`, `stardust_bow_pulling_1.png` and `stardust_bow_pulling_2.png` in the textures folder, the build writes a model for each pulling texture and an item model switching between them as the bow is drawn. A crossbow does the same from `_pulling_<n>`, and shows a loaded arrow or firework rocket from `<id>_arrow.png` and `<id>_firework.png`. `RangedWeapon` tunes a crossbow's charge time, damage and ammunition, as in [RangedWeapon](../1_definitions_setup/en.md#rangedweapon).

## Change an item another module declared

`Item.from_id(id)` returns the object a module registered, whatever module runs it, so a later module sets fields on it instead of declaring the item again:

```python
simplunium = Item.from_id("simplunium_ingot")
simplunium.wiki_buttons = [WikiButton({"text": "Found as simplunium ore, or made from its raw form.", "color": "yellow"})]
simplunium.recipes.append(CraftingShapelessRecipe(category="misc", ingredients=[Ingr("simplunium_block")], result_count=9))
```

`Item(id="simplunium_ingot")` for an id already declared changes nothing: the first object stays registered, and the build warns that the second is ignored. Assigning a new list to `recipes` replaces the generated recipes, `append` keeps them.

## Run commands when a custom block is placed

Every function of a block has a name on `Block.functions`, so no path is typed by hand. `place_secondary` runs as the display entity the block summons when it is placed:

```python title="src/link.py"
solar_panel = Block.from_id("solar_panel")
solar_panel.functions.place_secondary.obj.append("""
data modify entity @s transformation.scale[1] set value 1.005f
data modify entity @s transformation.translation[1] set value 0.002f
""")
```

`.obj` is the beet function, which exists once `stewbeet.plugins.datapack.custom_blocks` has run, so this goes in a plugin listed after it in `pipeline`, such as the template's `src/link.py`. Earlier it raises `KeyError`, where `write_function` would put the commands ahead of the block's own setup. `BlockFunctions("solar_panel")` gives the same paths without a definition lookup. The other names, such as `second` and `destroy`, are in [Resource locations and BlockFunctions](../1_definitions_setup/en.md#resource-locations-and-blockfunctions).

## Next steps

- [Definitions](../1_definitions_setup/en.md): every field of `Item` and `Block`, and every recipe type.
- [Tutorial, step 7](../0_getting_started/en.md#7-add-a-whole-ore-tier): an ore, its tools and its armour from one material entry.

