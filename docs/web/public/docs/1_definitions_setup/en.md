
# Definitions reference

A definition is a Python object registered in `Mem.definitions` when it is created. The build plugins read that dictionary to write models, loot tables, recipes, translations and the in-game manual. For a walkthrough, see [Items and blocks](../items_and_blocks/en.md).

## Mem.definitions

`Mem.definitions` is a `dict[str, Item]` keyed by id, without namespace. Creating an `Item`, or any subclass of it, registers the object under its `id`.

```python
item = Item(id="life_crystal")
assert Item.from_id("life_crystal") is item
assert "life_crystal" in Mem.definitions
```

| Call | What it does |
|---|---|
| `Item.from_id(id)` | Returns the registered object, of whatever class it was created with. Raises `KeyError` when there is none. |
| `Item.from_id(id, strict=False)` | Same, and creates and registers an `Item(id=id)` when there is none. |
| `Mem.definitions[id]` | The same object, without a class check. |

An item created with an `id` already in `Mem.definitions` is not registered: the build warns, the registered object keeps all its fields, and `Item.from_id(id)` keeps returning the first one. An empty `id` is never registered. To change an existing definition, fetch it with `from_id` and set its fields.

`Mem.external_definitions` holds the `ExternalItem` objects, keyed by `namespace:id`. An `Ingr` naming an item of another datapack reads them.

| Field | Type | Default | What it does |
|---|---|---|---|
| `id` | `str` | required | `namespace:id` of the item, as in `simplenergy:machine_block`. |
| `custom_data_predicate` | `JsonDict \| str` | required | What the item's `custom_data` must contain for a recipe to match it. |
| `components` | `JsonDict` | `{}` | Components of the item, written without `minecraft:`. |
| `loot_table` | `str \| Resource[LootTable] \| None` | `None` | Loot table of the other datapack giving the item. A recipe that gives the item as its result needs it. |
| `base_item` | `str` | `CUSTOM_ITEM_VANILLA` | Vanilla item the external item is based on. |

## Item

`Item` is a keyword-only dataclass.

| Field | Type | Default | What it does |
|---|---|---|---|
| `id` | `str` | required | Unique id. A `:` in it prints a warning and keeps the part after the last `:`. |
| `base_item` | `str` | `CUSTOM_ITEM_VANILLA` (`minecraft:recovery_compass`) | Vanilla item the custom item is built on. `minecraft:` is added when missing. |
| `manual_category` | `str \| None` | `None` | Category of the item in the in-game manual. Without one the item has no manual page. See [Manual categories](#manual-categories). |
| `recipes` | `list[RecipeBase]` | `[]` | Recipes giving this item. Each recipe without a `group` gets the item's id. A tag ingredient such as `#minecraft:eggs` is replaced by one recipe per item of the tag. |
| `override_model` | `JsonDict \| None` | `None` | Merged over the model generated from the textures. `{}` writes no model file. |
| `hand_model` | `JsonDict \| None` | `None` | Model shown in every display context except those of `override_model_contexts`. |
| `override_model_contexts` | `list[str] \| None` | `None` | Display contexts keeping the regular model when `hand_model` is set. `None` means `Item.DEFAULT_OVERRIDE_MODEL_CONTEXTS`: `["none", "fixed"]`, the item display entities and item frames. |
| `wiki_buttons` | `list[WikiButton] \| TextComponent \| None` | `None` | Buttons of the item's manual page. Setting it without `manual_category` prints a warning. See [Wiki buttons and the manual item](#wiki-buttons-and-the-manual-item). |
| `components` | `JsonDict` | `{}` | Item components. A `minecraft:` prefix on a key is removed. A key starting with `!` removes the component and its value is reset to `{}`. |
| `skip_gives` | `bool` | `False` | Leaves the item out of the loot tables and of the give-all function. |
| `remainder` | `str \| None` | `None` | Id of the definition left once the item is eaten or drunk. It becomes the `use_remainder` component, carrying the container's `item_name`, `item_model` and `custom_data`, and the manual links the two pages. |
| `ranged_weapon` | `RangedWeapon \| None` | `None` | Tuning of a bow or crossbow. See [RangedWeapon](#rangedweapon). |

The class also carries `origin`, a field set by the `source_maps` plugin that is not a constructor argument.

```python
Item(
	id="stardust_ingot",
	manual_category="material",
	components={"item_name": {"text": "Stardust Ingot", "color": "aqua"}, "max_stack_size": 99},
)
```

## Block class

`Block` extends `Item` with the fields below. Its `base_item` defaults to `CUSTOM_BLOCK_VANILLA` (`minecraft:furnace`), which gives the item a `container` component carrying the Smithed custom block data and hides it from the tooltip.

| Field | Type | Default | What it does |
|---|---|---|---|
| `vanilla_block` | `VanillaBlock \| None` | `None` | Vanilla block placed in the world as the block's host. |
| `no_silk_touch_drop` | `NoSilkTouchDrop \| LootTable \| str \| None` | `None` | What drops when the block is broken without silk touch. A `str` is an item id, dropping one of it. A `LootTable` is rolled as it is. |
| `mining` | `Mining \| None` | `None` | Tool needed to get the item. See [Mining](#mining). |
| `growing_seed` | `GrowingSeed \| None` | `None` | Makes the block a seed that grows over time. See [GrowingSeed](#growingseed). |
| `on_place` | `str \| None` | `None` | Commands appended to the placement functions. Prints a warning at build, `functions.place_secondary.obj.append(...)` does the same without it. |

`BlockAlternative` is a `Block` whose `base_item` is `minecraft:item_frame`: the block is placed as an item frame, and its `vanilla_block` is `VanillaBlock(contents=True)`. `BlockHead` is a `Block` whose `base_item` is `minecraft:player_head`: the block is placed as a player head, and its `vanilla_block` id carries the head's profile.

```python
BlockHead(
	id="stardust_cable",
	manual_category=ENERGY,
	vanilla_block=VanillaBlock(id="minecraft:player_head{profile:" + str(stardust_cable_profile) + "}"),
	components={"custom_data": {"energy": {"transfer": 480}}, "profile": stardust_cable_profile},
)
```

A regular `Block` has no placement advancement of its own, since the Smithed custom block library detects it. `BlockAlternative` and `BlockHead` have one, `Block.advancement`.

### VanillaBlock configuration

| Field | Type | Default | What it does |
|---|---|---|---|
| `id` | `str \| None` | `""` | Vanilla block id with optional states, as in `minecraft:furnace[lit=false]`. `minecraft:` is added when missing. `None` with `contents=True`. |
| `contents` | `bool` | `False` | The block has no vanilla block and is held by an item frame. Sets `id` to `None`. Incompatible with `block_facing`. |
| `block_facing` | `False \| "player"` | `False` | `"player"` rotates the placed host as vanilla does: towards the player for a furnace, the way the player looks for stairs and fence gates. Sets `visual_facing` to `"player"` when that is left at `"none"`. |
| `visual_facing` | `"none" \| "player" \| "item_frame"` | `"none"` | Orientation of the displayed model. `"player"` gives four horizontal directions, `"item_frame"` the six of the frame's `Facing`. |
| `apply_facing` | `False \| True \| "entity" \| None` | `None` | Shorthand for the two fields above. `True` sets both to `"player"`, `"entity"` sets `visual_facing` to `"player"`. |
| `half` | `"click" \| None` | `None` | A slab, stairs or trapdoor host takes its half from where the player clicked. Raises `ValueError` for another host. |
| `interaction` | `Interaction \| None` | `None` | Interaction entity breaking the block when hit. For a host without collision. |
| `uvlock` | `bool` | `False` | Shows a copy of the model turned for each facing instead of turning the display, so its textures keep the world grid. Needs `visual_facing="player"`. |
| `margin` | `float` | `1.002` | Scale of each element of the displayed model about its own center, so no face lies on a face of the host. `1.0` leaves the size. Ignored with `contents=True`. |
| `machine_speed` | `float \| None` | `None` | A furnace, smoker, blast furnace or brewing stand cooks or brews this many times faster. Raises `ValueError` for another host. |

`half="click"` reads where the player clicked from `{ns}:custom_blocks/_aim/main`. The `type` of a slab and the `half` of stairs and trapdoors take the result. `#floor {ns}.data` is also left at 1 when the player clicked the top of the block below.

A stairs host takes a corner `shape` from its neighbours, and its display follows it every second with a copy of the model cut from its elements, drawn facing south. A furnace, smoker or blast furnace host with an `_on` model shows it while it burns. Both switch through the display's `custom_model_data` string, and only for a model StewBeet draws.

### Interaction

| Field | Type | Default | What it does |
|---|---|---|---|
| `width` | `float` | `1.01` | Width of the interaction entity. |
| `height` | `float` | `1.01` | Height, from the bottom of the block. A little more than a block so it is targeted before the host. |
| `seat` | `float \| None` | `None` | Height above the bottom of the block at which using it seats the player. `None` is no seat. |
| `hits` | `int` | `1` | Hits needed to break the block. Each counts only when it comes less than `hit_timeout` ticks after the previous one. |
| `hit_timeout` | `int` | `20` | Ticks between two counted hits. |
| `sound` | `str` | `minecraft:block.stone` | Sound group, played as `<sound>.hit` on each hit and `<sound>.break` on the break. |

Hosts without collision or that cannot be mined are `minecraft:barrier`, `minecraft:structure_void` and `minecraft:light[level=N]`. Hitting the entity breaks the block and drops its item unless the breaker is in creative. Commands run when a player uses the interaction go in `{ns}:custom_blocks/_interaction/use`, run as the interaction with the player tagged `{ns}.user`.

```python
Block(
	id="chair",
	vanilla_block=VanillaBlock(id="minecraft:barrier", visual_facing="player", interaction=Interaction(seat=0.5, hits=3, sound="minecraft:block.wood")),
)
```

### Mining

| Field | Type | Default | What it does |
|---|---|---|---|
| `tool` | `"pickaxe" \| "axe" \| "shovel" \| "hoe"` | `"pickaxe"` | Kind of tool that gets the item. |
| `level` | `"wood" \| "stone" \| "iron" \| "diamond" \| "netherite"` | `"wood"` | Weakest tool level that gets the item. Each tool of a level also mines every level below it. |

A weaker tool breaks the block without dropping its item. The class has three read-only properties: `tools`, the vanilla tools of the level or a stronger one, `item_tag`, the tag `{ns}:mining/<tool>_<level>` listing them, and `hosts`, the vanilla blocks making vanilla itself require the level, empty for any tool but a pickaxe and for `netherite`.

| Host of the block | Behavior |
|---|---|
| None given | The first of `Mining.hosts`, for example `minecraft:diamond_block` for `iron`. Vanilla drop rules then decide, mining speed and animation included. With no `hosts` the build raises `ValueError`. |
| One of `Mining.hosts` | Used as it is. Any other real host raises `ValueError`. |
| An `Interaction` host | The breaker's main hand is checked against `Mining.item_tag`. Works for every tool kind. |
| `VANILLA_BLOCK_FOR_ORES` (`minecraft:polished_deepslate`) | With a level above `wood`, the nearest player within 8 blocks who is neither in creative nor in spectator is checked against `Mining.item_tag`. |

```python
Block(id="ruby_ore", vanilla_block=VANILLA_BLOCK_FOR_ORES, mining=Mining(level="iron"))
```

### NoSilkTouchDrop

Set exactly one of `id` and `loot_table`, or the constructor raises `AssertionError`.

| Field | Type | Default | What it does |
|---|---|---|---|
| `id` | `str` | `""` | Item id to drop, for example `raw_simplunium`. |
| `loot_table` | `LootTable \| str \| None` | `None` | A loot table, or its resource location, dropping instead of `id` and `count`, rolled with the breaker's tool. |
| `count` | `int \| dict` | `1` | Dropped amount, an integer or `{"min": 1, "max": 3}`. |
| `experience` | `float \| dict` | `0.0` | Experience dropped, as a number or `{"min": 3, "max": 7}`. The fractional part of a number is the chance of one more point: `2.5` gives 2 points, and a third half of the time. The manual shows it in the hover of the mining recipe. |

A dict for `count` or `experience` needs both `min` and `max`.

```python
Block(
	id="simplunium_ore",
	vanilla_block=VANILLA_BLOCK_FOR_ORES,
	no_silk_touch_drop=NoSilkTouchDrop(id="raw_simplunium", count={"min": 2, "max": 4}, experience={"min": 1, "max": 3}),
)
```

### RangedWeapon

| Field | Type | Default | What it does |
|---|---|---|---|
| `charge_time` | `float \| None` | `None` | Seconds a crossbow takes to load. Vanilla is 1.25. |
| `damage_multiplier` | `float` | `1.0` | Multiplies the damage of the arrows it shoots. |
| `ammunition` | `str \| None` | `None` | Id of the only definition a crossbow loads. Anything else is given back. |
| `name` | `str` | `"Heavy Draw"` | Tooltip name of the hidden enchantment applying it. |

The item gets the enchantment `Item.ranged_weapon_enchantment` at level 1, tagged as a curse so a grindstone keeps it, and no enchantment glint. A crossbow with `_pulling_<n>`, `_arrow` and `_firework` textures gets the vanilla crossbow item model: drawn by its charge, and showing what it holds once loaded.

```python
Item(id="crossbow", base_item="minecraft:crossbow", ranged_weapon=RangedWeapon(charge_time=2.5, damage_multiplier=1.5, ammunition="bolt"))
```

### GrowingSeed

| Field | Type | Default | What it does |
|---|---|---|---|
| `texture_basename` | `str` | required | Base of the stage textures, named `<texture_basename>_stage_<n>.png`. |
| `seconds` | `int` | required | Time to reach the last stage. |
| `planted_on` | `str` | required | Block the seed must sit on. `minecraft:` is removed. |
| `loots` | `list[GrowingSeedLoot] \| str` | required | Loot of the harvest, or the resource location of a loot table. |

`GrowingSeedLoot`:

| Field | Type | Default | What it does |
|---|---|---|---|
| `id` | `str` | required | Item id to drop. |
| `rolls` | `JsonDict \| int` | `1` | A count, or a number provider such as `{"type": "minecraft:uniform", "min": 3, "max": 9}`. |
| `fortune` | `JsonDict \| None` | `None` | Fortune bonus, such as `{"extra": 0, "probability": 0.5}`. |

```python
BlockAlternative(
	id="diamond_seed",
	vanilla_block=VanillaBlock(contents=True),
	growing_seed=GrowingSeed(texture_basename="diamond", seconds=1200, planted_on="stone", loots=[
		GrowingSeedLoot(id="minecraft:diamond", rolls={"type": "minecraft:uniform", "min": 0, "max": 2}, fortune={"extra": 0, "probability": 0.1}),
	]),
)
```

## Painting

`Painting` extends `Item` with `base_item="minecraft:painting"` and one more field. The component `painting/variant` is set to `<namespace>:<id>` when absent.

| Field | Type | Default | What it does |
|---|---|---|---|
| `painting_data` | `PaintingData` | required | Size, texture and text of the painting. |

`PaintingData`:

| Field | Type | Default | What it does |
|---|---|---|---|
| `width` | `int` | required | Width in blocks. |
| `height` | `int` | required | Height in blocks. |
| `texture` | `str \| None` | the item id | Texture file name without `.png`, looked up in the textures folder. |
| `author` | `TextComponent \| None` | `ctx.project_author` | Author shown in the tooltip. |
| `title` | `TextComponent \| None` | the id with spaces and capitals | Title shown in the tooltip. |

```python
Painting(
	id="stewbeet_painting",
	painting_data=PaintingData(texture="stewbeet_painting_2x2", author={"text": "Stoupy", "color": "yellow"}, width=2, height=2),
)
```

## Recipe system

Every recipe class derives from `RecipeBase`. Its fields are valid on every class below.

| Field | Type | Default | What it does |
|---|---|---|---|
| `result_count` | `int` | `1` | Amount of the result. |
| `category` | `str \| None` | `None` | Recipe book category written to the vanilla recipe. |
| `group` | `str \| None` | the item id | Recipe book group. |
| `result` | `Ingr \| None` | the item the recipe belongs to | What the recipe gives. |
| `manual_priority` | `int \| None` | `None` | Weight of the recipe's button on the manual page. When too many buttons are present, the lowest weight is dropped first. `None` weighs 1. |
| `smithed_crafter_command` | `str \| None` | `None` | Command run by a Smithed Crafter recipe. Without it the recipe gives the result's loot table. |

An ingredient is checked at construction: it needs an `item` or a `components` key, or the class raises `ValueError`.

| Class | Fields it adds | Notes |
|---|---|---|
| `CraftingShapedRecipe` | `shape: list[str]`, `ingredients: dict[str, Ingr]` | At most 3 rows of 3 columns, all rows of one length. Every symbol of `ingredients` must appear in `shape`. |
| `CraftingShapelessRecipe` | `ingredients: list[Ingr]` | |
| `SmeltingRecipe` | `ingredient: Ingr`, `experience: float = 0.0`, `cookingtime: int = 200` | `cookingtime` in ticks. |
| `BlastingRecipe` | `ingredient: Ingr`, `experience: float = 0.0`, `cookingtime: int = 100` | The duration in a blast furnace. The written value is doubled from 26.3, where a blast furnace gets its speed from its fuel. |
| `SmokingRecipe` | `ingredient: Ingr`, `experience: float = 0.0`, `cookingtime: int = 100` | Doubled from 26.3 like the blasting one. |
| `CampfireCookingRecipe` | `ingredient: Ingr`, `experience: float`, `cookingtime: int` | No defaults: both are required. |
| `StonecuttingRecipe` | `ingredient: Ingr` | |
| `SmithingTransformRecipe` | `template`, `base`, `addition`: `Ingr` | |
| `SmithingTrimRecipe` | `template`, `base`, `addition`: `Ingr`, `pattern: str` | `pattern` is the trim pattern id. |
| `PulverizingRecipe` | `ingredient: Ingr` | A SimplEnergy pulverizer recipe. |
| `AwakenedForgeRecipe` | `ingredients: list[Ingr]`, `particle: str \| None = None` | A Stardust Fragment awakened forge recipe. The manual's forge page has a 3x3 grid for up to 9 ingredients and a 3x4 grid above. |
| `HardcodedRecipe` | `type` | A vanilla special recipe, such as `crafting_special_armordye` or `crafting_transmute`. `type` is required and must be one of the vanilla special recipe types. |

`experience` and `cookingtime` are checked as a number and an integer.

```python
CraftingShapedRecipe(shape=["II", "CC", "CC"], ingredients={"I": Ingr("minecraft:iron_ingot"), "C": Ingr("simplunium_ingot")})
```

### Ingr

`Ingr(id, ns=None, count=None, **kwargs)` builds the dictionary naming an ingredient. `Ingredient` and `IngrRepr` are aliases.

| Argument | What it does |
|---|---|
| `id` | An id with a `:` is a vanilla item or an item of a datapack: `{"item": id}`. Without a `:` it is an item of a namespace, matched by its custom data: `{"components": {"minecraft:custom_data": {ns: {id: True}}}}`. A dict is copied as it is. |
| `ns` | Namespace of an id without a `:`. The project id by default. |
| `count` | Added as `count`. Used for a result, or by a recipe type supporting counts. |
| `kwargs` | Added to the dictionary. |

```python
Ingr("minecraft:stick")                     # {'item': 'minecraft:stick'}
Ingr("steel_ingot")                         # {'components': {'minecraft:custom_data': {'<project id>': {'steel_ingot': True}}}}
Ingr("tin_ingot", ns="mechanization")       # the same, in the namespace mechanization
Ingr("#minecraft:eggs")                     # an item tag, expanded in recipes into one recipe per item
```

Methods used by the plugins: `to_id()`, `to_name()`, `to_item()`, `to_predicate()`, `to_vanilla_item_id()`, `item_to_id()` and `register_loot_table()`.

## Material generation

`generate_everything_about_these_materials(ores, ignore_recipes=False)` calls `generate_everything_about_this_material(material, equipments_config=None, ignore_recipes=False)` for each entry of `ores`, a `dict[str, EquipmentsConfig | None]`. It reads `meta.stewbeet.textures_folder` and defines an item for each texture it finds.

The material name sets the base used by every generated id. A name with an underscore is cut before its last one (`steel_ingot` gives `steel`, `minecraft:copper_ingot` gives `copper`). A name ending with `!` is its own base (`awakened_stardust!` gives `awakened_stardust`), as does a name without an underscore (`minecraft:stone` gives `stone`).

| Texture | Defined as |
|---|---|
| `<base>`, `<base>_fragment`, `<base>_ingot`, `<base>_nugget`, `raw_<base>`, `<base>_dust`, `<base>_stick`, `<base>_rod` | An `Item` with `manual_category="material"`. |
| `<base>_block`, `raw_<base>_block` | A `Block` with `manual_category="material"` and no `vanilla_block`: set it afterwards. |
| `<base>_ore`, `deepslate_<base>_ore` | A `Block` with `manual_category="material"`, `vanilla_block=VANILLA_BLOCK_FOR_ORES`, and `no_silk_touch_drop` set to `raw_<base>` when that texture exists, else to the material itself. |
| `<base>_helmet`, `_chestplate`, `_leggings`, `_boots` | An armor `Item` with `manual_category="equipment"`. Needs a config. Its `base_item` is the vanilla armor of the config's `equivalent_to`. |
| `<base>_sword`, `_pickaxe`, `_axe`, `_shovel`, `_hoe`, `_spear` | A tool `Item` with `manual_category="equipment"`. Its `base_item` is the vanilla tool of `equivalent_to` when a config is given. |
| `<base>_layer_1`, `<base>_layer_2` | The equipment asset drawing the armor on a player: layer 1 for the helmet, chestplate and boots, layer 2 for the leggings. The armor then gets an `equippable` component. |

Recipes come with the items: a block from 9 of the material and back, an ingot from 9 nuggets, smelting and blasting (200 and 100 ticks, 0.8 experience) from the raw item, the dust or the ores, pulverizing recipes for the dust, 4 sticks from 2 material, the usual vanilla shapes for tools and armor, and a nugget from smelting an equipment piece. `ignore_recipes`, or the config's, skips them all. Equipment recipes have `manual_priority=0`.

Each piece's `max_damage` is its vanilla durability for `equivalent_to`, multiplied by `pickaxe_durability` over the vanilla pickaxe durability. The `custom_data` of every generated item carries a `smithed.dict` entry naming its kind and base.

`add_recipes_for_dust(material, pulverize, smelt_to)` defines `<material>_dust` from its texture. It adds smelting and blasting recipes giving `smelt_to`, the reverse pulverizing recipe, and a pulverizing recipe giving 2 dust for each entry of `pulverize`. A `str` entry is the vanilla item of that name. `add_recipes_for_all_dusts(dusts_configs)` takes a dict from material to `(pulverize, smelt_to)`.

### EquipmentsConfig

`EquipmentsConfig` is a plain class taking these arguments.

| Argument | Type | Default | What it does |
|---|---|---|---|
| `equivalent_to` | `DefaultOre` | `DefaultOre.DIAMOND` | Vanilla tier the base stats come from. |
| `pickaxe_durability` | `float \| int` | `0` | Durability of the pickaxe, from which every piece scales. `0` uses the vanilla pickaxe durability of `equivalent_to`. |
| `attributes` | `dict[str, float] \| None` | `{}` | Attribute modifiers added to the vanilla stats, with operation `add_value`. |
| `ignore_recipes` | `bool` | `False` | Skips the recipes of this material. |

Attributes are named without prefix: a key containing `player.` or `generic.` prints a warning, as does a `knockback_resistance` of 1 or more, which Minecraft multiplies by 10 on equipment. `attack_damage` and `mining_efficiency` go on tools only, `armor`, `armor_toughness` and `knockback_resistance` on armor only, and any other attribute, such as `movement_speed` or `burning_time`, on both. An `attack_damage` of 1 on a diamond pickaxe makes it 6. Anything else belongs to the item once generated: set it on `Item.from_id(...).components`.

### DefaultOre

| Member | Vanilla tier |
|---|---|
| `NETHERITE` | netherite |
| `DIAMOND` | diamond |
| `IRON` | iron |
| `GOLD` | golden |
| `COPPER` | copper |
| `CHAINMAIL` | stone tools, chainmail armor |
| `LEATHER` | wooden tools, leather armor |

`VanillaEquipments` holds the vanilla stats of each tier: `VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"]` is 250. Its members are `HELMET`, `CHESTPLATE`, `LEGGINGS`, `BOOTS`, `SWORD`, `PICKAXE`, `AXE`, `SHOVEL`, `HOE` and `SPEAR`.

## Wiki buttons and the manual item

`WikiButton(content)` wraps a text component, shown as the hover of an info button on the item's manual page.

`Item.wiki_buttons` takes a list holding at least one `WikiButton`, one button each. Any other value, a text component or a plain list of them, is a single button.

```python
Item.from_id("steel_ingot").wiki_buttons = [
	WikiButton([{"text": "Steel is a stronger variant of iron.\n"}, {"text": "It provides better durability.", "color": "yellow"}]),
	WikiButton({"text": "This is another button.", "color": "aqua"}),
]
```

The manual plugin creates the item `manual`: `base_item` `minecraft:written_book`, the item model `<ns>:manual`, `item_name` set to `meta.stewbeet.manual.name`, a stack size of 16, no glint and the lore `by <author>`. A definition with the id `manual` is merged into it: its components win, and its recipes are the ones the item has. With `use_dialog: 2` and no `manual` definition, no item is created.

```python
Item(
	id="manual",
	manual_category="miscellaneous",
	recipes=[
		CraftingShapelessRecipe(category="misc", ingredients=[Ingr("minecraft:book"), Ingr("steel_ingot")]),
		CraftingShapelessRecipe(category="misc", ingredients=[Ingr("manual")]),
	],
)
```

## Music discs

`generate_custom_records(records="auto", category=None, attenuation_distance=None)` defines one disc per sound. It reads `meta.stewbeet.records_folder`, and the build stops when that key is missing.

| Argument | Type | Default | What it does |
|---|---|---|---|
| `records` | `dict[str, str] \| str \| None` | `"auto"` | A dict from disc id to file name in the folder, or `"auto"`, `"all"` and `None` for every `.ogg` of the folder. |
| `category` | `str \| None` | `None` | `manual_category` of the discs. |
| `attenuation_distance` | `int \| None` | `None` | Distance in blocks beyond which the disc is silent. `None` is the vanilla 16. |

With `"auto"`, the id of a disc is its cleaned file name: lowercase letters and digits, with spaces and hyphens turned into `_`. A file that is not an `.ogg` prints a warning and is skipped.

Each disc is an `Item` with `jukebox_playable` set to `<ns>:<id>`, `item_name` `Music Disc`, `max_stack_size` 1 and `rarity` `rare`. The file name without extension is the song's description. The duration read from the file gives `length_in_seconds` as the duration plus one second, and `comparator_output` as the duration modulo 16. The sound is streamed under the disc's id.

## Manual categories

`manual_category` is a free string. The manual groups items by its exact value, shows each group on a page titled with the value in title case, and lists no item without a category. A category holding more items than `max_items_per_row * max_rows_per_page` is split into numbered pages, and more categories than that fits on one page makes the build fail.

Two spellings are two categories. The material helpers write `"material"` for ingredients and blocks and `"equipment"` for tools and armor, so a hand-written item shares their page by using the same values.

## Resource locations and BlockFunctions

Every location StewBeet derives from an id is a property returning a `Resource`. A `Resource` is a `str` holding `namespace:path`, so it works in f-strings, as a `write_function` path and as a dict key. It also gives the beet file.

| Property or method | Value for `Item(id="steel_ingot")` |
|---|---|
| `loot_table` | `ns:i/steel_ingot` |
| `loot_table_for(n)` | `ns:i/steel_ingot_x4`, or `_x4to6` for `{"min": 4, "max": 6}` |
| `item_model` | `ns:steel_ingot`, or the `item_model` component when it is set |
| `generated_item_model` | `ns:steel_ingot`, always the file StewBeet writes |
| `model` | `ns:item/steel_ingot` |
| `texture` | `ns:item/steel_ingot` |
| `recipe(index=1)` | `ns:steel_ingot`, `ns:steel_ingot_2` for index 2 |
| `ranged_weapon_enchantment` | `ns:ranged_weapon/steel_ingot` |

`Block` adds `functions`, `no_silk_touch_loot_table` (`ns:custom_blocks/no_silk_touch_drop/<id>`), `seed_loot_table` (`ns:seeds/<id>`), `advancement` (a `ValueError` for a regular `Block`), `alternative_advancement`, `head_advancement`, `head_search` (`ns:custom_blocks/_player_head/search_<id>`), and `seed_stage_name`, `seed_stage_item_model`, `seed_stage_model` and `seed_stage_texture` for a growth stage, named after `texture_basename`. `Painting` adds `variant`, `painting_texture` and `asset_id`.

| Method of `Resource` | What it does |
|---|---|
| `obj` | The beet file. Raises `KeyError` when it does not exist yet. Assigning to it writes the file. |
| `get(default=None)` | The beet file, or `default`. |
| `exists()` | Whether the file is in the pack. |
| `setdefault(default=None)` | The file, inserting `default` or an empty one when absent. |
| `write(value)` | Writes the file and returns it. |
| `delete()` | Removes the file when present. |
| `child(name)`, `suffixed(suffix)`, `sibling(name)` | Derived resources: `<path>/<name>`, `<path><suffix>`, `<folder>/<name>`. |
| `namespace`, `relative_path`, `file_type` | The parts of the location. |

`Block.functions` returns a `BlockFunctions`, which is also built directly: `BlockFunctions(block_id, namespace=None)` needs no definition. `functions["name"]` gives any function of the block's folder, `functions.folder` the folder, and iterating it lists the functions already in the pack.

| Property | Function in `ns:custom_blocks/<id>/` | Runs |
|---|---|---|
| `place_main` | `place_main` | At the block's position when it is placed. |
| `place_secondary` | `place_secondary` | As the summoned item display or item frame, when the block is placed. |
| `place_check` | `place_check` | Checks the placed block is this one before `place_main`. |
| `search` | `search` | Searches the placed entity of an item frame block. |
| `get_facing` | `get_facing` | Computes the facing from the player's orientation. |
| `destroy` | `destroy` | When the block is destroyed. |
| `replace_item` | `replace_item` | Replaces the dropped item with the block's item. |
| `update_seed_model` | `update_seed_model` | Sets a growing seed's model to its stage. |
| `is_fully_grown` | `is_fully_grown` | When a growing seed reaches its last stage. |
| `tick`, `tick_2`, `second`, `second_5`, `minute` | the same names | Every tick, 2 ticks, second, 5 seconds, minute, as the block's entity. |

```python
steel_block = Block.from_id("steel_block")
write_function(steel_block.functions.tick, "particle heart ~ ~1 ~ 0.5 0.5 0.5 0.01 1")
write_function(BlockFunctions("steel_block").second, "particle angry_villager ~ ~1 ~ 0.2 0.2 0.2 0.01 10")
```

## Recognized texture patterns

A texture is matched to a definition by its file name: `<id>.png`, or `<id>_<suffix>.png` for a variant. A variant is looked up among the files of the textures folder starting with the id and holding at most two more underscores than the id.

Block patterns apply to a `Block` whose `base_item` is the default one, or whose `override_model` names a block parent. A single texture gives `block/cube_all`. Otherwise the first pattern whose sides all have a texture wins.

| Parent | Textures |
|---|---|
| `block/cake` | `<id>_bottom`, `<id>_side`, `<id>_top`, `<id>_inner` |
| `block/orientable_with_bottom` | `<id>_front`, `<id>_bottom`, `<id>_side`, `<id>_top` |
| `block/cube_bottom_top` | `<id>_bottom`, `<id>_side`, `<id>_top` |
| `block/orientable` | `<id>_front`, `<id>_side`, `<id>_top` |
| `block/cube_column` | `<id>_end`, `<id>_side` |

A block matching none of them stops the build, unless its `override_model` gives the textures.

| Item pattern | Textures and condition |
|---|---|
| Overlay | `<id>_overlay` becomes the second layer of the model. |
| Leather armor | A `base_item` starting with `leather_` gets its texture as the second layer too, for dyeing. |
| Bow | A `base_item` ending with `bow` and textures `<id>_pulling_0`, `<id>_pulling_1`, and so on, drawn in order as the bow is pulled. A crossbow also reads `<id>_arrow` and `<id>_firework`. |
| Spear | An id ending with `_spear` and a texture `<id>_in_hand` shows that texture outside the gui, on the ground, in frames and on shelves. |
| Powered | A texture ending with `_on` gives the item and the block an `_on` model. A furnace, smoker or blast furnace host shows it while it burns. |

## Setup helper functions

Each function reads `Mem.definitions` at the moment it is called, so it runs after every definition is created.

| Function | What it does |
|---|---|
| `add_item_model_component(black_list=None)` | Sets `item_model` to the generated item model on each definition that has none, except the ids of `black_list`. |
| `add_item_name_and_lore_if_missing(is_external=False, black_list=None)` | Sets `item_name` to the id in title case when absent, and adds the `meta.stewbeet.source_lore` line to `lore`. |
| `add_private_custom_data_for_namespace(is_external=False, black_list=None)` | Sets `custom_data.<ns>.<id>` to `true`, and `custom_data.smithed.id` and `origin`. This is how items are detected in recipes and functions. |
| `add_smithed_ignore_vanilla_behaviours_convention()` | Sets `custom_data.smithed.ignore.functionality` and `crafting` to `true`. |
| `set_manual_components(white_list)` | Components shown in the hover of an item in the manual. An empty list changes nothing. |
| `export_all_definitions_to_json(file_name, is_external=False, verbose=True)` | Writes every definition to one JSON file, without `override_model`. |
| `resolve_use_remainders()` | Writes `use_remainder` on each item with a `remainder`. The recipe, loading and loot table plugins call it. |

`is_external=True` runs on `Mem.external_definitions` instead.

## Next steps

- [Items and blocks](../items_and_blocks/en.md): declare an item, a block and their recipes step by step.
- [Helpers](../2_writing_to_files/reference/en.md): the functions writing the files a definition points to.
- [Custom blocks](../plugins/datapack.custom_blocks.md): every file the plugin writes for a `Block`.

