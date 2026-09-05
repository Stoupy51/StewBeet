# Step E spike: can a mecha AST command be attributed to the module that wrote it?

**Status: PASS**, run 2026-09-05 against mecha 0.104.1, bolt 0.50.1 and beet 0.116.0. Raw output in [result.json](./result.json).

This is the gate on step E. Keep it as a regression test: it detects a mecha or bolt release that changes what `AstNode.location` means, which would turn every emitted map into a confident jump to the wrong file.

## The question

Every `mecha.AstNode` carries `location: SourceLocation(pos, lineno, colno)`, so a map is a walk over the compiled AST. What the location does **not** carry is a filename, and the obvious substitute, the compilation unit's own `filename`, is wrong as soon as two modules contribute to one function.

`ws/` is the smallest project that exhibits it: `main.bolt` and `helper.bolt` both `append function demo:shared:`.

## Result

| Check | Result | Meaning |
|---|---|---|
| `unit_filename` | `helper.bolt` | The unit names **one** contributor, the first. Reading it for every command is the trap. |
| command 0 | `pos=49 line=3 col=5` | Written by `helper.bolt`, which is what the unit says. |
| commands 1 and 2 | `pos=58 line=4 col=5`, `pos=80 line=5 col=5` | Written by `main.bolt`. `helper.bolt` has only three lines, so trusting the unit maps them past its end. |
| `owners` per command | exactly **1** each, correct each time | Checking `pos`, `lineno` and `colno` against each candidate source resolves the file. |

**The mechanism**: the three fields of a `SourceLocation` are mutually redundant, so a source that did not produce the node has to agree on the offset *and* on the line *and* on the column to be a false positive. `sits_at` in [ws/probe.py](./ws/probe.py) is the whole check.

Zero candidates or several is a real possibility on a large project, and the answer there is an unmapped line. FR-010 makes that a validity condition rather than a quality target.

## Two ordering facts the run also settled

- **The emitter must be listed before `mecha` and work after its `yield`.** Listed after, the `Module` compilation units are purged from `mc.database` by the time it runs, and their sources are exactly what the check needs. This is the opposite of `stewbeet.plugins.sniffer.emit`'s placement rule.
- **`mecha.contrib.source_map` is not a source map.** It prepends a `# [source_map] <filename>` header comment and nothing else. Requiring it expecting line mappings gets a comment.

## Running it

```bash
cd ws
BOLT_PROBE_OUT=../result.json python -m beet -p beet.json build
```

Needs `bolt` and `mecha` importable, both of which come with StewBeet. Nothing else, and it writes nothing outside this folder.
