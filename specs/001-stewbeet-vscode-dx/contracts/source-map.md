# Contract: `.mcfunction.map`

The interop surface between StewBeet, the VS Code extension, and any third-party debugger (Sniffer). Consumers must be able to read it with an off-the-shelf source map library.

## Status: validated against a reference implementation

Sniffer's author supplied a working example, preserved verbatim at [reference/](./reference/). It is a fictional TypeScript datapack DSL compiled to a datapack, with maps, so it demonstrates the format without depending on StewBeet.

```
reference/
├── generated/pack/data/ns/function/hit.mcfunction[.map]
├── generated/pack/data/ns/function/nested/aura.mcfunction[.map]
├── generated/pack/pack.mcmeta
└── source/combat/hit.ts, source/spawn.ts
```

Every segment in both maps has been decoded and checked against its source line. The decoder walkthrough is in [Appendix A](#appendix-a-decoded-reference). Where this document and the reference disagree, **the reference wins**, with one stated exception: its author has since confirmed that the `sourcesContent` field in it is an oversight and should be ignored.

## Format

[Source Map v3](https://tc39.es/ecma426/), the same JSON shape JavaScript tooling has used for a decade. This is `reference/generated/pack/data/ns/function/hit.mcfunction.map` in full:

```json
{
  "version": 3,
  "file": "hit.mcfunction",
  "sourceRoot": "../../../../..",
  "sources": [
    "source/combat/hit.ts"
  ],
  "names": [],
  "mappings": "AAKA;AACA;AACA;AAAA;AACA"
}
```

| Field | Value |
|---|---|
| `version` | Always `3`. A consumer seeing anything else must ignore the file, not fail. |
| `file` | Basename of the generated function, e.g. `hit.mcfunction`. |
| `sourceRoot` | Relative path from the **map file's own directory** to the project root, so `sources` entries stay project-relative and no absolute path is ever written. Depth varies per map: `../../../../..` for a function at `data/ns/function/`, `../../../../../..` for one at `data/ns/function/nested/`. |
| `sources` | Source paths relative to `sourceRoot`. **Several are normal**, see G6. Deduplicated, in first-use order. |
| `names` | Always `[]`. mcfunction has no symbol names to record here. |
| `mappings` | Base64 VLQ, one group per generated line, groups separated by `;`. |

### `sourcesContent` is not part of the format

The reference file carries one. Its author has confirmed that was an oversight and it should be ignored, so **StewBeet omits the key entirely**. The field is optional in Source Map v3, consumers read sources from disk through `sourceRoot`, and omitting it is both smaller and unambiguous.

This is the right outcome for StewBeet at scale anyway. The reference has two functions; a real project generates on the order of 1000, each map inlining every source that contributed to it. At 1 to 3 sources per function and 5 to 20 KB per Python file, inlining would cost tens of megabytes of duplicated Python in the build output, for files sitting two directories away.

The case inlining would have served, a pack running where the editor cannot read the sources, is already served by Sniffer's `pathMapping` setting.

## Mappings encoding

Each generated line contributes at most one segment, because an mcfunction line is one command. A segment is four VLQ fields, each delta-encoded against the previous segment **in the file**, not within the line:

```text
[ generatedColumn, sourceIndex, sourceLine, sourceColumn ]
```

- `generatedColumn` is always `0`, so its delta is always `0`.
- `sourceLine` deltas carry across a source change. In `aura.mcfunction.map`, segment 2 moves from `hit.ts` line 8 to `spawn.ts` line 5 with a `sourceIndex` delta of `+1` and a `sourceLine` delta of `-3`. Standard behaviour, worth stating because it is the detail hand-rolled encoders get wrong.
- All line and column numbers are 0-based, as the standard requires.

Two shapes of "no mapping", and they are not interchangeable:

- **Empty group** (two consecutive `;`): this generated line has no known origin. Generated headers and blank separators land here.
- **Absent group** (`mappings` simply runs out before the file does): every remaining generated line is unmapped. The reference uses this for its trailing `sourceMappingURL` comment, which is why `hit.mcfunction` has 6 lines but `mappings` has only 5 groups.

The VLQ alphabet and continuation-bit scheme are the standard ones; see [Variable-length quantity](https://rosettacode.org/wiki/Variable-length_quantity#Python) for the encoder and [source map internals](https://www.polarsignals.com/blog/posts/2025/11/04/javascript-source-maps-internals) for the delta rules.

## Placement and discovery

- One map per generated function, written as a sibling: `data/<ns>/function/<path>.mcfunction.map`.
- Discovery is by convention: given `foo.mcfunction`, look for `foo.mcfunction.map`.
- The generated function's **last** line is `## sourceMappingURL=<basename>.mcfunction.map`. Note **two** hash characters, matching the reference. It must be last, and it must be unmapped, because Sniffer counts comments and blank lines when placing breakpoints so a leading comment would shift every mapped line.
- Maps are emitted only when the `stewbeet.plugins.sniffer` plugin is in the pipeline, and then they appear in every artifact the build produces, the archive zip included.

### When emission happens, and why it is a pipeline entry of its own

Two ordering needs pull in opposite directions. Capture must be installed **before** anything writes
a function, which is what `require` guarantees: beet runs everything there before it even loads the
pack (`ProjectBuilder.bootstrap` requires `config.require`, then `load`, then `render`, then yields).
Emission must happen **after** every rewriting plugin (`auto.headers` above all) and still **before**
`stewbeet.plugins.archive`, because that zip is what `copy_to_destination` drops into
`saves/<world>/datapacks` and therefore what a debugger loads.

A beet generator cannot span that gap. beet runs every plugin's forward pass first, then unwinds the
generators in reverse (`GenericPipeline.run` in `beet/toolchain/pipeline.py`), so a teardown always
runs after `archive`, never before it. Confirmed by building the canonical pipeline: the zip came out
with no maps **and** with `.mcfunction` files missing the `sourceMappingURL` comment the build
directory had, two artifacts from one build that disagreed.

So the plugin has two entries:

| Entry | Where | Does |
|---|---|---|
| `stewbeet.plugins.sniffer` | `require`, next to `stewbeet` | installs capture, and at teardown writes anything the emit step missed, with a warning |
| `stewbeet.plugins.sniffer.emit` | `pipeline`, after every writer and before `stewbeet.plugins.archive` | writes the sidecars and appends the discovery comments |

`require` rather than an early pipeline entry, because position inside `require` cannot be got wrong
and no write can precede it. Capture is live while the pack's own hand-written `.mcfunction` files
load; they record chunks with no origin, so they get no map and no comment. A pipeline entry still
works when it sits before every writer, which is what `tests/plugin_23_sniffer_with_headers` covers.

Emission is idempotent: a function already carrying a `sourceMappingURL` line is skipped, so listing
the step twice, or falling through to the teardown after it already ran, never doubles a comment.

### When the pack is copied out of the workspace

`sourceRoot` is relative, so it resolves correctly in `build/` and breaks once `copy_to_destination` copies the pack into a Minecraft world folder. That is the correct trade: relative paths keep the build reproducible and machine-independent, and Sniffer's existing `pathMapping` setting is exactly the mechanism for telling a debugger where the sources really live. Debug from `build/`, or configure `pathMapping`.

## Guarantees

- **G1**: If generated line `n` is mapped, the mapped source position is inside a `write_*` call or a declaration in that file. For the mecha producer, it is the command's own position in the module that wrote it.
- **G2**: Mapped lines are strictly increasing in generated order. The map never goes backwards.
- **G3**: A missing mapping means "unknown origin", never "same as the previous line". Consumers must not interpolate.
- **G4**: An unmapped line is always safe to skip. No consumer is required to handle it.
- **G5**: Every entry in `sources` is a file in the project's own source tree. A map never points into the StewBeet package, beet, bolt, mecha, stouputils, `site-packages` or the stdlib. When no project origin exists for a line, the line is unmapped, because a jump into library internals is worse than no jump.
- **G6**: One map may carry several sources. Confirmed by the reference: `aura.mcfunction` is generated from calls in both `hit.ts` and `spawn.ts`, and its map carries two sources with the segments switching between them. Consumers offering navigation should present all of them rather than only the first.
- **G7**: Several generated lines may map to the same source line. Confirmed by the reference: `effect('slowness', 3)` on line 8 of `hit.ts` expands to both `effect clear` and `effect give`, two segments pointing at the same position. This is the normal case for any statement that expands, and StewBeet hits it whenever one Python line writes multiple commands.

## Two producers, one format

The same artifact is written by two plugins with nothing in common but the encoder, and a consumer cannot tell them apart. It does not need to: everything above holds for both. What differs is how much precision each one had to start with.

| | `stewbeet.plugins.sniffer` | `stewbeet.plugins.sniffer.mecha` |
|---|---|---|
| Sources | `.py` files calling `write_*` | `.bolt` modules and `.mcfunction` files compiled by mecha |
| Where positions come from | reconstructed by frame walk plus an AST index, because none exist | read off `AstNode.location`, because they were never lost |
| `sourceColumn` | the start of the string literal | **the command's real column** |
| Reconciled with `difflib` | yes, `auto.headers` rewrites every function | yes, for the same reason |

Both are opt-in pipeline entries, and both emit nothing when a line has no origin in the project's own source.

**The column is the one place a consumer may want to know which wrote the map**, and it can tell without being told: a StewBeet map's columns all point at string literals, while a mecha map's point at commands. Nothing in the format depends on the difference, so a consumer that ignores columns entirely is correct for both.

### What each producer can see

Neither producer maps everything, and the boundaries are different.

**`stewbeet.plugins.sniffer`** captures at three points: `beet.Function.append` / `.prepend`, `write_function`'s overwrite branch, and `NamespaceContainer.process`, which every insertion into a pack passes through with both the namespace and the key in hand. That last one is what makes beet's own idiom work, in all of its spellings:

```python
ctx.data.functions["ns:mine"] = Function("say hi")     # mapped
ctx.data["ns"].functions["mine"] = Function("say hi")  # mapped
ctx.data[Function]["ns:mine"] = Function("say hi")     # mapped
write_function("ns:mine", "say hi")                    # mapped
```

An assignment records only when the caller is genuinely assigning, which the AST index decides. `write_function`'s overwrite branch assigns too, and records itself one frame further down, so without that check every helper write would be recorded twice. An assignment of empty content records nothing, so a `Function()` filled by later appends points at the appends.

**`stewbeet.plugins.sniffer.mecha`** reads positions off the AST, and an offset only means something relative to the text it was parsed from. A function assembled in memory has no file behind it, so its commands are unmapped however confidently their position reads. Roughly a third of a real bolt project's command lines map; the rest are synthesised, rewritten past recognition, or come from a library.

Both boundaries are the same rule: FR-010 makes an unmapped line the correct answer whenever the origin is not certain, because a confident jump to the wrong file costs the reader more than no jump.

## Non-guarantees

- Column precision inside a line, **from the StewBeet producer**. `sourceColumn` is `0` throughout the reference and points at the start of the string literal in ours, not at the character that produced the command. mcfunction diagnostics carry their own column, which the extension applies to the Python line separately. The mecha producer does carry a real column, so this non-guarantee is producer-specific rather than a property of the format.
- Round-tripping content written from a variable or a helper's return value. Those map to the `write_*` call line, flagged `exact: false` at capture time and indistinguishable in the emitted map.
- Stability across builds. A map is only valid for the build that produced it.

## Test fixtures

`contracts/fixtures/` holds paired inputs and expected maps, consumed by both the Python encoder tests and the JavaScript decoder tests, so the two implementations cannot drift:

- `simple/` a single `write_function` with a literal triple-quoted string.
- `appended/` three `write_function` calls from two Python files into one path.
- `headered/` the same, after `auto.headers` prepends a header block, proving empty groups land on the header lines.
- `fstring/` an f-string whose interpolation changes the rendered line count, proving the collapse-to-first-line fallback.
- `declared/` a custom block whose `place_secondary` is generated by a plugin and then appended to by the developer. Two sources, two runs of lines, neither pointing at the plugin (G5, G6).
- `unattributable/` a plugin write with no attribution scope, proving the whole chunk is emitted unmapped instead of pointing into `stewbeet/`.
- `editable_install/` the same project with StewBeet installed editable from inside the project root, proving the library exclusion is not just a project-root check.
- `expanding/` one Python line writing two commands, proving G7 and the zero-delta segment.

Additionally, the decoder must reproduce [Appendix A](#appendix-a-decoded-reference) from `reference/` exactly. That is a conformance test against someone else's encoder, which no fixture we write ourselves can replace.

## Appendix A: decoded reference

Produced by decoding `mappings` and resolving each segment through `sourceRoot`.

`hit.mcfunction.map`, `sourceRoot` `../../../../..`, mappings `AAKA;AACA;AACA;AAAA;AACA`:

| Generated line | Content | Maps to |
|---|---|---|
| 0 | `say hit!` | `source/combat/hit.ts:6:0` -> `say('hit!');` |
| 1 | `damage @s 4 minecraft:generic` | `source/combat/hit.ts:7:0` -> `damage(4);` |
| 2 | `effect clear @s minecraft:slowness` | `source/combat/hit.ts:8:0` -> `effect('slowness', 3);` |
| 3 | `effect give @s minecraft:slowness 3 0` | `source/combat/hit.ts:8:0` -> the same line, G7 |
| 4 | `function ns:nested/aura` | `source/combat/hit.ts:9:0` -> `aura();` |
| 5 | `## sourceMappingURL=hit.mcfunction.map` | no group, mappings ended |

`aura.mcfunction.map`, `sourceRoot` `../../../../../..`, mappings `AAQA;ACHA;AACA`:

| Generated line | Content | Maps to |
|---|---|---|
| 0 | `particle minecraft:enchant ~ ~1 ~ ...` | `source/combat/hit.ts:9:0` -> `aura();` |
| 1 | `scoreboard players set @s ns.aura 60` | `source/spawn.ts:6:0` -> `aura();` |
| 2 | `execute as @e[tag=ns.spawned] run ...` | `source/spawn.ts:7:0` -> `aura.tick('ns.spawned');` |
| 3 | `## sourceMappingURL=aura.mcfunction.map` | no group, mappings ended |

Line 1 of `aura` is the segment worth studying: `ACHA` decodes to `[0, +1, -3, 0]`, moving to the next source **and** three lines back, because the deltas are file-wide rather than per-source.
