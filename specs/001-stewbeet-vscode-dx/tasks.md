# Tasks: StewBeet VS Code DX, steps D and E (bolt language id, mecha AST map emitter)

**Input**: Design documents from `/specs/001-stewbeet-vscode-dx/`

**Prerequisites**: Steps A, B, B2, C and C2 are shipped. Extension 1.6.x forwards to Spyglass, resolves interpolated paths, relays diagnostics off the projection and navigates in both directions. A StewBeet build emits `.mcfunction.map` sidecars. Step C2's list is archived at [tasks-C2-projection-content.md](./tasks-C2-projection-content.md) with one open item, T035, a manual check that does not block anything here.

**Scope**: **Steps D and E only**, the two requirements [spec.md](./spec.md) named as deferred: FR-016 (`bolt` language id and grammar) and FR-017 (map emission from the mecha AST). Step D is JavaScript and JSON, step E is Python. Step F, live bolt editing, stays out and keeps needing its own research pass.

**Tests**: Yes. Both halves are testable without a running editor: the grammar through the existing TextMate harness, the emitter through doctests and a beet integration folder.

**Organization**: By user story, in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths in every description

## Path Conventions

Extension at `extension/vscode/`, CommonJS, no build step. Sources in `src/`, grammars in `syntaxes/`, unit tests in `test/*.test.js` run by `node --test`. Python package at `python_package/stewbeet/`, integration tests as one beet project per folder under `python_package/tests/`, each run by `scripts/run_integration_tests.py`.

---

## Why these two steps sit together

They are the last two unbuilt MUSTs in the spec, they are both bolt-side, and **neither depends on the other**. D gives `.bolt` files a language id, without which no server can ever select them. E gives bolt and mecha projects the same `.mcfunction.map` sidecars StewBeet already emits, which the extension consumes without a single line of new JavaScript, because step C's consumer never asks who wrote the map.

Different languages, different directories, zero shared files. Two people can take one each, and one person can alternate whenever a test run is slow.

**What E is worth**: [contracts/dialects.md](./contracts/dialects.md) calls layer 1 the golden layer, the one that makes this a product rather than a StewBeet tool. E is what proves that claim, since it is the first non-StewBeet producer.

## What the probe established

A throwaway bolt project compiled through beet settled four things E rests on. Reproduce it as T002 before writing the emitter, because the third finding is the one that decides the design.

1. **The positions are there and they are exact.** `mc.database[function].ast.commands[i].location` is a `SourceLocation(pos, lineno, colno)` into the `.bolt` source, 1-based on both line and column. No frame walk, no `difflib`, no AST re-parse.
2. **The compilation unit's `filename` is the project-relative path of the *first* module that contributed**, not of every command in the function.
3. **A function assembled from two modules therefore cannot be attributed from `filename` alone.** A `demo:shared` built by `append function demo:shared:` in both `main.bolt` and `helper.bolt` serialised to three lines whose locations were `(49, 3, 5)`, `(58, 4, 5)` and `(80, 5, 5)`, of which the first belongs to `helper.bolt` and the other two to `main.bolt`. Reading the unit's `filename` for all three maps two of them onto lines 4 and 5 of a file that has only three, which is a plausible-looking wrong jump and exactly what FR-010 forbids. **This is the normal case, not an edge case**: every component in [shulker](file:///d:/advanced_desktop/shulker) appends to `PLAYER_TICK` from its own module.
4. **`pos`, `lineno` and `colno` are mutually redundant, so the triple names its own file.** Checking each candidate module source for "is offset `pos` at line `lineno`, column `colno`" resolved all three commands above to exactly one candidate, and the right one every time. That is the attribution mechanism, and a zero-candidate or multi-candidate result is emitted unmapped.

Two further facts, both about ordering:

- **The emitter must be listed before `mecha` in the pipeline and do its work after `yield`.** Listed after `mecha`, the `Module` compilation units are already purged from the database when it runs, and their sources are what finding 4 needs.
- **`mecha.contrib.source_map` already exists and is not one.** It prepends a `# [source_map] <filename>` header comment and nothing else. The name collision is worth stating once so nobody reuses it by mistake.

---

## Phase 1: Setup

**Purpose**: Confirm the gap D fills is still real, and commit the evidence E is designed on.

- [ ] T001 [P] Re-verify that no installed extension and no marketplace extension claims the `.bolt` extension, then record the finding and its date in the "An immediate, nearly free win" section of [contracts/dialects.md](./contracts/dialects.md). That section's claim is what justifies the whole of step D, and it was last checked in 2026-08. If something now registers `.bolt`, step D becomes a routing question instead of a grammar and the rest of Phase 3 needs rewriting before it is started
- [ ] T002 Commit the bolt attribution probe under `specs/001-stewbeet-vscode-dx/spike/bolt-attribution/`, as the constitution's third principle requires: the two-module beet project, the plugin that dumps each command's `location` next to its compilation unit's `filename`, and the raw output. Two modules both appending to one function is the whole point of the fixture; a single-module probe proves nothing, because `filename` happens to be right there

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Give the mecha emitter something to reuse, so E adds a front half rather than a second copy of the format.

**US1 does not depend on any of this.** Step D touches no Python at all, so Phase 3 can start on day one alongside these.

- [ ] T003 Decide where the mecha emitter lives and record the decision in the "Naming" section of [contracts/dialects.md](./contracts/dialects.md), which currently promises a standalone beet plugin extracted out of StewBeet. **Recommendation: `stewbeet.plugins.sniffer.mecha`**, a submodule any plain beet project can already require by its dotted path with no new distribution, no release process and no second changelog. Say so in the contract rather than leaving it describing a package that does not exist
- [ ] T004 Extract the dialect-free half of `python_package/stewbeet/plugins/sniffer/emit.py` into `python_package/stewbeet/plugins/sniffer/sidecar.py`: `SOURCE_MAPPING_URL`, `function_file_path`, `source_root_for`, `pack_output_depth`, `carries_discovery_comment`, and the append-and-write body of `write_maps` as a `write_sidecar(ctx, path, func, mapped)` taking already-resolved `dict[int, SourceOrigin]`. What stays in `emit.py` is the one StewBeet-specific line, reading `Mem.source_map_chunks` and running `align`. Carry the doctests across unchanged
- [ ] T005 Move the project-source filter out of `python_package/stewbeet/plugins/sniffer/origin.py` into the shared half, so FR-010 is enforced by one gate for both producers. Only the filter moves: the frame walk, the AST index and the tier ordering are StewBeet's reconstruction machinery and have no meaning for a producer whose positions were never lost
- [ ] T006 Prove step B is untouched by the split: `python_package/tests/plugin_22_sniffer_source_maps`, `plugin_23_sniffer_with_headers` and `plugin_24_sniffer_attribution` must pass byte for byte through `scripts/run_integration_tests.py`. A refactor that quietly changes a `sourceRoot` breaks navigation in a way no unit test sees

**Checkpoint**: `encode`, `model` and `sidecar` know nothing about StewBeet, and the StewBeet emitter still emits exactly what it did.

---

## Phase 3: User Story 1 - A bolt file opens as code (Priority: P1) 🎯 MVP

**Goal**: Open any of shulker's 141 `.bolt` files and get a language id, syntax colours and comment toggling, where today VS Code shows plain text.

**Independent Test**: Open `d:/advanced_desktop/shulker/src/component/ammo.bolt`. The status bar says Bolt, `class`, `def` and strings are coloured, the command lines inside `build` are coloured as commands, and ctrl+/ inserts `#`. Maps to FR-016.

- [ ] T007 [US1] Add a `contributes.languages` entry to `extension/vscode/package.json`: id `bolt`, aliases `["Bolt", "bolt"]`, `extensions: [".bolt"]`, and a `configuration` pointing at a language configuration file. Do **not** add `mcfunction` to that contribution: FR-015 partitions ownership by file and Spyglass owns that id
- [ ] T008 [US1] Settle `extension/vscode/language-configuration.json`, which sits at the extension root and is referenced by nothing in `package.json`. Either wire it in as bolt's configuration, correcting `autoClosingPairs` for Python's triple quotes and adding `indentationRules` for the trailing colon that opens a bolt block, or delete it and write a fresh `bolt-language-configuration.json`. Say which in the commit, because a stray file that looks wired in is how the next reader loses an hour
- [ ] T009 [US1] Create `extension/vscode/syntaxes/bolt.tmLanguage.json` with scope name `source.bolt`, whose base pattern list includes `source.python`. Bolt is Python with command statements interleaved, so Python is the ground and commands are the exception, never the other way round
- [ ] T010 [US1] Add the command-statement rule to `extension/vscode/syntaxes/bolt.tmLanguage.json`: a line whose first token is a root command literal delegates the rest of the line to `source.mcfunction.embedded`, the grammar the extension already ships. **Generate the literal set from mecha rather than typing it**, so SC-003 stays true, and record the one-liner that regenerates it in the grammar's `comment` field. It is 92 literals today, read off `Mecha.spec.tree.children`
- [ ] T011 [US1] Handle the collisions in the same rule. `return` is the only literal that is also a Python keyword, and Python wins there since `return x` is overwhelmingly a Python return in a `.bolt` file. `list`, `item`, `time`, `test`, `random`, `version`, `stop`, `tick`, `help` and `data` are ordinary Python identifiers, so the head only counts as a command when what follows it is not Python: no `=`, `.`, `(`, `[` or `,`. A trailing `:` must stay allowed, since `function path:` and `append function PLAYER_TICK:` are bolt's nesting form
- [ ] T012 [US1] Colour bolt's three import forms in `extension/vscode/syntaxes/bolt.tmLanguage.json`: `import demo:helper`, `from server:core import SERVER_TICK` and `from ./type import Component`. Python's own grammar renders `server:core` as a syntax error, which is the most visible thing wrong with reading a bolt file today
- [ ] T013 [US1] Colour the nesting head as a command in `extension/vscode/syntaxes/bolt.tmLanguage.json`, so `append function PLAYER_TICK:` and `function self.tick_reload` show the resource location as a resource location. The argument is frequently a Python expression rather than a literal path, and those must keep Python's colours instead of being swallowed by the command rule
- [ ] T014 [US1] [P] Extend `extension/vscode/test/grammar.test.js` for the new grammar: valid JSON, scope name `source.bolt`, every `match`, `begin` and `end` compiling as a RegExp, and the literal set matching the count the generator produced. It already walks the other two grammars the same way
- [ ] T015 [US1] Extend `extension/vscode/test/tokenize.test.js` with real-engine cases against `source.bolt`: a `def` and a `class` keep Python's scopes, `say hello` is a command, `return x` is Python, `item = 3` is Python, `item modify entity @s ...` is a command, `from lib:predicates import has_item_predicate` colours the resource location, and `append function PLAYER_TICK:` colours the head. That harness skips when it cannot find MagicPython, so state in the task that a run which reports skips has verified nothing
- [ ] T016 [US1] Run the grammar over all 141 files in `d:/advanced_desktop/shulker/src/` and check that none of them ends up in one runaway scope. A begin pattern whose end never matches turns the rest of the file into one colour, and a 141-file corpus is the cheapest way to find that
- [ ] T017 [US1] Confirm `extension/vscode/src/extension.js` reacts to nothing in a bolt document: no block decorations, no virtual documents, no CodeLens. Step D contributes a grammar and an id, and the providers are all StewBeet-shaped. Do not add `onLanguage:bolt` to `activationEvents` either, since grammars need no activation and an extension that wakes up for a file it does nothing with is pure cost

**Checkpoint**: FR-016 holds. `.bolt` has an id, which is what step F needs before it can select anything.

---

## Phase 4: User Story 2 - A bolt or mecha build emits source maps (Priority: P2)

**Goal**: A beet project compiling bolt or `.mcfunction` through mecha writes the same `.mcfunction.map` sidecars StewBeet writes, read straight off the AST.

**Independent Test**: Build the probe project from T002 with the emitter in its pipeline and decode the sidecar: every command line points at the module that wrote it, at the right line, and the two-module function splits its lines between two `sources` entries. Maps to FR-017, FR-013 and FR-014.

- [ ] T018 [US2] Create `python_package/stewbeet/plugins/sniffer/mecha/__init__.py` with a `beet_default(ctx)` generator doing its work after `yield`, and say in its docstring that it must be listed **before** `mecha` in the pipeline. Listed after, the `Module` compilation units are gone from `mc.database` by the time it runs, and their sources are what T019 needs. This is the opposite of `stewbeet.plugins.sniffer.emit`'s placement rule and will be got wrong otherwise
- [ ] T019 [US2] Implement `owner_of(location, sources)` in `python_package/stewbeet/plugins/sniffer/mecha/attribute.py`: for each candidate compilation unit that has a `source`, accept it when offset `location.pos` sits at line `location.lineno` column `location.colno` of that source. Candidates are every unit in `mc.database` carrying a source, which is what makes the check work across modules. Doctest it on the probe's own numbers
- [ ] T020 [US2] Return `None` from `owner_of` when zero or more than one candidate matches, in `python_package/stewbeet/plugins/sniffer/mecha/attribute.py`, and emit that line unmapped. FR-010 is a validity condition, not a quality target: a jump to the wrong file is worse than no jump, and a two-line module can easily agree with a longer one by accident
- [ ] T021 [US2] Reject candidates that fail the shared project-source filter from T005, in `python_package/stewbeet/plugins/sniffer/mecha/attribute.py`. shulker loads `vendor/*`, so a bolt project maps into installed libraries by default unless this is applied, and FR-010 forbids that as firmly for bolt as for StewBeet
- [ ] T022 [US2] Resolve the generated line of each command in `python_package/stewbeet/plugins/sniffer/mecha/lines.py` by counting the newlines the serializer actually produced, not by assuming one command per line. Dense layout does emit one line per top-level command, but `preserve` layout interleaves the source's own comments and blank lines, and shulker's config sets formatting options of its own
- [ ] T023 [US2] Emit nothing for a function whose reconstructed line count disagrees with its final `func.text`, in `python_package/stewbeet/plugins/sniffer/mecha/lines.py`, and count those in the summary the plugin logs. A plugin listed after `mecha` that rewrites text is the case this protects against, and the StewBeet side needed a whole `difflib` pass for the same reason
- [ ] T024 [US2] Convert mecha's 1-based `lineno` and `colno` to the map's 0-based fields in `python_package/stewbeet/plugins/sniffer/mecha/__init__.py`, and keep the real column rather than zeroing it. Column precision is the one thing this producer gets for free and the StewBeet path explicitly does not promise, so throwing it away here would be a choice, not a limitation
- [ ] T025 [US2] Write the sidecars through `write_sidecar` from T004, in `python_package/stewbeet/plugins/sniffer/mecha/__init__.py`, so the discovery comment, the `sourceRoot` arithmetic and the idempotence check are the ones step B already validated against Sniffer's reference implementation
- [ ] T026 [US2] [P] Add `python_package/tests/plugin_25_sniffer_mecha_bolt/` as a beet project: two `.bolt` modules both appending to one function, the emitter before `mecha` in the pipeline, and an assertions plugin that decodes the emitted `mappings` and asserts each line's source and line number. This is the probe promoted to a regression test, and the multi-module shape is the assertion that matters
- [ ] T027 [US2] [P] Add a second case to `python_package/tests/plugin_25_sniffer_mecha_bolt/` covering a plain `.mcfunction` file compiled by mecha with no bolt at all. FR-014 says the map format and encoder are shared across dialects, and a mecha-only project is the cheapest proof that the emitter is not secretly bolt-specific
- [ ] T028 [US2] Assert in the same folder that a module under the loaded `vendor/` tree produces unmapped lines rather than a mapping into it, per T021. The rule is only worth anything if a test would notice it being dropped

**Checkpoint**: FR-017 holds. A second, entirely different producer writes the same artifact.

---

## Phase 5: User Story 3 - A bolt project lights up with no extension change (Priority: P3)

**Goal**: The claim [contracts/dialects.md](./contracts/dialects.md) is built on, tested rather than asserted: the map consumer does not know who wrote the map.

**Independent Test**: Open a bolt project's build output in VS Code with the shipped extension, ctrl+click a line in a generated `.mcfunction`, and land in the `.bolt` file that wrote it. No JavaScript was changed to make that work. Maps to FR-013.

- [ ] T029 [US3] Build [shulker](file:///d:/advanced_desktop/shulker) with the emitter in its pipeline, using its own `uv` environment, since `bolt_expressions`, `bolt_native_macros` and `bolt_selectors` are not installed in the interpreter StewBeet runs under. Record how many of its functions got a map and how many lines came out unmapped, since a very high unmapped ratio means T019 is failing quietly rather than the project being unusual
- [ ] T030 [US3] With that build open, ctrl+click a generated line and confirm `stewbeet.goToSource` lands on the right `.bolt` line, then confirm no file under `extension/vscode/src/` was touched to get there. If something did need touching, it belongs in this task list rather than in step C's, and the dialect-agnostic claim in the contract needs correcting
- [ ] T031 [US3] Set a Sniffer breakpoint from a `.bolt` line against the same build, the way [quickstart.md](./quickstart.md)'s interop section does it for StewBeet. SC-002 says Sniffer needs no StewBeet-specific code, and a bolt project is the strongest available evidence for that

**Checkpoint**: The product is no longer a StewBeet tool.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T032 Measure the emitter against NFR-002 on shulker: median of five builds with it absent against five with it enabled, under 20% overhead. It reads an AST that mecha already built and does no parsing, so anything near that ceiling means T019 is rescanning sources per command instead of once
- [ ] T033 [P] Update the sequencing and layers tables in [contracts/dialects.md](./contracts/dialects.md) so D and E read as shipped, and add the emitter's pipeline placement rule to the "Emitting maps per dialect" section. That section currently describes the mecha producer as a plan
- [ ] T034 [P] Add a "two producers, one format" section to [contracts/source-map.md](./contracts/source-map.md) stating what differs between them: the mecha side carries real columns, the StewBeet side maps to a line and column zero. A consumer reading both should know which promise it is holding
- [ ] T035 [P] Add phases D and E to [quickstart.md](./quickstart.md) with their validation steps, including the `mecha.contrib.source_map` name collision, so the next reader does not require it expecting a source map and get a header comment
- [ ] T036 [P] Update `extension/vscode/README.md` and `extension/vscode/CHANGELOG.md` for the bolt language id, and bump `extension/vscode/package.json`. The README currently describes a Python-only extension, and this is the first thing it does for a file that is not `.py`
- [ ] T037 [P] Record the `languages` contribution and the `source.bolt` grammar in [contracts/extension-api.md](./contracts/extension-api.md), whose "Grammar: what is highlighted as mcfunction" section covers only the Python injection
- [ ] T038 [P] Move FR-016 and FR-017 out of the deferred block in [spec.md](./spec.md), deleting the sentence that says neither is in the current pass and both get their own `/speckit-tasks` list when their turn comes. Their turn is this list
- [ ] T039 Rebuild the extension package with `extension/build_publish.sh`, which copies the icon and licence in and cleans them up afterwards. Do not call `vsce` directly
- [ ] T040 Run the full gate: `npm test` and `npm run test:integration` in `extension/vscode/`, plus `ruff check stewbeet tests`, `pyright stewbeet tests`, `scripts/sync_api.py --check`, `scripts/all_doctests.py` and `scripts/run_integration_tests.py` in `python_package/`

---

## Dependencies

```
Phase 1 (T001-T002)  <- verify the gap, commit the probe
        |
        +-- Phase 3 (T007-T017)  US1 step D, JavaScript and JSON only
        |
        +-- Phase 2 (T003-T006)  the dialect-free split
                    |
                    +-- Phase 4 (T018-T028)  US2 step E, the mecha front half
                                |
                                +-- Phase 5 (T029-T031)  US3 the payoff, needs a real bolt build
```

**Story independence**: US1 and US2 share no file and no language. US1 needs only T001; US2 needs T002 and Phase 2. US3 is the only task group needing both a bolt build and the shipped extension, and it verifies rather than builds.

## Parallel opportunities

- **Phase 3 runs alongside Phase 2 and Phase 4 from the start.** They are the two halves of this list and the whole reason both steps are in one file.
- Inside Phase 3, T014 and T015 are two different test files and parallel with each other, though both need T010 through T013 to exist first.
- Inside Phase 4, T026, T027 and T028 are three cases in one fixture folder and can be written together once T018 through T025 land.
- T033 through T038 are six different files and parallel with each other.

## Implementation strategy

**MVP is Phase 3.** Step D is an afternoon, it needs no Python, no build and no other step, and it turns 141 files in a real project from plain text into code. It is also the only thing on this list a bolt author notices without reading a map.

**Phase 4 is where the value is.** D is a courtesy; E is the step that makes navigation, diagnostic relocation and Sniffer breakpoints work for a dialect StewBeet cannot even parse, with no new consumer code. Take it second, not later.

**T019 is where this can go wrong.** Everything else on the Python side fails visibly. A file attribution that is merely plausible ships a map that sends people to the wrong file with total confidence, which is the failure FR-010 exists to forbid. T020's refusal to guess is not defensive padding, it is the requirement.
