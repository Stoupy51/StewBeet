# StewBeet

> Editor support for the [beet](https://github.com/mcbeet/beet) ecosystem: **beet**, **bolt**, **mecha** and **[StewBeet](https://stewbeet.paralya.fr/)**.
> `.bolt` files get their own language, and the mcfunction strings inside your Python get highlighting, completion, errors and links to the built datapack.

https://github.com/user-attachments/assets/18b87420-9b65-4971-8c51-e72eae709e65

| You write                                               | You get                                                                                                                            |
|---------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| `.bolt` modules                                         | The **Bolt** language: advanced highlighting, completion and ctrl+click on the commands, and a lens per function the module writes |
| bolt inside a `.mcfunction`                             | The same, and Spyglass taken off a file it cannot parse                                                                            |
| plain **beet**, `ctx.data.functions[p] = Function(...)` | The commands inside are commands: coloured, completed, checked, and linked to what the build wrote                                 |
| **mecha**                                               | Navigation from every generated line back to the source line it came from                                                          |
| **StewBeet** `write_*` helpers                          | All of the above, plus every `{...}` path resolved to what it really is                                                            |

Every example below comes from [`demo/`](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode/demo), a pack you can build and open yourself.

## Quick start

1. Install [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). It provides completion, hover and errors.
2. For navigation to the build, add the sniffer plugin to your beet config (`beet.yml`):

```yaml
require:
    - "stewbeet.plugins.sniffer"  # <- this one (requires "stewbeet" to be pip-installed or in your venv)
```

## Bolt

https://github.com/user-attachments/assets/57fd9d18-1643-45bc-8257-4942865c9be4

`.bolt` files open as **Bolt**, with a grammar generated from mecha's command tree:
`item = 3` is Python, `item modify entity @s ...` is a command.

- **Completion, errors and ctrl+click** on commands, through Spyglass. Python expressions are masked.
- **A lens per function** the module writes, leading to the generated file(s).
- **Computed paths stay clickable**: `function gui.open` resolves to what the last build wrote.

### Bolt inside a `.mcfunction`

These files get the `bolt` language id too. Spyglass still reports them from disk,
so **StewBeet: Exclude Bolt Files From Spyglass** adds them to `.spyglassrc.json`,
or your build can keep that list updated:

```yaml
pipeline:
    - "mecha"
    - "stewbeet.plugins.spyglass"
```

## beet

Plugins using beet's own API need nothing else than `stewbeet.plugins.sniffer`:

![Beet code highlighting](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/beet.png)

https://github.com/user-attachments/assets/92a49027-a47a-49f5-aa6a-2236f975bc25

- **Errors as you type**, no build needed. Build errors are relayed onto the Python that wrote the command.
- **Navigation both ways**: go to definition lands on the call that wrote a function, find references lists every writer, and a lens above each block opens what it generated.

## StewBeet

```py
write_function(f"{ns}:machines/tick", f"""
execute unless score @s energy.storage >= @s {ns}.energy_rate run return fail
execute if entity @s[tag={ns}.turbine] run function {ns}:turbine/tick
""")
```

Each `{...}` is filled with what the last build resolved it to, so ctrl+click and completion **work on computed paths**.
A name resolved on one line is reused where the build covers nothing, such as commands assembled in a variable.
Nothing evaluates your Python, and what stays unknown keeps a `_` mask.

### What counts as a block

| Written as        | Example                                                                                 |
|-------------------|-----------------------------------------------------------------------------------------|
| `write_*` helpers | `write_function`, `write_versioned_function`, `write_load_file`, ...                    |
| A variable        | `content = f"""..."""` and every `+=` up to the call that consumes it                   |
| A list            | `.append`, `+= [...]`, literals, comprehensions, `"\n".join(lines)`                     |
| Your own function | Any parameter annotated `McFunction`                                                    |
| beet's own API    | `Function(...)` from a string or a `list[str]`, plus `.append`, `.prepend` and `.lines` |

Highlighting a variable needs the `McFunction` annotation (a plain `str` alias from `stewbeet`). Everything else works without it:

![MCFunction type highlighting](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/mcfunction_type.png)

## Coming from [Aegis](https://marketplace.visualstudio.com/items?itemName=thenuclearnexus.mecha-language-server)

Compared to Aegis, StewBeet is lighter and easier to install, but it does not provide Python symbols in completion (yet).

|                            | Aegis                                      | StewBeet                        |
|----------------------------|--------------------------------------------|---------------------------------|
| `.bolt` highlighting       | None, read as `mcfunction`                 | **Bolt grammar**                |
| Commands in Python strings | No                                         | **Yes**                         |
| Source to build navigation | No                                         | **Both directions**             |
| Needs                      | `ms-python.python` and your environment    | **Nothing**                     |
| `.bolt` completion         | **Full compiler, Python symbols included** | Commands only, through Spyglass |

Keep Aegis if you need that last row.

## Does it need my venv?

**No.** The extension only reads your sources and the `.mcfunction.map` files your build writes thanks to the `stewbeet.plugins.sniffer` plugin.

## Settings

All under `StewBeet.*`:

| Setting                  | Default                 |                                                                                                  |
|--------------------------|-------------------------|--------------------------------------------------------------------------------------------------|
| `languageFeatures`       | `true`                  | Completion, hover, signature help and go to definition inside the blocks                         |
| `suggestSpyglass`        | `true`                  | Offer the Spyglass install once, when it is missing                                              |
| `buildOutput`            | `""`                    | Where the generated pack is, absolute or relative to the workspace. Empty searches the workspace |
| `sourceMapDiagnostics`   | `true`                  | Relay build errors onto the Python that wrote the command                                        |
| `resolveInterpolations`  | `true`                  | Fill each `{...}` with what the last build resolved it to                                        |
| `diagnosticRuleDenylist` | `["undeclaredSymbol"]`  | Rules never relayed onto Python                                                                  |
| `codeLens`               | `true`                  | The link above a block that produced a function                                                  |
| `headerLinks`            | `true`                  | Resource locations in a generated file's `#>` header                                             |
| `boltInMcfunction`       | `true`                  | Give a `.mcfunction` holding bolt the `bolt` language id                                         |
| `enableBlockDecorations` | `true`                  | The coloured box around a block                                                                  |
| `backgroundColor`        | `rgba(80,40,0,0.15)`    | Any CSS colour                                                                                   |
| `borderColor`            | `rgba(200,120,30,0.30)` | Any CSS colour                                                                                   |
| `borderWidth`            | `"2px"`                 |                                                                                                  |

Commands, from the palette: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.
**From a `.vsix`:** `code --install-extension StewBeet.vsix`, or **Extensions -> `...` -> Install from VSIX...**

mcfunction grammar taken from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction) and adapted to our needs.

