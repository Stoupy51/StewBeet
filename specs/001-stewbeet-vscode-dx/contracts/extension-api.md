# Contract: VS Code extension surface

What the StewBeet extension registers, and what it expects from its neighbours.

The mechanism behind the forwarded providers, the Spyglass facts they rely on, the spike that gates them and the fallbacks are all in [spyglass-integration.md](./spyglass-integration.md). This file is the surface only.

## Virtual document scheme

**Scheme**: `stewbeet-mcfunction`

**URI shape**: path `/<block index>/<python basename>.mcfunction`, with the originating document's URI carried in the **query**.

The originating URI goes in the query rather than in a path segment because VS Code decodes percent escapes in a path, which would corrupt an encoded `file:///d:/...` embedded there. The trailing `.mcfunction` is load-bearing: it is what makes VS Code assign the document language id `mcfunction`, which is what makes Spyglass's document selector match.

**Content rule**: the virtual document is the full Python buffer with every character outside the target block replaced by a space, newlines preserved, and every f-string interpolation span replaced by what the last build resolved it to, or by a same-length run of `_` when that is unknown.

**Coordinate rule**: lines stay in lockstep, columns do not.

- One Python line is always one virtual line, so a line number means the same thing on both sides and the line-granular source maps keep working.
- A line's columns may differ, because `{ns}` is four characters and `simplenergy` is eleven. `project()` returns a per-line table of the spans whose width changed, and every position going out to Spyglass and every range coming back passes through `toVirtual` or `toPython`. A line absent from that table has identical columns on both sides, which is every line of a project with no build.
- A position inside a substituted span translates to the span's start. There is no character-level correspondence inside one.
- A range overlapping a substituted span has no honest Python equivalent and is **dropped**, never guessed at. This matters only for the edits a completion item carries, which are applied to the author's own buffer.
- Spyglass sees a file of blank lines with one command block in it, which parses cleanly.
- Exactly one block is exposed per virtual document, so completions never leak between blocks.

**Substitution rule**: a value is recovered by anchoring, never by evaluating Python. The literal text before a span and the literal text after it must both be found where they belong in the line the build wrote, and what sits between them is the value. Leading and trailing whitespace is ignored on both sides, since a build may strip a line's indentation. Any mismatch, which is what a stale build looks like, falls back to the mask for that line. A span crossing a line boundary is never substituted, since replacing it would move a newline.

**Registered as**: `vscode.workspace.registerTextDocumentContentProvider`, with an `onDidChange` event fired when the underlying Python document changes.

## Forwarded requests

Registered on `{ language: 'python' }`, each provider first asks `blocks.js` whether the position is inside a block and returns `undefined` if not.

| Provider | Forwards to | Notes |
|---|---|---|
| `CompletionItemProvider` | `vscode.executeCompletionItemProvider` | Trigger characters are Spyglass's own eleven for mcfunction: `' '`, `'['`, `'='`, `'!'`, `','`, `'{'`, `':'`, `'/'`, `'.'`, `'"'`, `"'"`. Pass an `itemResolveCount` or items arrive without documentation. Every `range`, `textEdit` and `additionalTextEdits` is translated back to Python columns, or dropped when it overlaps a substituted span; VS Code then falls back to the word under the cursor, which it computes from the Python document. One dropped entry drops the whole `additionalTextEdits` set, since a partial application is worse than none. |
| `HoverProvider` | `vscode.executeHoverProvider` | The hover range is translated back to Python columns. |
| `SignatureHelpProvider` | `vscode.executeSignatureHelpProvider` | |
| `DefinitionProvider` | `vscode.executeDefinitionProvider`, then the source map | Phase C intercepts Spyglass's answer (the generated `.mcfunction`) and rewrites the target to the Python origins. Spyglass answers with `Location`, not `LocationLink`, confirmed by the integration run and recorded as `us3_answerShape`; both shapes are handled since the API guarantees neither. Returns `Location[]`, one per distinct source in the target's map, ordered by generated line, so a function assembled from a declaration and a developer append opens the peek list with both. Falls back to the generated file when the map has no sources. |
| `ReferenceProvider` | `vscode.executeReferenceProvider`, then the source map | Every generated hit is rewritten to its Python origin. Hits with no origin are returned as generated locations. |

**Contract with Spyglass**: none, beyond it registering providers for language id `mcfunction` without a scheme restriction. Verified true today. If a future Spyglass release restricts the scheme, the fallback is to spawn a private `@spyglassmc/language-server` process (see research.md, Option A risks).

**Failure mode**: if no provider answers, every forwarded request resolves to `undefined` and the editor behaves exactly as it does today. Nothing throws, nothing is logged at error level.

## Diagnostic relay (step C, shipped)

**Collection name**: `stewbeet`

Subscribes to `vscode.languages.onDidChangeDiagnostics`. For each changed URI that is a generated `.mcfunction` with a sibling map, every diagnostic is rewritten:

- Target line comes from the map.
- Target range is the full Python line, since the map does not carry column precision (see the source map contract's non-guarantees).
- `source` becomes `stewbeet (<original source>)` so the origin stays visible.
- Diagnostics on unmapped generated lines are dropped.
- Diagnostics whose rule is in `StewBeet.diagnosticRuleDenylist` are dropped. The rule is the diagnostic's `code`, which arrives as a string, a number or `{ value, target }` depending on the server.

Diagnostics are grouped per Python file and replaced wholesale on each change, so stale entries cannot accumulate.

**Where diagnostics come from (FR-019)**: a language server publishes only for documents it has been handed, and opening one is not asking. The relay therefore reads Spyglass's answers on the **virtual documents it already serves for completion**. Their lines are in lockstep with the Python, so an error comes home with no build, no source map, and nothing under the build output ever opened. It appears as the author types.

A generated `.mcfunction` the author opens themselves still relays through the source map, which is the only path carrying a build's own output. Where both describe the same mistake the projection's wins, because it knows which columns are wrong and the generated file knows only which line.

The pass is shaped by four numbers, in `src/diagnostics.js` and `src/virtual.js`:

- **120 ms debounce** on the reaction, since the server reports on a document in bursts as it parses it.
- **One wake per changed block**, batched into a single round trip. Blocks whose text did not move are not woken, so typing in one block does not pay for every other block in the file.
- **3 s per wake, 20 s per pass.** A request that never comes back leaves the pass marked running, and every later pass then returns immediately with the squiggles frozen where they were.
- **30 s keepalive.** VS Code lets go of a document nothing is showing once enough have been opened, and the server stops reporting on it with no event to say so, so the blocks are asked again on a timer.

Nothing runs at all while `StewBeet.sourceMapDiagnostics` is off.

**Diagnostics about a mask are dropped.** An interpolation the build cannot resolve becomes a run of `_`, and a parser that has swallowed one is lost for the rest of the line. Suppression keys on where a diagnostic **points**, not on what it overlaps, so a typo earlier on a masked line is still reported while the placeholder stays quiet. Everything the parser says past the mask on that line goes with it: a real mistake sitting after a placeholder goes unreported, which is the better trade.

**Rule extraction**: the denylist matches `code` when the server sets it, and otherwise the `(rule: X)` suffix Spyglass writes at the end of the message. Spyglass leaves `code` empty, so matching only on `code` silences nothing.

**Invalidation cost (step C2)**: dropping the build-derived state clears the decode caches, re-runs the workspace map search, reprojects every served virtual document and recomputes every lens. A build writes one map per function, so this is debounced by 600 ms; doing it per event ran all of that 117 times for one build and was the single largest source of editor lag.

## CodeLens (step C2)

Registered on `{ language: 'python' }`. One lens sits on the first line of each block that produced a function in the current build, titled with the resource location it produced and invoking `stewbeet.goToGenerated` with that target as an argument.

A block with no generated counterpart gets **no lens at all**, rather than one reporting that there is nothing to open, so a project with no build looks exactly as it did before. Lenses refresh when a map is written or deleted.

## Grammar: what is highlighted as mcfunction (FR-022, FR-023)

Three mechanisms, all in the injection grammar, all matching one place at a time:

- **A string handed straight to a `write_*` call.** Twelve rules, one per function group and quote style.
- **A variable annotated `McFunction`**, plus every `+=` onto that same name. The rule opens at `name: McFunction =` and closes at the first line that is neither an append to that name nor blank, its `end` backreferencing the name captured by its `begin`. Nothing else can carry the annotation across lines: a grammar has no variable bindings, so the author states the intent and the rule's own extent does the rest.
- **A list annotated `list[McFunction]`**, its literal entries and every `append` onto that name. Its `end` also holds the run open across `if`, `elif`, `else`, `for`, `while`, `try`, `except`, `finally`, `with`, `match` and `case`, because the appends a declaration collects are routinely wrapped in a branch. An `append` onto any other name closes it.

**A spanning rule must hand its lines back to Python.** While a begin/end rule is open, only its own patterns apply, so the two rules above would strip Python's colours from every line between a declaration and its appends. Both therefore end their `patterns` with `{"include": "source.python"}`, both carry the scope `meta.mcfunction-span.stewbeet`, and the grammar's `injectionSelector` is `L:source.python -meta.mcfunction-span.stewbeet`. The exclusion is load-bearing: without it the included Python re-triggers this injection inside itself and the tokenizer overflows its stack.

`McFunction` is `str`, exported from `stewbeet`, so annotating changes nothing at runtime. Block detection in `blocks.js` never needed it and still does not: an unannotated variable keeps its decorations, completion and diagnostics, and gains only the colours when annotated.

**A project's own functions are found by `blocks.js`, not by the grammar.** A `def` whose parameter is annotated `McFunction` makes that argument of every call to it a block, so `write("ns:x", "say hi")` gets the block box, completion and diagnostics. `self` and `cls` are discounted so the call site's argument index lines up. This cannot be done in the grammar: a `def` and a call to it share no text, and a rule that matched any call would colour every Python string. Colour therefore stops at the variable annotation; everything else the extension does reaches these calls.

**Inline and block content are tokenized by different entry points.** `#root` for a block, `#root-inline` for a string whose content starts mid-line. They differ in one rule: a `say` block ends at a quote closing the line when inline, because that quote closes the Python string, and must not when in a block, because `say something "quoted"` is an ordinary line that happens to end in a quote. Commands are recognised at `^` or at `\G`, the latter being where an inline embed starts; without it the first word of an inline string falls through to the generic name rule and is not read as a command.

## Languages: the `bolt` id and grammar (FR-016, step D)

The extension contributes **one language**, `bolt`, claiming `.bolt` with `bolt-language-configuration.json`. It contributes **no `mcfunction` language**: FR-015 partitions ownership by file, and Spyglass owns that id.

| Contribution | Value |
|---|---|
| `languages[0].id` | `bolt` |
| `languages[0].extensions` | `[".bolt"]` |
| `grammars[2].scopeName` | `source.bolt` |
| `grammars[2].language` | `bolt` |
| `activationEvents` | **unchanged**. A grammar needs no activation, and no provider selects a bolt document |

`source.bolt` is Python first: its `patterns` are `#module-import`, `#nesting-statement`, `#command-statement`, then `source.python` last. Python must come last, or it claims every line before a command rule is tried.

- **`#command-statement`** matches a line whose first token is a root command literal, and hands the line to `source.mcfunction.embedded#root`, the grammar this extension already ships. Its `begin` is a zero-width lookahead so the embedded grammar still sees `^`, which is what lets its own `say` rule treat the message as a message.
- **The literal set is generated from mecha**, 91 of the 92 roots of `Mecha.spec.tree.children`. The regeneration command is recorded in the rule's `comment`, and `grammar.test.js` asserts the count and the absence of `return`. `return` is dropped because it is Python's keyword first.
- **A head is only a command when what follows is not Python.** The rule carries a negative lookahead for `=`, every augmented assignment, `.`, `(`, `[`, `,` and an annotation `:`, so `item = 3` and `list(x)` stay Python while `item modify entity @s ...` is a command. A trailing `:` stays allowed, since that is bolt's nesting form.
- **`#nesting-statement`** owns `function`, `append function`, `prepend function` and `merge function`, offering a resource location first and falling through to Python, because the argument is a computed expression as often as a literal path.
- **`#python-call`** rescues a call inside a command argument: nothing in mcfunction puts a bare `(` after a word, so `has_item_predicate(self.item.d())` keeps Python's colours. It also ends at the line end, so an unbalanced parenthesis costs one line rather than the rest of the file.

**Verified against a real corpus**: all 141 `.bolt` files in shulker, 9075 lines, with no runaway scope. The long single-scope runs that do appear are a 45-line dict literal, blocks of consecutive commands, and the multi-line JSON body of an `advancement` command, which recovers when its braces balance.

**Out of scope for step D**: a `.mcfunction` file containing bolt syntax. That file keeps language id `mcfunction` and belongs to Spyglass, which cannot parse it. See [dialects.md](./dialects.md).

## Header links in generated files (step C2)

Not asked for by any requirement, and kept because it is the cheap half of navigation nobody had built. StewBeet's generated headers name the function they belong to and, after `@within`, the functions that call it, but they sit in `#` comments where Spyglass sees prose and offers nothing.

Registered on `{ language: 'mcfunction', scheme: 'file' }`:

- A `DocumentLinkProvider` turns every resource location in a header comment into a link to the file it names. A location naming no real file, and prose that merely contains a colon, stay plain text. The link covers the resource location alone, not the whole comment.
- A `CodeLensProvider` puts one lens above the header, leading back to the Python that wrote the function. It is the mirror of the lens in Python files: from a block you reach what it produced, and from what was produced you reach the block.

Both are off when `StewBeet.headerLinks` is `false`. `src/headers.js` holds the scanning, keeps no `vscode` import at module scope, and is unit-tested in `test/headers.test.js`.

## Commands

The first three depend on the source maps a build emits, and without one they report on the status bar that the line has no recorded origin rather than doing nothing silently. The last two are relay controls and need no build.

| Command | Step | Title | Behaviour |
|---|---|---|---|
| `stewbeet.goToGenerated` | **C, shipped** | StewBeet: Go to Generated Function | From a Python position inside a block, open the generated `.mcfunction` at the mapped line. The inverse of ctrl+click. Accepts an optional `{ file, line }` argument, which is how the CodeLens skips the cursor lookup. |
| `stewbeet.goToSource` | **C, shipped** | StewBeet: Go to Python Source | From a generated `.mcfunction` position, open the Python source at the mapped line. |
| `stewbeet.reloadSourceMaps` | **C, shipped** | StewBeet: Reload Source Maps | Drop the decoded map cache. An escape hatch when a build finishes outside the watcher's view. |
| `stewbeet.refreshDiagnostics` | **C2, shipped** | StewBeet: Refresh Build Diagnostics | Force a relay pass now instead of waiting for the keepalive. |
| `stewbeet.diagnosticsStatus` | **C2, shipped** | StewBeet: Show Diagnostics Status | Report what the relay has captured, published and passed over, so a quiet relay can be told apart from a clean file. |

## Settings

Added to the existing `StewBeet.*` configuration block:

| Setting | Step | Type | Default | Meaning |
|---|---|---|---|---|
| `StewBeet.languageFeatures` | **A, shipped** | `boolean` | `true` | Master switch for the forwarded providers. |
| `StewBeet.buildOutput` | **C, shipped** | `string` | `""` | Glob or path to the generated datapack root. Empty searches the whole workspace for `.mcfunction.map` files, since a pack's output does not have to sit under `build`. |
| `StewBeet.sourceMapDiagnostics` | **C, shipped** | `boolean` | `true` | Whether to relay generated-file diagnostics onto Python. |
| `StewBeet.resolveInterpolations` | **C2, shipped** | `boolean` | `true` | Whether to fill each interpolation with what the last build resolved it to. Off restores step A's masking exactly, which is the escape hatch for a project the anchoring cannot handle. |
| `StewBeet.diagnosticRuleDenylist` | **C2, shipped** | `string[]` | `["undeclaredSymbol"]` | Rules never relayed onto Python. Empty relays everything. |
| `StewBeet.codeLens` | **C2, shipped** | `boolean` | `true` | Whether to show the link above a block that produced a function. |
| `StewBeet.headerLinks` | **C2, shipped** | `boolean` | `true` | Whether resource locations in a generated file's `#>` header comments become links. |

## Backwards compatibility

The existing grammar injection, block decorations and their four `StewBeet.*` settings are untouched. A user who installs this version and nothing else sees exactly what they see today.
