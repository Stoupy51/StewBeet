
# SimplEnergy

Helpers for a pack whose machines run on [DatapackEnergy](https://github.com/ICY105/DatapackEnergy), the energy library SimplEnergy uses: batteries that keep their charge, energy shared between neighbouring devices, cables and servos that change shape as they connect, machine screens drawn by the resource pack, and blocks the wrench turns.

Import them from `stewbeet.contrib.simplenergy` and call each one from your `beet_default`, the way SimplEnergy does in [`src/link.py`](https://github.com/Stoupy51/SimplEnergy/blob/main/src/link.py). [Source](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/contrib/simplenergy)

## Energy comes from the block

A block joins the energy network through the `energy` of its `custom_data`. The [Custom blocks](../plugins/datapack.custom_blocks.md) plugin reads it, with no call from you:

```python title="src/definitions/additions/energy.py"
Block(
  id="wind_turbine",
  ...
  components={"custom_data": {"energy": {
    "generation": 20,
    "max_storage": 800,
    "blocked_faces": ["top"],
  }}},
)
```

| Key | What it makes the block |
|---|---|
| `generation` | A generator, producing this many kW |
| `usage` | A machine, using this many kW |
| `transfer` | A cable, with this transfer rate |
| `max_storage` | The most it holds, in kJ. With neither of the three above, the block is a battery |
| `storage` | A battery's charge when the item is placed, in kJ |
| `blocked_faces` | The faces a cable cannot connect to: `top`, `bottom`, `front`, `back`, `left`, `right` |

## Batteries keep their charge

```python
keep_energy_for_batteries([
  "simple_battery",
  "advanced_battery",
])
```

A broken battery drops an item holding its charge, shown in its lore, and gets it back once placed again. Two charged batteries never stack.

It adds to each battery's `destroy` and `replace_item`, and writes `utils/keep_energy` and `calls/update_energy_lore/`, the last one in the `#energy:v1/update_energy_lore/main` tag.

## Neighbours share their energy

```python
setup_energy_balancing([
  "solar_panel",
  "simple_battery",
])
```

Every 5 seconds, touching blocks of the same kind and the same `max_storage` split their energy evenly. A block starts a share once it holds 20 kJ, and energy that a full block cannot take is lost.

It writes `balancing/`, a call in `second_5`, and the `<namespace>.can_balance` tag given to each block when placed.

## Energy cables

```python
energy_cables_models([
  "simple_cable",
  "elite_cable",
])
```

Each cable needs `<textures_folder>/<cable>.png`, laid out like SimplEnergy's [`simple_cable.png`](https://github.com/Stoupy51/SimplEnergy/blob/main/assets/textures/simple_cable.png). It gets 64 models, one per set of connected sides, and DatapackEnergy picks one whenever a neighbour changes.

It writes `calls/energy/cable_update`, in the `#energy:v1/cable_update` tag.

## Item cables

```python
item_cables_models({
  "basic_item_cable": None,
})
```

With `None`, the textures are `<cable>/center`, `<cable>/pillon` and `<cable>/glass` under the textures folder. A dictionary from the model's texture keys `"0"`, `"1"` and `"2"` to other paths replaces them.

A placed cable joins the [ItemIO](https://github.com/edayot/ItemIO) network and leaves it when broken. The pack writes `calls/itemio/cable_update`, in the `#itemio:event/cable_update` tag.

## Servo mechanisms

```python
servo_mechanisms_models({
  "servo_extractor": {"type": "extract"},
  "servo_inserter": {"type": "insert"},
})
```

A servo moves items between ItemIO containers. Its textures default to `<type>_default` and `<type>_connected`, and its "off" texture is a darkened grey copy of the default one. A player turns a servo off by rotating it in its item frame, and on again with one more turn.

It writes `utils/servo/`, an advancement on `player_interacted_with_entity`, and `calls/itemio/network_update`, in the `#itemio:event/network_update` tag.

## Machine screens

```python
gui = setup_gui_in_resource_packs({
  "electric_furnace":
    GuiTranslation.furnace_bottom,
})
```

Every PNG in `<textures_folder>/gui/` becomes an item model. One whose name holds a key of the dictionary is drawn over the whole container screen, from the slot its `GuiTranslation` names:

| Translation | Slot holding the model |
|---|---|
| `furnace_bottom` | A furnace's fuel slot |
| `furnace_top` | A furnace's ingredient slot |
| `brewing_stand` | A brewing stand's fuel slot |
| `barrel_bottom_right` | A barrel's 27th slot |

Any other PNG becomes a flat item. The function returns each file's model, such as `{"gui/electric_furnace.png": "simplenergy:gui/electric_furnace"}`, for the item you put in that slot.

## The wrench turns your machines

```python
setup_wrench([
  "electric_furnace",
  "pulverizer",
])
```

Tags each block `simplenergy.rotatable` when placed. The Mechanization wrench then turns it with `simplenergy:utils/wrench/rotate`, a function of SimplEnergy, so the pack runs beside SimplEnergy. `tag_ns="<namespace>"` uses your own tag and function instead.

The wrench also breaks any of your custom blocks, through `#mechanization:wrench_break`.

## Limits

- DatapackEnergy, and ItemIO for item cables and servos, must be among the pack's [libraries](../5_dependencies/en.md).
- `insert_lib_calls()` does nothing: the Custom blocks plugin registers energy blocks. Remove the call.

## Next steps

- [Custom blocks](../plugins/datapack.custom_blocks.md): every option of a placeable block.

