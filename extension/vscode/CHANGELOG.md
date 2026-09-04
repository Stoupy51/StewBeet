# Changelog

## 1.4.0

Errors now reach your Python as you type, with no build and no generated file opened. Blocks passed to `write_*` in a variable are finally seen.

- **Diagnostics come from the projection, not the build.** Spyglass reports on the virtual documents the extension already keeps open for completion, and their lines are in lockstep with your Python, so an error comes home with no source map involved. It appears as you type rather than after a rebuild, and nothing under `build/` is ever opened.
- **Commands passed in a variable count as blocks.** `content: str = f"""..."""` followed by `write_function(path, content)` gets highlighting, the block box and completion, and so does a later `content += """..."""`. That was 14% of a real project going unseen.
- **The string quotes no longer raise errors.** The projection handed `"""` to a datapack parser, which correctly replied that it is not a command. Only the commands are projected now.
- **The `#>` header links to your Python** instead of to the file you are already reading.
- New command **StewBeet: Show Diagnostics Status**, and the relay traces what it does to the **StewBeet** output channel.

A block written in a variable still gets no interpolation substitution: the source map records the `write_function` call, and the text sits somewhere else entirely. Highlighting, completion and literal paths all work; `{ns}` stays masked there.

## 1.3.2

The column translation was not reaching the requests at all, which is why completion landed a few characters to the left and accepting one could eat text.

- **Accepting a completion no longer damages the line.** `matches ` plus the suggestion `matches` produced `matchesmatches`, because the replace range came back in the resolved text's columns and was applied to your file untranslated.
- **Completion asks at the right place.** After `scoreboard players ` it offered `objectives` and `players`, the choices for the word before, because the position was sent seven columns early, the difference between `{ns}` and `simplenergy`.
- **Ctrl+click underlines the right characters**, for the same reason.
- The projection and the request path now share one cached result per document version, so they cannot disagree about a column again.
- **Header comments in generated files are clickable.** The function names after `@within`, and the one on the `#>` line, lead to the function they name.
- **A lens above a generated file's header** leads back to the Python that wrote it, the reverse of the lens in your Python files.
- New setting `StewBeet.headerLinks`, and a new command **StewBeet: Refresh Build Diagnostics**.
- The relay now logs what it does to the **StewBeet** output channel, so a quiet relay can be diagnosed.

## 1.3.1

Fixes for what the first run of 1.3.0 on a real pack exposed. Three of the four were mine.

- **The editor is responsive again.** A build writes one source map per function, and each one was throwing away every cache, searching the workspace for maps again, reprojecting every open block and recomputing every link. On a 270-function pack that ran a hundred times for a single build. It now runs once.
- **Only the functions your open Python files produced are loaded** for diagnostics, instead of every function in the pack.
- **Diagnostics survive a rebuild.** VS Code disposes a document nothing is looking at and the language server drops its diagnostics with it, so squiggles appeared and vanished. What the server reported is now remembered per file.
- **`undeclaredSymbol` is actually silenced.** The denylist matched the diagnostic's `code`, which Spyglass leaves empty; it names the rule at the end of the message instead. Both are read now.
- **Ctrl+click underlines the right characters.** The highlight range came back in the resolved text's columns, so `{ns}.data` underlined `{ns}.data matche`, which is what `simplenergy.data` is wide.

## 1.3.0

Everything 1.2.0 added worked, and almost nothing reached it: StewBeet code writes `function {ns}:utils/loop`, not a literal path, and an interpolation is Python that Spyglass cannot read. Each one is now filled in with what the last build resolved it to, so the whole feature set applies to the code you actually write.

- **Interpolated resource locations** resolve. Ctrl+click on `function {ns}:utils/loop` lands on the `write_function` call that wrote it, and completion after `{ns}:` offers your own function paths. Nothing evaluates your Python: the value is read off the line the build produced.
- **Diagnostics refresh on a rebuild** without opening anything in the build output. The generated files a build touched are handed to the language server as they are written, in debounced batches so a full rebuild slows down instead of freezing.
- **`undeclaredSymbol` is no longer relayed** by default. It fires on every scoreboard objective a dependency declares, which Spyglass cannot see, and a false error on a Python line is far more intrusive than the same one in a generated file.
- **A clickable link above each block** that produced a function, naming it, so Go to Generated Function is one click rather than a palette search.
- New settings: `StewBeet.resolveInterpolations`, `StewBeet.diagnosticRuleDenylist`, `StewBeet.codeLens`.
- `StewBeet.buildOutput` left empty now searches the whole workspace for `.mcfunction.map` files rather than only under a `build` directory, so output that lives elsewhere is found.

A line the current build does not cover keeps the `_` mask it had in 1.2.0, and so does a line whose surrounding text no longer matches what was built. Substitution can be turned off entirely with `"StewBeet.resolveInterpolations": false`.

## 1.2.0

Navigation and diagnostics now cross the boundary between your Python and the datapack it generates, using the `.mcfunction.map` sidecars a build emits.

- **Go to definition** on a resource location lands on the `write_function` call that produced it, instead of on the generated `.mcfunction`. When a function was assembled from several places, a custom block's declaration plus your own append, the peek list offers all of them.
- **Find references** on a generated resource location lists every Python call site that writes to it.
- **Diagnostics** reported against generated files are mirrored onto the Python line that wrote the command, sourced `stewbeet (spyglassmc)`.
- New commands: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**.
- New settings: `StewBeet.buildOutput` (where the generated pack is, empty to autodetect) and `StewBeet.sourceMapDiagnostics`.

All of it needs a build in the workspace, produced with `stewbeet.plugins.sniffer` in the pipeline. Without one there are no maps, definition falls back to the generated file exactly as in 1.1.0, and nothing else changes.

## 1.1.0

Language features inside mcfunction strings, provided by [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server) rather than reimplemented here.

- **Completion** inside `write_*` string blocks, including the resource locations your own pack defines.
- **Hover** and **signature help** in the same blocks.
- **Go to definition** on a resource location, landing on the generated `.mcfunction` it refers to. Jumping back to the `write_function` call needs source maps and is not implemented yet.
- New setting `StewBeet.languageFeatures` (default `true`) to turn all of the above off.

Each block is projected into a virtual `.mcfunction` document whose offsets match the Python buffer exactly, so requests forward to Spyglass and every returned range applies unchanged. Spyglass stays optional: without it, highlighting and decorations behave exactly as in 1.0.6.

## 1.0.6

Syntax highlighting and block decorations for mcfunction strings in StewBeet `write_*` calls.
