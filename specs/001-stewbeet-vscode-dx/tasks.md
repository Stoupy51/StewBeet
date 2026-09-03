# Tasks: StewBeet VS Code DX, step B2 (attribution scopes)

**Input**: Design documents from `/specs/001-stewbeet-vscode-dx/`

**Prerequisites**: Step B is merged. `stewbeet.plugins.sniffer` captures writes and `stewbeet.plugins.sniffer.emit` writes the sidecars.

**Scope**: **Step B2 only.** Content a StewBeet plugin generates on a declaration's behalf maps to the **declaration site**, not to the plugin that emitted it. Python-only; the VS Code extension is not touched. Steps C through G stay out.

**Tests**: Yes. Every prior step of this feature was carried by its integration fixture, and B2's whole risk is misattribution, which is invisible without one.

**Organization**: By user story, in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths in every description

## Path Conventions

Python package at `python_package/stewbeet/`, integration fixtures at `python_package/tests/<name>/` with a `beet.yml` and a `src/`.

---

## Why this step exists

`attribute_to` was written and unit-tested in step B, and **nothing calls it**. Until something does, every line a plugin generates from `Mem.definitions` resolves to tier 3 and is emitted unmapped. That is correct but useless: on a real pack, custom blocks are most of the generated output, so most of the pack has no map.

**The blocker found while planning this step**: `Item.origin` is `None` on every declaration today, so wiring `attribute_to` in first would silently do nothing. Proven against the current build:

```python
Mem.sniffer_enabled = True
item = Item(id="my_ingot", base_item="minecraft:stick")   # from a project file
item.origin   # None
```

The cause is in `resolve_origin()`. Tier 1 requires the frame to sit on a **write call**, confirmed against the AST index, and a `Block(...)` declaration is not a write call. That check exists for a good reason (it stops a plugin's write from attributing to the user's `main()`, which is project code that authored nothing), but it makes the declaration case unreachable. Phase 2 fixes that, and nothing in phase 3 works until it does.

---

## Phase 1: Setup

**Purpose**: Nothing to initialise. The package, the plugin entries and the fixture conventions all exist from step B.

*(No tasks. Start at Phase 2.)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Make a declaration able to carry its own origin. Every user story below is dead code until this phase is done.

- [ ] T001 Add `declaration_origin()` to `python_package/stewbeet/plugins/sniffer/origin.py`, resolving the site of a declaration rather than of a write. Unlike `resolve_origin` it does **not** consult the AST index, because a constructor's caller is the declaration by construction: it walks out of the library frames and takes the first project frame. It MUST return `None` when the frame that called the constructor is itself library code, which is the case where a StewBeet plugin builds an `Item` and the first project frame would be the user's `main()`, exactly the misattribution the AST check prevents on the write path
- [ ] T002 Resolve the **column**, not just the line, in `declaration_origin()` using `frame.f_code.co_positions()` indexed by `frame.f_lasti // 2`, which gives the exact span of the call expression on Python 3.11+. A line-only origin lands on column 0 and makes a peek list point at the indentation rather than at the `Block(` call. Fall back to column 0 when `co_positions()` yields no column, which it does for frames built without position tables
- [ ] T003 Add doctests to `python_package/stewbeet/plugins/sniffer/origin.py` for `declaration_origin()` covering the three outcomes: called from a project frame, returns that frame's position; called from a library frame, returns `None`; called with no project frame anywhere on the stack, returns `None`
- [ ] T004 Point `Item.__post_init__` in `python_package/stewbeet/core/cls/item.py` at `sniffer.declaration_origin()` instead of `sniffer.resolve_origin()`, and export it from `python_package/stewbeet/plugins/sniffer/__init__.py` next to the others. `Block`, `BlockAlternative` and `BlockHead` inherit this through `super().__post_init__()`, so the extra `block.py` frame sits between the constructor and the declaration and MUST be walked past as library code
- [ ] T005 Verify the capture actually fires end to end before building anything on it: with `Mem.sniffer_enabled` set, an `Item(...)` declared in a project file MUST come back with a non-`None` `origin` whose `file` is that project file and whose `line` is the declaration's. This is the exact assertion that fails on today's code

**Checkpoint**: A declaration knows where it was declared. `attribute_to` can now push something other than nothing.

---

## Phase 3: User Story 1 - A generated block function points at its declaration (Priority: P1) 🎯 MVP

**Goal**: Ctrl+clicking a custom block's generated function leads to the `Block(...)` call that caused it, not to `custom_blocks/__init__.py` and not to the user's `main()`.

**Independent Test**: Build `tests/plugin_24_sniffer_attribution`, decode the map of a generated block function, and land on the `Block(...)` line of the fixture's own declarations file. Maps to spec Scenario 3, FR-011, and guarantee G5.

- [ ] T006 [US1] Wrap the per-definition loop body in `python_package/stewbeet/plugins/datapack/custom_blocks/__init__.py` with `attribute_to(obj)`, at the `for item, data in Mem.definitions.items():` loop that starts at line 121. `obj` is already bound on the next line, so the scope is one `with` and one indent level
- [ ] T007 [US1] Leave the pack-level scaffolding in the same file **outside** any scope: `custom_blocks/get_rotation`, `check_light` and `compute_brightness` are written before the loop and belong to no declaration. They MUST stay unmapped rather than being attributed to whichever block happens to be first, which is what a scope opened too early would do
- [ ] T008 [US1] Create the fixture `python_package/tests/plugin_24_sniffer_attribution/` with a `beet.yml` listing `stewbeet.plugins.sniffer` in `require`, then `src.definitions`, `stewbeet.plugins.datapack.custom_blocks`, `src.link`, `stewbeet.plugins.sniffer.emit` in the pipeline, following the shape of `plugin_22_sniffer_source_maps/beet.yml`
- [ ] T009 [US1] Write `python_package/tests/plugin_24_sniffer_attribution/src/definitions.py` declaring one custom block with a vanilla block base, so `custom_blocks` generates the `place_main` / `place_secondary` / `destroy` family from it. Keep the declaration on a known line, the assertions check that exact line
- [ ] T010 [US1] Write `python_package/tests/plugin_24_sniffer_attribution/src/assertions.py` as a generator plugin listed first, asserting that a `custom_blocks`-generated function's map names `src/definitions.py` and that the mapped line is the `Block(...)` declaration. Reuse the independent VLQ decoder from `plugin_22_sniffer_source_maps/src/assertions.py` rather than importing the encoder under test
- [ ] T011 [US1] Assert the two negatives in the same file, which are what catch a broken tier order: no `sources` entry anywhere in the pack names `custom_blocks/__init__.py` or any other library file, and no mapping points at the fixture's own pipeline entry point. A tier order that silently falls through to the first project frame passes every positive assertion and fails these

**Checkpoint**: FR-011 holds for custom blocks. The most-generated part of a real pack is mapped.

---

## Phase 4: User Story 2 - Both origins survive on one function (Priority: P1)

**Goal**: When an author appends to a function a plugin generated for them, the map carries **both** the declaration and their own append, each keeping its own lines.

**Independent Test**: In the same fixture, append to a generated block function from a plugin ordered after `custom_blocks`, then decode: two sources, both in the project, on different lines. Maps to spec Scenario 3, FR-012, and guarantee G6.

- [ ] T012 [US2] Extend `python_package/tests/plugin_24_sniffer_attribution/src/link.py` to append to the declared block's `place_secondary` the supported way, `Block.from_id(...).functions.place_secondary.obj.append(...)`, which reaches beet directly without passing through `write_function`. This is the path the `Function.append` patch exists for, and the only one that exercises it from user code
- [ ] T013 [US2] Assert in `python_package/tests/plugin_24_sniffer_attribution/src/assertions.py` that `place_secondary`'s map has **two** `sources`, that the appended line resolves to the `.obj.append(` call in `src/link.py` through tier 1, and that the plugin-generated lines above it still resolve to the `Block(...)` declaration through tier 2
- [ ] T014 [US2] Assert the ordering guarantee in the same file: the appended line's generated index is **after** the generated lines, matching the order the writes happened in. A mapping that is correct per line but scrambled across chunks passes a per-line check and fails this

**Checkpoint**: FR-012 holds. Scenario 3 of the spec is fully covered.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T015 [P] Extend the attribution scope to the remaining per-definition loops, one `with attribute_to(...)` each, in `python_package/stewbeet/plugins/datapack/loot_tables/__init__.py`, `python_package/stewbeet/plugins/custom_recipes/__init__.py`, `python_package/stewbeet/plugins/compatibilities/simpledrawer/__init__.py` and `python_package/stewbeet/plugins/compatibilities/neo_enchant/__init__.py`. Each is independent of the others and of the phases above, and each MUST leave its pack-level scaffolding outside the scope the way T007 does
- [ ] T016 Re-measure the build overhead against the step B baseline of **+4.9%** on SimplEnergy, median of five runs, discarding the first. `declaration_origin` runs on every `Item` and `Block` construction, which is a hot path on a large pack in a way the write path is not. NFR-002 budgets 20%
- [ ] T017 [P] Update `specs/001-stewbeet-vscode-dx/data-model.md` so `SourceOrigin` records that a declaration origin is resolved without the AST index and why, and drop the line in `python_package/stewbeet/plugins/sniffer/attribution.py`'s docstring saying nothing enters the scope yet
- [ ] T018 [P] Update `docs/web/public/docs/plugins/sniffer.md` to say that content generated from a declaration maps to the declaration, and which plugins are scoped so far. A reader whose custom recipes are unmapped needs to see that it is a known boundary, not a bug
- [ ] T019 Run the full gate: `ruff check stewbeet --config ./pyproject.toml`, `python scripts/all_doctests.py`, `python scripts/run_integration_tests.py`. All three MUST pass, with the fixture count up by one

---

## Dependencies

```
Phase 2 (T001-T005)  <- blocks everything, Item.origin is None without it
        |
        +-- Phase 3 (T006-T011)  US1, the MVP
        |         |
        |         +-- Phase 4 (T012-T014)  US2, extends the same fixture
        |
        +-- T015  independent of US1 and US2, only needs Phase 2
```

**Story independence**: US2 shares US1's fixture, so it is sequential after it in practice. It is still separately testable: its assertions fail on their own if the `Function.append` capture regresses, whatever US1 does.

## Parallel opportunities

- Inside Phase 2, T001 and T002 touch the same function and are sequential. T003 follows both.
- Inside Phase 3, T008 and T009 are one fixture and are cheapest written together. T010 and T011 both edit `assertions.py`, so sequential.
- T015 splits four ways across four plugin files, all parallel, and does not wait on Phase 3 or 4.
- T017 and T018 are documentation in different files, parallel with each other and with anything.

## Implementation strategy

**MVP is Phase 2 plus Phase 3.** That alone turns the largest generated surface of a real pack from unmapped into mapped, and it is what makes step C's ctrl+click feel finished rather than half-broken.

Stop after Phase 4 if time is short. T015 is a mechanical repetition of T006 across four more plugins and buys breadth, not correctness; every plugin left unscoped keeps emitting unmapped lines, which is the designed degradation and not a failure.
