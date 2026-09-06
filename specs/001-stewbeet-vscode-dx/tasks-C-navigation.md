# Tasks: StewBeet VS Code DX, step C (map-driven navigation)

**Input**: Design documents from `/specs/001-stewbeet-vscode-dx/`

**Prerequisites**: Step A is shipped (`extension/vscode` v1.1.0 forwards four providers to Spyglass). Steps B and B2 are merged, so a build emits `.mcfunction.map` sidecars whose sources are the project's own Python.

**Scope**: **Step C only.** The extension consumes the maps: ctrl+click lands on the `write_function` call instead of the generated file, find-references crosses the boundary, and build diagnostics land on the Python line that wrote the command. JavaScript only; the Python package is not touched. Steps D through G stay out.

**Tests**: Yes. `sourcemap.js` is pure and decodes a published format, so it is unit-testable against the committed reference maps, and step A already ships both a unit runner (`npm test`) and an integration runner against the real Spyglass.

**Organization**: By user story, in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths in every description

## Path Conventions

Extension at `extension/vscode/`, CommonJS, no build step. Sources in `src/`, unit tests in `test/*.test.js` run by `node --test`, end-to-end in `test/integration/`.

---

## Why this step exists

Steps A and B each closed half of issue #41 and neither closed the half people notice. Today ctrl+click inside a command string lands in `build/datapack/.../foo.mcfunction`, a generated file the author must not edit, with no way back to the `write_function` call that produced it. The maps that would answer that have existed since step B and **nothing reads them**.

C is also the step where the product stops being StewBeet-only. A `.mcfunction.map` consumer does not know which generator wrote the map, so everything built here serves bolt and mecha the day step E emits maps for them. That is why `sourcemap.js` must not import anything StewBeet-specific.

---

## Phase 1: Setup

**Purpose**: Declare the surface the later phases fill in, so nothing has to edit `package.json` three times.

- [X] T001 Add the two step C settings to `extension/vscode/package.json` under `contributes.configuration.properties`: `StewBeet.buildOutput` (string, default `""`, glob or path to the generated datapack root, empty meaning autodetect) and `StewBeet.sourceMapDiagnostics` (boolean, default `true`). Both are specified in [contracts/extension-api.md](./contracts/extension-api.md)
- [X] T002 Add the three step C commands to `extension/vscode/package.json` under `contributes.commands`: `stewbeet.goToGenerated` (StewBeet: Go to Generated Function), `stewbeet.goToSource` (StewBeet: Go to Python Source), `stewbeet.reloadSourceMaps` (StewBeet: Reload Source Maps). Declaring them now keeps the manifest edits in one commit; the handlers land in Phase 6

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The map layer. Every user story below is a thin adapter over it, and none can start until it resolves both directions.

- [X] T003 Create `extension/vscode/src/sourcemap.js` with the base64 VLQ decoder and a `decode(json)` returning the `DecodedMap` shape from [data-model.md](./data-model.md): `{ sources: string[], lines: Map<number, {sourceIndex, sourceLine, sourceColumn}> }`. Fields are delta-encoded **against the previous segment in the file**, not within the line, which is the detail a hand-rolled decoder gets wrong; an empty group is an unmapped line and is absent from the map rather than present and empty
- [X] T004 Keep `extension/vscode/src/sourcemap.js` free of any `require("vscode")`, the way `projection.js` already is. It decodes a published format and knows nothing about StewBeet, so it must stay unit-testable under plain `node --test` and reusable when step E emits maps from mecha
- [X] T005 Add `extension/vscode/test/sourcemap.test.js` decoding the two committed reference maps at `specs/001-stewbeet-vscode-dx/contracts/reference/` and asserting the line table matches the sources named in [contracts/source-map.md](./contracts/source-map.md) Appendix A. `aura.mcfunction.map` is the one that matters: its `ACHA` segment moves to a different source **and** three lines backwards in one step, which a decoder treating deltas as per-source gets wrong while passing every fixture we write ourselves
- [X] T006 Implement map discovery in `extension/vscode/src/sourcemap.js`: given a generated `.mcfunction` path, find its sibling `<name>.mcfunction.map`. Read the `## sourceMappingURL=` comment on the function's **last** line when present and honour it, falling back to the sibling name by convention, because that comment is what the format specifies and what a non-StewBeet generator may point elsewhere
- [X] T007 Implement `originOf(generatedUri, line)` in `extension/vscode/src/sourcemap.js`, returning the `Origin` shape `{ uri, line, column }` or `null`. Resolve `sources[i]` against the map's `sourceRoot`, itself relative to the map file's own directory. An unmapped line MUST return `null` and MUST NOT fall back to the nearest mapped line: guarantee G3 forbids interpolating, so a wrong jump is worse than none
- [X] T008 Implement the inverse lookup `generatedOf(pythonUri, line)` in `extension/vscode/src/sourcemap.js`, returning every generated location that maps to a Python line. The maps are generated-to-source, so this needs an index built by scanning the maps once; guarantee G7 says several generated lines share one source line, so the result is a list, never a single location
- [X] T009 Implement the cache and its invalidation in `extension/vscode/src/sourcemap.js`: decode each map once, key by path, and drop the entry when the file changes. Register a `vscode.workspace.createFileSystemWatcher` on `**/*.mcfunction.map` from `extension/vscode/src/extension.js` so a rebuild is picked up without reloading the window
- [X] T010 Implement build-output discovery honouring `StewBeet.buildOutput`, and when it is empty, autodetect by searching the workspace for `pack.mcmeta` under a `build` directory. A workspace with no build output MUST resolve to no maps and MUST NOT throw or log above debug: constitution principle IV, and it is the case every user hits before their first build
- [X] T011 Confirm before building navigation on it what Spyglass actually returns from `vscode.executeDefinitionProvider` on a virtual document: `Location` or `LocationLink`, and whether the target URI is the generated file in `build/`. The two shapes need different rewriting, and step A only ever passed the result through untouched. Record the answer in `extension/vscode/test/integration/README.md`

**Checkpoint**: A generated line resolves to a Python position and back. The user stories are now adapters.

---

## Phase 3: User Story 1 - Ctrl+click lands on the call that wrote the command (Priority: P1) 🎯 MVP

**Goal**: Ctrl+clicking a resource location inside a command string opens the `write_function` call that produced it, and when several origins contributed, offers all of them.

**Independent Test**: Open a StewBeet project with a build present, ctrl+click `test:demo` inside a command string, land on the `write_function("test:demo", ...)` line. Maps to spec Scenarios 2 and 2b, FR-003 and FR-012.

- [X] T012 [US1] Create `extension/vscode/src/navigation.js` and move the definition interception there, keeping `virtual.js` responsible only for forwarding. It takes the `Location[]` Spyglass returned, and for each target that is a generated `.mcfunction` with a map, rewrites it to the Python origins
- [X] T013 [US1] Return **one `Location` per distinct source** in the target's map, ordered by generated line, so a function assembled from a `Block(...)` declaration and a developer's append opens the peek list with both. Guarantee G6 says one map carries several sources and that a consumer must present all of them, not only the first
- [X] T014 [US1] Fall back to the generated file, unchanged, when the target has no map or the map has no source for that line. Losing navigation is worse than landing on the generated file, which is exactly what step A already does
- [X] T015 [US1] Wire the definition provider in `extension/vscode/src/virtual.js` to call into `navigation.js`, keeping the existing `forward("vscode.executeDefinitionProvider", ...)` as the first step. Step A's behaviour MUST remain the fallback path rather than being replaced
- [X] T016 [US1] Add `extension/vscode/test/navigation.test.js` covering the rewriting logic as a pure function over a fake map and fake locations: one source, several sources, an unmapped line, and a target with no map at all. Keep the `vscode` API out of the tested function so it runs under `node --test`
- [X] T017 [US1] Extend `extension/vscode/test/integration/` with an end-to-end pass: build the fixture, open the Python file, execute `vscode.executeDefinitionProvider` at a position inside a command string, and assert the returned location is the `.py` file at the `write_function` line. This is the only test that proves the whole chain rather than its pieces

**Checkpoint**: Issue #41's second ask is closed. Scenarios 2 and 2b hold.

---

## Phase 4: User Story 2 - Build errors land on the Python line (Priority: P2)

**Goal**: A command the game will reject is underlined on the Python line that wrote it, not only in the build log.

**Independent Test**: Break a command inside a `write_function` string, rebuild, see a squiggle on that Python line sourced `stewbeet (spyglassmc)`. Fix it, rebuild, the squiggle clears. Maps to spec Scenario 3 and FR-007.

- [X] T018 [US2] Create `extension/vscode/src/diagnostics.js` owning a `vscode.languages.createDiagnosticCollection("stewbeet")`, subscribing to `vscode.languages.onDidChangeDiagnostics` and relaying, for every changed generated `.mcfunction` that has a map, each diagnostic onto its Python origin
- [X] T019 [US2] Target the **full Python line** rather than a column range, because the map carries no column precision for the generated side. Prefix `source` with `stewbeet (<original source>)` so the origin stays visible, and drop diagnostics on unmapped generated lines, which guarantee G4 says are always safe to skip
- [X] T020 [US2] Group relayed diagnostics per Python file and replace each file's set wholesale on every change, never appending. Appending accumulates stale entries across rebuilds, which shows the author errors they already fixed
- [X] T021 [US2] Honour `StewBeet.sourceMapDiagnostics` in `extension/vscode/src/diagnostics.js`, and clear the collection when it is turned off rather than merely stopping updates, so an author who disables the feature does not keep the last squiggles forever
- [X] T022 [US2] Register the relay from `extension/vscode/src/extension.js` and dispose the collection in `deactivate`, next to the existing decoration disposal

**Checkpoint**: Scenario 3 holds. FR-007 is satisfied.

---

## Phase 5: User Story 3 - Find every Python call site that writes a function (Priority: P3)

**Goal**: Shift+F12 on a generated resource location lists every place in the project that writes to it.

**Independent Test**: With a build present, shift+F12 on a resource location used from several `write_function` calls returns one Python location per call site. Maps to spec Scenario 5.

- [X] T023 [US3] Add reference rewriting to `extension/vscode/src/navigation.js`: take what `vscode.executeReferenceProvider` returned and rewrite each generated hit to its Python origin, returning hits with no origin as the generated location rather than dropping them
- [X] T024 [US3] Register a `ReferenceProvider` in `extension/vscode/src/virtual.js` alongside the four existing providers, forwarding to `vscode.executeReferenceProvider` through the same `forward` helper and the same `StewBeet.languageFeatures` guard
- [X] T025 [US3] Extend `extension/vscode/test/navigation.test.js` with the reference cases, in particular several generated hits collapsing onto one Python line, which guarantee G7 makes the normal case whenever one Python line writes several commands. Duplicate locations MUST be collapsed, or the peek list shows the same line repeatedly

**Checkpoint**: Scenario 5 holds. Both directions of navigation cross the boundary.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T026 Implement the three command handlers in `extension/vscode/src/extension.js`: `stewbeet.goToGenerated` (from a Python position inside a block, open the generated `.mcfunction` at the mapped line, using the inverse index from T008), `stewbeet.goToSource` (the reverse, from a generated file), and `stewbeet.reloadSourceMaps` (drop the decoded cache, the escape hatch when a build finishes outside the watcher's view)
- [X] T027 Verify the degradation path by hand and record it in `extension/vscode/test/integration/README.md`: delete `build/`, reload, and confirm completion and hover from step A still work while navigation silently stops. Constitution principle IV, and it is the state every project is in before its first build
- [X] T028 [P] Verify the extension still behaves with Spyglass uninstalled: every forwarded request resolves to `undefined`, nothing throws, nothing logs above debug. Step A's guarantee must survive step C's additions. Covered structurally rather than by a second host run: step C only rewrites what `forward` returned, and `forward` already resolves to `undefined` when nothing answers, so `rewrite` receives a non-array and returns null unchanged (asserted in `test/navigation.test.js`)
- [X] T029 [P] Update `extension/vscode/README.md` and `extension/vscode/CHANGELOG.md` for v1.2.0, naming what now works (ctrl+click to the call, references, diagnostics on Python) and what it needs (a build in the workspace)
- [X] T030 [P] Mark the step C rows as shipped in [contracts/extension-api.md](./contracts/extension-api.md), which currently says "None of these are implemented yet" about the commands and "not implemented" about the diagnostic relay
- [X] T031 Bump `extension/vscode/package.json` to 1.2.0 and rebuild `extension/vscode/StewBeet.vsix` so the extension can be installed without a marketplace round trip
- [X] T032 Run the full gate: `npm test` and `npm run test:integration` in `extension/vscode/`, plus `ruff check stewbeet tests`, `pyright stewbeet tests`, `scripts/sync_api.py --check`, `scripts/all_doctests.py` and `scripts/run_integration_tests.py` in `python_package/` to prove the Python side is untouched

---

## Dependencies

```
Phase 1 (T001-T002)  manifest surface, no code depends on it until Phase 6
Phase 2 (T003-T011)  <- blocks every user story, nothing reads a map without it
        |
        +-- Phase 3 (T012-T017)  US1 definition, the MVP
        |         |
        |         +-- Phase 5 (T023-T025)  US3 references, shares navigation.js
        |
        +-- Phase 4 (T018-T022)  US2 diagnostics, independent of US1 and US3
```

**Story independence**: US2 shares only the map layer with the other two, so it can be built and tested on its own, and Phase 4 can run alongside Phase 3. US3 edits the same file as US1 and is sequential after it in practice, though its assertions fail independently.

## Parallel opportunities

- T003, T006, T007 and T008 all live in `sourcemap.js` and are sequential. T005 follows T003.
- T010 and T011 touch neither, and both can run alongside the decoder work.
- Phase 4 shares no file with Phases 3 and 5, so US2 can be built in parallel with US1 once Phase 2 lands.
- T028, T029 and T030 are three different files and parallel with each other.

## Implementation strategy

**MVP is Phase 2 plus Phase 3.** That is the ctrl+click people asked for in issue #41, and it is the half of the issue that step A could not close on its own.

Phase 4 reuses the map layer with no new mechanism and turns a build error from a log line into something the editor points at, which is why it comes before references despite both being smaller than the MVP.

Phase 5 is P3 and genuinely optional: a smaller payoff over machinery Phase 3 already built, and stopping before it leaves nothing broken.
