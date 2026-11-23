
# Block ticking

Runs a function of your block on every placed copy of it, each tick, second or minute. Write the function and this plugin finds it.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.finalyze.custom_blocks_ticking`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/finalyze/custom_blocks_ticking/__init__.py)

## Make a block tick

Write one of these functions in the block's folder, `custom_blocks/<block>/`:

| Function | Runs |
|---|---|
| `tick` | Every tick, 20 times a second |
| `tick_2` | Every 2 ticks |
| `second` | Every second |
| `second_5` | Every 5 seconds |
| `minute` | Every minute |

Take its path from the block rather than typing it:

```python
obj = Block.from_id("solar_panel")
write_function(obj.functions.second, """
scoreboard players add @s energy.storage 5
""")
```

The function runs as the block's item display, at its position.

## What this plugin writes

For each function name a block uses, here `second`:

- The block's `place_secondary` tags its display `<namespace>.second` and counts it in `#second_entities`.
- Its `destroy` takes it off the count.
- The pack's `second` function calls `custom_blocks/second` while the count is above 0.
- `custom_blocks/second` sends each tagged display to its block's function:

```mcfunction title="custom_blocks/second.mcfunction"
execute if entity @s[tag=simplenergy.solar_panel] run function simplenergy:custom_blocks/solar_panel/second
execute if entity @s[tag=simplenergy.pulverizer] run function simplenergy:custom_blocks/pulverizer/second
```

`/function <namespace>:_stats_custom_blocks` also lists how many placed blocks run each function.

## Limits

- The tag is given when a block is placed. A block placed before its function existed does not run it until it is broken and placed again.
- Only a function named exactly as in the table, directly in the block's folder, counts.
- A thousand blocks on `tick` run their function 20,000 times a second. The [Performance](../10_performance/en.md) guide shows what to move to `second`.

## Next steps

- [Performance](../10_performance/en.md): keeping many ticking blocks cheap.

