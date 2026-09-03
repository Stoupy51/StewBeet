# Tasks: Step B, source map emission (`stewbeet.plugins.sniffer`)

**Input**: Design documents from `/specs/001-stewbeet-vscode-dx/`

**Scope**: **Step B only.** A build emits Source Map v3 `.mcfunction.map` sidecars linking each generated line back to the Python line that wrote it, and only ever to the project's own source. Python-only; the VS Code extension is not touched.

**Prerequisites**: [contracts/source-map.md](./contracts/source-map.md) (the output contract, validated against a working reference at [contracts/reference/](./contracts/reference/)), [research.md](./research.md) (origin resolution, capture points, alignment), [data-model.md](./data-model.md) (entities), [plan.md](./plan.md).

**Explicitly out of scope**, named rather than dropped, per the constitution's scope-discipline rule:

- **B2**: wiring `attribute_to(...)` into StewBeet's own generation loops (FR-011, FR-012). The scope machinery is built here so B2 is roughly five lines per plugin; no plugin is instrumented in this pass. Until B2, plugin-generated content resolves to tier 3 and is emitted **unmapped**, which is correct and safe.
- **C**: the extension consuming the maps. **E**: the mecha emitter. **D, F, G**: bolt work. See [contracts/dialects.md](./contracts/dialects.md).

**Tests**: included, following the repository's existing conventions rather than new ones.

- Integration: numbered folders under `python_package/tests/`, each a `beet.yml` pipeline ending in `src.assertions`, discovered by `python_package/scripts/run_integration_tests.py`. Next free number is 22.
- Doctests in the modules themselves, run by `python_package/scripts/all_doctests.py`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3
- Paths are repository-relative

## Path Conventions

All work is under `python_package/`. Code is `pyright` strict and `ruff check` clean, tabs for indentation, two trailing newlines per file, structural `# Imports` / `# Constants` / `# Classes` / `# Functions` banners.

---

## Phase 1: Setup

**Purpose**: Package skeleton and the pipeline hook, before any behaviour exists

- [X] T001 Create the package `python_package/stewbeet/plugins/sniffer/__init__.py` with a `beet_default(ctx: Context)` entry point that sets `Mem.ctx = ctx` and returns immediately, following the shape of `python_package/stewbeet/plugins/compute_sha1/__init__.py`, including the `@stp.measure_time` decorator and the lazy-import preamble every plugin carries
- [X] T002 [P] Create the integration test folder `python_package/tests/plugin_22_sniffer_source_maps/` with a `beet.yml` whose pipeline is `src.definitions`, `src.link`, `stewbeet.plugins.sniffer`, `src.assertions`, modelled on `tests/plugin_10_auto_headers/beet.yml`. Deliberately **omit** `stewbeet.plugins.auto.headers` so this fixture exercises emission without post-processing
- [X] T003 [P] Add `source_map_chunks: dict[str, list[WriteChunk]]` and `attribution: list[AttributionScope]` to `python_package/stewbeet/core/__memory__.py`, documented under each field like the existing `Mem` state, and reset both in `stewbeet/plugins/initialize` alongside the other per-build state so `beet watch` does not accumulate across rebuilds

**Checkpoint**: The plugin loads and does nothing.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The entities and the origin resolver. Every user story below sits on these.

**CRITICAL**: No user story work can begin until T009 is done.

### Entities

- [X] T004 [P] Create `python_package/stewbeet/plugins/sniffer/model.py` with frozen dataclasses `SourceOrigin` (file, line, column, exact), `WriteChunk` (lines, origin), `AttributionScope` (origin), `LineMapping` (generated_line, source_index, source_line, source_column) and `FunctionSourceMap` (generated_path, source_root, sources, mappings), exactly as specified in [data-model.md](./data-model.md). No `dict[str, dict[...]]` blobs anywhere

### Origin resolution

- [X] T005 [P] Implement the project-source filter in `python_package/stewbeet/plugins/sniffer/origin.py`: a path qualifies only when it is under a configured root (defaulting to `ctx.directory`, beet's project directory) **and** not under the package directory of `stewbeet`, `beet`, `bolt`, `mecha` or `stouputils`, and contains no `site-packages` component. The second condition is not implied by the first: StewBeet is frequently installed editable from inside the repository being built, so a library path can sit under the project root
- [X] T006 Implement the cached AST index in `python_package/stewbeet/plugins/sniffer/origin.py`: parse a caller file once with `ast`, cache by path and mtime, and expose a lookup from a line number to the enclosing write call and the position of its content argument. Recognise the six `write_*` functions plus `.append(...)` and `.prepend(...)` on a `Resource.obj`. A `Constant` str or `JoinedStr` argument yields the literal's own `lineno`; anything else yields the call line with `exact=False`
- [X] T007 Implement tier 1 of `resolve_origin()` in `python_package/stewbeet/plugins/sniffer/origin.py`: walk outward with `sys._getframe` and return the innermost frame that passes the project-source filter **and** whose line the AST index confirms is a write call. The AST condition is what makes the tier order work: without it a plugin-generated write resolves to the user's `main()` entry point, which passes the filter and authored nothing, so tier 1 would always win and tier 2 would never fire
- [X] T008 [P] Implement the attribution scope in `python_package/stewbeet/plugins/sniffer/attribution.py`: an `attribute_to(definition)` context manager pushing an `AttributionScope` onto `Mem.attribution`, reentrant, innermost wins. Add tier 2 to `resolve_origin()` reading the top of that stack, and tier 3 returning `None`. No StewBeet plugin is instrumented in this pass, that is step B2
- [X] T009 [P] Capture the declaration site on `Item`: add `origin: SourceOrigin | None` to `python_package/stewbeet/core/cls/item.py` as a non-init field excluded from `repr`, `compare` and `to_dict`, populated in `__post_init__` by the same tier-1 walk. `Item` is `@dataclass(kw_only=True, slots=True)`, so this must be a declared field rather than an attribute set afterwards

### Capture

- [X] T010 Implement capture in `python_package/stewbeet/plugins/sniffer/capture.py` by patching `beet.Function.append` and `.prepend` at plugin activation and restoring them at teardown. The plugin belongs in `require`, so activation happens before beet loads the pack and no write can precede it; the pack's own hand-written functions then record chunks with no origin, which produce no map. This is the single choke point every incremental write flows through, `write_function`'s own append and prepend included. Guard the patch by checking the methods look as expected and degrade to emitting nothing plus one warning if beet's internals have moved
- [X] T011 Add capture to the overwrite branch of `write_function` in `python_package/stewbeet/core/utils/io/functions.py`, which constructs a fresh `Function` and assigns it into the container rather than appending, so the `Function.append` hook never sees it. Clear the path's chunk list first, mirroring the overwrite semantics exactly
- [X] T012 Make chunk recording mirror `write_function` exactly in `python_package/stewbeet/plugins/sniffer/capture.py`: append adds a chunk, prepend inserts at index 0, overwrite clears then appends, and a `condition` returning `False` records nothing. Several chunks with different origins in one list is the normal case, not an edge case

**Checkpoint**: Chunks and origins are recorded during a build. Nothing is written to disk yet.

---

## Phase 3: User Story 1 - A third-party debugger can consume the maps (Priority: P1) 🎯 MVP

**Goal**: `beet build` with the plugin in the pipeline emits one `.mcfunction.map` beside each generated function, in a format Sniffer can read without knowing anything about StewBeet.

**Independent Test**: Build `tests/plugin_22_sniffer_source_maps`, decode a map, and land on the `write_function` string that produced the command. Maps to spec Scenario 4 and FR-004, FR-005, FR-006.

- [X] T013 [US1] Implement base64 VLQ encoding in `python_package/stewbeet/plugins/sniffer/encode.py`, with the standard alphabet and continuation bit, sign in the least significant bit. Roughly fifteen lines; see the reference linked from [contracts/source-map.md](./contracts/source-map.md)
- [X] T014 [US1] Implement the `mappings` string builder in `python_package/stewbeet/plugins/sniffer/encode.py`: one segment per mapped generated line as `[generatedColumn, sourceIndex, sourceLine, sourceColumn]`, all four **delta-encoded against the previous segment in the file rather than within the line**, generated column always 0, all values 0-based. A generated line with no origin emits an **empty group** (two consecutive `;`); trailing unmapped lines emit **no group at all** and the string simply ends. Those two are distinct and both legal
- [X] T015 [US1] Add doctests to `python_package/stewbeet/plugins/sniffer/encode.py` proving conformance with someone else's encoder: encoding the line table of `contracts/reference/.../hit.mcfunction.map` MUST produce exactly `AAKA;AACA;AACA;AAAA;AACA`, and `aura.mcfunction.map`'s MUST produce exactly `AAQA;ACHA;AACA`. The second is the one that matters: its `ACHA` segment moves to a different source **and** three lines backwards in one step, which a hand-rolled encoder treating deltas as per-source gets wrong while passing every fixture we write ourselves
- [X] T016 [US1] Implement line alignment in `python_package/stewbeet/plugins/sniffer/align.py` using `difflib.SequenceMatcher` over the recorded chunk lines against the function's final text. `equal` and `replace` opcodes keep their mapping, `insert` opcodes stay unmapped, `delete` opcodes are dropped. Roughly forty lines, stdlib only, and transformation-agnostic by construction
- [X] T017 [US1] Compute `sourceRoot` per map in `python_package/stewbeet/plugins/sniffer/encode.py` as the relative path from **the map file's own directory** to the project root, with `sources` relative to that. Depth therefore varies per function: `../../../../..` for a function at `data/ns/function/`, one more level for one under `nested/`. Nothing absolute is ever written. Omit the `sourcesContent` key entirely, it is not part of the format
- [X] T018 [US1] Write the sidecars in `python_package/stewbeet/plugins/sniffer/emit.py`, as a pipeline step of its own listed after every writer and **before** `stewbeet.plugins.archive`: one `<name>.mcfunction.map` beside each generated function, and append `## sourceMappingURL=<basename>.mcfunction.map` as the function's **last** line, with **two** hash characters. It must be last and must be unmapped, because Sniffer counts comments and blank lines when placing breakpoints so a leading comment would shift every mapped line
- [X] T019 [US1] Ensure emission is opt-in and costs nothing when off: capture is a no-op unless the plugin is in the pipeline, and no `.map` files exist after a build without it. The maps MUST reach the archive zip, because that zip is what `copy_to_destination` puts in `saves/<world>/datapacks` and therefore what a debugger loads. `stewbeet.plugins.archive` runs in the pipeline's forward pass, so a generator's teardown is too late; emission is its own pipeline entry placed before it, capture goes in `require` where no write can precede it, and the capture plugin's teardown writes anything left over with a warning rather than silently skipping it
- [X] T020 [US1] Write `python_package/tests/plugin_22_sniffer_source_maps/src/assertions.py` asserting: one map per generated function; `version` is 3; `names` is empty; no `sourcesContent` key; every function's last line is the two-hash `## sourceMappingURL`; and decoding a known function's mappings lands on the expected line of the expected `src/*.py` file

**Checkpoint**: SC-002 is reachable. A debugger can consume the output with an off-the-shelf source map library.

---

## Phase 4: User Story 2 - A jump never lands in library code (Priority: P1)

**Goal**: Every `sources` entry is a file in the project's own tree. A generated line with no valid project origin is emitted unmapped rather than pointed at `site-packages`.

**Independent Test**: Grep every emitted map's `sources` for `site-packages` and `/stewbeet/` and find nothing, including when StewBeet is installed editable from inside the project root. Maps to FR-010 and guarantee G5.

**Depends on** US1's resolver: this hardens what US1 built rather than running fully parallel to it.

- [X] T021 [US2] Enforce the filter at construction in `python_package/stewbeet/plugins/sniffer/model.py`: `SourceOrigin` validates its path and a failing candidate produces `None` rather than a degraded origin. An invalid origin must be unrepresentable, because a jump into library internals is worse than no jump
- [X] T022 [US2] Verify the editable-install case explicitly, since it is the one a naive project-root check passes and must not: with `stewbeet` installed editable from inside the repository being built, no emitted map may name a file under the `stewbeet` package directory
- [X] T023 [P] [US2] Add to `python_package/tests/plugin_22_sniffer_source_maps/src/assertions.py` a scan of every emitted map asserting no `sources` entry contains `site-packages`, or resolves inside the `stewbeet`, `beet`, `bolt`, `mecha` or `stouputils` package directories
- [X] T024 [P] [US2] Add an assertion that content written by a StewBeet plugin with no attribution scope is emitted **unmapped**, and in particular never attributed to the plugin's own source file nor to the project's entry point
- [X] T025 [US2] Add doctests to `python_package/stewbeet/plugins/sniffer/origin.py` covering the filter: a project file passes, a `site-packages` path fails, and a path inside the `stewbeet` package fails even when it is under the project root

**Checkpoint**: G5 holds. Navigation built on these maps cannot mislead.

---

## Phase 5: User Story 3 - Maps stay correct after StewBeet rewrites every function (Priority: P2)

**Goal**: `auto.headers` rewrites every function with `overwrite=True` to prepend a header block, and `auto.text_renders` and `auto.lang_file` substitute inside lines. Mappings survive all of it.

**Independent Test**: Build a pipeline that includes `auto.headers`, then confirm the generated header lines are unmapped and every command line still maps to its authoring line. Maps to FR-009.

**Depends on** US1's aligner.

- [X] T026 [US3] Create `python_package/tests/plugin_23_sniffer_with_headers/` with a `beet.yml` whose pipeline includes `stewbeet.plugins.auto.headers` **before** `stewbeet.plugins.sniffer`, so the plugin sees the rewritten text, mirroring a real project's ordering
- [X] T027 [US3] Write `python_package/tests/plugin_23_sniffer_with_headers/src/assertions.py` asserting that the generated `#>` header lines are unmapped (empty groups), that the first real command still maps to its authoring line in `src/*.py`, and that mapped generated lines remain strictly increasing (G2)
- [X] T028 [P] [US3] Add an assertion covering `auto.text_renders`-style in-line substitution: a line whose text was rewritten keeps its mapping, because `difflib` reports it as `replace` rather than `insert` plus `delete`
- [X] T029 [US3] Add doctests to `python_package/stewbeet/plugins/sniffer/align.py` covering each opcode: `equal` keeps, `replace` keeps, `insert` yields unmapped lines, `delete` drops. These are the semantics the whole post-processing story rests on

**Checkpoint**: FR-009 holds against StewBeet's own pipeline, not just a toy one.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T030 [P] Verify NFR-002: median of five builds with the plugin absent must stay within 2% of a baseline, and with it enabled must stay under 20% overhead. Measure on a real project such as [SimplEnergy](file:///d:/advanced_desktop/SimplEnergy), not on a test fixture
- [X] T031 [P] Verify NFR-001 and SC-003 by running the anchored grep from [quickstart.md](./quickstart.md) over `python_package/stewbeet/plugins/sniffer`, confirming no mcfunction syntax knowledge was added
- [X] T032 [P] Run `ruff check src --config ./pyproject.toml` and `pyright` in strict mode over the new package. No `Any`, no `# type: ignore`, no `cast` used to silence rather than to assert an invariant
- [X] T033 [P] Confirm `python_package/scripts/all_doctests.py` picks up every new module's doctests, and that `python_package/scripts/run_integration_tests.py` discovers both new test folders
- [X] T034 Document the plugin in the StewBeet docs: what it emits, that it is opt-in, that maps are excluded from release archives, and that debugging should happen from `build/` because `sourceRoot` is relative and stops resolving once `copy_to_destination` copies the pack elsewhere
- [X] T035 Run the Phase B section of [quickstart.md](./quickstart.md) end to end, including the library-leak scan
- [X] T036 Send [contracts/source-map.md](./contracts/source-map.md) and a sample emitted map to Sniffer's author to confirm their reader accepts real StewBeet output, closing the loop on SC-002

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup. **Blocks all three user stories**
- **US1 (Phase 3)**: depends on Phase 2. The MVP
- **US2 (Phase 4)**: depends on US1's resolver
- **US3 (Phase 5)**: depends on US1's aligner
- **Polish (Phase 6)**: depends on the stories you intend to ship

### Within Phase 2

```
T004 ──> T005 ──> T006 ──> T007 ──> T010 ──> T011 ──> T012
              └─> T008
              └─> T009
```

T005 is the filter every tier depends on. T008 and T009 are independent of each other once T007 lands.

### Within US1

```
T013 ──> T014 ──> T015          (encoder, proven against the reference)
T016 ─────────────┐
T017 ─────────────┴──> T018 ──> T019 ──> T020
```

### Parallel Opportunities

- T002 and T003 in Setup
- T004, T005, T008, T009 early in Phase 2
- T013 to T015 (encoder) run parallel to T016 (aligner): different files, no shared state
- T023, T024 within US2
- Most of Phase 6

---

## Parallel Example: US1 encoder and aligner

```bash
# Different files, no shared state, both feed T018:
Task: "VLQ + mappings builder + reference conformance doctests in plugins/sniffer/encode.py"
Task: "difflib alignment of recorded chunks against final text in plugins/sniffer/align.py"
```

---

## Implementation Strategy

### MVP: Phases 1 to 3

Setup, Foundational, then User Story 1. That is 20 tasks and produces maps a third-party debugger can read, which is the whole point of step B and the thing Sniffer is waiting on. **Stop and validate here** with T036 before continuing.

### Incremental delivery

US2 is small and critical; do it before anyone builds navigation on the output, because a map that points into `site-packages` is worse than no map. US3 is what makes the plugin usable on a real StewBeet project, since `auto.headers` runs in essentially all of them.

### The two places this is most likely to go wrong

**T015**, the reference conformance doctests. VLQ deltas are file-wide rather than per-source. An encoder that gets this wrong passes every fixture we write ourselves and fails only against someone else's output, which is exactly why the reference is committed.

**T007**, the AST condition on tier 1. Without it every ctrl+click in the project eventually lands on the user's `main()`, because that frame passes the project-source filter while having authored nothing.
