# Tasks: StewBeet VS Code DX, step C2 (real content in the projection)

**Input**: Design documents from `/specs/001-stewbeet-vscode-dx/`

**Prerequisites**: Steps A, B, B2 and C are shipped. Extension 1.2.0 forwards to Spyglass, a build emits `.mcfunction.map` sidecars, and navigation crosses the boundary in both directions.

**Scope**: **Step C2 only.** The four things step C's first run on SimplEnergy exposed: interpolated paths do not resolve, diagnostics need the generated file open, relayed diagnostics carry library noise, and navigation is palette-only. JavaScript only; the Python package is not touched.

**Tests**: Yes. The substitution changes the one invariant everything in step A rests on, and a bug there silently corrupts the user's Python rather than merely failing to navigate.

**Organization**: By user story, in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths in every description

## Path Conventions

Extension at `extension/vscode/`, CommonJS, no build step. Sources in `src/`, unit tests in `test/*.test.js` run by `node --test`, end-to-end in `test/integration/`.

---

## Why this step exists

Step C works and almost nothing reaches it. SimplEnergy contains **one** literal resource location in its entire source, because the StewBeet idiom computes paths in Python: `function {ns}:utils/foo`, `function {funcs["work"]}`. The projection masks every interpolation with `_`, Spyglass sees `function ___:utils/foo`, resolves nothing, and step C has nothing to rewrite. Confirmed by the run: ctrl+click works on a literal path and does nothing on an interpolated one.

**The resolved text already exists on disk.** The generated `.mcfunction` holds `function simplenergy:utils/foo`, and the map already says which generated line each block line produced. The same correspondence step C validated to the character in the `Go to Python Source` direction can be read the other way to fill the projection with real content. Nothing needs to understand Python.

**The cost is the invariant.** `projection.js` returns a string of the same length as the Python buffer, so a position in one is the same position in the other and no range is ever translated. `{ns}` is four characters and `simplenergy` is eleven. Substituting breaks that, and every returned range then needs translating. Phase 1 settles how before any of it is wired in.

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Substitute real content into the projection and keep positions honest. Every user story below except US2 and US4 is unreachable until this holds.

There is no setup phase: the extension, its test runners and the map layer all exist from steps A and C.

- [X] T001 Decide and record the coordinate rule in `extension/vscode/src/projection.js`'s module comment before writing code: **lines stay in lockstep, columns do not**. One Python line remains one virtual line so the map's line-granular correspondence keeps working, while a line's columns may differ because a substitution changes its width. This is the invariant step A documented as "no range ever needs translating", and it is being deliberately narrowed
- [X] T002 Add `resolveLine(pythonLine, generatedLine, spans)` to `extension/vscode/src/projection.js`, recovering what each interpolation resolved to by anchoring on the literal text around it: the segment before a span must match, the segment after it must match, and what sits between in the generated line is the resolved value. Return `null` when the anchors do not match, which is what a stale build looks like
- [X] T003 Make `resolveLine` refuse a resolved value containing a newline, falling back to the `_` mask for that span. A substitution that adds a line breaks the one-Python-line-is-one-virtual-line rule that everything else depends on, and no resource location is ever multi-line
- [X] T004 Return a per-line column translation table alongside the substituted text from `project()` in `extension/vscode/src/projection.js`: for each line, the spans whose width changed, as `{ start, pythonWidth, virtualWidth }`. Everything else in the line keeps its column
- [X] T005 Implement `toVirtual(position, table)` and `toPython(position, table)` in `extension/vscode/src/projection.js`, translating a column by summing the width deltas of the spans that start before it on that line. A position **inside** a substituted span maps to the span's start, since there is no meaningful character-level correspondence within it
- [X] T006 Extend `extension/vscode/test/projection.test.js`: substituting a longer value keeps the line count, keeps every newline offset, and round-trips `toPython(toVirtual(p))` for positions before, inside and after a span. The round-trip is the property that protects the user's buffer
- [X] T007 Add `StewBeet.resolveInterpolations` (boolean, default `true`) to `extension/vscode/package.json` and honour it in `extension/vscode/src/virtual.js`. Turning it off restores step A's masking exactly, which is the escape hatch if a project hits an alignment case this step did not foresee

**Checkpoint**: The projection can carry real content and positions survive the round trip.

---

## Phase 2: User Story 1 - Navigation works on the paths StewBeet actually writes (Priority: P1) 🎯 MVP

**Goal**: Ctrl+click on `function {ns}:utils/foo` lands on the `write_function` call, the same as it already does on a literal path.

**Independent Test**: In SimplEnergy, ctrl+click an interpolated resource location such as `function {ns}:utils/battery_switcher/loop` and land on the Python that wrote it. Maps to FR-018.

- [X] T008 [US1] Feed the generated content into the content provider in `extension/vscode/src/virtual.js`: for the block being served, look up each line's generated counterpart through `sourcemap.generatedFrom` and pass it to `project()`. A block with no map, or a line with no mapping, keeps the `_` mask for that line, so a project without a build behaves exactly as it does today
- [X] T009 [US1] Translate the outbound position in `forward()` in `extension/vscode/src/virtual.js` with `toVirtual` before handing it to Spyglass, and cache the translation table beside the served document so the inbound direction can reuse it
- [X] T010 [US1] Translate every range Spyglass returns back with `toPython`, in `extension/vscode/src/virtual.js`: hover ranges, definition ranges that point **inside the Python document**, and signature help. Ranges pointing at a generated file are step C's business and must not be touched here
- [X] T011 [US1] Translate or drop the edit ranges carried by completion items in `extension/vscode/src/virtual.js`, both `textEdit` and `additionalTextEdits`. **This is the one that can corrupt a buffer rather than merely fail**: an accepted completion applies its edit to the Python document, and an untranslated range overwrites the wrong characters. An edit whose range covers a substituted span MUST be dropped rather than guessed at
- [X] T012 [US1] Extend `extension/vscode/test/integration/` with an interpolated case: add `function {ns}:probe/alpha` to the fixture's `demo.py`, give the generated file the resolved text and a map that covers it, then assert both that completion still answers and that definition resolves to the Python line. The fixture's current block is entirely literal and cannot catch a substitution bug
- [X] T013 [US1] Verify by hand on SimplEnergy that accepting a completion inside a line containing an interpolation leaves the buffer intact. The unit tests cover the arithmetic; only a real editor covers what VS Code does with the edits

**Checkpoint**: FR-018 holds. Navigation applies to the code StewBeet projects are actually written in.

---

## Phase 3: User Story 2 - Diagnostics arrive without opening the generated file (Priority: P2)

**Goal**: Break a command, rebuild, see the squiggle on the Python line, without opening anything in `build/`.

**Independent Test**: With the build watched, introduce an error, rebuild, and see the squiggle appear on the Python line unaided. Maps to FR-019.

- [X] T014 [US2] Hand the changed generated files to the language server in `extension/vscode/src/diagnostics.js` by calling `vscode.workspace.openTextDocument` on them, which loads a document without showing it. A server publishes diagnostics only for documents it has been given, which is why the relay currently has nothing to relay until the author opens the file by hand
- [X] T015 [US2] Drive that from the existing `**/*.mcfunction` watcher and open **only the files the watcher reported**, in `extension/vscode/src/extension.js`. A full rebuild rewrites every function in the pack, and opening all of them at once is the difference between a refresh and a freeze
- [X] T016 [US2] Debounce the reaction in `extension/vscode/src/diagnostics.js` so one rebuild produces one pass rather than one per file, and cap how many documents are opened in a single pass. A pack with two thousand functions must degrade to a slower refresh, never to an unresponsive window
- [X] T017 [US2] Superseded by T035. FR-019 now reads diagnostics off the projection, so there is no rebuild-driven path left to verify: an error is squiggled as it is typed, with no build at all. The half that still matters, that a full rebuild does not lock the editor, moved to T035

**Checkpoint**: FR-019 holds. The relay works the way the author expected it to.

---

## Phase 4: User Story 3 - Library noise stays out of the Python (Priority: P2)

**Goal**: `Cannot find objective "energy.storage"`, raised because a dependency declares the objective and Spyglass cannot see it, stops landing on Python lines.

**Independent Test**: With the rule filtered, SimplEnergy shows no `undeclaredSymbol` squiggle on its Python while real errors still appear. Maps to FR-020.

- [X] T018 [US3] Add `StewBeet.diagnosticRuleDenylist` (array of strings, default `["undeclaredSymbol"]`) to `extension/vscode/package.json`, and filter on it in `extension/vscode/src/diagnostics.js` by matching the diagnostic's `code`. Spyglass is not wrong that the objective is undeclared; the noise is ours for moving it onto a Python line where it is far more intrusive than in a generated file nobody opens
- [X] T019 [US3] Document the default and how to empty it in `extension/vscode/README.md`, since a silenced-by-default rule that nobody can find is worse than the noise it replaces

**Checkpoint**: FR-020 holds. What reaches the Python is worth reading.

---

## Phase 5: User Story 4 - Navigation without the palette (Priority: P3)

**Goal**: A block that produced generated content says so in the editor, and the jump is one click.

**Independent Test**: Open a file with `write_function` blocks and see a clickable lens on each one whose content was generated. Maps to FR-021.

- [X] T020 [US4] Create `extension/vscode/src/codelens.js` with a `CodeLensProvider` for Python documents, placing one lens on each block whose path resolves to a generated file, invoking `stewbeet.goToGenerated`. Reuse `blocksOf` from `extension/vscode/src/virtual.js` rather than rescanning
- [X] T021 [US4] Show no lens at all when the block has no generated counterpart, in `extension/vscode/src/codelens.js`. A lens that reports nothing on every block in a project without a build is worse than no feature
- [X] T022 [US4] Add `StewBeet.codeLens` (boolean, default `true`) to `extension/vscode/package.json` and register the provider from `extension/vscode/src/extension.js`. Lenses are the kind of ornament some people want off, and VS Code users expect that switch

**Checkpoint**: FR-021 holds.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T023 Re-check the degradation path after the substitution lands: with `build/` renamed away, `extension/vscode/src/virtual.js` must fall back to masking and every step A feature must keep working. The substitution introduces a second way for the projection to be wrong, and this is the check that it fails softly
- [X] T024 [P] Update `extension/vscode/README.md` and `extension/vscode/CHANGELOG.md` for 1.3.0, saying plainly that navigation now works on interpolated paths and what the four new settings do
- [X] T025 [P] Update [contracts/extension-api.md](./contracts/extension-api.md) with the four settings and the CodeLens provider, and correct the "Virtual document scheme" section, which currently states that offsets are preserved exactly and ranges never need translating
- [X] T026 [P] Record in [quickstart.md](./quickstart.md) what the interpolated case now does, replacing the row that says ctrl+click does nothing on `function {ns}:...`
- [X] T027 Bump `extension/vscode/package.json` to 1.3.0 and rebuild the package with `extension/build_publish.sh`, which copies the icon and the licence in and cleans them up afterwards. Do not call `vsce` directly
- [X] T028 Run the full gate: `npm test` and `npm run test:integration` in `extension/vscode/`, plus `ruff check stewbeet tests`, `pyright stewbeet tests`, `scripts/sync_api.py --check`, `scripts/all_doctests.py` and `scripts/run_integration_tests.py` in `python_package/` to prove the Python side is untouched

---

## Dependencies

```
Phase 1 (T001-T007)  <- the coordinate rule and the substitution engine
        |
        +-- Phase 2 (T008-T013)  US1 interpolated navigation, the MVP
        |
        +-- Phase 5 (T020-T022)  US4 CodeLens, needs the map layer only

Phase 3 (T014-T017)  US2 diagnostics, independent of the projection entirely
Phase 4 (T018-T019)  US3 rule filter, independent, one setting
```

**Story independence**: US2 and US3 touch only `diagnostics.js` and share nothing with the projection work, so both can be built and shipped without Phase 1. US4 needs the map layer from step C but not the substitution.

## Parallel opportunities

- Phases 3 and 4 can run alongside Phase 1 from the start. They are the two cheapest wins and neither risks the projection.
- Inside Phase 1, T002 and T003 are the same function and are sequential; T004 and T005 follow; T006 follows both.
- T024, T025 and T026 are three different files and parallel with each other.

## Implementation strategy

**MVP is Phase 1 plus Phase 2.** It is the difference between a feature that demos and a feature that applies to the user's own code.

**Take Phases 3 and 4 first if a quick win matters.** Together they are one afternoon, they need none of the risky work, and they fix two things the author hit within minutes of installing 1.2.0.

**Phase 1 is where this step can go wrong.** Everything else fails visibly; a bad column translation silently rewrites the wrong characters when a completion is accepted. T011 and T013 exist for that, and neither should be skipped to save time.

---

## Phase 7: Convergence

Appended by `/speckit-converge`. The codebase shipped 1.4.0 through 1.5.1 without a task list, so the
spec, the contracts and the docs describe a diagnostic relay that no longer exists and miss a setting,
two commands and a module. Nothing here changes behaviour the author relies on except T029.

**Out of this step, named rather than dropped**: FR-016 (`bolt` language id) and FR-017 (mecha AST map
emitter) are unbuilt and stay that way for now. They are steps D and E in [plan.md](./plan.md)'s phasing
table and get their own `/speckit-tasks` pass, not a phase inside a step C2 list.

FR-019 is settled in [spec.md](./spec.md) rather than by a task here. The relay reads the projection and
opens nothing under the build output, which needs no build at all, so the requirement moved to describe
what the code does.

- [ ] T029 Add a grammar rule keying on the annotation, `name: McFunction = <string>`, to `extension/vscode/syntaxes/mcfunction-injection.tmLanguage.json` per FR-023 (partial). **`McFunction` is the name**, already spelled that way by `type McFunction = str` in `python_package/stewbeet/core/utils/io/functions.py`, already reaching `from stewbeet import *`, and now spelled that way in FR-023 too. Only the grammar half is missing. Match the annotation with an optional `f` prefix and every quote style, the way the twelve `write_*` patterns beside it already do, and cover it in `extension/vscode/test/grammar.test.js`, whose 13 tests all exercise the `write_*` anchor and none the annotation
- [ ] T031 Rewrite the "Loading what a build wrote (step C2)" block of [contracts/extension-api.md](./contracts/extension-api.md) per plan: diagnostic relay contract (contradicts). It documents a `**/*.mcfunction` watcher, a 40-document cap, an 8 s hold and a 400 ms debounce, none of which exist. Describe the live projection relay in their place: the 120 ms debounce, the 3 s per-wake and 20 s per-pass timeouts, the 30 s idle wake, and the rule that the projection's diagnostic wins over the generated file's
- [ ] T032 Add `StewBeet.headerLinks` to the Settings table and `stewbeet.refreshDiagnostics` and `stewbeet.diagnosticsStatus` to the Commands table of [contracts/extension-api.md](./contracts/extension-api.md) per plan: extension surface contract (partial). The Commands section also opens with "All three are shipped in 1.2.0", which is no longer the count
- [ ] T033 Bring `extension/vscode/README.md` to 1.5.1 per FR-020 and FR-022 (partial): add `headerLinks` to the settings table, add the two missing commands to the command table, correct the Diagnostics row that still calls them "Build errors mirrored onto the Python line" when they now arrive as you type with no build, and say in the highlighting section that commands handed to a `write_*` call in a variable are seen
- [ ] T034 Correct the two Phase C rows in [quickstart.md](./quickstart.md) that say diagnostics appear "on a rebuild alone" per plan: validation guide (contradicts). Replace the rebuild trigger with typing, and keep a row for the generated files the author opens themselves, which is the one path that still relays from disk
- [ ] T035 Verify on SimplEnergy that an error typed into a block is squiggled with no build present at all, and that a full rebuild neither freezes the editor nor silences the relay, per tasks.md T017 (partial). T017's wording predates the mechanism change and names a rebuild-driven check the relay no longer performs; leave T017 as it stands and record the result against this task. `extension/vscode/test/integration/result.json` covers the typing half already, so the rebuild half is what is missing
- [ ] T036 Settle the SC-003 verification grep in [quickstart.md](./quickstart.md), which expects no matches and finds one per SC-003 (contradicts). `extension/vscode/src/projection.js:281` carries `execute store reslt score #height {ns}.data` as an example in a doc comment. Either reword the comment or exclude comment lines from the pattern, and say which was chosen so the next reader does not re-derive it
- [ ] T037 Record `extension/vscode/src/headers.js`, its test and the `StewBeet.headerLinks` setting in [contracts/extension-api.md](./contracts/extension-api.md) (unrequested). Resource locations in a generated file's `#>` header comments are clickable and a lens sits above the header, which no requirement, plan phase or task ever asked for. It is small, tested and useful, so document it under the navigation surface rather than remove it
