
# SimpleDrawer

Lets SimpleDrawer's compacting drawers store your ingots, nuggets and storage blocks, and convert between them.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.compatibilities.simpledrawer`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/compatibilities/simpledrawer/__init__.py)

## What it reads

An item named `<material>_block` counts as a storage block when its `custom_data` holds a `smithed.dict`, which the material helpers of the definitions write for you. The plugin then looks for the other forms by name:

| Form | Found as |
|---|---|
| Ingot | `<material>_ingot`, else `<material>`, else `<material>_fragment` |
| Nugget | `<material>_nugget` |

A block starting with `raw_` uses `raw_<material>` as its ingot and has no nugget. A block with neither ingot nor nugget is skipped.

It also reads your recipes. A crafting recipe with the block as its only ingredient gives how many ingots a block decompresses into. The same with the ingot gives nuggets per ingot. Without such a recipe, both counts are 9.

## What this plugin writes

- `#simpledrawer:material` calls `calls/simpledrawer/material`, which checks the item in the drawer against each form of each material.
- `calls/simpledrawer/<material>/block`, `ingot` and `nugget` set the type of the form (0, 1 or 2) and call `main`.
- `calls/simpledrawer/<material>/main` sets the counts and the material name, and copies your items from `<namespace>:items`.

## Limits

- Nothing is written when no block matches, and the build does not warn.
- The name shown for a material is its id with spaces and capitals, such as `Steel Alloy` for `steel_alloy`. It is not translated.

## Next steps

- [Using datapack libraries](../5_dependencies/en.md): SimpleDrawer is installed like any other library.

