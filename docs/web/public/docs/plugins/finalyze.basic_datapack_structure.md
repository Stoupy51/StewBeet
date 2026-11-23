
# Tick, second and minute functions

Runs the functions you write named `tick_2`, `second`, `second_5` and `minute` at their interval, with no timer to write yourself.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.finalyze.basic_datapack_structure`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py)

## Write a timed function

Write the function with the versioned helper:

```python
write_versioned_function("second", """
scoreboard players add #seconds simplenergy.data 1
""")
```

The plugin only adds a timer for a function that exists when it runs. Functions written later in the pipeline are missed.

| Function | Runs | Score it runs at |
|---|---|---|
| `tick_2` | Every 2 ticks | 3 |
| `second` | Every 20 ticks | 20 |
| `second_5` | Every 100 ticks | 90, after a reset to -10 |
| `minute` | Every 1200 ticks | 1201, after a reset to 1 |

To run something on every placed copy of a block, use [Block ticking](finalyze.custom_blocks_ticking.md) instead.

## What this plugin writes

- A `Reset timer` line at the top of each timed function, which sets `#<name>` of `<id>.data` back to its start value.
- A `Timers` paragraph at the top of the `tick` function. It adds 1 to each timer, then runs each function whose score reached its threshold.

The start values of `tick_2` and `second_5` differ from the others on purpose, so that functions do not all run on the same tick.

The `tick` function runs only once the pack has loaded.

## Limits

- A timer counts server ticks. A lagging server runs a `second` function less than once a real second.
- Only these four intervals exist.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): `write_versioned_function` and the other helpers.

