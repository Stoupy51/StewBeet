# Tasks: Step A, Spyglass forwarding for StewBeet strings

**Input**: Design documents from `/specs/001-stewbeet-vscode-dx/`

**Scope**: **Step A only.** Completion, hover, signature help and a definition that lands in the generated `.mcfunction`, all inside StewBeet `write_*` string blocks. No build required, no source maps, no bolt. Steps B through G are out of scope for this file.

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [contracts/spyglass-integration.md](./contracts/spyglass-integration.md) (the implementation reference for every task here), [contracts/extension-api.md](./contracts/extension-api.md).

**Gate**: already cleared. The Q2 spike passed, see [spike/](./spike/). Do not re-derive the mechanism, it is proven and documented.

**Tests**: included. plan.md specifies `node --test` following the existing `test/blocks.test.js` pattern, and quickstart.md requires an offset-preservation assertion. Unit tests cover the pure modules only (`npm test`, scoped to `test/*.test.js`); the VS Code-dependent parts are covered by the integration harness in Phase 6 (`npm run test:integration`).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3
- Paths are repository-relative

## Path Conventions

All step A work is in `extension/vscode/`. No Python changes, no new npm dependencies: Spyglass is reached through `vscode.commands.executeCommand`, and the extension stays CommonJS `src/*.js` as it is today.

---

## Phase 1: Setup

**Purpose**: Configuration surface, before any behaviour exists

- [X] T001 Add `StewBeet.languageFeatures` boolean setting (default `true`) to the `contributes.configuration.properties` block in `extension/vscode/package.json`, described as the master switch for Spyglass-backed language features
- [X] T002 Confirm `activationEvents` in `extension/vscode/package.json` still contains only `onLanguage:python`, and that Spyglass is **not** added to `extensionDependencies` (NFR-003 requires it stay a soft dependency)

**Checkpoint**: Settings exist, nothing reads them yet

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The virtual document machinery. Every user story below is a thin provider on top of it.

**CRITICAL**: No user story work can begin until T009 is done.

### Block scanning

- [X] T003 Extend `findClosingQuote` and `skipInterpolation` in `extension/vscode/src/blocks.js` to record the `{...}` spans they skip, and export a new `findInterpolationSpans(text, block)` returning `{start, end}[]` for one block. Do not change `findBlockOffsets`'s existing return shape, `test/blocks.test.js` must keep passing
- [X] T004 [P] Add unit tests for `findInterpolationSpans` in `extension/vscode/test/blocks.test.js`, covering a plain string, a single `{name}`, nested braces, a literal `{{`, and an interpolation containing its own quoted string

### Virtual documents

- [X] T005 [P] Create the pure `project(text, start, end, interpolationSpans)` function: every character outside `[start, end)` becomes a space, newlines are preserved, and each interpolation span becomes a same-length run of `_`. See spyglass-integration.md Part 3. **Shipped in `extension/vscode/src/projection.js`, not `virtual.js`**: `virtual.js` must import `vscode` and would be untestable under `node --test`, and the constitution requires JavaScript modules that can be pure to have no `vscode` import
- [X] T006 [P] Add the pure virtual URI helpers to `extension/vscode/src/projection.js`. **Shipped as `virtualPath(blockIndex, baseName)` and `blockIndexFromPath(path)`**, with the originating document carried in the URI's `query` rather than an encoded path segment: VS Code decodes percent escapes in a path and would corrupt an encoded `file:///d:/...` embedded there. The `.mcfunction` suffix is load-bearing, it is what assigns the language id
- [X] T007 Add unit tests in `extension/vscode/test/projection.test.js` asserting that `project()` output has **exactly** the same length as its input and the same newline positions, that content inside the block is byte-identical, and that URI encode/decode round-trips. Offset identity is the property the whole design rests on
- [X] T008 Add `blockAt(document, position)` to `extension/vscode/src/virtual.js`, returning the block index containing the position or `undefined`, built on `findBlockOffsets` from `blocks.js`
- [X] T009 Add the `TextDocumentContentProvider` for the `stewbeet-mcfunction` scheme to `extension/vscode/src/virtual.js`, with a cache keyed by `(python uri, block index)`, an `onDidChange` emitter fired for affected virtual URIs on `workspace.onDidChangeTextDocument`, and cache eviction when the Python document closes

### Forwarding helper

- [X] T010 Add `forward(command, document, position, ...extraArgs)` to `extension/vscode/src/virtual.js`: return `undefined` when `StewBeet.languageFeatures` is false or `blockAt` misses, otherwise `await vscode.workspace.openTextDocument(virtualUri)` then `vscode.commands.executeCommand(command, virtualUri, position, ...extraArgs)`. Every failure resolves to `undefined`, nothing throws, nothing logs above debug (NFR-003)
- [X] T011 Wire `virtual.js` into `activate()` in `extension/vscode/src/extension.js`: register the content provider, push it onto `context.subscriptions`, and leave the existing decoration logic untouched

**Checkpoint**: A virtual document can be produced and requests can be forwarded. No provider is registered yet, so the editor behaves exactly as before.

---

## Phase 3: User Story 1 - Completing a command (Priority: P1) 🎯 MVP

**Goal**: An author typing `execute as @a run ` inside a `write_function` string gets the same completion list Spyglass offers in a `.mcfunction` file, including the project's own function paths.

**Independent Test**: Open a StewBeet `.py` file, put the caret mid-command inside a `write_*` string, trigger suggest, and see vanilla commands. Put the caret on `write_function` itself and see normal Python completions with no mcfunction items. Maps to spec Scenario 1 and FR-001.

- [X] T012 [US1] Implement `CompletionItemProvider` in `extension/vscode/src/virtual.js` forwarding to `vscode.executeCompletionItemProvider`, passing `context.triggerCharacter` and an `itemResolveCount` of 50. Without the resolve count items arrive with no `documentation` or `detail`, because VS Code will not call `resolveCompletionItem` for items this extension did not create
- [X] T013 [US1] Register the provider on `{ language: 'python' }` in `extension/vscode/src/extension.js` with Spyglass's own eleven mcfunction trigger characters, exactly: `' '`, `'['`, `'='`, `'!'`, `','`, `'{'`, `':'`, `'/'`, `'.'`, `'"'`, `"'"`. Any other set makes completion fire in different places than it does in a real `.mcfunction` file
- [X] T014 [US1] Verify results need no range translation. Evidence is T007's offset-identity property tests (same length, same newline positions, block content byte-identical), which make any returned range valid in the Python document by construction, plus the integration harness applying real Spyglass completions at a Python position

**Checkpoint**: Issue #41's headline ask is closed. Completion works with no build and no source maps.

---

## Phase 4: User Story 2 - Hover and signature help (Priority: P1)

**Goal**: The same block gives Spyglass's hover and signature help, so an author can read what a selector or argument means without leaving the string.

**Independent Test**: Hover `@a` inside a block and see Spyglass's selector hover. Type a command and see the signature. Both absent outside a block. Maps to FR-002.

- [X] T015 [P] [US2] Implement `HoverProvider` in `extension/vscode/src/virtual.js` forwarding to `vscode.executeHoverProvider`, returning the first result unchanged
- [X] T016 [P] [US2] Implement `SignatureHelpProvider` in `extension/vscode/src/virtual.js` forwarding to `vscode.executeSignatureHelpProvider`
- [X] T017 [US2] Register both on `{ language: 'python' }` in `extension/vscode/src/extension.js`, with a single space as the signature help trigger character to match Spyglass's server capability

**Checkpoint**: The block is readable as well as writable.

---

## Phase 5: User Story 3 - Following a reference to the generated file (Priority: P1)

**Goal**: Ctrl+click on a resource location inside a block navigates to the generated `.mcfunction` it refers to.

**Independent Test**: With a built datapack in the workspace, ctrl+click `mynamespace:greet` inside a command string and land in `build/.../greet.mcfunction`. Maps to spec Scenario 2, **partially**: step C later rewrites the target to the originating Python call site through the source map. Landing in the generated file is the honest step A answer and is useful on its own.

- [X] T018 [US3] Implement `DefinitionProvider` in `extension/vscode/src/virtual.js` forwarding to `vscode.executeDefinitionProvider`, returning locations unchanged
- [X] T019 [US3] Register it on `{ language: 'python' }` in `extension/vscode/src/extension.js`
- [X] T020 [US3] Add a note to `extension/vscode/README.md` stating that definition currently lands in the generated function and that navigating to the `write_function` call arrives with source maps, so the partial behaviour is not mistaken for a bug

**Checkpoint**: All three step A stories work independently.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T021 [P] Port the Q2 spike from `specs/001-stewbeet-vscode-dx/spike/` into `extension/vscode/test/integration/` as a runnable regression test. It is the only thing that detects a future Spyglass release adding a `scheme` filter to its document selector, which would silently break every provider above. Record the two launch traps from `spike/README.md`: clear `ELECTRON_RUN_AS_NODE` and the `VSCODE_*` variables, and launch `Code.exe` directly rather than the detaching `code` wrapper. **The throwaway VS Code profile MUST be written to the OS temp dir, never inside the repository**: a profile in the working tree puts git askpass sockets under a directory Spyglass's file watcher cannot `scandir`, and the resulting EPERM restarts the language server until it stops retrying. `.gitignore` does not constrain file watchers
- [X] T022 [P] Verify NFR-003 by disabling the Spyglass extension and confirming every provider resolves to `undefined`, the editor behaves exactly as it did before this feature, and nothing is logged above debug level
- [X] T023 [P] Verify the `StewBeet.languageFeatures` setting actually gates all four providers, toggling it off and confirming the editor returns to grammar-and-decorations only
- [X] T024 [P] Update `extension/vscode/README.md` with the new capabilities, and state that Spyglass (`SPGoding.datapack-language-server`) is an optional but strongly recommended companion
- [X] T025 Run the Phase A section of [quickstart.md](./quickstart.md) end to end against a real project, for example [SimplEnergy](file:///d:/advanced_desktop/SimplEnergy)
- [X] T026 Bump `version` in `extension/vscode/package.json` and add a changelog entry
- [X] T027 [P] Verify FR-008, that the editor-only features survive a missing build. The integration harness asserts vanilla completions (83, sourced from Spyglass's game data) separately from project resource locations (`probe:alpha`, `probe:beta`, sourced from the build output), so the first is demonstrably independent of the second. Recorded as a row in [quickstart.md](./quickstart.md) Phase A
- [X] T028 [P] Verify NFR-001 and SC-003, that no mcfunction syntax knowledge was added, by running the grep in [quickstart.md](./quickstart.md). Anchor the pattern on mcfunction token shapes (`@a[`, `scoreboard players`, `execute as|at|if|store`) rather than bare words: a plain `execute` pattern false-positives on `vscode.execute*`, a VS Code API name

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies, start immediately
- **Foundational (Phase 2)**: depends on Setup. **Blocks all three user stories**
- **US1, US2, US3 (Phases 3 to 5)**: all depend only on Phase 2, and are independent of each other
- **Polish (Phase 6)**: depends on the stories you intend to ship

### Within Phase 2

```
T003 ──> T004
     └─> T008 ──> T009 ──> T010 ──> T011
T005 ──> T007
T006 ──> T007
```

T005 and T006 are pure and independent of T003. T008 needs `blocks.js`, T009 needs the projection and the URI codec, T010 needs the provider.

### User Story Dependencies

None between them. Each is a provider registration on top of `forward()`. US1 is the MVP; US2 and US3 are each two to three tasks once Phase 2 exists.

### Parallel Opportunities

- T004, T005, T006 can run together after T003
- T015 and T016 can run together
- All of Phase 6 except T025 and T026 can run together
- US1, US2 and US3 can be worked in parallel by different people once T011 lands

---

## Parallel Example: Phase 2

```bash
# After T003 lands, these three touch different concerns:
Task: "Unit tests for findInterpolationSpans in extension/vscode/test/blocks.test.js"
Task: "Pure project() function in extension/vscode/src/virtual.js"
Task: "Pure encodeVirtualUri/decodeVirtualUri in extension/vscode/src/virtual.js"
```

---

## Implementation Strategy

### MVP: Phases 1 to 3

Setup, Foundational, then User Story 1. That is roughly 13 tasks and closes the headline half of issue #41, with no build, no source map and no bolt work. **Stop and validate here** against a real project before continuing.

### Incremental delivery

US2 and US3 are cheap additions once Phase 2 exists, two to three tasks each, and both are shippable independently. Phase 6's T021 is the one polish task worth doing before release rather than after, because it is the regression guard for the entire mechanism.

### What this file deliberately excludes

Steps B through G from [contracts/dialects.md](./contracts/dialects.md): source map emission, attribution scopes, map-driven navigation and diagnostics, the `bolt` language id, the mecha AST emitter, bolt live editing, and the upstream Spyglass plugin API. Each needs its own tasks pass. In particular T020 exists precisely because step A's definition behaviour is partial and should be documented as such rather than quietly shipped as if complete.
