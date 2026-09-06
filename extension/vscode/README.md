
# StewBeet mcfunction Syntax

> Syntax highlighting, block decorations and **language features** for **mcfunction** code embedded inside [StewBeet](https://stewbeet.paralya.fr/) `write_*` Python calls, plus syntax highlighting for **`.bolt`** files.

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
| `headerLinks`            | `true`                  | Make resource locations in a generated file's `#>` header clickable |
| `boltInMcfunction`       | `true`                  | Give a `.mcfunction` holding bolt the `bolt` language id, so Spyglass is not asked to parse it |
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

**Commands handed over in a variable count too.** `content = f"""..."""` followed by
`write_function(path, content)` gets the block box, completion and errors, and so does a later
`content += """..."""`. To colour the commands as well, annotate the variable:

```python
from stewbeet import McFunction

content: McFunction = f"""
say hi
function {ns}:greet
"""
content += """
say appended, coloured too
"""
write_function(f"{ns}:hello", content)
```

`McFunction` is `str`, so annotating changes nothing about how the value behaves. It exists because
a grammar matches one place at a time and cannot tell that `content` reaches a `write_function`
call seven lines down, so you say so instead. Everything except the colours works without it.

The annotation carries to every `+=` onto the same name, up to the first statement that is not
one, so a function built by appending is coloured throughout. A `+=` onto a different name is left
alone.

**A list of commands works the same way.** Annotate it `list[McFunction]` and every `append` onto
it is coloured, including the ones inside an `if` or a `for`, along with the entries of a list
literal:

```python
output_list: list[McFunction] = []
if machine == "electric_brewing_stand":
    output_list.append('data modify entity @s foo set value {"Slot":0b}')
else:
    output_list.append('say otherwise')
```

An `append` onto any other name ends the run and is left alone.

**Your own functions count too.** Annotate a parameter `McFunction` and the strings passed to it
are treated as blocks:

```python
def write(path: str, cont: McFunction) -> None:
    write_function(path, cont)

write("ns:hello", "execute if score #x obj matches 1 run say hi")
```

That one is detection rather than colour: the call gets the block box, completion and errors,
because the extension reads your whole file and can see the `def`. Syntax colours come from a
grammar, which matches one place at a time and cannot connect a call to a `def` elsewhere, so the
commands inside stay uncoloured. Annotating the variable is what colours it.

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
| Diagnostics | Command errors underlined on the Python line, as you type, with no build |

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

Five commands come with it, from the palette:

| Command | What it does |
| ------- | ------------ |
| StewBeet: Go to Python Source | From a generated `.mcfunction`, open the Python that wrote the line |
| StewBeet: Go to Generated Function | The inverse, from a Python line to what it produced |
| StewBeet: Reload Source Maps | Drop the cache when a build finished outside the watcher's view |
| StewBeet: Refresh Build Diagnostics | Ask for the errors now instead of waiting |
| StewBeet: Show Diagnostics Status | Say what the relay has seen, so a quiet relay is not mistaken for a clean file |
| StewBeet: Exclude Bolt Files From Spyglass | Add the `.mcfunction` files holding bolt to your project's `.spyglassrc.json` |

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

### Writing a function with beet's own API

The six `write_*` helpers are not the only thing recognised. beet's own way of putting a function in the pack works too, in every spelling:

```python
ctx.data.functions["ns:mine"] = Function("say hi")
ctx.data["ns"].functions["mine"] = Function("say hi")
ctx.data[Function]["ns:mine"] = Function("say hi")
ctx.data.functions["ns:mine"] = Function(["say one", "say two"])   # one block per entry
ctx.data.functions["ns:mine"].append("say more")
```

All of these get colours, completion, diagnostics and a lens to what they generated, and the source map points back at the line that wrote them.

**The subscript is what makes it safe.** A bare `Function("say hi")` is left alone, because the class name is common enough to appear in unrelated Python; giving one a path is what marks it as a datapack function. A wrapper of your own opts in the same way it always did, by annotating its parameter:

```python
def put(path: str, content: McFunction):
    ctx.data.functions[path] = Function(content)

put("ns:mine", "say hi")
```

### Bolt files

`.bolt` files open as **Bolt** instead of plain text, with syntax highlighting and `#` comment toggling. Nothing else registers that extension, so before this they had no language id at all, which also meant no language server could ever be asked to serve them.

Bolt is Python with commands interleaved at statement level, so the grammar treats Python as the ground and commands as the exception:

```python
from server:core import SERVER_TICK      # server:core is a resource location, not a syntax error

class Ammo(Component):
    def build(self):
        append function PLAYER_TICK:     # command, and PLAYER_TICK stays Python
            execute if predicate has_item_predicate(self.item.d()) run function self.tick
        return self.item                 # Python, because `return` is Python's keyword first
```

A word that is both a command and an identifier, such as `item`, `data`, `time` or `list`, is only a command when what follows it is not Python: `item = 3` is an assignment, `item modify entity @s ...` is a command.

Completion, hover and go-to-definition *inside* a `.bolt` file need a compiler-backed language server, which only mecha can provide, and that is not part of this extension. Navigation across the build boundary does work, and needs no server at all:

- **A lens on each function the file produced**, at the first line that produced it, leading to the generated `.mcfunction`.
- **A lens on the generated file leading back**, and the resource locations in its `#` header comments become links: `#> ns:name` opens the bolt that wrote it, `@within` opens the caller.

Both need a build that emitted `.mcfunction.map` sidecars. Add `stewbeet.plugins.sniffer.mecha` to your pipeline, **before** `mecha`, and they appear.

### Bolt inside a `.mcfunction`

A project can enable bolt syntax inside `.mcfunction` files, and StewBeet's own minimal template does:

```python
# src/data/minimal/function/hello.mcfunction
for i in range(1, 6):
    say f"Hello, world! {i}"
```

That file is a `.mcfunction`, so Spyglass parses it as commands, fails on the `for`, and underlines most of it. When bolt is detected in one, the extension gives it the `bolt` language id instead, so it is highlighted as what it is. A vanilla `.mcfunction` is never touched, and neither is anything a build wrote. Turn it off with `StewBeet.boltInMcfunction`.

**The language id is only half of it.** Spyglass indexes a whole data pack off disk, so it reports the file whether or not you have it open, and no extension can clear another extension's diagnostics. Spyglass has its own exclusion list, which does silence it, so **StewBeet: Exclude Bolt Files From Spyglass** adds the file to your project's `.spyglassrc.json`. You are offered this once, only when there is something to fix, and nothing is written unless you accept.

## Grammar

mcfunction grammar from [MinecraftCommands/syntax-mcfunction](https://github.com/MinecraftCommands/syntax-mcfunction), bundled via [StewBeet](https://github.com/Stoupy51/StewBeet/blob/main/extension/vscode/syntaxes/mcfunction.tmLanguage.json).

The bolt grammar's command names are generated from mecha's own command tree rather than written by hand; the regeneration command is recorded in the grammar file.

## Installation

**From the marketplace:** search *StewBeet* in the Extensions panel.

**From a `.vsix` file:**
```bash
code --install-extension stewbeet-1.0.0.vsix
```
Or: **Extensions -> `...` -> Install from VSIX...**

