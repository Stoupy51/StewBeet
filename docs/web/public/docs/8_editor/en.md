# Editor support

The [StewBeet extension for VSCode](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) is editor support for the whole [beet](https://github.com/mcbeet/beet) ecosystem: **beet**, **bolt**, **mecha** and **StewBeet**.
`.bolt` files get their own language, and the mcfunction strings inside your Python get highlighting, completion, errors and links to the built datapack.

<video src="/vscode_extension.mp4" controls loop muted playsinline preload="auto">
</video>

**Install**: search *StewBeet* in the Extensions panel, or [open it on the marketplace](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet).<br>
**Needs your venv**: no. It reads your sources and the files your build writes, nothing else.<br>
**Source Code**: [`extension/vscode`](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode) <br>

| You write | You get |
|-----------|---------|
| `.bolt` modules | The **Bolt** language: highlighting, completion and ctrl+click on the commands, and a lens per function the module writes |
| bolt inside a `.mcfunction` | The same, and Spyglass taken off a file it cannot parse |
| plain **beet**, `ctx.data.functions[p] = Function(...)` | The commands inside are commands: coloured, completed, checked, and linked to what the build wrote |
| **mecha** | Navigation from every generated line back to the source line it came from |
| **StewBeet** `write_*` helpers | All of the above, plus every `{...}` path resolved to what it really is |

## Setup

1. Install [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). It provides the completion, hover and errors the extension routes into your blocks.
2. For navigation to the build, add the [sniffer](../plugins/sniffer.md) plugin to your `beet.yml`:

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"    # writes the .mcfunction.map files the editor navigates with
```

That is the whole setup. The extension works without step 2, minus the links between your Python and the built pack.

## Bolt

<video src="/vscode_extension_bolt.mp4" controls loop muted playsinline preload="auto">
</video>

`.bolt` files open as **Bolt**, with a grammar generated from mecha's command tree: `item = 3` is Python, `item modify entity @s ...` is a command.

- **Completion, errors and ctrl+click** on the commands, through Spyglass. Python expressions are masked.
- **A lens per function** the module writes, leading to the generated file.
- **Computed paths stay clickable**: `function gui.open` resolves to what the last build wrote.

A `.mcfunction` holding bolt gets the `bolt` language id too. Spyglass still reads those from disk, so **StewBeet: Exclude Bolt Files From Spyglass** adds them to `.spyglassrc.json`, or your build keeps that list updated with the [spyglass](../plugins/spyglass.md) plugin.

See [Approach 4: Bolt](../2_writing_to_files/en.md#approach-4-bolt) for the language itself.

## beet

<video src="/vscode_extension_beet.mp4" controls loop muted playsinline preload="auto">
</video>

Plugins using beet's own API need nothing beyond `stewbeet.plugins.sniffer`:

- **Errors as you type**, no build needed. Build errors are relayed onto the Python that wrote the command.
- **Navigation both ways**: go to definition lands on the call that wrote a function, find references lists every writer, and a lens above each block opens what it generated.

## StewBeet

```python
write_function(f"{ns}:machines/tick", f"""
execute unless score @s energy.storage >= @s {ns}.energy_rate run return fail
execute if entity @s[tag={ns}.turbine] run function {ns}:turbine/tick
""")
```

Each `{...}` is filled with what the last build resolved it to, so ctrl+click and completion work on computed paths.
A name resolved on one line is reused where the build covers nothing, such as commands assembled in a variable.
Nothing evaluates your Python, and what stays unknown keeps a `_` mask.

### What counts as a block

| Written as | Example |
|------------|---------|
| `write_*` helpers | `write_function`, `write_versioned_function`, `write_load_file`, ... |
| A variable | `content = f"""..."""` and every `+=` up to the call that consumes it |
| A list | `.append`, `+= [...]`, literals, comprehensions, `"\n".join(lines)` |
| Your own function | Any parameter annotated `McFunction` |
| beet's own API | `Function(...)` from a string or a `list[str]`, plus `.append`, `.prepend` and `.lines` |

Highlighting a variable needs the `McFunction` annotation (a plain `str` alias from `stewbeet`). Everything else works without it.

## Commands

From the palette: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.

## Settings

All under `StewBeet.*`:

| Setting | Default | |
|---------|---------|---|
| `languageFeatures` | `true` | Completion, hover, signature help and go to definition inside the blocks |
| `suggestSpyglass` | `true` | Offer the Spyglass install once, when it is missing |
| `buildOutput` | `""` | Where the generated pack is, absolute or relative to the workspace. Empty searches the workspace |
| `sourceMapDiagnostics` | `true` | Relay build errors onto the Python that wrote the command |
| `resolveInterpolations` | `true` | Fill each `{...}` with what the last build resolved it to |
| `diagnosticRuleDenylist` | `["undeclaredSymbol"]` | Rules never relayed onto Python |
| `codeLens` | `true` | The link above a block that produced a function |
| `headerLinks` | `true` | Resource locations in a generated file's `#>` header |
| `boltInMcfunction` | `true` | Give a `.mcfunction` holding bolt the `bolt` language id |
| `enableBlockDecorations` | `true` | The coloured box around a block |
| `backgroundColor` | `rgba(80,40,0,0.15)` | Any CSS colour |
| `borderColor` | `rgba(200,120,30,0.30)` | Any CSS colour |
| `borderWidth` | `"2px"` | |

## Coming from Aegis

Compared to [Aegis](https://marketplace.visualstudio.com/items?itemName=thenuclearnexus.mecha-language-server), StewBeet is lighter and easier to install, but it does not provide Python symbols in completion yet.

| | Aegis | StewBeet |
|---|-------|----------|
| `.bolt` highlighting | None, read as `mcfunction` | **Bolt grammar** |
| Commands in Python strings | No | **Yes** |
| Source to build navigation | No | **Both directions** |
| Needs | `ms-python.python` and your environment | **Nothing** |
| `.bolt` completion | **Full compiler, Python symbols included** | Commands only, through Spyglass |

Keep Aegis if you need that last row.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): everything the extension reads, including Bolt.
- [stewbeet.plugins.sniffer](../plugins/sniffer.md): the source maps behind the navigation.
- [stewbeet.plugins.spyglass](../plugins/spyglass.md): keeping Spyglass off files it cannot parse.
