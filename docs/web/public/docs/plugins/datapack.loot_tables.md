
# Loot tables

Writes a loot table for each item of your definitions, so commands, recipes and other loot tables can give it, and a function giving every item in chests.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.datapack.loot_tables`. It needs `source_lore` in the `stewbeet` section of `beet.yml`, which the templates set. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/loot_tables/__init__.py)

## Give an item

```mcfunction
loot give @s loot stardust:i/life_crystal
```

From Python, take the loot table from the item:

```python
Item.from_id("life_crystal").loot_table
# stardust:i/life_crystal
```

## What this plugin writes

- `loot_table/i/<item>.json`: one of the item, its base item with every component of its definition, and the components written `"!name"` removed.
- `loot_table/i/<item>_x<count>.json` for each count other than 1 that one of the item's recipes gives, such as `i/stardust_ingot_x5`.
- `loot_table/i/<namespace>_manual.json` when the pack has a manual: the same as `i/manual`, under a name no other pack uses.
- `loot_table/creative_loot_table.json`: one of each item.
- `function/_give_all`: chests of 27 items, named "Chest [1/3]" and so on, with the source lore.

An item with `skip_gives=True` gets none of these.

## Limits

- Each loot table gives the item and nothing else. A drop with a chance, a tool condition or Fortune is a loot table you write yourself.

## Next steps

- [Definitions](../1_definitions_setup/en.md): `skip_gives`, and the components each item carries.

