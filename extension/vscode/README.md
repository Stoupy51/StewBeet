
# StewBeet mcfunction Syntax

> Syntax highlighting, block decorations and **language features** for **mcfunction** code embedded inside [StewBeet](https://stewbeet.paralya.fr/) `write_*` Python calls.

---

## Recommended companion: Spyglass

Install [Datapack Helper Plus](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server) (`SPGoding.datapack-language-server`) to get completion, hover, signature help and go-to-definition inside your mcfunction strings.

This extension does not implement any of that itself. It projects each mcfunction string into a virtual document and asks Spyglass, so you get exactly what you would get in a real `.mcfunction` file, and every Spyglass release improves it for free.

Spyglass is optional. Without it, syntax highlighting and block decorations work as before and the language features are silently unavailable.

---

## Configuration

All settings are under `StewBeet.*` in your `settings.json`:

| Setting                  | Default                 | Description                     |
| ------------------------ | ----------------------- | ------------------------------- |
| `languageFeatures`       | `true`                  | Completion, hover, signature help and go-to-definition inside mcfunction strings |
| `enableBlockDecorations` | `true`                  | Toggle block decorations on/off |
| `backgroundColor`        | `rgba(80,40,0,0.15)`    | Background fill color           |
| `borderColor`            | `rgba(200,120,30,0.30)` | Border color                    |
| `borderWidth`            | `"2px"`                 | Border thickness                |

Example customization:
```jsonc
// settings.json - example with a greenish theme and thinner borders
"StewBeet.backgroundColor": "rgba(0,60,30,0.15)",
"StewBeet.borderColor": "rgba(80,200,100,0.40)",
"StewBeet.borderWidth": "1px"
```

---

## Comparison without and with the extension

![Comparison gif](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/comparison.gif)

## Features

### Syntax highlighting
Triple-quoted and single-line strings passed to the following functions are highlighted as mcfunction:

| Function                                           | Content argument |
| -------------------------------------------------- | ---------------- |
| `write_function(path, content, ...)`               | 2nd              |
| `write_versioned_function(path, content, ...)`     | 2nd              |
| `write_scheduled_function(duration, content, ...)` | 2nd              |
| `write_load_file(content, ...)`                    | 1st              |
| `write_unload_file(content, ...)`                  | 1st              |
| `write_tick_file(content, ...)`                    | 1st              |

All string forms are supported: `"""..."""`, `'''...'''`, `"..."`, `'...'`, and their `f`-string variants.  
Python interpolations (`{variable}`) inside f-strings are parsed correctly and never mistaken for mcfunction syntax.

### Block decorations
Multi-line strings are wrapped in a unified colored rectangle. Single-line strings get an inline border that starts exactly at the quote character.

### Language features (requires Spyglass)

Inside those same blocks, and nowhere else:

| Feature | What you get |
| ------- | ------------ |
| Completion | Vanilla commands, plus the resource locations your own pack defines |
| Hover | Spyglass's documentation for selectors, arguments and resource locations |
| Signature help | The argument list of the command you are typing |
| Go to definition | Jumps to the generated `.mcfunction` a resource location refers to |

Completion knows about your project's own functions once the pack has been built at least once, because it resolves against the same symbol table Spyglass builds from your build output.

Turn the whole thing off with `"StewBeet.languageFeatures": false`.

> **Note on go to definition.** It currently lands on the **generated** `.mcfunction` file, not on the `write_function` call that produced it. Jumping back to the Python source needs source maps, which the build does not emit yet. This is a known limitation, not a bug.

## Grammar

mcfunction grammar from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction), bundled via [StewBeet](https://github.com/Stoupy51/StewBeet/blob/main/extension/vscode/syntaxes/mcfunction.tmLanguage.json).

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.

**From a `.vsix` file:**
```bash
code --install-extension stewbeet-1.0.0.vsix
```
Or: **Extensions -> `...` -> Install from VSIX...**

