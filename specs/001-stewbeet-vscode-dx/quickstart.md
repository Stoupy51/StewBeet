# Phase 1: Validation Guide

How to prove each phase works. Every scenario is runnable against a real StewBeet project.

## Prerequisites

- VS Code 1.74+, with `SPGoding.datapack-language-server` (Spyglass) and `MinecraftCommands.syntax-mcfunction` installed.
- A StewBeet project that builds, for example [SimplEnergy](file:///d:/advanced_desktop/SimplEnergy).
- Python 3.14+ and the local `stewbeet` package installed in editable mode.
- The extension loaded from source: open `extension/vscode/` in VS Code and press F5.

## Spike first: does Spyglass see a virtual document?

Everything in phase A rests on open question Q2. Settle it before writing providers.

The runnable script, the pass criteria and the three-step escalation for a failure are in [contracts/spyglass-integration.md](./contracts/spyglass-integration.md) Part 5. Keep the spike afterwards as a regression test: it is the one thing that detects a future Spyglass release adding a scheme filter to its document selector.

## Phase A: completion and hover inside a block

```python
write_function("test:demo", """
execute as @a run say hi
""")
```

| Step | Expected |
|---|---|
| Put the caret after `execute as @a run ` and trigger suggest | Vanilla command completions appear |
| Type `function te` | Resource locations from the project's built datapack appear |
| Hover `@a` | Spyglass's selector hover appears |
| Put the caret on `write_function` itself and trigger suggest | Normal Python completions, no mcfunction items |
| Uninstall Spyglass and repeat | No completions, no errors in the extension host log |
| Open a workspace with **no built datapack** and repeat the first row | Vanilla command completions still appear (FR-008). Only the project's own resource locations are missing, because those come from the build |

Run `npm test` in `extension/vscode/` to confirm `test/projection.test.js` asserts that projecting a block preserves every offset. Then run `npm run test:integration` for the end-to-end pass against the real Spyglass; see [test/integration/README.md](../../extension/vscode/test/integration/README.md).

## Phase B: source maps are emitted and correct

Add the plugin's two entries to the project's `beet.yaml`, then build:

```yaml
require:
  - stewbeet
  - stewbeet.plugins.sniffer        # runs before the pack is even loaded

pipeline:
  - ...
  - stewbeet.plugins.auto.headers
  - stewbeet.plugins.sniffer.emit   # after every writer, before the archive
  - stewbeet.plugins.archive
```

```sh
beet build
```

| Check | Expected |
|---|---|
| `ls build/*/data/*/function/**/*.mcfunction.map` | One map per generated function |
| `python -c "import json;print(json.load(open(<a map>))['version'])"` | `3` |
| Decode a map with `@jridgewell/trace-mapping` | Generated line 0 of a headered function is unmapped, the first command line maps into the author's `.py` |
| `tail -1` any generated function | `## sourceMappingURL=<name>.mcfunction.map`, two hashes, and no mapping group for it |
| Check `sourceRoot` on a nested function | Deeper than a top-level one, since it is relative to the map's own directory |
| Open the mapped Python line | It is a line inside the `write_function` string that produced the command |
| Build without the plugin | No `.map` files, and build time within noise of the previous run |
| `unzip -l build/*_datapack.zip \| grep '\.map'` | The maps are in the zip too, since that zip is what reaches `saves/<world>/datapacks` |
| Drop `stewbeet.plugins.sniffer.emit` and rebuild | Maps still written, plus a warning that the archive did not get them |

**The check that matters most.** No map may point into a library:

```sh
python - <<'PY'
import json, pathlib
bad = [str(p) for p in pathlib.Path("build").rglob("*.mcfunction.map")
       for s in json.loads(p.read_text())["sources"]
       if "site-packages" in s or "/stewbeet/" in s.replace("\\", "/")]
print("LEAKED:", bad) if bad else print("clean")
PY
```

**Expected**: `clean`. Run it again with StewBeet installed editable from inside the project root, which is the case that a naive project-root check passes and must not.

**Conformance against someone else's encoder.** Before trusting our own fixtures, point the decoder at Sniffer's reference implementation and check it reproduces Appendix A of the source map contract:

```sh
pytest python_package/tests/test_sniffer.py -k reference
```

It decodes `specs/001-stewbeet-vscode-dx/contracts/reference/**/*.map` and asserts every segment resolves to the expected source line. Two segments there are worth the whole test: `AAAA` in `hit`, where one source statement expands to two commands, and `ACHA` in `aura`, where a segment moves to a different source and three lines backwards in the same step. A hand-rolled VLQ encoder that gets file-wide deltas wrong passes every fixture we write ourselves and fails this.

Then the rest: `headered/` proves `difflib` alignment survives `auto.headers`, `declared/` proves a custom block's generated lines reach the declaration, and `editable_install/` proves the library exclusion is independent of the project root.

## Phase B2: attribution reaches the declaration

Declare a custom block, then extend its `place_secondary` the modern way, from a plugin ordered after `stewbeet.plugins.datapack.custom_blocks`:

```python
# blocks.py, the declaration
Block(id="my_block", vanilla_block=VanillaBlock(id="minecraft:furnace"))

# my_plugin.py, running after custom_blocks
Block.from_id("my_block").functions.place_secondary.obj.append("say appended")
```

`Block.from_id` returns the declared instance itself rather than rebuilding one, so the origin
captured at declaration survives the round trip. A definition loaded from JSON instead of declared
in Python has no declaration site at all, so its generated content stays unmapped.

| Check | Expected |
|---|---|
| Decode `place_secondary`'s map | Two sources, both in the project |
| The `say appended` line | Maps to the `.obj.append(` line in `my_plugin.py`, resolved by tier 1 |
| Lines `custom_blocks` synthesised from the declaration | Map to the `Block(...)` call in `blocks.py`, resolved by tier 2 |
| Lines `custom_blocks` emitted from nothing declarable | Unmapped, and in particular never pointing at `custom_blocks/__init__.py` |
| Any line at all | Never points at the project's `main()` entry point |

The last two rows are the ones that catch a broken tier order.

The `say appended` row is also what covers the capture point itself, since `.obj.append` bypasses `write_function` entirely and reaches beet directly. That line is mapped only because `beet.Function.append` is patched, so the assertion fails on its own if the patch ever stops being installed. No manual experiment needed.

## Phase C: navigation and diagnostics

With phase B's build present:

| Step | Expected |
|---|---|
| Ctrl+click `test:demo` inside a command string | Cursor lands on the `write_function("test:demo", ...)` call |
| Ctrl+click a path built from an f-string | Same, because the map resolves it |
| Ctrl+click an **interpolated** path (`function {ns}:utils/loop`) | Lands on the `write_function` call, the same as a literal one. The interpolation is filled in with what the build resolved it to before Spyglass sees the line |
| Completion after `{ns}:` | Offers the pack's own function paths |
| Ctrl+click a custom block's `place_secondary` | Peek list with both the `Block(...)` declaration and the developer's append |
| Shift+F12 on a generated resource location | Every Python call site that generates a call to it |
| Break a command | A red squiggle on the Python line inside the string, as you type. No rebuild, and nothing under `build/` opened |
| Fix it | The squiggle clears, again without a rebuild |
| Open a generated `.mcfunction` yourself | Its own diagnostics relay onto the Python too, sourced `stewbeet (spyglassmc)`. This is the one path that reads a build's output |
| A block that produced a function | Carries a lens above it naming the function, one click to open it |
| `"StewBeet.resolveInterpolations": false` | Interpolations go back to `_`, and ctrl+click on one stops resolving. Everything else keeps working |
| Delete `build/` | Navigation stops, completion from phase A keeps working |

### What a real run establishes

Run against SimplEnergy with the sniffer plugin in the pipeline:

| Check | Result |
|---|---|
| Ctrl+click a **literal** resource location | Works, lands on the `write_function` call |
| Ctrl+click an **interpolated** one (`function {ns}:...`) | Works. FR-018 |
| Shift+F12 | Works |
| `Go to Generated Function`, then `Go to Python Source` | Both work, and land on the matching line: `execute store result score #height simplenergy.data ...` in the generated file returns to `execute store result score #height {ns}.data ...` in `machines.py` |
| Diagnostics | Appear as you type, with no build at all and no generated file open. FR-019 |
| Relayed diagnostic quality | `undeclaredSymbol` is not relayed, so an objective a dependency declares raises nothing on the Python. Real errors still arrive. FR-020 |
| Navigation without the palette | A lens above each block that produced a function. FR-021 |
| Deleting the build | Navigation stops, completion keeps working |

## Sniffer interop (validates SC-002, part of step B)

Not owned by this feature, and deliberately unlettered: step D is the `bolt` language id, not this. See [contracts/dialects.md](./contracts/dialects.md) for the canonical sequencing.

1. Build with the plugin, launch Minecraft with Sniffer, attach from VS Code.
2. Set a breakpoint on a Python line inside a `write_function` string.
3. Run the function in game.

**Expected**: execution halts on the corresponding command. If Sniffer has not implemented map consumption yet, verify instead that setting the breakpoint on the generated `.mcfunction` line named by the map halts correctly, which is the same assertion one indirection away.

## Success criteria mapping

| Criterion | Validated by |
|---|---|
| SC-001 completion and ctrl+click | Phase A table (completion) and Phase C table (ctrl+click to the authoring line) |
| SC-002 Sniffer needs no StewBeet code | The Sniffer interop section above |
| SC-003 no mcfunction syntax knowledge added | The grep below |

### SC-003: no mcfunction syntax was reimplemented

```sh
grep -rnE '@[aeprs]\[|\bscoreboard players\b|\bexecute (as|at|if|store)\b' \
  python_package/stewbeet/plugins/sniffer extension/vscode/src \
  | grep -vE ':\s*(//|#|\*)'
```

**Expected**: no matches.

Anchor on mcfunction-specific token shapes rather than bare words. A pattern matching plain `execute` produces a false positive on `vscode.execute*`, which is a VS Code API name and not a Minecraft command. Test fixtures are excluded by construction because the paths listed are source directories only.

**Comment lines are excluded, and that exclusion is the point of the check.** A command quoted in a doc comment is an example of what the code is handed, not knowledge of what it means. `projection.js` quotes `execute store reslt score #height {ns}.data` to explain which column a diagnostic lands on, and rewording it to satisfy a grep would make the comment worse. What SC-003 forbids is a grammar, a command tree or registry data in executable code, which is what the filtered grep tests for.
