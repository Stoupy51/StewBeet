# stewbeet.plugins.sniffer

The `sniffer` plugin records where every generated line came from, and writes a<br>
[Source Map v3](https://tc39.es/ecma426/) `.mcfunction.map` sidecar next to each generated function.<br>
An editor or a debugger reading one of those maps can jump from a command in the built datapack<br>
straight to the `write_function` call in your Python that produced it.

The format is the same one JavaScript tooling has used for a decade, so it is readable by anything<br>
that already speaks source maps, including [Sniffer](https://github.com/mcbookshelf/sniffer),<br>
the Minecraft debugger the plugin is named after.

### <u>What it looks like</u>

**The Python that wrote the command, the command, and the sidecar that links them**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/sniffer.source_map.jpg">

**Required**: Nothing. It is off unless you ask for it.<br>
**Position**: One entry in `require`, one in `pipeline`. See below.<br>
**Source Code**: [`stewbeet/plugins/sniffer/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/sniffer/__init__.py) <br>
**Source Code**: [`stewbeet/plugins/sniffer/emit.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/sniffer/emit.py) <br>


## What it does

- Records every `write_function`, `write_versioned_function`, `.obj.append(...)` and friends, in call order
- Resolves each write back to the line and column of the Python that made it
- Realigns the recorded lines against the final text, so post-processing like `auto.headers` does not shift the mapping
- Writes one `<name>.mcfunction.map` per function, plus a `## sourceMappingURL=` comment as the function's last line
- Maps content a plugin generated from one of your declarations back to that `Block(...)` or `Item(...)` call
- Never names a file inside StewBeet, beet, bolt, mecha or stouputils: a mapping points at your own source or at nothing

## Configuration

There is nothing to configure. There are two entries, and they go in different sections:

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"          # starts recording

pipeline:
    - "src.setup_definitions"
    - "..."
    - "src.link"
    - "stewbeet.plugins.auto.headers"
    - "stewbeet.plugins.sniffer.emit"     # writes the maps
    - "stewbeet.plugins.archive"
```

`stewbeet.plugins.sniffer` goes in `require`, next to `stewbeet` itself. Everything in `require` runs
before the pack is even loaded, so nothing can write a function before recording starts. Its position
within `require` does not matter. Recording the pack's own hand-written `.mcfunction` files as they
load costs nothing: they have no Python behind them, so they get no map and no comment.

`stewbeet.plugins.sniffer.emit` must come **after** every plugin that writes or rewrites functions,
and **before** `stewbeet.plugins.archive`. The archive is the zip that ends up in
`saves/<world>/datapacks`, so a map written after it was zipped is a map the game never loads.
Forget this entry and the maps are still written, at the very end of the build, with a warning
telling you what missed them.

## What you get

A generated function ends with its discovery comment:

```mcfunction
say Starting root
function tns:helper/do_work
## sourceMappingURL=root.mcfunction.map
```

And the sidecar next to it names your own source, relative to the project root:

```json
{
	"version": 3,
	"file": "root.mcfunction",
	"sourceRoot": "../../../../..",
	"sources": ["src/link.py"],
	"names": [],
	"mappings": "AAKA;AACA;AACA"
}
```

`sourcesContent` is deliberately absent. Consumers read your sources from disk through `sourceRoot`,
and inlining a whole project into every map would cost tens of megabytes.

## What is mapped, and what is not

A command you wrote yourself maps to the line you wrote it on. A command a plugin generated from one
of your declarations maps to the declaration, not to the plugin: ctrl+clicking inside a custom
block's `place_main` leads to your `Block(...)` call.

Scoped so far: `datapack.custom_blocks`, and the parts of `custom_recipes` that write a function per
item (smithed, furnace, pulverizer, awakened forge). Everything else a plugin generates on its own
account stays unmapped, which is the designed behaviour rather than a failure: an unmapped line costs
you nothing, a line pointing at the wrong place costs you a wasted search.

Two more things stay unmapped by design:

- **Pack-level scaffolding.** `custom_blocks/get_rotation` and friends are written once for the whole
  pack and belong to no declaration, so they are attributed to none.
- **Definitions with no Python declaration**, loaded from JSON or coming from `external_definitions`.
  There is no call to point at.

## Shipping a release

The maps are only in your build because you asked for them. A release build that does not ask for them
produces exactly the same datapack it always did, byte for byte, with no maps and no
`sourceMappingURL` comments.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): the calls this plugin records.
- [All plugins](README.md): the rest of the pipeline, in the order it runs.
- [Configuring the build](../3_beet_config/en.md): enabling, ordering and configuring plugins.
