# Phase 1: Data Model

Every record below is a frozen dataclass on the Python side. Nothing is a `dict[str, dict[str, ...]]` blob.

## Python side (`stewbeet.plugins.source_maps`)

### `SourceOrigin`

Where a chunk of written content came from in the author's Python.

| Field | Type | Meaning |
|---|---|---|
| `file` | `str` | Absolute path of the `.py` file that called a `write_*` function. |
| `line` | `int` | 0-based line of the content literal's first line, or of the call when the argument is not a literal. |
| `column` | `int` | 0-based column of the literal's opening quote, or of the call. |
| `exact` | `bool` | `False` when the origin is the call rather than a literal, so consumers can weight the mapping. |

**Validation**, enforced at construction so an invalid origin cannot exist:

- `line >= 0`, `column >= 0`.
- `file` is under one of the configured project roots.
- `file` is **not** under the package directory of `stewbeet`, `beet`, `bolt`, `mecha` or `stouputils`, and contains no `site-packages` component. This check is not implied by the previous one: StewBeet is frequently installed editable from inside the repo being built.

A candidate failing any of these does not produce a degraded `SourceOrigin`, it produces `None`.

### `AttributionScope`

The ambient fallback used when no project frame is on the stack, pushed by StewBeet plugins that generate on a declaration's behalf.

| Field | Type | Meaning |
|---|---|---|
| `origin` | `SourceOrigin` | The declaration's own capture site, recorded by `Item.__post_init__`. |
| `field` | `str \| None` | Optional keyword argument of the declaration whose literal is the real source, e.g. `"on_place"`. Resolved against the cached AST of the declaration call. |

Held as a stack on `Mem`, entered with `attribute_to(definition, field=None)`. Reentrant, and the innermost scope wins.

### `WriteChunk`

One `write_*` call's contribution to one function, recorded in call order.

| Field | Type | Meaning |
|---|---|---|
| `lines` | `tuple[str, ...]` | The content as written, split on newlines, no trailing empty element. |
| `origin` | `SourceOrigin \| None` | Where those lines came from, or `None` when no project origin could be resolved. |

**Origin resolution**, in order, first hit wins:

1. Innermost stack frame passing the project-source filter, refined to the content argument's literal position through the AST index.
2. Top of the attribution scope stack.
3. `None`.

**State transitions** mirror `write_function` exactly:

- `append` appends a chunk to the path's list.
- `prepend` inserts a chunk at index 0.
- `overwrite` clears the list, then appends, so origins replaced by an overwrite vanish from the map.
- A `condition` that returns `False` records nothing.

Several chunks with different origins in one list is the normal case, not an edge case: a custom block's `place_secondary` typically holds a plugin-attributed chunk and a developer-authored one.

### `LineMapping`

One resolved generated line.

| Field | Type | Meaning |
|---|---|---|
| `generated_line` | `int` | 0-based line in the final `.mcfunction`. |
| `source_index` | `int` | Index into the map's `sources` array. |
| `source_line` | `int` | 0-based line in that source file. |
| `source_column` | `int` | 0-based column in that source file. |

**Invariants**: `generated_line` values are strictly increasing within a map, and lines with no origin (generated headers, blank separators, the trailing `## sourceMappingURL` comment) are simply absent. Two `LineMapping`s may share a `source_line`, which is what happens whenever one Python line writes several commands.

### `FunctionSourceMap`

The emitted artifact for one generated function.

| Field | Type | Meaning |
|---|---|---|
| `generated_path` | `str` | Resource-location path, e.g. `mynamespace:v1.0/tick`. |
| `source_root` | `str` | Relative path from the map file's own directory to the project root. Depth varies per function, so it is computed per map, not once. |
| `sources` | `tuple[str, ...]` | Source paths relative to `source_root`, deduplicated, in first-use order. Several is the normal case. |
| `mappings` | `tuple[LineMapping, ...]` | Resolved lines. |

`sourcesContent` is not modelled and not emitted. The key is omitted from the JSON entirely.

Serialised through the [source map contract](./contracts/source-map.md), which is validated against a working reference implementation at `contracts/reference/`.

## Relationships

```text
Item(...) declared in user code
        |  __post_init__ captures its own SourceOrigin
        v
   Item.origin  <---- attribute_to(obj_block) ---- plugin generation loop
                                                          |
developer's own write_function ---------------------------+
                                                          |
                                                          v
                                                    WriteChunk  ---- many per ---->  path
                                                          |
                                                          |  end of pipeline: difflib alignment
                                                          |  against the function's final text
                                                          v
                                                    LineMapping -- many per --> FunctionSourceMap -- one per --> .mcfunction
```

`Mem.source_map_chunks: dict[str, list[WriteChunk]]` holds the capture stage, keyed by resource-location path. `Mem.attribution: list[AttributionScope]` is the ambient stack. Both are reset by `plugins.initialize` like the other `Mem` build state, so `beet watch` does not accumulate across rebuilds.

`Item` gains one non-init field, `origin: SourceOrigin | None`, excluded from `repr`, `compare` and `to_dict`. `Item` is `@dataclass(kw_only=True, slots=True)`, so this must be a declared field rather than an attribute set after the fact.

## Extension side (JavaScript)

Plain objects, no classes. Shapes documented so the tests can assert them.

### `Block`

Already produced by `blocks.js`, unchanged: `{ start: number, end: number }` offsets into the Python document, where `start` is the opening quote including any `f` / `r` prefix.

### `DecodedMap`

`{ sources: string[], lines: Map<number, { sourceIndex, sourceLine, sourceColumn }> }`, keyed by generated line. Built once per `.mcfunction.map` and invalidated on file change.

### `Origin`

`{ uri: vscode.Uri, line: number, column: number }`, the result of resolving a generated location back to Python.

## Validation rules

- A map whose `version` is not `3` is ignored rather than throwing, so a future format bump degrades to "no navigation" instead of breaking the editor.
- A map whose sources cannot be resolved on disk is ignored for navigation but still used for diagnostics suppression.
- Capture is a no-op unless the `source_maps` plugin is in the pipeline, so a release build records nothing and pays nothing.
