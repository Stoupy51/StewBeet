# Contract: the four dialects, and how one extension serves them

The goal is one extension covering plain **beet**, **bolt**, **mecha** and **StewBeet**, compatible with Spyglass rather than competing with it.

This document is the scope map. It exists because the four dialects are not four flavours of the same problem: two of them embed mcfunction in fundamentally different ways, and that difference decides which mechanism can serve them.

## The two embedding shapes

**Lexically delimited** (StewBeet). Commands live inside Python string literals. The boundaries are found by lexing quotes, which `extension/vscode/src/blocks.js` already does with no compiler and no project build.

```python
write_function("ns:demo", """
execute as @a run say hi
""")
```

**Semantically interleaved** (bolt, mecha). Commands and Python-like code alternate at statement level, indentation-scoped. Nothing short of the real compiler can say which lines are commands.

```python
class Ammo(Component):
    def build(self):
        append function PLAYER_TICK:
            execute if predicate has_item_predicate(self.item.conditional_dict()) run function self.tick_reload
```

That is real code from [shulker](file:///d:/advanced_desktop/shulker) (`src/component/ammo.bolt`). `append function ...:` and `execute if predicate ... run function ...` are commands; `class`, `def` and the `has_item_predicate(...)` call are Python. No regex separates them, and the `self.tick_reload` inside a command argument is a Python expression.

**Consequence**: the virtual-document trick in [spyglass-integration.md](./spyglass-integration.md) serves StewBeet and cannot serve bolt. Bolt needs a compiler-backed language server. That is not a preference, it is what the grammar forces.

## Three layers

| Layer | Serves | Mechanism | Dialect-specific? |
|---|---|---|---|
| **1. Source maps** | everything the build emits | `.mcfunction.map` sidecars, consumed by the extension and by Sniffer | **No.** This is the golden layer. |
| **2. Live editing, delimited** | StewBeet | virtual documents forwarded to Spyglass | StewBeet only |
| **3. Live editing, interleaved** | bolt, mecha | compiler-backed server | bolt/mecha only |

Layer 1 is the one worth building first and the one that unifies the product. Once a build emits maps, navigation back to source, diagnostics relocation onto the authoring line, and Sniffer breakpoints all work **identically** whether the generator was StewBeet's `write_function`, a bolt module, a mecha rule or a hand-written beet plugin. The consumer side does not know or care which dialect produced the map.

Layers 2 and 3 are the parts that cannot be shared, and they are additive: a project using neither still gets layer 1.

## Emitting maps per dialect

Same output contract ([source-map.md](./source-map.md)), two very different producers.

**StewBeet**: no source positions exist anywhere, so they are reconstructed. Capture hooks `beet.Function.append` / `.prepend` plus `write_function`'s overwrite path, resolves an origin by frame walk plus a cached AST index, and reconciles against the final text with `difflib` because `auto.headers` rewrites every function afterwards. That machinery is the subject of [research.md](../research.md).

**bolt and mecha**: the positions already exist. Every `mecha.AstNode` carries

```python
location: SourceLocation      # NamedTuple(pos, lineno, colno)
end_location: SourceLocation
```

so emitting a map is a walk over the compiled AST reading `location` off each `AstCommand`, with no frame walking and no AST re-parse. It gets column precision for free, which StewBeet's path explicitly does not promise: a nested `execute function ./goodbye:` maps to the `function` token inside that line rather than to its start.

This is why the emitter is split: `capture` is StewBeet-specific, while `encode`, `sidecar`, `sources` and `align` are shared. A mecha backend plugs a different front half onto the same encoder.

**`align` is shared rather than StewBeet-specific**, which the first design got wrong. A StewBeet pipeline runs `auto.headers` after `mecha`, so every function gains a header block after it was compiled and nothing lines up positionally, exactly as on the StewBeet side. The minimal template does this, so the mecha producer reconciles with `difflib` too.

**Three rules the implementation settled**, all measured on [shulker](file:///d:/advanced_desktop/shulker) and recorded in the spike at [spike/bolt-attribution/](../spike/bolt-attribution/):

1. **List the emitter before `mecha`** in the pipeline. It works after its `yield`, and beet unwinds generator plugins in reverse, so listing it first is what leaves the `Module` compilation units and their sources in the database. This is the opposite of `stewbeet.plugins.sniffer.emit`'s placement rule.
2. **A location carries no filename, and the compilation unit's `filename` names only the first contributing module.** The file is recovered from the redundancy between `pos`, `lineno` and `colno`, with the command's own first word breaking ties at positions every file agrees on, such as the very first character.
3. **Index the database by resource location, not by file instance.** A plugin that rewrites a function replaces the object the pack holds, and an identity lookup then finds nothing.

Roughly a third of a real bolt project's command lines map. The rest have no trustworthy origin: modules bolt synthesises in memory, positions valid in no project source, and positions whose line and column are valid in the declaring file while the offset disagrees. That last group is why the offset is checked at all, since dropping it maps generated commands onto whatever Python declaration happens to sit at that line.

## The Spyglass compatibility problem, precisely

[Aegis](file:///d:/advanced_desktop/aegis) is a mecha/bolt language server (`aegis-core`, `aegis-server` in Python, `aegis-vscode` and `aegis-jetbrains` as clients). It shadows beet's `Context`, `Pipeline` and `ProjectBuilder` to compile a document and hand its providers a real mecha AST plus diagnostics, with features for completion, definition, hover, references, rename and semantic tokens. Architecturally it is the right answer for bolt, because only mecha can parse bolt.

Its incompatibility with Spyglass is not architectural. It is one line:

```jsonc
"aegis.client.documentSelector": { "default": [ { "scheme": "file", "language": "mcfunction" } ] }
```

Both extensions claim language id `mcfunction`, so installing both gives doubled completions, doubled and contradictory diagnostics, and competing semantic tokens. Aegis contributes **no `languages` and no `grammars`** of its own; it declares `minecraftcommands.syntax-mcfunction` and `ms-python.python` as extension dependencies and rides their language ids.

**The fix is routing, not merging.** Partition by file, because the dialects genuinely do not overlap:

| File | Owner | Why |
|---|---|---|
| `.mcfunction` in a vanilla datapack | **Spyglass** | Better at vanilla: mcdoc, registries, NBT checking. |
| generated `.mcfunction` in build output | **Spyglass**, results mapped back through layer 1 | It is a real datapack. |
| `.bolt` | **mecha-backed server** | Spyglass cannot parse it at all. |
| `.py` StewBeet strings | **Spyglass**, via virtual documents | Layer 2. |

The partition holds in practice: [shulker](file:///d:/advanced_desktop/shulker) is 141 `.bolt` files, 14 `.py`, and **zero** `.mcfunction` in `src/`. A bolt project's authored sources are `.bolt`; the `.mcfunction` files are build output.

The caveat to watch is `meta.bolt.entrypoint`, which shulker sets to `"*"`. A project can enable bolt syntax inside `.mcfunction` files, and then the partition needs the beet config to decide the owner rather than the extension alone.

**A project does do it: StewBeet's own minimal template.** `templates/minimal_template.zip` ships `src/data/minimal/function/hello.mcfunction` holding `for i in range(1, 6):` and `execute function ./goodbye:`, which is bolt inside a `.mcfunction`. The step E emitter maps it correctly, because it reads the compiled AST and never looks at the file extension.

**The partition is decided by content rather than by the beet config**, which is less than this section imagined and enough in practice. The extension reads the file: a Python import, a `def`, a `for` ending in a colon, a name followed by `=`, or a body left open with a `{` are all impossible in vanilla mcfunction, so a file carrying one is bolt and gets the `bolt` language id. Zero false positives over 1047 generated functions in shulker and SimplEnergy. Reading `meta.bolt.entrypoint` would be more principled and would answer no question the content does not already answer, so it stays unbuilt.

**Ownership has two halves, and only one is a language id.** Changing the id stops Spyglass answering for the open document. It does not stop Spyglass indexing the pack off disk and publishing about a file nothing has opened, and no VS Code API lets one extension clear another's diagnostics. Spyglass's own `env.exclude` does clear them, so the second half is a line in the project's `.spyglassrc.json`, offered by a command rather than written behind the author's back. Routing, not merging, applied to a config file.

What is still step F is everything *inside* such a file: completion, hover and go-to-definition need mecha, and no amount of routing substitutes for a compiler.

## An immediate, nearly free win

**Nothing registers the `.bolt` file extension.** Re-checked 2026-09-05 across all 35 installed extensions: no `languages` contribution and no grammar scope claims it, while 8 of them do contribute languages, which is the control that says the scan works. The marketplace has no bolt grammar either, and [mcbeet/bolt](https://github.com/mcbeet/bolt) ships none. So 141 files in shulker open as plain text, with no language id, no syntax highlighting and no comment toggling.

Contributing a `bolt` language id plus a TextMate grammar is small, self-contained, risk-free, and unblocks everything else, since a document with no language id cannot be selected by any language server. It is the first bolt-side step for that reason, not because highlighting is the most valuable feature.

## Naming

The StewBeet-side plugin is **`stewbeet.plugins.sniffer`**, named for the debugger it feeds.

**Two different things share that word, so prose must disambiguate every time.** Write the plugin as
`` `sniffer` `` in backticks, or "the `sniffer` plugin"; write the debugger as "Sniffer", capitalised
and unquoted. A sentence like "the sniffer plugin emits maps Sniffer reads" is correct and readable;
"sniffer emits maps sniffer reads" is not. The same applies to headings and task descriptions.

Its capture and alignment halves are StewBeet-specific, but the encoder and the output contract are not. The shared half is `encode`, `model`, `sidecar` and `filter`, none of which import anything from StewBeet.

**The mecha front end is `stewbeet.plugins.sniffer.mecha`**, a submodule rather than a distribution of its own. A plain beet project requires it by its dotted path like any other plugin, so a separate package would buy nothing but a second release process and a second changelog. The `stewbeet` install it implies is the honest cost, and it is one `pip install` against a dependency the project already builds with. Splitting it out remains possible later precisely because the shared half has no StewBeet imports to unpick.

## Sequencing

Deliberately incremental. Each step is independently useful and none blocks another except where stated.

| Step | Delivers | Dialect | Depends on |
|---|---|---|---|
| **A** | Completion, hover, signature help in `write_*` strings | StewBeet | Nothing. Spike passed. |
| **B** | `stewbeet.plugins.sniffer` emits maps | StewBeet | Nothing |
| **B2** | Attribution scopes reach declarations | StewBeet | B |
| **C** | Map-driven navigation, references, relocated diagnostics | **any dialect with maps** | A, B |
| **C2** | Interpolated paths resolve in the projection | StewBeet | C |
| **D** | `bolt` language id and grammar. **Shipped** | bolt | Nothing |
| **E** | Mecha AST map emitter, `stewbeet.plugins.sniffer.mecha`. **Shipped** | bolt, mecha | C for the payoff, D for nothing |
| **F** | Bolt live editing, adopt or route to a mecha-backed server | bolt, mecha | D |
| **G** | Upstream Spyglass `env.plugins`, collapses A | all | Upstream review |

C is the step where the product stops being a StewBeet tool. It consumes maps and does not care who wrote them, so E makes bolt projects light up with no further extension work.

**E proved that.** `extension/vscode/src/sourcemap.js` read 381 maps a bolt build produced and resolved all 815 of their origins to real `.bolt` lines, with no change to any file under `extension/vscode/src/`. One generated function, `event/reset.mcfunction`, resolves into three different modules.

F is the largest and least defined step, and the open question is whether to adopt aegis (contribute the routing fix upstream, or vendor its server) or to write a thinner one. That decision needs its own research pass and is deliberately not made here.
