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

**Loading what a build wrote (step C2)**: a language server publishes diagnostics only for documents it has been handed, so the relay had nothing to relay until the author opened a generated file themselves. A `**/*.mcfunction` watcher now collects the files a build touches and calls `vscode.workspace.openTextDocument` on them, which loads a document without showing it. The batching is what keeps this usable on a real pack:

- Writes are debounced by 400 ms, so one rebuild produces one pass rather than one per file.
- At most 150 documents are opened per pass, and the remainder waits for the next one. A pack with two thousand functions refreshes more slowly; it never blocks the window.
- Nothing is opened at all while `StewBeet.sourceMapDiagnostics` is off.

## CodeLens (step C2)

Registered on `{ language: 'python' }`. One lens sits on the first line of each block that produced a function in the current build, titled with the resource location it produced and invoking `stewbeet.goToGenerated` with that target as an argument.

A block with no generated counterpart gets **no lens at all**, rather than one reporting that there is nothing to open, so a project with no build looks exactly as it did before. Lenses refresh when a map is written or deleted.

## Commands

All three are shipped in 1.2.0 and depend on the source maps a build emits. Without a build they report on the status bar that the line has no recorded origin rather than doing nothing silently.

| Command | Step | Title | Behaviour |
|---|---|---|---|
| `stewbeet.goToGenerated` | **C, shipped** | StewBeet: Go to Generated Function | From a Python position inside a block, open the generated `.mcfunction` at the mapped line. The inverse of ctrl+click. Accepts an optional `{ file, line }` argument, which is how the CodeLens skips the cursor lookup. |
| `stewbeet.goToSource` | **C, shipped** | StewBeet: Go to Python Source | From a generated `.mcfunction` position, open the Python source at the mapped line. |
| `stewbeet.reloadSourceMaps` | **C, shipped** | StewBeet: Reload Source Maps | Drop the decoded map cache. An escape hatch when a build finishes outside the watcher's view. |

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

## Backwards compatibility

The existing grammar injection, block decorations and their four `StewBeet.*` settings are untouched. A user who installs this version and nothing else sees exactly what they see today.
