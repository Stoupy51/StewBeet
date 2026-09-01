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
- Maps are emitted only when the `stewbeet.plugins.sniffer` plugin is in the pipeline, and are excluded from release archives.

### When the pack is copied out of the workspace

`sourceRoot` is relative, so it resolves correctly in `build/` and breaks once `copy_to_destination` copies the pack into a Minecraft world folder. That is the correct trade: relative paths keep the build reproducible and machine-independent, and Sniffer's existing `pathMapping` setting is exactly the mechanism for telling a debugger where the sources really live. Debug from `build/`, or configure `pathMapping`.

## Guarantees

- **G1**: If generated line `n` is mapped, the mapped source position is inside a `write_*` call or a declaration in that file.
- **G2**: Mapped lines are strictly increasing in generated order. The map never goes backwards.
- **G3**: A missing mapping means "unknown origin", never "same as the previous line". Consumers must not interpolate.
- **G4**: An unmapped line is always safe to skip. No consumer is required to handle it.
- **G5**: Every entry in `sources` is a file in the project's own source tree. A map never points into the StewBeet package, beet, bolt, mecha, stouputils, `site-packages` or the stdlib. When no project origin exists for a line, the line is unmapped, because a jump into library internals is worse than no jump.
- **G6**: One map may carry several sources. Confirmed by the reference: `aura.mcfunction` is generated from calls in both `hit.ts` and `spawn.ts`, and its map carries two sources with the segments switching between them. Consumers offering navigation should present all of them rather than only the first.
- **G7**: Several generated lines may map to the same source line. Confirmed by the reference: `effect('slowness', 3)` on line 8 of `hit.ts` expands to both `effect clear` and `effect give`, two segments pointing at the same position. This is the normal case for any statement that expands, and StewBeet hits it whenever one Python line writes multiple commands.

## Non-guarantees

- Column precision inside a line. `sourceColumn` is `0` throughout the reference and points at the start of the string literal in ours, not at the character that produced the command. mcfunction diagnostics carry their own column, which the extension applies to the Python line separately.
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
