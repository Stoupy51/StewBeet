# 001: StewBeet VS Code Developer Experience

Give StewBeet authors the editing experience Spyglass already gives `.mcfunction` authors, without StewBeet learning a single mcfunction rule.

Closes [issue #41](https://github.com/Stoupy51/StewBeet/issues/41): autocomplete inside `write_function` strings, and ctrl+click from a function reference to the `write_function` that created it.

## Read in this order

| Document | What it holds |
|---|---|
| [spec.md](./spec.md) | The problem, six user scenarios, twelve functional requirements, three success criteria. |
| [research.md](./research.md) | Six architectural options with the reasoning for each adoption and rejection. Five resolved unknowns, and all five open questions now closed with their reasoning. |
| [spike/](./spike/) | The Q2 spike, its probe workspace and its raw output. **Passed.** Keep it as a regression test. |
| [plan.md](./plan.md) | Technical context, constitution check, file-by-file structure, phasing, complexity justifications. |
| [contracts/spyglass-integration.md](./contracts/spyglass-integration.md) | **The priority deliverable.** Everything about making Spyglass answer questions about StewBeet's Python files, self-contained. |
| [contracts/source-map.md](./contracts/source-map.md) | The `.mcfunction.map` format, guarantees, and test fixtures. Validated segment by segment against Sniffer's reference implementation, preserved at [contracts/reference/](./contracts/reference/). |
| [contracts/dialects.md](./contracts/dialects.md) | **The scope map.** The four dialects, the two embedding shapes, the three layers, and the Spyglass routing fix. |
| [contracts/extension-api.md](./contracts/extension-api.md) | Providers, commands, settings the extension registers. |
| [data-model.md](./data-model.md) | Entities on both sides of the boundary. |
| [quickstart.md](./quickstart.md) | How to validate each phase against a real project. |

## The two mechanisms, in one paragraph each

**Spyglass forwarding.** The extension already knows where every mcfunction string block sits (`extension/vscode/src/blocks.js`). Project each block into a virtual `.mcfunction` document that is the Python buffer with everything outside the block replaced by spaces, then forward completion, hover and signature help to Spyglass with `vscode.execute*Provider`. Offsets are identity, so there is no position math anywhere. Spyglass's document selector carries no scheme filter, which is the single fact the whole approach rests on. No build required.

**Source maps.** A StewBeet plugin emits Source Map v3 `.mcfunction.map` files linking each generated line back to the Python line that wrote it, and **only ever to the project's own source**, never into the StewBeet package or any library. That one artifact powers go-to-definition onto the `write_function` call, find-references, relocating build diagnostics onto Python ranges, and Sniffer breakpoints.

## The long-term target

One extension serving plain **beet**, **bolt**, **mecha** and **StewBeet**, compatible with Spyglass rather than competing with it. [contracts/dialects.md](./contracts/dialects.md) is the scope map.

The key structural fact: source maps are dialect-agnostic and the live-editing layers are not. Once a build emits `.mcfunction.map`, navigation, diagnostic relocation and Sniffer debugging work identically whether StewBeet, bolt, mecha or a hand-written beet plugin produced the output. That is the layer that makes it one product rather than four.

## Priority and sequencing

Spyglass forwarding first. It is the headline ask, it has no build-time dependency, and it is the smallest piece.

| Step | Delivers | Dialect | Blocked by |
|---|---|---|---|
| **A. Spyglass forwarding** | Completion, hover, signature help. Definition landing in the generated file. | StewBeet | Nothing. The Q2 spike passed, see [spike/](./spike/). |
| **B. `stewbeet.plugins.sniffer`** | `.mcfunction.map` files. Unblocks Sniffer independently of the extension. | StewBeet | Nothing. Parallel to A. |
| **B2. Attribution scopes** | Plugin-generated content maps to the declaration that caused it. | StewBeet | B. Incremental, plugin by plugin. |
| **C. Map-driven navigation** | Definition on the authoring line, references, diagnostics relocated. | **any dialect with maps** | A and B. |
| **D. `bolt` language id + grammar** | Syntax highlighting for `.bolt`, which nothing on this machine provides today. | bolt | Nothing. |
| **E. Mecha AST map emitter** | Maps straight from `AstNode.location`, no reconstruction needed. | bolt, mecha | C for the payoff. |
| **F. Bolt live editing** | Adopt or route to a mecha-backed server. Largest and least defined. | bolt, mecha | D, plus its own research pass. |
| **G. Upstream `env.plugins`** | Collapses step A into a real Spyglass plugin. Optional, unbounded timeline. | Upstream review. |

**C is where this stops being a StewBeet tool.** It consumes maps without knowing who wrote them, so E makes bolt projects light up with no further extension work.

## External context this feature depends on

- **Spyglass**, checkout at `d:/advanced_desktop/Spyglass`. Its architecture is recorded in `contracts/spyglass-integration.md` Part 1 with file and line references, so that document stands alone if the checkout is gone.
- **Sniffer**, checkout at `d:/advanced_desktop/sniffer`. A Fabric mod plus VS Code extension exposing a running game as a Debug Adapter. `.mcfunction.map` consumption was not implemented in that checkout, which had only `pathMapping` for remote paths. Its author has since supplied a **working reference implementation of the map format**, copied into [contracts/reference/](./contracts/reference/) so it cannot be lost, and confirmed that the `sourcesContent` field in it is an oversight to be ignored. The format is settled with nothing outstanding; `contracts/source-map.md` is written against it, segment by segment.
- **shulker**, checkout at `d:/advanced_desktop/shulker`. A real bolt-heavy beet project: 141 `.bolt`, 14 `.py`, zero `.mcfunction` in `src/`. The test bed for the bolt side, and the evidence that the file partition in `contracts/dialects.md` holds.
- **aegis**, checkout at `d:/advanced_desktop/aegis`. An existing mecha/bolt language server plus VS Code and JetBrains clients. Right architecture for bolt, incompatible with Spyglass for one line of configuration. See Option G in research.md.
- **StewBeet's own extension**, `extension/vscode/`. Today a TextMate injection grammar plus block decorations. `src/blocks.js` is reused unchanged except for exposing interpolation spans.
