
# Item models

Writes the model and the `items/` definition of each item and block of your definitions from the textures of your textures folder, so a texture named after an item is enough to draw it.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.resource_pack.item_models`. It needs `textures_folder` in the `stewbeet` section of `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/item_models/__init__.py)

## Name your textures

The plugin scans `textures_folder` for `.png` files and finds an item's textures by file name, whatever the subfolder. The textures that start with the item's id are its variants.

```text
steel_ingot.png
simplunium_block.png
super_furnace_front.png
super_furnace_side.png
super_furnace_top.png
super_furnace_on.png
```

- A block with one texture shows it on every face.
- A block with several textures takes the first of these shapes whose sides all exist, as `<id>_<side>.png`:

| Shape | Sides |
|---|---|
| `cake` | `bottom`, `side`, `top`, `inner` |
| `orientable_with_bottom` | `front`, `bottom`, `side`, `top` |
| `cube_bottom_top` | `bottom`, `side`, `top` |
| `orientable` | `front`, `side`, `top` |
| `cube_column` | `end`, `side` |

- A texture ending in `_on` is the lit state. The plugin writes a second model from it, which a burning furnace host shows.
- A bow takes `<id>_pulling_0`, `<id>_pulling_1` and so on. A crossbow also takes `<id>_arrow` and `<id>_firework` for its loaded states.
- A leather item takes `<id>_overlay` as its second layer.
- A spear takes `<id>_in_hand` for the model it shows outside the GUI.

## What this plugin writes

- `models/item/<id>.json`: the model, with a copy per state the item has (`_on`, a bow's `_pulling_<n>`).
- `items/<id>.json`: the item model definition.
- `textures/item/<texture>.png`, with its `.mcmeta` when the source has one.
- Entries in the `minecraft` atlases for the vanilla block textures a model uses: `items` from pack format 73, `blocks` before.
- One model, item model and texture per growth stage of a growing seed, from `<texture_basename>_stage_<n>.png`.
- Extra model copies for a block with `uvlock` or `half`, and for a stairs host, which the display picks by state.

Only the items whose `item_model` is in your namespace are written.

## Options

| Option | Default | What it does |
|---|---|---|
| `meta.stewbeet.textures_folder` | required | The folder scanned for `.png` files |
| `Item.override_model` | `None` | Merged over the generated model. `{"textures": None}` drops its textures, `{}` writes no model |
| `Item.hand_model` | `None` | The model shown in hand, in the GUI and on the ground |
| `Item.override_model_contexts` | `["none", "fixed"]` | The display contexts that keep the regular model when `hand_model` is set |

## Limits

- A texture the model needs and the folder lacks logs an error naming `<name>.png`, and the item gets no model.
- A block whose textures fill no shape logs an error listing the shapes, unless its `override_model` sets textures.
- Two textures of the same file name in different subfolders collide, and only one is read.

## Next steps

- [Definitions](../1_definitions_setup/en.md#block-class): the `VanillaBlock` options that add model copies.

