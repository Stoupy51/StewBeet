# StewBeet

> Editor support for the [beet](https://github.com/mcbeet/beet) ecosystem: **beet**, **bolt**, **mecha** and **[StewBeet](https://stewbeet.paralya.fr/)**.
> `.bolt` files get a language of their own, which nothing else on the marketplace provides, and the mcfunction strings inside your Python are code: highlighted, completed, checked as you type, and linked both ways to the datapack your build produces.

<!-- GIF 1, the hero. Take 4 in demo/README.md: in machines.py, completion fires on a command and then on your own
     paths after `{ns}:`. Ctrl+click a `function {ns}:...` and land in the generated file. Click
     the lens there and come back. ~12s, editor only. -->
![Completion and navigation inside a block](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/hero.gif)

| You write | You get |
|---|---|
| `.bolt` modules | The **Bolt** language: highlighting that knows `item = 3` from `item modify entity @s`, comment toggling, and a lens per function the module writes |
| bolt inside a `.mcfunction` | The same, and Spyglass taken off a file it cannot parse |
| plain **beet**, `ctx.data.functions[p] = Function(...)` | The commands inside are commands: coloured, completed, checked, and linked to what the build wrote |
| **mecha** | Navigation from every generated line back to the source line, off the maps a build emits |
| **StewBeet** `write_*` helpers | All of the above, plus every `{...}` path resolved to what it really is |

Nothing here runs your project. See [Does it need my venv?](#does-it-need-my-venv) below.

## Quick start

1. Install [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). It answers the completion, hover and errors; this extension projects your strings to it. The extension offers the install once if it is missing, and everything else works without it.
2. For anything that crosses into the build, add the sniffer to your `beet.yml`:

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"
```

That is the whole configuration, for the helpers and for what mecha compiles alike.
A project with no StewBeet in it at all lists `stewbeet.plugins.sniffer.mecha` in its pipeline instead, before `mecha`.
The maps are written beside each generated function, and `stewbeet.plugins.archive` writes them before it zips, so the build directory and the zip agree.
Without a build nothing errors: navigation falls back to opening the generated `.mcfunction`.

## Bolt

<!-- GIF 2. Take 1 in demo/README.md: gui.bolt open, the status bar reading Bolt, then the three
     lenses, then the peek list one of them opens. ~8s. -->
![A bolt module, coloured, with a lens on each function it writes](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/bolt.gif)

`.bolt` files open as **Bolt** rather than plain text.
Nothing else registers that extension, so before this they had no language id at all.

Bolt is Python with commands interleaved, so the grammar treats Python as the ground and commands as the exception: `item = 3` is an assignment, `item modify entity @s ...` is a command.
The command names are generated from mecha's own command tree, so they cannot drift from what mecha accepts.

A module routinely writes dozens of functions, and each gets a lens on the line that opened it, so `function f"{self.path}/open":` leads to `voltaic:gui/pulverizer/open` in the build.
Navigation works in a bolt project exactly as in a Python one, from the `.mcfunction.map` sidecars.
Completion *inside* a `.bolt` file needs a compiler-backed server, which only mecha can provide and which is not part of this extension.

### Bolt inside a `.mcfunction`

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

## beet

A plugin that writes functions with beet's own API needs no helper and no StewBeet:

```python
ctx.data.functions["voltaic:turbine/tick"] = Function("""
execute store result score #height voltaic.data run data get entity @s Pos[1]
execute if score #height voltaic.data matches 150.. run scoreboard players add @s energy.storage 40
""")
```

Those two lines are commands, and everything below applies to them: completion, errors on the Python line, the lens to what they became, ctrl+click across the boundary.
All three spellings are read, `ctx.data.functions[p]`, `ctx.data["ns"].functions[p]` and `ctx.data[Function][p]`, along with `.append(...)` and `.prepend(...)` onto one.

### Errors on your own lines, as you type

<!-- GIF 3. Take 3 in demo/README.md, step 3: break `matches` in turbine.py and the squiggle lands
     on the Python line with nothing built and nothing else open. ~6s. -->
![A command error underlined on the Python line](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/diagnostics.gif)

No build, and nothing under `build/` is ever opened.
Errors reported against generated files reach Python too, for the files you open yourself.
`undeclaredSymbol` is not relayed by default, since it fires on every objective a dependency declares; `StewBeet.diagnosticRuleDenylist` decides.

### Navigation across the boundary

<!-- GIF 4. Take 3 step 4 and take 5: ctrl+click a path, land in the generated file, follow an
     `@within` header link, then the lens back. ~8s. -->
![A lens leading to every function a line produced](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/navigation.gif)

Go to definition on a resource location lands on the call that produced it, find references lists every call site writing to it, and a lens above each block leads to what it generated.
One line often produces several functions, a `write_function` in a loop or a `Block(id=...)` declaration, so the lens says how many and opens the peek list VS Code uses for references.
The `#>` header comments in a generated file are clickable in both directions.

**The links follow your edits.** A map records the line a command was written on when the build ran, and you keep typing afterwards.
Lines you delete above a call take its lens up with them, a line moved with alt+up keeps its own, and a call you delete outright loses its lens rather than sliding onto its neighbour.
Nothing is rebuilt for that, and a build puts everything back on the lines it just read.

## StewBeet

The helpers write one function per call, and the path is almost never a literal:

```python
write_function(f"{ns}:utils/loop", f"""
function {ns}:utils/battery_switcher/loop
execute if score #height {ns}.data matches 150.. run say high
""")
```

Every `{...}` is Python that a datapack parser cannot read, so each one is filled in with what the last build resolved it to.
Ctrl+click on `{ns}:utils/battery_switcher/loop` lands on the call that wrote it, and completion after `{ns}:` offers your own paths.
Nothing evaluates your Python: the value comes off the line the build produced.
A line no build covers keeps a `_` mask.

### What counts as a block

| Written as            | Example                                                                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| The `write_*` helpers | `write_function(path, content)`, `write_versioned_function`, `write_scheduled_function`; `write_load_file`, `write_unload_file`, `write_tick_file` take theirs first |
| A variable            | `content = f"""..."""`, every `+=` onto it, up to the call that consumes it                                                                                          |
| A list                | `lines.append(...)`, `lines += [...]`, a list literal, a comprehension                                                                                               |
| A joined list         | `write_function(path, "\n".join(lines))`, where the separator is a separator                                                                                         |
| Your own function     | a parameter annotated `McFunction` makes that argument a block at every call                                                                                         |
| beet's own API        | `ctx.data.functions[path] = Function(...)` in all three spellings, `.append(...)` onto one, and `.obj.append(...)`                                                    |

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

## Coming from Aegis

[Aegis](https://marketplace.visualstudio.com/items?itemName=thenuclearnexus.mecha-language-server) is the other extension for this ecosystem, and this one replaces it for everything except one thing.

|  | Aegis | This extension |
|---|---|---|
| `.bolt` highlighting | No grammar and no language: it maps `*.bolt` to the `mcfunction` language id, so a `for` loop is read as a command | A Bolt grammar, generated from mecha's command tree |
| Commands inside Python strings | Not covered | Coloured, completed, checked, and linked to the build |
| Source to build navigation | Not covered | Both directions, off the `.mcfunction.map` sidecars |
| What it needs to run | `ms-python.python`, a working environment, and your project loaded by a server it launches | Nothing. It reads files |
| Completion inside a `.bolt` file | Yes, from the real compiler | No, and it says so above |

That last row is the one honest reason to keep Aegis installed. Everything else it does, this does without asking for your interpreter, and it does the parts Aegis never covered.

## Does it need my venv?

**No.** The extension never imports, launches or looks for `stewbeet`, `beet`, `bolt` or `mecha`, so it does not care whether they are installed globally, in a `.venv`, in uv's cache or not at all. It reads three things and nothing else:

- your source files, for the blocks and the grammar,
- the `.mcfunction.map` sidecars your build wrote, for everything that crosses into the pack,
- whatever answers for the `mcfunction` language, in practice Spyglass, which ships its own server.

The bolt grammar's command names are generated from mecha's command tree offline and shipped inside the extension, so no mecha is needed to read a `.bolt` file either.

Your venv matters for exactly one thing: running `beet build`. Do that however you already do it, and the editor picks up what it wrote.

## Configuration

All settings are under `StewBeet.*`:

| Setting                  | Default                 |                                                                          |
|--------------------------|-------------------------|--------------------------------------------------------------------------|
| `languageFeatures`       | `true`                  | Completion, hover, signature help and go to definition inside the blocks |
| `suggestSpyglass`        | `true`                  | Offer the Spyglass install once, when it is missing                      |
| `buildOutput`            | `""`                    | Where the generated pack is. Empty searches the workspace for maps       |
| `sourceMapDiagnostics`   | `true`                  | Relay build errors onto the Python that wrote the command                |
| `resolveInterpolations`  | `true`                  | Fill each `{...}` with what the last build resolved it to                |
| `diagnosticRuleDenylist` | `["undeclaredSymbol"]`  | Rules never relayed onto Python                                          |
| `codeLens`               | `true`                  | The link above a block that produced a function                          |
| `headerLinks`            | `true`                  | Resource locations in a generated file's `#>` header                     |
| `boltInMcfunction`       | `true`                  | Give a `.mcfunction` holding bolt the `bolt` language id                 |
| `enableBlockDecorations` | `true`                  | The coloured box around a block                                          |
| `backgroundColor`        | `rgba(80,40,0,0.15)`    | Any CSS colour                                                           |
| `borderColor`            | `rgba(200,120,30,0.30)` | Any CSS colour                                                           |
| `borderWidth`            | `"2px"`                 |                                                                          |

Commands, from the palette: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.

## Grammar

mcfunction grammar from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction), bundled via [StewBeet](https://github.com/Stoupy51/StewBeet/blob/main/extension/vscode/syntaxes/mcfunction.tmLanguage.json).
The bolt grammar's command names are generated from mecha's command tree; the regeneration command is recorded in the grammar file.

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.

**From a `.vsix`:** `code --install-extension StewBeet.vsix`, or **Extensions -> `...` -> Install from VSIX...**
