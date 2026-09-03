# Implementation Plan: StewBeet VS Code Developer Experience

**Branch**: `001-stewbeet-vscode-dx` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-stewbeet-vscode-dx/spec.md`

## Summary

Give StewBeet authors the editing experience Spyglass already gives `.mcfunction` authors, without StewBeet learning a single mcfunction rule.

Two independent mechanisms, both built on things that already exist:

1. **Virtual documents.** The extension already knows where every mcfunction string block sits (`blocks.js`). Project each block into a whitespace-padded virtual `.mcfunction` document and forward completion, hover and signature help to Spyglass with `vscode.execute*Provider`. Offsets are identity, so there is no position math.
2. **Source maps.** A StewBeet plugin emits Source Map v3 `.mcfunction.map` files linking each generated line back to the Python line that wrote it, **and only ever to the project's own source**. That one artifact powers go-to-definition onto the `write_function` call, find-references, relocating build diagnostics onto Python ranges, and Sniffer breakpoints, all from a published standard that other tools can already read.

The second mechanism's difficulty is not encoding, it is attribution. A jump that lands in `site-packages/stewbeet/plugins/` is worse than no jump, so the mapping is allowed to point at project files or nowhere at all. Content a plugin generates from a declaration is attributed to the declaration, through an ambient scope the plugin enters around its generation loop; the declaration's own site was captured by `Item.__post_init__`, which runs in the developer's file. Anything still unattributable is emitted unmapped.

Mechanism 1 needs no build and closes the completion half of issue #41. Mechanism 2 needs a build and closes the navigation half, plus unlocks the debugger.

**Scope beyond StewBeet.** The target is one extension serving plain beet, bolt, mecha and StewBeet, compatible with Spyglass rather than competing with it. Mechanism 2 is the layer that unifies them, because a `.mcfunction.map` consumer does not know or care which generator produced the map; mechanism 1 serves only StewBeet, because bolt interleaves commands with Python at statement level and needs the real compiler to find them. [contracts/dialects.md](./contracts/dialects.md) is the scope map and owns the sequencing.

## Technical Context

**Language/Version**: Python 3.14+ (StewBeet plugin), JavaScript / ES2022 on Node 18+ (VS Code extension, matching the current CommonJS `src/*.js` layout)

**Primary Dependencies**: `beet` 0.116+, `difflib` and `ast` from the stdlib (Python side). No new npm runtime dependency on the extension side: Spyglass is reached through `vscode.commands.executeCommand`, and the optional Spyglass extension is declared in `extensionDependencies` only if it is made hard-required (it is not, see NFR-003).

**Storage**: `.mcfunction.map` sidecar files in the build output. No database, no cache beyond beet's own.

**Testing**: `npm test` for the extension's pure modules (`node --test`, scoped to `test/*.test.js`) and `npm run test:integration` for the end-to-end pass against the real Spyglass; doctests plus `pytest` for the Python plugin. Contract fixtures under `contracts/`.

**Target Platform**: VS Code 1.74+ desktop. The virtual-document mechanism is desktop-only in practice because it relies on the Spyglass extension being installed.

**Project Type**: Two co-located deliverables in one repo: a beet plugin inside the Python package, and a VS Code extension. The extension is intended to grow into a multi-dialect tool covering beet, bolt, mecha and StewBeet; see [contracts/dialects.md](./contracts/dialects.md).

**Performance Goals**: Forwarded completion under 150 ms perceived latency (bounded by Spyglass). Source map emission under 20% of total build time with the plugin enabled, and within 2% of a baseline build when the plugin is absent, both as the median of five runs (NFR-002).

**Constraints**: Must not reimplement mcfunction syntax (NFR-001). Must not break the build when the extension is absent, and must not break the extension when the build is absent (FR-008). Mapping must survive `auto.headers` rewriting every function (FR-009).

**Scale/Scope**: A large StewBeet project generates on the order of 1000 functions and 50k generated lines per build.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against [constitution v1.0.0](../../.specify/memory/constitution.md), ratified 2026-09-01.

| Principle | Status | Evidence |
|---|---|---|
| I. Reuse Before Building | PASS | Every capability names the tool it reuses: Spyglass for language features, Source Map v3 for the mapping format, `difflib` for line reconciliation, mecha's own `AstNode.location` for bolt positions. Rejected alternatives are recorded in [research.md](./research.md). |
| II. Typed and Strict by Default | PASS | Every record in [data-model.md](./data-model.md) is a frozen dataclass, no `dict[str, dict[...]]` blobs. `pyright` strict and `ruff check` apply to the step B plugin; no Python has shipped yet. |
| III. Prove Assumptions Before Building On Them | PASS | The Q2 spike was run before implementation, is committed with its raw output at [spike/](./spike/), and is kept as a regression test at `extension/vscode/test/integration/`. The map format was validated segment by segment against a reference implementation at [contracts/reference/](./contracts/reference/). |
| IV. Degrade, Never Break | PASS | NFR-003 requires Spyglass to stay optional and every forwarded request resolves to `undefined` when it is absent; FR-008 requires the editor-only features to survive a missing build. Both are verified, see T022 and T027. |
| V. Maintainable by Humans | PASS | `plugins/sniffer/` is a package from the start, grouped by feature. No abstraction layer over Spyglass: requests are forwarded by their explicit command names. |

**Justified deviations**, both recorded in Complexity Tracking below: the global capture state on `Mem`, and the ambient attribution stack. Principle V discourages globals, and both are justified there rather than waved through.

**Post-design re-check**: no new violations. The design added no class that exists only to namespace a function, and no interface that is called once. The pure/impure module split in the extension is required by the constitution's own rule that JavaScript modules which can be pure must have no `vscode` import.

## Project Structure

### Documentation (this feature)

```text
specs/001-stewbeet-vscode-dx/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: options explored and rejected
├── data-model.md        # Phase 1: entities
├── quickstart.md        # Phase 1: how to validate
├── README.md            # Index and reading order
├── spike/               # Q2 probe, workspace and raw result. Passed, keep as regression test
├── contracts/
│   ├── spyglass-integration.md  # Priority deliverable, self-contained
│   ├── source-map.md            # The .mcfunction.map contract
│   ├── dialects.md              # Scope map: beet/bolt/mecha/StewBeet, layers, routing
│   ├── reference/               # Sniffer's working example, preserved verbatim
│   └── extension-api.md         # Provider and command contracts
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
python_package/stewbeet/
├── core/utils/io/
│   └── functions.py                 # + provenance capture on the overwrite path only
├── core/cls/item.py                 # + Item.origin captured in __post_init__
├── core/__memory__.py               # + Mem.source_map_chunks, Mem.attribution
├── plugins/datapack/custom_blocks/
│   └── __init__.py                  # + attribute_to(obj_block) around the generation loop
└── plugins/sniffer/
    ├── __init__.py                  # beet_default: the capture generator, listed early
    ├── emit.py                      # beet_default: writes the sidecars, listed before archive
    ├── capture.py                   # patches beet.Function.append/prepend, restores at teardown
    ├── origin.py                    # project-source filter, frame walk, cached ast index
    ├── attribution.py               # attribute_to scope, Mem.attribution stack
    ├── align.py                     # difflib alignment of recorded chunks vs final text
    └── encode.py                    # Source Map v3 + base64 VLQ

extension/vscode/
├── src/
│   ├── extension.js                 # step A: registers the providers below
│   ├── blocks.js                    # step A: + expose interpolation spans
│   ├── projection.js                # step A: pure projection and virtual URI paths, no vscode import
│   ├── virtual.js                   # step A: TextDocumentContentProvider + request forwarding
│   ├── sourcemap.js                 # step C: .mcfunction.map discovery, parse and lookup
│   ├── navigation.js                # step C: definition / references across the boundary
│   └── diagnostics.js               # step C: relay Spyglass diagnostics onto Python ranges
└── test/
    ├── blocks.test.js               # existing, extended in step A
    ├── projection.test.js           # step A: projection keeps offsets identical
    ├── sourcemap.test.js            # step C: decode round-trip against contract fixtures
    └── integration/                 # step A: end-to-end against the real Spyglass
```

`projection.js` and `virtual.js` are split rather than merged because the constitution requires
JavaScript modules that can be pure to have no `vscode` import, which is what keeps the projection
and URI logic testable under `node --test`.

**Structure Decision**: Both deliverables stay where they already live. The Python side becomes a normal StewBeet plugin package (`plugins/sniffer/`) so it is opt-in through the beet pipeline like every other plugin, with the single exception of the capture hook, which has to live in `core/utils/io/functions.py` because that is where writes happen. The extension keeps its flat CommonJS `src/` layout and its pure, unit-testable modules.

## Phasing

**Spyglass forwarding is the priority.** It is the headline ask, it has no build-time dependency, and it is the smaller of the two mechanisms. Its full design is in [contracts/spyglass-integration.md](./contracts/spyglass-integration.md), which is written to stand alone without the Spyglass checkout.

| Phase | Delivers | Depends on | Rough size |
|---|---|---|---|
| **A. Spyglass forwarding** | Completion, hover, signature help inside blocks. Definition landing in the generated `.mcfunction`. Closes half of #41 with no build required. | Nothing. Q2 spike passed, see [spike/](./spike/). | ~250 lines JS |
| **B. Source map emission** | `.mcfunction.map` files, project-source targets only. Unblocks Sniffer independently of the extension. | Nothing | ~280 lines Python |
| **B2. Attribution scopes** | Plugin-generated content maps to the declaration that caused it, starting with `custom_blocks`. Incremental: unscoped plugins emit unmapped lines. | B, plus a declaration resolver B does not provide | ~60 lines Python, then ~5 per plugin |
| **C. Map-driven navigation** | Definition landing on the `write_function` call, references, diagnostics relocated onto Python. Closes the rest of #41. | A and B | ~200 lines JS |
| **C2. Real content in the projection** | Interpolated paths resolve, so navigation works on the idiom StewBeet projects actually use. Plus the three papercuts step C's first real run exposed. | C | ~150 lines JS |
| **D. `bolt` language id + grammar** | Nothing registers `.bolt` today, so those files have no language id at all and no server can select them. | Nothing | small |
| **E. Mecha AST map emitter** | Maps for bolt/mecha read straight from `AstNode.location`. No capture, no alignment. | Shared `encode` from B | ~80 lines Python |
| **F. Bolt live editing** | Adopt, route to, or replace aegis. Needs its own research pass before sizing. | D | unsized |
| **G. Upstream `env.plugins`** | Deletes phase A in favour of a real Spyglass plugin. Optional, unbounded timeline. | Upstream review | 2 PRs |

**C2 exists because C's first run on a real project found the ceiling.** Everything works, and almost nothing is reachable: SimplEnergy writes exactly one literal resource location in its whole source, because the StewBeet idiom computes paths in Python (`function {ns}:...`, `function {funcs["work"]}`). The projection masks every interpolation with `_`, so Spyglass sees `function ___:utils/foo`, resolves nothing, and there is nothing for C to rewrite. Completion is unaffected, since it acts on what you type. Navigation on an already-written path is not.

Phase A ships first because it is the visible ask and has no build-time dependency. Phase B can proceed in parallel since it touches only Python.

**B2 is not just wiring.** `attribute_to` reads `Item.origin`, and B leaves that field `None` on every declaration: `resolve_origin` anchors tier 1 on a **write call** confirmed against the AST index, and a `Block(...)` constructor is not one. That check is what stops a plugin's write from attributing to the user's `main()`, so it cannot simply be relaxed. B2 therefore opens with a separate resolver that anchors on the constructor's caller instead, and returns nothing when that caller is itself library code.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Global mutable capture state on `Mem` | Provenance has to be recorded at every `write_*` call without changing any public signature or asking callers to pass a recorder. | Threading a recorder parameter through `write_function`, `write_versioned_function`, `write_load_file`, `write_tick_file`, `write_unload_file` and `write_scheduled_function` changes six public APIs for a debug-only feature. |
| An ambient attribution stack, which is a second global | Plugin-generated content has no project frame on the stack at all, so the frame walk cannot reach the declaration that caused it. Something has to carry that context across the gap. | Passing the declaration explicitly to every write would put a source-map argument into plugin code that has nothing to do with source maps. Attributing to the user's entry point instead is in-project and useless. |
| One extra field on `Item` | The declaration's own site must be captured while the developer's frame is still on the stack, which is only true inside `__post_init__`. | Recomputing it later is impossible, the frame is gone. Keeping a side table keyed by item id duplicates the lifetime of `Mem.definitions` for no gain. |
| Two definition sources (virtual doc in phase A, source map in phase C) | Phase A ships before any build exists and its definition result is free. | Waiting for phase C to ship any navigation delays the feature for no gain. Phase C replaces phase A's definition provider rather than adding to it, so the duplication is temporary by construction. |
| Alignment pass instead of trusting recorded positions | `auto.headers` rewrites every function after it is written, so recorded line numbers are stale by the end of the pipeline. | Making each rewriting plugin maintain the mapping spreads the invariant across the codebase and breaks silently whenever a new plugin is added. |
