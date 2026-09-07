
# stewbeet.plugins.spyglass

The `spyglass` plugin keeps [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server)<br>
from underlining source files it was never able to read.

A `.mcfunction` holding bolt, or mecha's `function ./name:` nesting, is not vanilla mcfunction.
Spyglass parses it as commands, fails on the first `for` or the first trailing colon, and reports most of the file as an error.
Nothing can clear another extension's diagnostics, but Spyglass skips whatever its own `env.exclude` names, and your build is the one thing that knows exactly which files belong on that list.

**Required**: Nothing. It is off unless you ask for it.<br>
**Position**: One entry in `pipeline`, anywhere after `mecha`.<br>
**Source Code**: [`stewbeet/plugins/spyglass/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/spyglass/__init__.py) <br>

## What it does

- Finds the `.mcfunction` sources no vanilla parser can read, from what the build actually compiled
- Adds them to `env.exclude` in your project's Spyglass config, creating `.spyglassrc.json` if you have none
- Takes an entry back when a file stops using bolt, so nothing stays excluded once it can be read
- Never touches a pattern you wrote yourself, and never touches any other key in the file

## Configuration

```yaml
pipeline:
    - "mecha"
    - "stewbeet.plugins.spyglass"
```

The first build that finds something to exclude asks you in the terminal, once, and remembers the answer in `.beet_cache`.
Answer up front instead, and no question is ever asked:

```yaml
meta:
    stewbeet:
        spyglass:
            manage_exclusions: true
```

**A build with no terminal writes nothing.**
A CI job, a watch loop or an editor-driven build has nobody to ask, and committing a config change its author never agreed to is worse than a squiggle.
Those builds print the reason and move on, until somebody answers or the `meta` key does.

## How a file is chosen

Two signals, both read off the build rather than matched against the text:

- **bolt generated Python for the file.** A plain function compiled while bolt is loaded generates none, so this says the file used bolt, not that bolt was available.
- **mecha split the file into more than one function.** That is `function ./name:` nesting, which is not vanilla syntax twice over: the line opening a body ends in a colon, and `./name` is not a resource location.

A vanilla `.mcfunction` matches neither and keeps everything Spyglass gives it.

## The editor writes the same file

The [StewBeet extension](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) offers the same exclusion for the file you are opening, which is what a project that has never been built still needs.
Both write `env.exclude`, in the same file, in the same formatting, and both only ever add, so running one does not undo the other.
The difference is what they know: the editor reads the text and infers, the build knows.
