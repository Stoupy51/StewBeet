# Changelog

## 1.2.0

Navigation and diagnostics now cross the boundary between your Python and the datapack it generates, using the `.mcfunction.map` sidecars a build emits.

- **Go to definition** on a resource location lands on the `write_function` call that produced it, instead of on the generated `.mcfunction`. When a function was assembled from several places, a custom block's declaration plus your own append, the peek list offers all of them.
- **Find references** on a generated resource location lists every Python call site that writes to it.
- **Diagnostics** reported against generated files are mirrored onto the Python line that wrote the command, sourced `stewbeet (spyglassmc)`.
- New commands: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**.
- New settings: `StewBeet.buildOutput` (where the generated pack is, empty to autodetect) and `StewBeet.sourceMapDiagnostics`.

All of it needs a build in the workspace, produced with `stewbeet.plugins.sniffer` in the pipeline. Without one there are no maps, definition falls back to the generated file exactly as in 1.1.0, and nothing else changes.

## 1.1.0

Language features inside mcfunction strings, provided by [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server) rather than reimplemented here.

- **Completion** inside `write_*` string blocks, including the resource locations your own pack defines.
- **Hover** and **signature help** in the same blocks.
- **Go to definition** on a resource location, landing on the generated `.mcfunction` it refers to. Jumping back to the `write_function` call needs source maps and is not implemented yet.
- New setting `StewBeet.languageFeatures` (default `true`) to turn all of the above off.

Each block is projected into a virtual `.mcfunction` document whose offsets match the Python buffer exactly, so requests forward to Spyglass and every returned range applies unchanged. Spyglass stays optional: without it, highlighting and decorations behave exactly as in 1.0.6.

## 1.0.6

Syntax highlighting and block decorations for mcfunction strings in StewBeet `write_*` calls.
