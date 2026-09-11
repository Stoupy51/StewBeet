# Changelog

## 2.0.0

Everything since 1.0.6, which coloured the mcfunction strings in your `write_*` calls and drew a box around them.
This one makes them code: checked as you type, navigable in both directions, and joined to the datapack your build produces.

### Language features inside the blocks

- **Completion, hover, signature help and go to definition**, answered by [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server) through a virtual `.mcfunction` whose offsets match your Python. Spyglass stays optional, and the install is offered once when it is missing.
- **Errors as you type**, with no build and with nothing under `build/` ever opened. Build errors are relayed onto the Python that wrote the command, `undeclaredSymbol` aside.
- **Interpolations resolved rather than masked.** `function {ns}:utils/loop` is read as the path it really is, off the line the last build produced. A name the build resolved once is reused where it covers nothing, so commands assembled in a variable are clickable too, and a name resolved two ways keeps its `_` mask. Nothing evaluates your Python.

### Crossing to the datapack and back

- **Go to definition** on a resource location lands on the call that produced it, and **find references** lists every call site writing to it.
- **A lens above each block**, naming the functions it produced and offering them by name when there are several. `Block(id=...)` maps back too, though it writes no commands of its own.
- **`#>` header comments in a generated file are clickable**, `@within` included.
- **Lenses, errors and resolved paths follow your edits**, with no rebuild. A line moved or re-indented keeps what it had, a line deleted passes nothing to its neighbour, and a build puts everything back where the map says.

### What counts as a block

- The `write_*` helpers; a variable and every `+=` up to the call that consumes it; a list, however it is built, bare or as `"\n".join(lines)`; a parameter annotated `McFunction`; and beet's own API, from a string or a `list[str]`, plus `.append`, `.prepend`, `.lines.append`, `.lines.extend` and `.obj.append`.
- **Colours need the `McFunction` annotation** on a variable or list, since a grammar cannot see the call a string reaches. It is `str`, exported from `stewbeet`, so it changes nothing at runtime.

### bolt

- **`.bolt` files open as Bolt**, with highlighting and comment toggling. The command names are generated from mecha's command tree, so they cannot drift from what mecha accepts.
- **Completion, diagnostics and ctrl+click inside them**, through the same projection the Python strings use: command lines are kept and dedented, the Python around them is blanked. A word one edit away from a command is read as that command, so `playound` is underlined where you typed it.
- **A `.mcfunction` holding bolt gets the `bolt` language id**, and **StewBeet: Exclude Bolt Files From Spyglass** writes it into your `.spyglassrc.json`. `stewbeet.plugins.spyglass` in the pipeline keeps that list from the build instead.

### Source maps

- **Everything that needs a build reads `.mcfunction.map` sidecars**, emitted by `stewbeet.plugins.sniffer` in your `require`. One line of `beet.yml`, for the helpers and for what mecha compiles alike; a project with no StewBeet in it lists `stewbeet.plugins.sniffer.mecha` instead.
- **The map is the function's sibling**, written before the archive plugin zips, with no `## sourceMappingURL=` line in what you ship.
- **bolt and mecha projects get the same maps**, with real columns. A line that cannot be narrowed to one of your own files stays unmapped rather than pointing at a plausible wrong one.

### Speed

- A full lens pass over a 141-file project takes 0.7 ms, and reading the origins of a generated file went from 83 to under 1 microsecond.
- A diagnostics pass costs one round trip rather than one per block, and only the blocks whose text moved are woken.

### Settings and commands

| Setting | Default | |
|---|---|---|
| `StewBeet.languageFeatures` | `true` | Completion, hover, signature help and go to definition inside the blocks |
| `StewBeet.suggestSpyglass` | `true` | Offer the Spyglass install once, when it is missing |
| `StewBeet.buildOutput` | `""` | Where the generated pack is. Empty searches the workspace for maps |
| `StewBeet.sourceMapDiagnostics` | `true` | Relay build errors onto the Python that wrote the command |
| `StewBeet.resolveInterpolations` | `true` | Fill each `{...}` with what the last build resolved it to |
| `StewBeet.diagnosticRuleDenylist` | `["undeclaredSymbol"]` | Rules never relayed onto Python |
| `StewBeet.codeLens` | `true` | The link above a block that produced a function |
| `StewBeet.headerLinks` | `true` | Resource locations in a generated file's `#>` header |
| `StewBeet.boltInMcfunction` | `true` | Give a `.mcfunction` holding bolt the `bolt` language id |

Commands: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.
The relay traces what it does to the **StewBeet** output channel, so a quiet relay can be told from a clean file.

## 1.0.6

Syntax highlighting and block decorations for mcfunction strings in StewBeet `write_*` calls.

