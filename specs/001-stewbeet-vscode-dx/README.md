# 001: StewBeet VS Code Developer Experience

Give StewBeet authors the editing experience Spyglass already gives `.mcfunction` authors, without StewBeet learning a single mcfunction rule.

Closes [issue #41](https://github.com/Stoupy51/StewBeet/issues/41): autocomplete inside `write_function` strings, and ctrl+click from a function reference to the `write_function` that created it.

## Read in this order

| Document | What it holds |
|---|---|
| [spec.md](./spec.md) | The problem, six user scenarios, twelve functional requirements, three success criteria. |
| [research.md](./research.md) | Six architectural options with the reasoning for each adoption and rejection. Four resolved unknowns. Four open questions. |
| [plan.md](./plan.md) | Technical context, constitution check, file-by-file structure, phasing, complexity justifications. |
| [contracts/spyglass-integration.md](./contracts/spyglass-integration.md) | **The priority deliverable.** Everything about making Spyglass answer questions about StewBeet's Python files, self-contained. |
| [contracts/source-map.md](./contracts/source-map.md) | The `.mcfunction.map` format, guarantees, and test fixtures. The interop contract with Sniffer. |
| [contracts/extension-api.md](./contracts/extension-api.md) | Providers, commands, settings the extension registers. |
| [data-model.md](./data-model.md) | Entities on both sides of the boundary. |
| [quickstart.md](./quickstart.md) | How to validate each phase against a real project. |

## The two mechanisms, in one paragraph each

**Spyglass forwarding.** The extension already knows where every mcfunction string block sits (`extension/vscode/src/blocks.js`). Project each block into a virtual `.mcfunction` document that is the Python buffer with everything outside the block replaced by spaces, then forward completion, hover and signature help to Spyglass with `vscode.execute*Provider`. Offsets are identity, so there is no position math anywhere. Spyglass's document selector carries no scheme filter, which is the single fact the whole approach rests on. No build required.

**Source maps.** A StewBeet plugin emits Source Map v3 `.mcfunction.map` files linking each generated line back to the Python line that wrote it, and **only ever to the project's own source**, never into the StewBeet package or any library. That one artifact powers go-to-definition onto the `write_function` call, find-references, relocating build diagnostics onto Python ranges, and Sniffer breakpoints.

## Priority

Spyglass first. It is the headline ask, it has no build-time dependency, and it is the smaller of the two.

| Phase | Delivers | Blocked by |
|---|---|---|
| **A. Spyglass forwarding** | Completion, hover, signature help. Definition landing in the generated file. | The Q2 spike in `spyglass-integration.md` Part 5. Nothing else. |
| **B. Source map emission** | `.mcfunction.map` files. Unblocks Sniffer independently of the extension. | Nothing. Parallel to A. |
| **B2. Attribution scopes** | Plugin-generated content maps to the declaration that caused it. | B. Incremental, plugin by plugin. |
| **C. Map-driven navigation** | Definition landing on the `write_function` call, references, diagnostics on Python lines. | A and B. |
| **D. Upstream `env.plugins`** | Deletes phase A in favour of a real Spyglass plugin. Optional, unbounded timeline. | Upstream review. |

## External context this feature depends on

- **Spyglass**, checkout at `d:/advanced_desktop/Spyglass`. Its architecture is recorded in `contracts/spyglass-integration.md` Part 1 with file and line references, so that document stands alone if the checkout is gone.
- **Sniffer**, checkout at `d:/advanced_desktop/sniffer`. A Fabric mod plus VS Code extension exposing a running game as a Debug Adapter. `.mcfunction.map` consumption is **not implemented yet**, only `pathMapping` for remote paths. Its author has confirmed the intent to reuse the JS/TS source map approach as JSON, without publishing an example, so `contracts/source-map.md` is written to be sent as the concrete proposal.
- **StewBeet's own extension**, `extension/vscode/`. Today a TextMate injection grammar plus block decorations. `src/blocks.js` is reused unchanged except for exposing interpolation spans.
