# Changelog

## 1.7.0

- **`.bolt` files open as code.** Nothing else on the marketplace registers that extension, so a bolt project's 141 source files opened as plain text: no language id, no highlighting, no comment toggling. They now get all three. Bolt is Python with commands interleaved, so Python is the ground and commands are the exception, and a word that is both a command and an identifier is only a command when what follows it is not Python.
- **Resource locations in bolt imports are coloured** rather than reported as a syntax error by Python's grammar, which is the most visible thing that was wrong with reading a bolt file.
- The command names come from mecha's own command tree, generated rather than typed, so they cannot drift from what mecha accepts.

## 1.6.2

- **Python is coloured again around an `McFunction` variable or list.** The rule that carries the annotation to a `+=` or an `append` stays open across the lines between them, and while it is open only its own patterns apply, so `if`, `else`, ordinary strings and the declaration itself all lost their colours. Those lines now fall through to Python's own grammar, and the injection excludes its own scope so that cannot recurse.

## 1.6.1

Commands written into a variable are coloured, and commands written on one line are coloured properly for the first time.

- **Annotate a variable `McFunction` and its commands are coloured.** `content: McFunction = f"""..."""` highlights like a string passed straight to `write_function`. A grammar matches one place at a time and cannot tell that `content` reaches a call further down, so you say so instead. `McFunction` is `str` and is exported from `stewbeet`, so annotating changes nothing about how the value behaves.
- **Every `+=` onto that name is coloured too**, up to the first statement that is not one, so a function built by appending is highlighted throughout rather than only in its first block. A `+=` onto a different name is left alone.
- **A `list[McFunction]` is coloured too**, both the entries of a list literal and every `append` onto the name, including appends sitting inside an `if` or a `for`. An `append` onto a different name ends the run and is left alone.
- **Your own functions are recognised.** Annotate a parameter `McFunction` and the strings passed to it get the block box, completion and errors, wherever the `def` sits in the file. Colours still need the annotation on a variable, because a grammar cannot connect a call to a `def` elsewhere.
- **A command written on a single line is now read as a command.** `write_function("ns:x", "say hi")` coloured `say` as a plain word, because the rules that recognise a command anchored to the start of a line and an inline string starts in the middle of one. That was true of every single-line string this extension has ever highlighted.
- The tests now run the real TextMate engine over the real Python grammar, which is what found both of the above. They skip, rather than pass, where that engine or a VS Code install is missing.

## 1.5.1

1.5.0 made the errors arrive. This makes them keep arriving, and cuts the noise they arrived with.

- **A stuck request can no longer freeze the relay.** Waking a block is a round trip to the language server, and one that never came back left the pass marked as running forever, so every later pass returned immediately and the squiggles stopped where they were. Each wake now gives up after 3 seconds, and a pass that overruns 20 seconds is treated as lost.
- **A pass costs one round trip instead of seventeen.** The blocks were woken one after another. They are now woken together, and only the ones whose text actually moved, so typing inside one block no longer pays for every other block in the file.
- **Far fewer errors about nothing.** A parser that has swallowed a `____` placeholder is lost for the rest of the line, and everything it says past that point describes a line nobody wrote. Those are dropped now, where before only the ones pointing straight at the placeholder were. A real mistake sitting after a placeholder on the same line goes unreported, which is the better trade.
- The output channel says how long each pass took, so "it feels slow" has a number.

## 1.5.0

Errors reached the Python file only by luck. The path that was supposed to deliver them was racing, and a rebuild killed it outright.

- **An error in a block is reported without opening anything.** A language server only looks at a document something has asked it about, and opening one is not asking. The blocks were opened and never asked, so whether a mistake was reported came down to whether the author happened to trigger completion in that exact block. Each block is now woken with one hover before its diagnostics are read.
- **A rebuild no longer switches diagnostics off.** VS Code lets go of documents nothing is showing once enough have been opened, and loading a rebuild's generated functions, forty at a time, was enough to evict every block in the file. The server then stopped reporting on them with no event to say so, and nothing ever recovered: the only way back was closing and reopening the Python file. Generated functions are no longer loaded at all, which is also what made the editor slow.
- **The relay does not spin.** Waking a document makes the server publish, and publishing is what asks for the next pass. Waking on every pass ran seven passes a second with nobody typing. A pass wakes when the Python changed and reads when the server has something to say, with a wake every 30 seconds so an eviction cannot go unnoticed.
- **The precise error wins.** When the same mistake arrives both from a generated file and from the projection, the projection's is kept: it knows which columns are wrong, and the generated file knows only which line.

Diagnostics from generated files still reach Python, for the files the author opens themselves.

## 1.4.3

- **A real mistake is reported again on a line that carries a `{...}`.** 1.4.1 suppressed every diagnostic that overlapped a masked interpolation, which was too broad: a typo like `execute store reslt score #height {ns}.data` produces an error running from the typo to the end of the line, so it crossed the mask and was thrown away with it. Suppression now depends on where the diagnostic **points**, not on what it overlaps, so the placeholder stays quiet and the typo does not.

## 1.4.2

- **One link per `write_*` call, not one per command.** Reading the source map alone put a link on every line of a function, because the map records an origin for each generated line. Blocks now say which call they feed, so the link lands on the call whether the commands sit inside it or arrive in a variable above it.

## 1.4.1

- **No more errors about the mask.** An interpolation the build cannot resolve becomes a run of `_`, and a parser told that `scoreboard players add @s obj ______` is missing an integer is right about the placeholder and says nothing about your code. Every diagnostic landing on a mask is now dropped, so `{energy["generation"]}` stops carrying a permanent red line.
- **Errors appear roughly four times sooner**, the wait before asking cut from 500 ms to 120 ms. What is left is Spyglass's own parsing time, which is not ours to shorten.
- **The link sits on the `write_function` call**, wherever the commands were written. It followed the string before, so a block built in a variable put the link above the assignment instead of above the call.

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
