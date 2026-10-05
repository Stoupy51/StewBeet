
# stewbeet.plugins.spyglass

The `spyglass` plugin keeps [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server)<br>
from underlining source files it was never able to read.

A `.mcfunction` holding bolt, mecha's `function ./name:` nesting or a command a plugin added to mecha is not vanilla mcfunction.
Spyglass parses it as commands, fails on the first `for` or the first trailing colon, and reports most of the file as an error.
Nothing can clear another extension's diagnostics, but Spyglass skips whatever its own `env.exclude` names, and your build is the one thing that knows exactly which files belong on that list.

**Required**: Nothing. It is off unless you ask for it.<br>
**Position**: One entry in `pipeline`, anywhere in it.<br>
**Source Code**: [`stewbeet/plugins/spyglass/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/spyglass/__init__.py) <br>

## What it does

- Finds the `.mcfunction` sources no vanilla parser can read, from what the build actually compiled
- Adds them to `env.exclude` in your project's Spyglass config, creating `.spyglassrc.json` if you have none
- Takes an entry back when a file stops using bolt, so nothing stays excluded once it can be read
- Declares the functions only an excluded file defines, in a `spyglass_declarations` pack beside the build output: an excluded file declares nothing, and a versioning refactor leaves the name your sources call absent from the build too
- Never touches a pattern you wrote yourself, and never touches any other key in the file

## Configuration

```yaml
pipeline:
    - "stewbeet.plugins.spyglass"
```

It reads mecha's compilation database, which is empty until mecha compiles, so it queues its own work for the very end of the build.
Order does not matter: listing it before `mecha`, after it, or in a project where another plugin requires mecha from Python all give the same result.

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

Four signals, all read off the build rather than matched against the text:

- **bolt generated Python for the file.** A plain function compiled while bolt is loaded generates none, so this says the file used bolt, not that bolt was available.
- **mecha split the file into more than one function.** That is `function ./name:` nesting, which is not vanilla syntax twice over: the line opening a body ends in a colon, and `./name` is not a resource location.
- **One of its commands spans several lines**, which mecha's `multiline` mode and bolt's brackets allow and vanilla does not.
- **One of its commands is one a plugin added to mecha**, such as bolt_compute's `compute bolt`, found by comparing each command with the vanilla command tree mecha ships for your Minecraft version.

A vanilla `.mcfunction` matches none and keeps everything Spyglass gives it.

## The editor writes the same file

The [StewBeet extension](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) offers the same exclusion, which is what a project without this plugin still needs.
Both write `env.exclude`, in the same file, in the same formatting, and both only ever add, so running one does not undo the other.
The editor names every file the last build compiled as bolt, read from its [sniffer](sniffer.md) maps, and before any build it infers from the text of the files you open.

