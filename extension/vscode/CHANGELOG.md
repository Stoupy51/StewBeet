# Changelog

## 1.1.0

Language features inside mcfunction strings, provided by [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server) rather than reimplemented here.

- **Completion** inside `write_*` string blocks, including the resource locations your own pack defines.
- **Hover** and **signature help** in the same blocks.
- **Go to definition** on a resource location, landing on the generated `.mcfunction` it refers to. Jumping back to the `write_function` call needs source maps and is not implemented yet.
- New setting `StewBeet.languageFeatures` (default `true`) to turn all of the above off.

Each block is projected into a virtual `.mcfunction` document whose offsets match the Python buffer exactly, so requests forward to Spyglass and every returned range applies unchanged. Spyglass stays optional: without it, highlighting and decorations behave exactly as in 1.0.6.

## 1.0.6

Syntax highlighting and block decorations for mcfunction strings in StewBeet `write_*` calls.
