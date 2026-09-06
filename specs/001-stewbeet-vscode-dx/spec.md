# Feature Specification: StewBeet VS Code Developer Experience

**Feature Branch**: `001-stewbeet-vscode-dx` | **Date**: 2026-08-30
**Status**: Draft
**Source**: [StewBeet issue #41](https://github.com/Stoupy51/StewBeet/issues/41) "Auto Complete Visual Studio Code extension"

## Problem

StewBeet authors write Minecraft commands as Python strings:

```python
write_function("mynamespace:hello", """
say hello
execute as @a run function mynamespace:greet
""")
```

The current [StewBeet extension](../../extension/vscode/) colors those strings and draws a box around them. Nothing else works inside the box: no completion, no hover, no diagnostics, no navigation. A typo in a command surfaces only when Minecraft loads the pack, and `function mynamespace:greet` is a dead string that ctrl+click cannot follow.

Meanwhile [Spyglass](https://spyglassmc.com/) already provides all of that for real `.mcfunction` files, and StewBeet already generates real `.mcfunction` files into its build output. The two never meet.

## User Scenarios

### Scenario 1: Completing a command (Priority: P1)

An author types `execute as @a run ` inside a `write_function` string and gets the same completion list Spyglass would offer in a `.mcfunction` file, including the resource locations of functions this project generates.

**Acceptance**: Completion appears inside the string block, is absent outside it, and offers project-defined function paths as well as vanilla commands.

### Scenario 2: Following a function reference (Priority: P1)

An author ctrl+clicks `mynamespace:greet` inside a command string and lands on the `write_function("mynamespace:greet", ...)` call that produced it, even when the path was assembled from an f-string.

**Acceptance**: Definition resolves to the Python call site. When the path is not attributable to a single call site, it falls back to the generated `.mcfunction` file rather than failing.

### Scenario 2b: Following a reference into generated content (Priority: P1)

An author declares a custom block, so a StewBeet plugin generates `mynamespace:block/my_block/place_secondary` on their behalf. They then append their own commands to that same function. Ctrl+clicking the path offers **both** origins: the `Block(...)` declaration that caused the plugin to generate it, and their own `write_function` call.

**Acceptance**: Definition returns every distinct origin contributing to the function, in generated order. Neither origin is a file inside the StewBeet package. Had the author used `overwrite=True`, only their own call is offered; a **library** rewriting the same function, as `auto.headers` does to every function in the pack, offers nothing of its own and takes nothing away.

### Scenario 3: Seeing an error before launching the game (Priority: P2)

A build produces a command the game will reject. The author sees the error underlined on the Python line that wrote it, not only in the build output.

**Acceptance**: Diagnostics reported against generated files appear on the originating Python range, and clear when the build is fixed.

### Scenario 4: Debugging with Sniffer (Priority: P2)

An author sets a breakpoint on a Python line inside a `write_function` string, runs [Sniffer](https://github.com/mcbookshelf/sniffer), and execution halts on the corresponding command in the running game.

**Acceptance**: StewBeet emits a mapping file that a third-party debugger can consume without knowing anything about StewBeet.

### Scenario 5: Finding every caller (Priority: P3)

An author asks for references of a generated function and gets every Python location whose generated output calls it, including calls emitted by StewBeet's own plugins.

**Acceptance**: References list Python call sites, and generated-only sites are reported as generated.

## Requirements

### Functional

- **FR-001**: The extension MUST provide completion inside StewBeet mcfunction string blocks, sourced from an existing Minecraft language service rather than a StewBeet-authored command parser.
- **FR-002**: The extension MUST provide hover and signature help inside those blocks, from the same source.
- **FR-003**: The extension MUST resolve go-to-definition on resource locations inside those blocks.
- **FR-004**: StewBeet MUST be able to emit, per generated function, a machine-readable mapping from generated line to originating Python file and line.
- **FR-005**: The mapping format MUST be an existing published standard, consumable by tools that have never heard of StewBeet.
- **FR-006**: Mapping emission MUST be opt-in, and when it is on, every artifact the build produces MUST carry the same content. A map that reaches `build/` but not the zip `copy_to_destination` ships is worse than no map, because the zip is what the game loads and the `sourceMappingURL` comment would then dangle.
- **FR-007**: The extension MUST surface diagnostics produced against generated files on the originating Python ranges.
- **FR-008**: The extension MUST degrade gracefully when no build output exists: language features that need only the editor buffer keep working.
- **FR-009**: Correctness of the mapping MUST survive StewBeet's own post-processing passes (`auto.headers`, `auto.text_renders`, `auto.lang_file`), which rewrite function bodies after they are first written.
- **FR-010**: A mapping MUST NEVER point inside the StewBeet package, beet, or any other installed library. Only files under the project's own source roots are valid targets. A generated line with no valid target MUST be emitted unmapped rather than mapped to a library file.
- **FR-011**: Content generated by a StewBeet plugin on behalf of a user declaration MUST map to that declaration's site in the project, not to the plugin code that emitted it. A definition with no Python declaration site, loaded from JSON or coming from `external_definitions`, has nothing to map to and its generated content MUST be emitted unmapped.
- **FR-012**: When several origins contribute to one generated function, each MUST keep its own lines, and navigation MUST offer all of them. An `overwrite=True` write whose origin resolves into the project discards the origins it replaced, because a developer is genuinely replacing content. An `overwrite=True` write with no project origin MUST discard nothing and record nothing: it is a library transforming text, and `auto.headers` does exactly that to every function in the pack, so an unconditional discard would wipe every mapping before emission runs.

### Non-functional

- **NFR-001**: No mcfunction grammar, command tree, or registry data may be reimplemented inside StewBeet or its extension.
- **NFR-002**: With the `sniffer` plugin absent from the pipeline, build wall time MUST stay within 2% of a baseline build without it, measured as the median of five runs. With it enabled, overhead MUST stay under 20% by the same measure.
- **NFR-003**: The extension must keep working if Spyglass is absent, with the Spyglass-backed features silently unavailable.

### Multi-dialect (scope extension)

The long-term target is one extension serving plain **beet**, **bolt**, **mecha** and **StewBeet**, compatible with Spyglass rather than competing with it. Delivered step by step; see [contracts/dialects.md](./contracts/dialects.md) for the layering and sequencing.

- **FR-018**: The projection MUST resolve interpolated resource locations rather than masking them, so navigation works on paths computed in Python. Masking makes the feature inapplicable to the idiom StewBeet projects use: SimplEnergy contains one literal resource location in its entire source. The generated file already holds the resolved text, and the map already says which generated line each block line produced, so the projection can substitute the built content instead of guessing at the Python.
- **FR-019**: Diagnostics MUST appear without the author opening the generated file, and without a build. A language server publishes diagnostics only for documents it has been given, so a closed generated `.mcfunction` produces none and there is nothing to relay. The extension MUST therefore read them off the virtual documents it already serves for completion, whose lines are in lockstep with the Python, and MUST NOT open anything under the build output. Errors then arrive as the author types rather than after a rebuild, and a pack with two thousand functions costs nothing.
  - A generated file the author opens themselves still relays through the source map, which is the only path that carries a build's own output.
  - Where the two describe the same mistake, the projection's diagnostic wins: it knows which columns are wrong, and the generated file knows only which line.
- **FR-020**: The relay MUST let the author silence diagnostic rules that are noise on generated content. `undeclaredSymbol` fires on every scoreboard objective a dependency declares, and moving that noise onto Python lines makes it far more intrusive than it is in a generated file nobody opens.
- **FR-021**: Navigation across the boundary MUST be reachable without the command palette. A block that produced generated content SHOULD advertise it in the editor.
- **FR-022**: Commands handed to a `write_*` call in a variable MUST be treated as a block. `content: str = f"""..."""` followed by `write_function(path, content)` is 14% of SimplEnergy's calls, and every feature that keys off a block was silently skipping them.
- **FR-023**: StewBeet MUST export a `McFunction` type alias for `str`, and the grammar MUST highlight any string annotated with it as mcfunction. This is what makes coloured commands possible in a variable, and it is the only mechanism available: a TextMate grammar matches one place at a time and cannot learn that `content` on line 206 reaches a `write_function` on line 213. Shape alone is not enough to infer from, since `notes: str = """..."""` must stay plain Python, so the author states the intent instead.
  - The alias MUST be re-exported from `stewbeet` so `from stewbeet import *` provides it, and MUST be `str` at runtime so annotating changes nothing about how the value behaves. `type McFunction = str` in `core/utils/io/functions.py` already satisfies this half.
  - The grammar MUST key on the annotation, `name: McFunction = <string>`, not on a name convention.
  - Block detection (FR-022) MUST keep working without the annotation, so an unannotated variable keeps decorations, completion and diagnostics and gains only the syntax colours when annotated.

- **FR-013**: The map-consuming half of the extension MUST be dialect-agnostic. It consumes `.mcfunction.map` and MUST NOT know which generator produced it.
- **FR-014**: The map format and its encoder MUST be shared across dialects. Only the capture half may be dialect-specific.
- **FR-015**: The extension MUST NOT claim language id `mcfunction` for files Spyglass already serves. Ownership is partitioned by file, not merged.
- **FR-016**: The extension MUST contribute a `bolt` language id and grammar, since no installed extension registers `.bolt` and a document without a language id cannot be served by any language server. The grammar MUST NOT author mcfunction knowledge of its own: the command names it needs are generated from mecha's command tree, and command bodies are handed to the mcfunction grammar the extension already ships.
- **FR-017**: bolt and mecha map emission MUST read positions from the mecha AST (`AstNode.location`), not reconstruct them. Reconstruction is a StewBeet-only necessity.
  - A location carries no filename and the compilation unit names only the first contributing module, so the writing file MUST be recovered from the position itself. A line whose file cannot be narrowed to exactly one MUST be emitted unmapped, per FR-010.
  - Emission MUST survive a plugin that rewrites functions after `mecha`, which `auto.headers` does to every function in a StewBeet pipeline.

### Out of scope

- Authoring a general-purpose vanilla Minecraft language server. Spyglass exists and is better at it.
- Refactoring or renaming across the source/mcfunction boundary.
- Bedrock Edition.
- Projects that enable bolt syntax inside `.mcfunction` files via `meta.bolt.entrypoint`. Deferred until one shows up; see the caveat in `contracts/dialects.md`.

## Success Criteria

- **SC-001**: Issue #41's two asks (completion, ctrl+click to the `write_function` call) both work on a real project.
- **SC-002**: Sniffer can set a breakpoint from a Python line without any StewBeet-specific code in Sniffer.
- **SC-003**: StewBeet contains zero lines of mcfunction syntax knowledge added by this feature.
