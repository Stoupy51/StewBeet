
# Scoreboard constants

Writes every number you use as a score holder in your functions into the load function, so you never declare constants by hand.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.auto.scoreboard_constants`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/scoreboard_constants/__init__.py)

## Use a constant

Write the number as `#<number> <id>.data` in any function:

```mcfunction
scoreboard players operation @s simplenergy.data *= #100 simplenergy.data
```

At build time the plugin finds `#100` and writes its value into the load function.

## What this plugin writes

For every distinct number, sorted, at the end of the load function:

```mcfunction
# Set scoreboard constants for simplenergy.data
scoreboard players set #-1 simplenergy.data -1
scoreboard players set #100 simplenergy.data 100
```

Nothing is written when no function uses a constant.

## Limits

- The pattern is `#` then an integer, optionally negative, then a space and `<id>.data`. A constant on another objective is left alone.
- It reads the functions of the pack as built. A function written by a plugin that runs after this one is not scanned.
- The scan is on text. A constant inside a comment or a string counts too.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): the functions this plugin reads.

