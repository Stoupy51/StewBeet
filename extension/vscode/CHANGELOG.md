# Changelog

## 2.1.0

### The links follow your edits

- **A lens, a diagnostic and a resolved path stay on the line they belong to while you edit around them.** A map records the line a command was written on when the build ran, and everything built on it pointed there until the next build: delete three lines above a `write_function` and its lens, its errors and its interpolations sat three lines too low. Each source file's lines are now followed from the edits VS Code reports.
- **A line moved keeps what it had.** Alt+up on a call reports one edit replacing two lines with the same two, swapped, which no arithmetic on line numbers can follow, so the lines are recognised by their own text. Re-indenting a block into a branch is followed for the same reason.
- **A line deleted loses its link rather than passing it on.** Nothing slides onto the neighbour underneath, and a call whose line has been emptied gets no lens at all.
- **A build puts everything back where the map says.** What was saved is what the build read, so an unsaved edit keeps its offset and a rebuild of a file you had already saved forgets it entirely.

### Completion, diagnostics and ctrl+click inside a bolt file

- **A `.bolt` file asks Spyglass through a projection**, the same way a Python string does: the command lines are kept and dedented, everything Python around them is blanked, and what reaches the server is a document that reads as a plain `.mcfunction` whose lines are in lockstep with the source. That is what a bolt file loses by not being `mcfunction`, given back.
- **Its commands are checked as you type**, through the same relay that reports on a Python block. A bolt file needs no build to be told that `playound` is not a command.
- **A word one letter from a command is read as that command.** `playound` and `sya` match no rule mecha has, so a strict classifier leaves them coloured as Python and nothing ever says they are wrong. A word further away than one edit is left alone, since `raw`, `append`, `damage_type` and a project's own macros all open a line and none of them is a typo.
- **Ctrl+click crosses two boundaries at once.** A resource location in a bolt command leads to the generated function, and the map from there leads to whatever wrote it, in whichever dialect.
- **A path your Python computes is resolved from the build.** `function gui.open` reaches Spyglass as the path the last build wrote there, which is what makes it clickable and what keeps it from being reported as a function nobody defined.
- **A Python line offers nothing at all.** Forwarding from a `for` loop would answer it with every command in the game, so a position is only forwarded from a line the grammar reads as a command.
- **The classifier is the grammar's own.** Both regexes are read out of the bolt grammar this extension ships, so a line coloured as a command is a line projected as one, and regenerating the grammar from mecha's command tree updates both.
- **The Python a command carries is masked**, so the rest of the line still parses: `execute if predicate has_item(self.item) run function ns:x` keeps its `run function ns:x`.
- **A file is served as one document per run of commands**, not one for the whole file, so a keystroke costs the parser the run it lands in rather than every command in the module.

### Changed

- **A lens with several targets offers them by name** rather than in the references peek, which stayed open over the file it had just opened.
- **beet's list of commands is read as commands.** `Function(["say a", "say b"])` holds two blocks, and so do `.lines.append(...)` and `.lines.extend([...])` onto a function already in the pack. A `Function` has no `extend` of its own, so nothing claims one: colouring an `AttributeError` as a command list would be worse than leaving it plain.

- **One line of `beet.yml` instead of two.** `stewbeet.plugins.sniffer` in `require` now maps what mecha compiled as well, from its own teardown: beet unwinds `require` last, so mecha has compiled and its compilation units are still there to read. `stewbeet.plugins.sniffer.mecha` stays for a bolt or mecha project with no StewBeet in it, and a project listing both is unaffected.

### Fixed

- **A relative `StewBeet.buildOutput` finds the build.** `"build"` was handed to `vscode.RelativePattern`, which reads a bare string as an absolute path, so it searched `<drive>:/build`, found no maps, and every lens, jump and resolved interpolation went quiet with nothing anywhere saying why. A relative value is now a workspace-relative glob, and a setting that still finds nothing falls back to searching the workspace.
- **A bolt `.mcfunction` in a StewBeet project is mapped again.** The sniffer's capture read the text of every file as the pack loaded it, and beet drops a file's `source_path` the moment it is deserialised, which is what mecha names a compilation unit after. Every bolt file under `data/<ns>/function/` came out unmapped whenever `stewbeet.plugins.sniffer` and `mecha` ran in the same build, so the extension had nothing to navigate them with. Fixed in the `stewbeet` package after 3.6.5, not in the extension.

## 2.0.0

Everything since 1.0.6, the last published version.
1.0.6 coloured the mcfunction strings in your `write_*` calls and drew a box around them.
This one makes them code: checked as you type, navigable in both directions, and joined to the datapack your build produces.

### Language features inside the blocks

- **Completion, hover, signature help and go to definition**, answered by [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server) rather than reimplemented here. Each block is projected into a virtual `.mcfunction` document whose offsets match the Python buffer exactly, so every range that comes back applies unchanged.
- **Interpolations are resolved rather than masked.** `function {ns}:utils/loop` is read as the path it really is: ctrl+click lands on the call that wrote it, and completion after `{ns}:` offers your own function paths. The value comes off the line the last build produced, so nothing evaluates your Python. A line no build covers keeps a `_` mask, and `StewBeet.resolveInterpolations` turns the substitution off.
- **Spyglass is still optional, and no longer silently missing.** The extension offers to install it once, on the first Python file holding blocks, when it is absent. Everything else works without it.

### Errors on your own lines

- **A mistake inside a block is reported as you type**, with no build, and with nothing under `build/` ever opened. The diagnostics come from the projection, whose lines are in lockstep with your Python.
- **Errors reported against generated files reach Python too**, for the files you open yourself, and are remembered per file so a rebuild cannot take them away. When the same mistake arrives from both sides the projection's wins: it knows which columns are wrong, where a generated file knows only the line.
- **A masked interpolation raises nothing**, and a real typo on the same line still does. Suppression depends on where a diagnostic points rather than on what it overlaps.
- **`undeclaredSymbol` is not relayed by default.** It fires on every objective a dependency declares, which Spyglass cannot see, and a false error on a Python line is far more intrusive than the same one in a generated file. `StewBeet.diagnosticRuleDenylist` decides.

### Crossing to the datapack and back

- **Go to definition** on a resource location lands on the `write_function` call that produced it, and **find references** lists every call site writing to it.
- **A clickable lens above each block**, naming the function it produced, and one on a generated file leading back to the Python. One lens per call, not one per command.
- **Every target, not just the first.** A `write_function` in a loop writes one function per iteration, and a generated function assembled from several places has several origins. Both open the peek list VS Code uses for references, and the lens says how many there are.
- **A declaration links too.** `Block(id=...)` writes no commands of its own, and the functions a plugin generates on its behalf map straight back to it.
- **Header comments in a generated file are clickable.** `#> ns:name` leads to the source that wrote it, `@within` to the caller.

### What counts as a block

- **Commands handed over in a variable**, which is 14% of a real project: `content = f"""..."""` and every `+=` onto that name, up to the call that consumes it. A name reused further down the file leads to the function it actually feeds, not to the first call.
- **A list of commands**, whether built by `append`, by `+=`, as a literal, or by a comprehension, and whether handed over bare or as `"\n".join(lines)`. The separator of a join is a separator, not a command.
- **Your own functions.** Annotate a parameter `McFunction` and the strings passed to it are blocks, wherever the `def` sits.
- **beet's own API.** `ctx.data.functions[path] = Function(...)` in all three spellings, `.append(...)` onto one, and `.obj.append(...)` on a StewBeet resource.
- **Colours follow the same shapes** once a variable or list carries the `McFunction` annotation, which is how a grammar is told that a string reaches a call it cannot see. `McFunction` is `str`, exported from `stewbeet`, so annotating changes nothing at runtime. A raw string, a single-line command and a doubled brace in an f-string are all read correctly.

### bolt

- **`.bolt` files open as code.** Nothing else on the marketplace registers that extension, so a bolt project's source files opened as plain text. They get a language id, highlighting and comment toggling. The command names are generated from mecha's own command tree rather than typed, so they cannot drift from what mecha accepts.
- **A `.mcfunction` holding bolt is not read as a broken vanilla file.** It is detected and given the `bolt` language id, so it is highlighted as what it is. Generated files are never switched.
- **And Spyglass can be told to skip it.** Changing a language id does not stop Spyglass indexing a data pack off disk, and no extension can clear another's diagnostics, so **StewBeet: Exclude Bolt Files From Spyglass** writes the file into your project's own `.spyglassrc.json`. Your build can keep that list instead: `stewbeet.plugins.spyglass` in the pipeline finds those files from what bolt and mecha actually compiled, asks once in the terminal, and retracts an entry when a file stops needing it.
- **A bolt source links to what it generated, and back**, the same as a Python one.

### Source maps

- **All of the above that needs a build reads `.mcfunction.map` sidecars**, emitted by `stewbeet.plugins.sniffer` in your `require`. That is the whole configuration: the archive plugin writes them before it zips, so the build directory and the zip carry the same thing.
- **The map is the function's sibling and the function is untouched.** No `## sourceMappingURL=` comment is written: it could only ever name the file next to it, at the cost of a line in everything you ship.
- **bolt and mecha projects get the same maps**, read off the compiled AST, with real columns. The extension consumes them without knowing which dialect produced them.
- **A mapping never points inside a library.** A line whose author cannot be narrowed to one of your own files is left unmapped rather than pointed at a plausible wrong one.

### Speed

- Looking up what a line generated no longer walks every mapped line in the project, and the two hottest reads no longer make a filesystem call each. Reading the origins of a generated file went from 83 to under 1 microsecond, and a full lens pass over a 141-file project takes 0.7 ms.
- A diagnostics pass costs one round trip rather than one per block, and only the blocks whose text moved are woken. A request that never comes back can no longer freeze the relay.

### Settings and commands

| Setting | Default | |
|---|---|---|
| `StewBeet.languageFeatures` | `true` | Completion, hover, signature help and go to definition inside the blocks |
| `StewBeet.suggestSpyglass` | `true` | Offer the Spyglass install once, when it is missing |
| `StewBeet.buildOutput` | `""` | Where the generated pack is. Empty searches the workspace for maps |
| `StewBeet.sourceMapDiagnostics` | `true` | Relay build errors onto the Python that wrote the command |
| `StewBeet.resolveInterpolations` | `true` | Fill each `{...}` with what the last build resolved it to |
| `StewBeet.diagnosticRuleDenylist` | `["undeclaredSymbol"]` | Rules never relayed onto Python |
| `StewBeet.codeLens` | `true` | The link above a block that produced a function |
| `StewBeet.headerLinks` | `true` | Resource locations in a generated file's `#>` header |
| `StewBeet.boltInMcfunction` | `true` | Give a `.mcfunction` holding bolt the `bolt` language id |

Commands: **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.
The relay traces what it does to the **StewBeet** output channel, so a quiet relay can be told from a clean file.

## 1.0.6

Syntax highlighting and block decorations for mcfunction strings in StewBeet `write_*` calls.
