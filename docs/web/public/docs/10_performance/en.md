
# Keeping functions fast

Conventions StewBeet packs follow in code that runs every tick. Each one names the helper that applies it when there is one.
Measure before and after with `/perf start`, then `/perf stop`: the zip it writes holds `server/profiling.txt`, the time each command took.

### Persistent entities instead of temporary ones

`execute summon ... run function ...` followed by `kill @s` creates and destroys an entity on every call, which costs more than most of what the function then does.
A command that needs an entity only as a holder (an `item_display` to run `loot replace entity @s contents` into, then read `item` from) uses a persistent one:

```python
from stewbeet import persistent_item_display, write_function

display: str = persistent_item_display("pulverizer_recipe")
write_function(f"{ns}:get_recipe", f"""
execute as {display} run function #{ns}:calls/recipes
data modify storage {ns}:main output set from entity {display} item
""")
```

`persistent_item_display(name)` adds to the load function a `forceload add` of the chunk at `FORCELOAD_BLOCK` (x -30000000, z 1600, shared with Bookshelf, Furnace NBT Recipes, and others) and an `execute unless entity <uuid> run summon` of the entity, once per name.
The UUID is derived from the project id and the name, so it never changes between builds and two projects never share one. The unload function kills the entity, and leaves the forceload to the other packs using that chunk.

The execution position stays the caller's: `execute as <uuid>` changes `@s`, not `~ ~ ~`.

### Write entity and block NBT only when it changes

`data modify entity` and `store result block` serialize the whole entity or block entity and load it back. Guard them with a cheap test of the value they would write:

```mcfunction
execute unless items entity @s contents *[minecraft:item_model="ns:machine_on"] run data modify entity @s item.components."minecraft:item_model" set value "ns:machine_on"
```

A value the game moves on its own every tick, like a furnace's `cooking_time_spent`, never equals the one written the tick before. Write it when what the player sees would change instead: Furnace NBT Recipes writes it once the progress arrow would show another of its 24 pixels.

### Test items with `if items`, not by copying their NBT

`data modify storage ... set from entity @s SelectedItem` serializes the whole player, inventory included, to read one item. `execute if items` reads the slot directly:

```mcfunction
execute if items entity @s weapon.offhand *[custom_data~{"ns":{"multimeter":true}}] run function ns:multimeter
execute if items block ~ ~ ~ container.26 *[!custom_data~{"common_signals":{"temp":true}}] run function ns:drop_intruder
```

Copy a container's `Items` only on the path that needs the full stack, and at most once per tick.

### Read a block entity once per tick

`execute if data block ~ ~ ~ {lit_time_remaining:0}` serializes the whole block entity, items included, for one value. When a function needs several values, copy the block once with `data modify storage ... set from block ~ ~ ~`, turn the values tested more than once into scores, and test slots with `if items block`.

### Keep per-entity state in scores and tags

A value an entity reads and writes every tick (a progression, an unlocked flag) costs a full entity serialization each way when it lives in NBT. Store it as a score or a tag on the entity, and move it to and from NBT only when the block is placed or broken, where the item carries it.

### Make an absent value absent

`data modify storage ... set value {}` before an optional `set from` leaves `{}` when the source is missing, and `execute unless data` then never sees the absence. Clear it with `data remove` instead.

### Reuse a result while its input does not change

`data modify A set from B` succeeds only when it changes `A`, so `execute store success` turns it into an equality test that also records the new value:

```mcfunction
execute store success score #changed ns.data run data modify storage ns:temp previous_input set from storage ns:temp input
execute if score #changed ns.data matches 1 run function ns:expensive_lookup
```

Remove `previous_input` where the reuse must stop: at the start of each block's tick, after something consumed the result, or in the load function when a `/reload` can change what the lookup returns.

### Order a chain of returns by frequency

In a function made of `execute if ... run return <value>` lines, put the most frequent case first, and check that each line tests the right target (`block ~ ~ ~` versus `entity @s`): a line that can never match makes every call run the whole chain.

