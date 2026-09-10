# StewBeet

> Editor support for the [beet](https://github.com/mcbeet/beet) ecosystem: **beet**, **bolt**, **mecha** and **[StewBeet](https://stewbeet.paralya.fr/)**.
> `.bolt` files get a language of their own, and the mcfunction strings inside your Python become code: highlighted, completed, checked as you type, and linked both ways to the datapack your build produces.

<!-- hero.gif: take 4 of demo/README.md, which names every step and every line. -->
![Completion and navigation inside a block](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/hero.gif)

| You write | You get |
|---|---|
| `.bolt` modules | The **Bolt** language: highlighting that knows `item = 3` from `item modify entity @s`, completion and ctrl+click on the commands, and a lens per function the module writes |
| bolt inside a `.mcfunction` | The same, and Spyglass taken off a file it cannot parse |
| plain **beet**, `ctx.data.functions[p] = Function(...)` | The commands inside are commands: coloured, completed, checked, and linked to what the build wrote |
| **mecha** | Navigation from every generated line back to the source line it came from |
| **StewBeet** `write_*` helpers | All of the above, plus every `{...}` path resolved to what it really is |

Nothing here runs your project, so nothing here needs your venv. Every example and every recording below comes from [`demo/`](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode/demo), a seventeen function pack you can build and open yourself.

## Quick start

1. Install [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). It answers the completion, hover and errors; this extension projects your strings to it. The extension offers the install once if it is missing, and everything else works without it.
2. For anything that crosses into the build, add the sniffer to your `beet.yml`:

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"
```

That is the whole configuration, for the helpers and for what mecha compiles alike.
A project with no StewBeet in it lists `stewbeet.plugins.sniffer.mecha` in its pipeline instead, before `mecha`.
Without a build nothing errors: navigation falls back to opening the generated `.mcfunction`.

## Bolt

<video src="./extension/vscode/images/bolt.mp4" autoplay loop muted playsinline></video>

`.bolt` files open as **Bolt** rather than plain text. Nothing else registers that extension, so before this they had no language id at all.

Bolt is Python with commands interleaved, so the grammar treats Python as the ground and commands as the exception: `item = 3` is an assignment, `item modify entity @s ...` is a command. The command names are generated from mecha's own command tree, so they cannot drift from what mecha accepts.

One module writes many functions, and each gets a lens on the line that opened it, so this one leads to `voltaic:gui/pulverizer/open` in the build:

```py
@cached_property
def open(self):
    function f"{self.path}/open":
        playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
        data modify entity @s equipment.head set from storage voltaic:gui Icon
```

**Completion, diagnostics and ctrl+click work inside a `.bolt` file too**, through the same projection the Python strings use: the command lines are kept and dedented, the Python around them is blanked, and Spyglass answers about a document that reads as a plain `.mcfunction`. Type `playound` and it is underlined where you typed it, with no build in between.

**A path your Python computes stays clickable.** `function gui.open` reaches Spyglass as whatever the last build wrote there, so ctrl+click leads to `voltaic:gui/pulverizer/open`, and from there to the line of the module that opened it.

What the projection cannot give you is anything only the compiler knows: a Python symbol, a bolt expression, the value behind `f"{self.path}/open"` that no build has resolved yet. Those are masked, and nothing is completed or reported about them.

### Bolt inside a `.mcfunction`

A `.mcfunction` holding bolt, which StewBeet's minimal template ships, is given the `bolt` language id too, so Spyglass is not asked to parse a `for` loop.

That is only half of it: Spyglass indexes a data pack off disk and reports the file whether or not you have it open, and no extension can clear another's diagnostics. Its own exclusion list does silence it, so **StewBeet: Exclude Bolt Files From Spyglass** writes the file into your `.spyglassrc.json`, offered once and never written without your say-so.

**Your build can keep that list instead.** The editor reads the file and infers; the build knows.

```yaml
pipeline:
    - "mecha"
    - "stewbeet.plugins.spyglass"
```

It asks once in the terminal, remembers in `.beet_cache`, and keeps `env.exclude` in step on every build: an entry is taken back when a file stops needing it, and a pattern you wrote is never touched.

## beet

A plugin writing functions with beet's own API needs no helper and no StewBeet. All of `demo/src/turbine.py` is blocks:

```py
ctx.data.functions["voltaic:turbine/tick"] = Function("""
execute store result score #height voltaic.data run data get entity @s Pos[1]
execute if score #height voltaic.data matches ..59 run return run function voltaic:turbine/stall
""")

# A Function is a list of commands behind its text, and takes one as readily
ctx.data.functions["voltaic:turbine/stall"] = Function([
    "# The turbine is turning, and too low for any wind to reach it",
    'data modify entity @s item.components."minecraft:item_model" set value "voltaic:turbine_stalled"',
])
ctx.data.functions["voltaic:turbine/stall"].lines.append("stopsound @a[distance=..16] ambient voltaic:turbine")
```

<!-- beet.gif: takes 3 and 5 of demo/README.md. -->
![Errors and navigation in a plain beet plugin](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/beet.gif)

**Errors arrive as you type**, with no build, and with nothing under `build/` ever opened. Errors reported against generated files reach Python too, for the files you open yourself. `undeclaredSymbol` is not relayed by default, since it fires on every objective a dependency declares and Spyglass cannot see those.

**Navigation crosses the boundary both ways.** Go to definition on a resource location lands on the call that produced it, find references lists every call site writing to it, and a lens above each block leads to what it generated. One line often produces several functions, so the lens says how many and offers them by name. The `#>` header comments in a generated file are clickable in both directions.

## StewBeet

The helpers write one function per call, and the path is almost never a literal:

```py
write_function(f"{ns}:machines/tick", f"""
execute unless score @s energy.storage >= @s {ns}.energy_rate run return fail
execute if entity @s[tag={ns}.turbine] run function {ns}:turbine/tick
""")
```

Every `{...}` is Python that a datapack parser cannot read, so each one is filled in with what the last build resolved it to. Ctrl+click on `{ns}:turbine/tick` lands on the call that wrote it, in another file and in another dialect, and completion after `{ns}:` offers your own paths. Nothing evaluates your Python: the value comes off the line the build produced, and a line no build covers keeps a `_` mask.

### What counts as a block

| Written as | Example |
|---|---|
| The `write_*` helpers | `write_function(path, content)`, `write_versioned_function`, `write_scheduled_function`; `write_load_file`, `write_unload_file`, `write_tick_file` take theirs first |
| A variable | `content = f"""..."""`, every `+=` onto it, up to the call that consumes it |
| A list | `lines.append(...)`, `lines += [...]`, a list literal, a comprehension |
| A joined list | `write_function(path, "\n".join(lines))`, where the separator is a separator |
| Your own function | a parameter annotated `McFunction` makes that argument a block at every call |
| beet's own API | `ctx.data.functions[path] = Function(...)` in all three spellings, from a string or a `list[str]`, plus `.append`, `.prepend`, `.lines.append`, `.lines.extend` and `.obj.append` |

Every string form works, `"""..."""` through `'...'`, with any `f`, `r`, `b` or `u` prefix.

**Colours need one annotation.** A grammar matches one place at a time and cannot tell that `work` reaches a call six lines further down, so you say so. `McFunction` is `str`, exported from `stewbeet`, so it changes nothing at runtime, and everything except the colours works without it:

```py
work: McFunction = f"""
loot replace block ~ ~ ~ container.1 loot {ns}:pulverizer/iron_dust
"""
work += f"scoreboard players reset #timer {ns}.data\n"
write_function(f"{ns}:machines/pulverizer/work", work)
```

## The links follow your edits

<!-- edits.gif: take 6 of demo/README.md. -->
![Lenses moving with the calls they belong to](https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images/edits.gif)

A map records the line a command was written on when the build ran, and you keep typing afterwards. Lines you delete above a call take its lens up with them, a line moved with alt+up keeps its own, and a call you delete outright loses its lens rather than passing it to the line underneath. Nothing is rebuilt for any of that, and a build puts everything back on the lines it just read.

## Coming from Aegis

[Aegis](https://marketplace.visualstudio.com/items?itemName=thenuclearnexus.mecha-language-server) is the other extension for this ecosystem, and this one replaces it for everything except one thing.

|  | Aegis | This extension |
|---|---|---|
| `.bolt` highlighting | No grammar and no language: it maps `*.bolt` to the `mcfunction` language id, so a `for` loop is read as a command | A Bolt grammar, generated from mecha's command tree |
| Commands inside Python strings | Not covered | Coloured, completed, checked, and linked to the build |
| Source to build navigation | Not covered | Both directions, off the `.mcfunction.map` sidecars |
| What it needs to run | `ms-python.python`, a working environment, and your project loaded by a server it launches | Nothing. It reads files |
| Completion and errors inside a `.bolt` file | Everything, from the real compiler: Python symbols and bolt expressions included | Commands, selectors and resource locations, through Spyglass. The Python is masked |

That last row is the one honest reason to keep Aegis installed.

## Does it need my venv?

**No.** The extension never imports, launches or looks for `stewbeet`, `beet`, `bolt` or `mecha`, so it does not care whether they are installed globally, in a `.venv`, or not at all. It reads your source files, the `.mcfunction.map` sidecars your build wrote, and whatever answers for the `mcfunction` language, in practice Spyglass, which ships its own server. Even the bolt grammar's command names are generated from mecha's command tree offline and shipped inside the extension.

Your venv matters for one thing: running `beet build`. Do that however you already do, and the editor picks up what it wrote.

## Settings

All under `StewBeet.*`:

| Setting | Default | |
|---|---|---|
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

Commands, from the palette: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.
**From a `.vsix`:** `code --install-extension StewBeet.vsix`, or **Extensions -> `...` -> Install from VSIX...**

mcfunction grammar from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction). The bolt grammar's command names are generated from mecha's command tree; the regeneration command is recorded in the grammar file.
