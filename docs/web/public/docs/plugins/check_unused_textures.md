
# Unused textures

Warns about the `.png` files of your textures folder that nothing in the resource pack uses.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.check_unused_textures`. It needs `textures_folder` in the `stewbeet` section of `beet.yml`, and runs late in the pipeline, once the textures are in. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/check_unused_textures/__init__.py)

## What this plugin writes

Nothing. It prints one warning listing the files, and the build goes on:

```text
Some textures are not used in the resource pack:
- 'assets/textures/old_ruby.png'
```

A texture counts as used when a generator consumed it, or when a texture of the resource pack has its file name in its source path.

## Limits

- The match is loose. A file named `ore.png` is not reported while `ruby_ore.png` is in the pack, since its name appears in that path.
- Without `textures_folder`, the build stops with `meta.stewbeet.textures_folder is not set`.

