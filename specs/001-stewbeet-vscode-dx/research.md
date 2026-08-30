# Phase 0: Research

## Landscape

### What exists today

| Piece | Location | What it does | Gap |
|---|---|---|---|
| StewBeet extension | [extension/vscode/](../../extension/vscode/) | TextMate injection grammar + block decorations. `blocks.js` already locates every mcfunction string block in a Python file. | No language service at all. |
| Spyglass | `@spyglassmc/*` on npm, VS Code extension `SPGoding.datapack-language-server` | Full LSP for `.mcfunction`, `.mcdoc`, snbt, pack JSON. Completion, hover, diagnostics, definition, references, semantic tokens, mcdoc-driven NBT checking. | Only sees files whose language id is `mcfunction`. Knows nothing about Python or beet. |
| Sniffer | [github.com/mcbookshelf/sniffer](https://github.com/mcbookshelf/sniffer) | Fabric mod + VS Code extension exposing a running game as a Debug Adapter. Breakpoints, stepping, call graph, in-game debug commands. | Maps breakpoints to `.mcfunction` files as written on disk. `.mcfunction.map` consumption is **not implemented**: only `pathMapping` (remote path rewriting) exists today. |
| StewBeet build output | `build/<pack>/data/<ns>/function/*.mcfunction` | Real datapack, already valid input for Spyglass. | Nothing ties a generated line back to the Python line that wrote it. |

### Verified facts about Spyglass

- `MetaRegistry.registerLanguage(languageID, options)` exists and takes a parser, completer, trigger characters, and file extensions (`packages/core/src/service/MetaRegistry.ts`). This is the sanctioned extension point.
- Initializers are hard-coded: `initializers: [mcdoc.initialize, je.initialize]` in `packages/language-server/src/server.ts:114` and again in the playground. There is no runtime loading.
- `Config.env.plugins: string[]` is **declared and defaulted to `[]` but never read anywhere in the repo**. The plugin API is announced in the package description and in the config schema, and does not exist.
- The VS Code client's document selector is `[{ language: 'mcfunction' }, { language: 'mcdoc' }, ...]` with **no scheme filter** (`packages/vscode-extension/src/extension.mts`). Any document with language id `mcfunction` is synced to the server, whatever its URI scheme.
- `Project.onDidOpen(uri, languageID, version, content)` rejects only the `archive:` scheme. Symbol resolution is project-global, not path-relative, so a document outside the project roots still completes against the project's symbol table.

## Options considered

### Option A: Virtual documents forwarded to Spyglass (request forwarding)

Register providers on `python`, build a virtual `.mcfunction` document per block under a custom scheme, forward requests with `vscode.executeCompletionItemProvider` and friends. This is the technique VS Code documents as [request forwarding](https://code.visualstudio.com/api/language-extensions/embedded-languages) for embedded languages: the virtual content is the Python buffer with everything outside the block replaced by whitespace, so offsets line up 1:1 and no position translation is needed.

- **Cost**: roughly 250 lines of JS on top of the existing `blocks.js`.
- **Buys**: completion, hover, signature help, document symbols, and a definition that lands in the generated `.mcfunction`.
- **Free upgrades**: every Spyglass release improves it with no work.
- **Risks**: depends on Spyglass's selector staying scheme-agnostic; the VS Code guide lists "cannot support diagnostic errors" as a limitation of this approach, though `vscode.languages.getDiagnostics(virtualUri)` plus `onDidChangeDiagnostics` does let a host relay them.

**Decision: adopt, and prioritise over everything else.** Smallest path to the headline ask, and it reimplements nothing. Full design, Spyglass facts sheet, spike protocol and fallbacks in [contracts/spyglass-integration.md](./contracts/spyglass-integration.md), written to stand alone without the Spyglass checkout.

### Option B: Own language server embedding `@spyglassmc/core`

Depend on `@spyglassmc/core` + `java-edition` + `mcfunction`, register a `python` language whose parser delegates to the mcfunction parser at string offsets.

- Architecturally correct, native offset handling via `Source` / `Range`, everything works including semantic tokens and formatting.
- Runs a **second** full Spyglass project in memory next to the user's Spyglass extension: duplicate mcmeta downloads, duplicate symbol tables. Or it replaces Spyglass entirely, and StewBeet inherits maintenance of a datapack LSP.

**Decision: reject.** Violates "smallest code" and makes StewBeet responsible for a language server it did not want to own.

### Option C: Upstream the dead `env.plugins` config into Spyglass

Implement plugin loading so `spyglass.json` can name packages whose `initialize(ctx)` runs against the real `MetaRegistry`, then ship `@stewbeet/spyglass-plugin` registering the `python` language. Requires a second upstream change to make the VS Code client's document selector dynamic.

- The genuinely clean end state: one Spyglass instance, one symbol table, and StewBeet's contribution is a parser shim of maybe 100 lines. It would also unlock Bolt and Mecha, so it is plausibly welcome upstream.
- Timeline is not ours. Two PRs, both in areas nobody has touched.

**Decision: pursue as a stretch goal, not a dependency.** Option A ships the same user-facing features today and is deleted the day Option C lands.

### Option D: Source maps for everything derived from the build

Emit Source Map v3 `.mcfunction.map` files next to generated functions. Orthogonal to A/B/C and the only way to get scenarios 2, 3, 4 and 5 right.

- Definition, references and diagnostics all become lookups against a mapping the build already knows, rather than guesses made by re-parsing Python.
- Sniffer's stated design already expects `.mcfunction.map` files, so this is the interop contract.

**Decision: adopt.**

### Option E: Static Python index of `write_*` call sites

Scan the workspace's `.py` files for `write_function("literal:path", ...)` and index resource location to Python location. Cheap, no build needed.

**Decision: reject.** Strictly weaker than Option D: it cannot resolve f-string paths, cannot see paths emitted by StewBeet's own plugins, and would be a second mechanism answering the same question. Once `beet watch` is running, the map is always current anyway.

### Option F: Validate strings at build time with Mecha

Mecha is already a StewBeet dependency and is a complete mcfunction parser in Python, but StewBeet only exposes it through `stewbeet ast` / `stewbeet codegen` inspection commands and never runs it over written content.

**Decision: out of scope here.** It would give build-time validation, not editor features, and Spyglass already validates the output. Worth a separate issue.

## Resolved unknowns

### How does StewBeet learn the Python origin of a written line?

The hard rule first: **a mapping may only ever point at the project's own source.** Never into the StewBeet package, never into beet, bolt, mecha, stouputils, site-packages or the stdlib. A line with no valid project origin is emitted unmapped. That is not a quality target, it is a validity condition, because a jump into `site-packages/stewbeet/plugins/...` is worse than no jump at all.

That rules out the obvious implementation. Walking out of the `stewbeet` package and taking the next frame is wrong for anything a plugin generates: when `plugins/datapack/custom_blocks` writes `place_secondary`, the frames above it are beet's pipeline runner and the user's entry point, and the declaration that actually caused the write returned long ago. Resolution needs two tiers.

**Tier 1, the frame walk.** Walk outward from `write_function` and take the innermost frame whose file passes the project-source filter. This nails the developer's own `write_function("ns:foo", """...""")`, and it also nails developer hooks invoked from inside a plugin, which is the answer you want in that case.

The frame gives the *call* line, not the string literal. A cached `ast` parse of that file resolves the enclosing `Call` node and reads the content argument's `lineno`:

- Literal `str` and `JoinedStr` (f-string) arguments both carry positions.
- Rendered f-strings can have a different line count than their literal; when counts disagree the chunk collapses onto the literal's first line rather than mapping wrongly.
- Non-literal content (a variable, a helper's return value) maps to the call line, flagged `exact: false`.

**Tier 2, the attribution scope.** When tier 1 finds nothing, the stack is entirely library code and the write is a plugin generating on behalf of a declaration. StewBeet plugins push that declaration onto an ambient stack around their generation loop:

```python
for item, obj_block in blocks.items():
	with attribute_to(obj_block):
		write_function(obj_block.functions.place_secondary, content)
```

`Item.__post_init__` already runs in the developer's file at declaration time, so it captures its own origin with the same tier-1 walk and stores it on the instance. The scope hands that stored origin to every write inside it.

`attribute_to` takes an optional field name (`attribute_to(obj_block, "on_place")`) so a plugin that knows the content came from a declared field can point at that keyword argument's literal instead of at the `Block(...)` call. The AST index already has the `Call` node, so reading one keyword out of it is free. Opt-in per call site, no plugin is obliged to use it.

**Tier 3**: no origin. `origin=None`, lines emitted as empty VLQ groups.

**The project-source filter.** A path is project source when it is under a configured root (defaulting to `ctx.directory`, beet's project directory) **and** not under any library directory. The second half is not redundant: StewBeet is often installed editable from a path inside the very repo being built, as in this one, so `python_package/stewbeet/` sits under the project root and must still be excluded. Exclusion is computed from the package directories of `stewbeet`, `beet`, `bolt`, `mecha` and `stouputils`, plus any `site-packages` component in the path.

**Alternatives considered**:
- *Frame walk only, no attribution scope*: attributes every plugin-generated line to the user's entry point, which is technically in the project and completely useless. Rejected.
- *Threading an origin parameter through the write API*: changes six public signatures for a debug feature, and every plugin author has to remember it. The ambient scope is opt-in and invisible when unused.
- *`co_positions()` on the caller frame*: gives the CALL instruction's span, not the argument's.
- *A `str` subclass carrying provenance*: infects every string StewBeet touches, and dies on the first `f"{x}"` or `.replace()`.

### How does the mapping survive post-processing?

It cannot be recorded once and trusted. `plugins/auto/headers` rewrites **every** function with `overwrite=True` to prepend a generated header block, and `auto.text_renders` / `auto.lang_file` substitute inside lines. So capture and emission are separated:

1. **Capture** (during writes): each `write_function` appends `(lines, python_file, python_line)` to a per-path chunk list, mirroring the existing append / prepend / overwrite semantics exactly.
2. **Emit** (end of pipeline): align the concatenated recorded lines against the function's final text with `difflib.SequenceMatcher`. `equal` and `replace` opcodes keep their mapping, `insert` opcodes (header lines) stay unmapped, `delete` opcodes are dropped.

stdlib only, roughly 40 lines, and it is transformation-agnostic: a future plugin that rewrites functions needs no changes here.

**Alternatives considered**: making every rewriting plugin maintain the mapping (invasive, and every new plugin becomes a chance to break it); forbidding rewrites (not an option, headers are a headline StewBeet feature).

### How do several origins share one function?

They do not need to share anything. Chunks are recorded in write order and each keeps its own origin, so a `place_secondary` assembled from a plugin's generation, a ticking plugin's addition and the developer's own append produces three runs of lines with three different origins. Per-line mapping already expresses that.

Two consequences worth stating:

- Go-to-definition on such a path returns a `Location[]`, not a single location, so VS Code shows the peek list. Ordered by generated line.
- `overwrite=True` clears the chunk list before recording, exactly as it clears the function text, so the origins it replaced disappear from the map. That is the correct answer and it falls out of mirroring the existing semantics rather than being special-cased.

### Which mapping format?

**Source Map v3** ([format internals](https://www.polarsignals.com/blog/posts/2025/11/04/javascript-source-maps-internals)), one sibling `foo.mcfunction.map` per generated function.

Sniffer's author has confirmed the intent to "not reinvent the wheel and reuse the way js/ts mapping is done", as JSON, without publishing an example file yet. So this is agreement on the format with the details still open, and [contracts/source-map.md](./contracts/source-map.md) is written to be sent as the concrete proposal.

The fit is exact, not approximate: a JS source map describes one bundled output built from many sources, which is what a generated `.mcfunction` assembled from several `.py` files is.

- Standard, so consumers already exist: `@jridgewell/trace-mapping` in JS, several readers in Python.
- Base64 VLQ encoding is about 15 lines to write ([reference](https://rosettacode.org/wiki/Variable-length_quantity#Python)), and StewBeet only needs the trivial subset: one segment per generated line, at generated column 0, with 4 fields `[genCol, sourceIndex, sourceLine, sourceCol]`. No `names`, no nested segments.
- The `.mcfunction.map` sibling naming is what Sniffer's design already assumes, so nothing needs negotiating.

**Alternatives considered**: a bespoke JSON line table (simpler to write, but every consumer then needs bespoke code, which is exactly the wheel we refuse to reinvent); a single whole-pack index file (one file to invalidate on any change, and it breaks the per-file discovery Sniffer expects).

### Where do the `.map` files go?

Next to the generated functions inside the build, discoverable by convention. Minecraft's function loader only reads `*.mcfunction` and ignores unknown siblings, so a dev build stays loadable. Release archives exclude them via the existing archive plugin.

An optional trailing `# sourceMappingURL=foo.mcfunction.map` comment matches the standard discovery mechanism. It must be the **last** line, since Sniffer counts comment lines when placing breakpoints.

## Open questions

- **Q1**: Should the map's source path be relative to the map file or to the project root? Relative to the map file matches Source Map v3, but build output can sit outside the workspace after `copy_to_destination`. Proposal: relative when possible, absolute `file:` URI otherwise.
- **Q2**: Does Spyglass's `LanguageClient` sync a virtual document that is opened but never shown in an editor? Needs a spike before committing to Option A. Fallback if not: open the virtual document in a hidden editor, or spawn a private `@spyglassmc/language-server` process.
- **Q3**: Send [contracts/source-map.md](./contracts/source-map.md) to Sniffer as the concrete proposal. Format is agreed, three details are not: the `.mcfunction.map` sidecar naming, whether a trailing `# sourceMappingURL=` comment is expected or forbidden, and whether unmapped lines are acceptable to their breakpoint placement (they must be, since generated headers cannot map anywhere).
- **Q4**: Which StewBeet plugins get an `attribute_to` scope in the first pass? `datapack/custom_blocks` is the motivating case. `finalyze/custom_blocks_ticking`, `datapack/loot_tables` and the manual generators are candidates. Everything without a scope simply emits unmapped lines, so this can be filled in incrementally and is not a blocker.
