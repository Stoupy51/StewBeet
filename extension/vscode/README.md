
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
| `resolveInterpolations`  | `true`                  | Fill each `{...}` with what the last build resolved it to |
| `buildOutput`            | `""`                    | Where the generated datapack is. Empty searches the whole workspace for `.mcfunction.map` files |
| `sourceMapDiagnostics`   | `true`                  | Show build errors on the Python line that wrote the command |
| `diagnosticRuleDenylist` | `["undeclaredSymbol"]`  | Rules never relayed onto Python |
| `codeLens`               | `true`                  | Show a link above each block to the function it produced |
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
| Go to definition | Jumps to the `write_function` call that produced the resource location |
| Find references | Every Python call site that writes to a resource location |
| Diagnostics | Build errors mirrored onto the Python line that wrote the command |

Completion knows about your project's own functions once the pack has been built at least once, because it resolves against the same symbol table Spyglass builds from your build output.

Turn the whole thing off with `"StewBeet.languageFeatures": false`.

### Crossing back to your Python (requires a build)

Go to definition, find references and the relayed diagnostics all read the `.mcfunction.map`
sidecars your build emits. Produce them by putting the sniffer plugin in your pipeline:

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"

pipeline:
    - "..."
    - "stewbeet.plugins.sniffer.emit"
    - "stewbeet.plugins.archive"
```

Three commands come with it, from the palette:

| Command | What it does |
| ------- | ------------ |
| StewBeet: Go to Python Source | From a generated `.mcfunction`, open the Python that wrote the line |
| StewBeet: Go to Generated Function | The inverse, from a Python line to what it produced |
| StewBeet: Reload Source Maps | Drop the cache when a build finished outside the watcher's view |

A block that produced a function also carries a clickable link above it, so the second command
is one click rather than a palette search. Turn it off with `"StewBeet.codeLens": false`.

Without a build there are no maps, and go to definition falls back to opening the generated
`.mcfunction`. Nothing errors and nothing else changes.

### Interpolated paths (requires a build)

StewBeet code rarely writes a literal resource location. It writes this:

```python
write_function(f"{ns}:utils/loop", f"""
function {ns}:utils/battery_switcher/loop
execute if score #height {ns}.data matches 150.. run say high
""")
```

Every `{...}` is Python, not mcfunction, so it is filled in with what the last build resolved
it to before Spyglass sees the line. Ctrl+click on `{ns}:utils/battery_switcher/loop` lands on
the `write_function` call that wrote it, completion offers your own function paths after
`{ns}:`, and the squiggles land on the right characters.

The values come from the source maps, so nothing evaluates your Python and nothing runs your
build. A line the current build does not cover keeps the `_` mask it had before, which is also
what happens when the build is stale enough that the surrounding text no longer matches.

Turn it off with `"StewBeet.resolveInterpolations": false`.

### What the diagnostics leave out

`undeclaredSymbol` is not relayed by default. It fires on every scoreboard objective or tag a
dependency declares, which Spyglass cannot see from your sources, and a false error on a Python
line is far more intrusive than the same one in a generated file nobody opens.

Relay everything with `"StewBeet.diagnosticRuleDenylist": []`, or add rules of your own to the
list to silence them.

## Grammar

mcfunction grammar from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction), bundled via [StewBeet](https://github.com/Stoupy51/StewBeet/blob/main/extension/vscode/syntaxes/mcfunction.tmLanguage.json).

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.

**From a `.vsix` file:**
```bash
code --install-extension stewbeet-1.0.0.vsix
```
Or: **Extensions -> `...` -> Install from VSIX...**

