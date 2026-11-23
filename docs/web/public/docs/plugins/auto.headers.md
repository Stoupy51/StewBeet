
# Function headers

Writes a comment header at the top of every function, saying what calls it, in which context, and which macro arguments it takes.

It runs last of the `auto` plugins in the `basic` and `extensive` templates, as `stewbeet.plugins.auto.headers`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/headers/__init__.py)

## What a header looks like

```mcfunction
#> stardust:dimensions/teleport_to
#
# @executed	as the player & at current position
#
# @within	stardust:dimensions/teleport_home
#
# @args		dimension (string)
#			x (int)
#			y (int)
#			z (int)
#
$execute in $(dimension) run tp @s $(x) $(y) $(z)
```

- `@within` lists the callers: a function, `#namespace:tag`, `advancement <id>`, `dialog <id>` or `enchantment <id>`. A function id written inside a string, such as a `suggest_command`, is listed as `string in <function>`.
- `@executed` is the execution context the callers give it, such as `as the player & at current position` for an advancement reward.
- `@args` is written for macro functions only. Types come from the NBT of each call (`10` is an `int`, `20.5f` a `float`, `"a"` a `string`), from `data modify storage` lines before a `with storage` call, and from the caller's own `@args` when it passes `$(name)` along.
- An uncalled function shows `@within ???`. When the project has a `<namespace>:v<version>/` folder, an uncalled function of the namespace outside that folder shows `(public)` instead, since you run it by hand or another pack does.

## Keep your own text

The plugin reads a header it finds, so the build is repeatable:

- Lines under `@args` that you wrote, descriptions included, are kept. Only missing arguments are added, and the build warns `had incomplete @args` for each function that was missing some.
- Any other comment line of the header (a description, an example) is kept below `@args`.

```mcfunction
# @args		count (int): How many to give
#			- at least 1
```

## What this plugin writes

- The `#>` header of each function of the datapack, rewritten on every build.

## Limits

- The analysis is cached in `.beet_cache` and recomputed whole when any function, tag, advancement, dialog or enchantment changes.
- Callers are found in the text of the files. A function id built at run time is not seen.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): where your functions come from.

