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

Run `node --test` in `extension/vscode/` to confirm `virtual.test.js` asserts that projecting a block preserves every offset.

## Phase B: source maps are emitted and correct

Add the plugin to the project's `beet.yaml` pipeline, then build:

```yaml
pipeline:
  - stewbeet.plugins.source_maps
```

```sh
beet build
```

| Check | Expected |
|---|---|
| `ls build/*/data/*/function/**/*.mcfunction.map` | One map per generated function |
| `python -c "import json;print(json.load(open(<a map>))['version'])"` | `3` |
| Decode a map with `@jridgewell/trace-mapping` | Generated line 0 of a headered function is unmapped, the first command line maps into the author's `.py` |
| Open the mapped Python line | It is a line inside the `write_function` string that produced the command |
| Build without the plugin | No `.map` files, and build time within noise of the previous run |

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

Run the contract fixtures: `pytest python_package/tests/test_source_maps.py`. Three fixtures carry the weight: `headered/` proves `difflib` alignment survives `auto.headers`, `declared/` proves a custom block's generated lines reach the declaration, and `editable_install/` proves the library exclusion is independent of the project root.

## Phase B2: attribution reaches the declaration

Declare a custom block with an `on_place` body, and separately append to its `place_secondary`:

```python
Block(id="my_block", base_block="minecraft:furnace", on_place="say placed")
write_function("mynamespace:block/my_block/place_secondary", "say appended")
```

| Check | Expected |
|---|---|
| Decode `place_secondary`'s map | Two sources, both in the project |
| The line generated from `on_place` | Maps to the `Block(...)` declaration, or to the `on_place=` argument if the scope names the field |
| The `say appended` line | Maps to the developer's own `write_function` |
| Lines emitted by `custom_blocks` with no declaration behind them | Unmapped, not pointing at `custom_blocks/__init__.py` |
| Rewrite the append as `overwrite=True` and rebuild | One source only, the developer's call |

## Phase C: navigation and diagnostics

With phase B's build present:

| Step | Expected |
|---|---|
| Ctrl+click `test:demo` inside a command string | Cursor lands on the `write_function("test:demo", ...)` call |
| Ctrl+click a path built from an f-string | Same, because the map resolves it |
| Ctrl+click a custom block's `place_secondary` | Peek list with both the `Block(...)` declaration and the developer's append |
| Shift+F12 on a generated resource location | Every Python call site that generates a call to it |
| Break a command, rebuild | A red squiggle on the Python line inside the string, sourced `stewbeet (spyglassmc)` |
| Fix it, rebuild | The squiggle clears |
| Delete `build/` | Navigation stops, completion from phase A keeps working |

## Phase D: Sniffer interop

Not owned by this feature, but the acceptance test for SC-002:

1. Build with the plugin, launch Minecraft with Sniffer, attach from VS Code.
2. Set a breakpoint on a Python line inside a `write_function` string.
3. Run the function in game.

**Expected**: execution halts on the corresponding command. If Sniffer has not implemented map consumption yet, verify instead that setting the breakpoint on the generated `.mcfunction` line named by the map halts correctly, which is the same assertion one indirection away.

## Success criteria mapping

| Criterion | Validated by |
|---|---|
| SC-001 completion and ctrl+click | Phase A and Phase C tables |
| SC-002 Sniffer needs no StewBeet code | Phase D |
| SC-003 no mcfunction syntax knowledge added | `grep -rn "execute\|@a\|scoreboard" python_package/stewbeet/plugins/source_maps extension/vscode/src` returns nothing outside test fixtures |
