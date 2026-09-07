
# StewBeet mcfunction Syntax

> The mcfunction strings inside your [StewBeet](https://stewbeet.paralya.fr/) Python are code: highlighted, completed, checked as you type, and linked both ways to the datapack your build produces.
> Plus a language for `.bolt` files, which nothing else on the marketplace provides.

<!-- GIF 1, the hero. In SimplEnergy's machines.py: type inside a write_function block, completion
     fires on a command and then on your own paths after `{ns}:`. Ctrl+click a `function {ns}:...`
     and land in the generated file. Click the lens there and come back. ~12s, editor only. -->
![Completion and navigation inside a block](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/hero.gif)

## Quick start

1. Install [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). It answers the completion, hover and errors; this extension projects your strings to it. The extension offers the install once if it is missing, and everything else works without it.
2. For anything that crosses into the build, add the sniffer plugin to your `beet.yml`:

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"
```

That is the whole configuration.
The maps are written beside each generated function, and `stewbeet.plugins.archive` writes them before it zips, so the build directory and the zip agree.
Without a build nothing errors: navigation falls back to opening the generated `.mcfunction`.

## What you get

### Errors on your own lines, as you type

<!-- GIF 2. Type `scoreboard players ste #x obj 1` inside a block. The squiggle lands on the Python
     line with nothing built and nothing else open. ~6s. -->
![A command error underlined on the Python line](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/diagnostics.gif)

No build, and nothing under `build/` is ever opened.
Errors reported against generated files reach Python too, for the files you open yourself.
`undeclaredSymbol` is not relayed by default, since it fires on every objective a dependency declares; `StewBeet.diagnosticRuleDenylist` decides.

### Navigation across the boundary

<!-- GIF 3. The write_function in machines.py's fuel loop: the lens reads `consume_dust (+2 more)`,
     clicking opens the peek with all three. Then ctrl+click `@within` in a generated file. ~8s. -->
![A lens leading to every function a line produced](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/navigation.gif)

Go to definition on a resource location lands on the call that produced it, find references lists every call site writing to it, and a lens above each block leads to what it generated.
One line often produces several functions, a `write_function` in a loop or a `Block(id=...)` declaration, so the lens says how many and opens the peek list VS Code uses for references.
The `#>` header comments in a generated file are clickable in both directions.

### Interpolated paths

StewBeet rarely writes a literal resource location, and every `{...}` is Python that a datapack parser cannot read.
Each one is filled in with what the last build resolved it to:

```python
write_function(f"{ns}:utils/loop", f"""
function {ns}:utils/battery_switcher/loop
execute if score #height {ns}.data matches 150.. run say high
""")
```

Ctrl+click on `{ns}:utils/battery_switcher/loop` lands on the call that wrote it, and completion after `{ns}:` offers your own paths.
Nothing evaluates your Python: the value comes off the line the build produced.
A line no build covers keeps a `_` mask.

## What counts as a block

| Written as | Example |
|---|---|
| The `write_*` helpers | `write_function(path, content)`, `write_versioned_function`, `write_scheduled_function`; `write_load_file`, `write_unload_file`, `write_tick_file` take theirs first |
| A variable | `content = f"""..."""`, every `+=` onto it, up to the call that consumes it |
| A list | `lines.append(...)`, `lines += [...]`, a list literal, a comprehension |
| A joined list | `write_function(path, "\n".join(lines))`, where the separator is a separator |
| Your own function | a parameter annotated `McFunction` makes that argument a block at every call |
| beet's own API | `ctx.data.functions[path] = Function(...)` in all three spellings, `.append(...)` onto one, and `.obj.append(...)` |

Every string form works, `"""..."""` through `'...'`, with any `f`, `r`, `b` or `u` prefix.

![The same file without and with the extension](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/comparison.gif)

**Colours need one annotation.** A grammar matches one place at a time and cannot tell that `content` reaches a call seven lines down, so you say so.
`McFunction` is `str`, exported from `stewbeet`, so it changes nothing at runtime, and everything except the colours works without it:

```python
from stewbeet import McFunction

content: McFunction = f"""
say hi
function {ns}:greet
"""
content += "say appended, coloured too"

lines: list[McFunction] = []            # appends onto it are coloured too,
lines.append("say inside a branch")     # including inside an `if` or a `for`
```

A bare `Function("say hi")` with no path is left alone, and so is an `append` onto a name nothing writes.
The subscript, or the call that consumes the name, is what marks commands as commands.

## Bolt

<!-- GIF 4. hello.mcfunction from the minimal template: a wall of red squiggles, then the same file
     coloured with a lens on it. Follow with the exclusion prompt. ~8s. -->
![A bolt file before and after](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/bolt.gif)

`.bolt` files open as **Bolt** rather than plain text, with highlighting and comment toggling.
Nothing else registers that extension, so before this they had no language id at all.
Bolt is Python with commands interleaved, so the grammar treats Python as the ground and commands as the exception: `item = 3` is an assignment, `item modify entity @s ...` is a command.
The command names are generated from mecha's own command tree, so they cannot drift from what mecha accepts.

A `.mcfunction` holding bolt, which StewBeet's own minimal template ships, is detected and given the `bolt` language id too, so Spyglass is not asked to parse a `for` loop.
That is only half of it: Spyglass indexes a data pack off disk and reports the file whether or not you have it open, and no extension can clear another's diagnostics.
Its own exclusion list does silence it, so **StewBeet: Exclude Bolt Files From Spyglass** writes the file into your `.spyglassrc.json`, offered once and never written without your say-so.

**Your build can keep that list instead.** The editor reads the file and infers; the build knows.

```yaml
pipeline:
    - "mecha"
    - "stewbeet.plugins.spyglass"
```

It asks once in the terminal, remembers in `.beet_cache`, and keeps `env.exclude` in step on every build: an entry is taken back when a file stops needing it, a pattern you wrote is never touched, and a build with no terminal writes nothing.
Two signals decide, both read off the build rather than guessed: bolt generated Python for the file, or mecha split it into more than one function.

Navigation works in a bolt project exactly as in a Python one, from `.mcfunction.map` sidecars.
Completion *inside* a `.bolt` file needs a compiler-backed server, which only mecha can provide and which is not part of this extension.

## Configuration

All settings are under `StewBeet.*`:

| Setting | Default | |
|---|---|---|
| `languageFeatures` | `true` | Completion, hover, signature help and go to definition inside the blocks |
| `suggestSpyglass` | `true` | Offer the Spyglass install once, when it is missing |
| `buildOutput` | `""` | Where the generated pack is. Empty searches the workspace for maps |
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

Commands, from the palette: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.

## Grammar

mcfunction grammar from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction), bundled via [StewBeet](https://github.com/Stoupy51/StewBeet/blob/main/extension/vscode/syntaxes/mcfunction.tmLanguage.json).
The bolt grammar's command names are generated from mecha's command tree; the regeneration command is recorded in the grammar file.

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.

**From a `.vsix`:** `code --install-extension StewBeet.vsix`, or **Extensions -> `...` -> Install from VSIX...**

