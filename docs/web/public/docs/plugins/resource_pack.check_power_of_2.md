
# Texture size check

Warns about the item and block textures whose width or height is not a power of 2.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.resource_pack.check_power_of_2`, with no configuration. It runs after the plugins that write textures. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/check_power_of_2/__init__.py)

## What this plugin writes

Nothing. It prints one warning listing each wrong texture and its size, and the build goes on:

```text
The following textures are not in power of 2
resolution (2x2, 4x4, 8x8, 16x16, ...):
- simplenergy:item/ruby	(15x16)
```

## Limits

- It reads the textures under `item/` and `block/`, in every namespace of the resource pack. Other folders are not checked.
- A texture taller than wide, whose height is a multiple of its width, is skipped as an animation strip. A 48x144 texture passes, a 48x48 one is flagged.

