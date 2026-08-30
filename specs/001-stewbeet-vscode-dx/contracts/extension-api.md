# Contract: VS Code extension surface

What the StewBeet extension registers, and what it expects from its neighbours.

The mechanism behind the forwarded providers, the Spyglass facts they rely on, the spike that gates them and the fallbacks are all in [spyglass-integration.md](./spyglass-integration.md). This file is the surface only.

## Virtual document scheme

**Scheme**: `stewbeet-mcfunction`

**URI shape**: `stewbeet-mcfunction://<encoded original uri>/<basename>.mcfunction`

The trailing `.mcfunction` is what makes VS Code assign the document language id `mcfunction`, which is what makes Spyglass's document selector match it. The rest of the path is opaque.

**Content rule**: the virtual document is the full Python buffer with every character outside the target block replaced by a space, newlines preserved. Consequences:

- Line and column of any position are identical in both documents. No translation table, no off-by-one.
- Spyglass sees a file of blank lines with one command block in it, which parses cleanly.
- Exactly one block is exposed per virtual document, so completions never leak between blocks.

**Registered as**: `vscode.workspace.registerTextDocumentContentProvider`, with an `onDidChange` event fired when the underlying Python document changes.

## Forwarded requests

Registered on `{ language: 'python' }`, each provider first asks `blocks.js` whether the position is inside a block and returns `undefined` if not.

| Provider | Forwards to | Notes |
|---|---|---|
| `CompletionItemProvider` | `vscode.executeCompletionItemProvider` | Trigger characters are Spyglass's own eleven for mcfunction: `' '`, `'['`, `'='`, `'!'`, `','`, `'{'`, `':'`, `'/'`, `'.'`, `'"'`, `"'"`. Pass an `itemResolveCount` or items arrive without documentation. Results are returned as-is; `additionalTextEdits` and `textEdit` ranges are already in matching coordinates. |
| `HoverProvider` | `vscode.executeHoverProvider` | Ranges pass through unchanged. |
| `SignatureHelpProvider` | `vscode.executeSignatureHelpProvider` | |
| `DefinitionProvider` | `vscode.executeDefinitionProvider`, then the source map | Phase A returns Spyglass's answer (the generated `.mcfunction`). Phase C intercepts it and rewrites the target to the Python origins. Returns `Location[]`, one per distinct source in the target's map, ordered by generated line, so a function assembled from a declaration and a developer append opens the peek list with both. Falls back to the generated file when the map has no sources. |
| `ReferenceProvider` | `vscode.executeReferenceProvider`, then the source map | Every generated hit is rewritten to its Python origin. Hits with no origin are returned as generated locations. |

**Contract with Spyglass**: none, beyond it registering providers for language id `mcfunction` without a scheme restriction. Verified true today. If a future Spyglass release restricts the scheme, the fallback is to spawn a private `@spyglassmc/language-server` process (see research.md, Option A risks).

**Failure mode**: if no provider answers, every forwarded request resolves to `undefined` and the editor behaves exactly as it does today. Nothing throws, nothing is logged at error level.

## Diagnostic relay

**Collection name**: `stewbeet`

Subscribes to `vscode.languages.onDidChangeDiagnostics`. For each changed URI that is a generated `.mcfunction` with a sibling map, every diagnostic is rewritten:

- Target line comes from the map.
- Target range is the full Python line, since the map does not carry column precision (see the source map contract's non-guarantees).
- `source` becomes `stewbeet (<original source>)` so the origin stays visible.
- Diagnostics on unmapped generated lines are dropped.

Diagnostics are grouped per Python file and replaced wholesale on each change, so stale entries cannot accumulate.

## Commands

| Command | Title | Behaviour |
|---|---|---|
| `stewbeet.goToGenerated` | StewBeet: Go to Generated Function | From a Python position inside a block, open the generated `.mcfunction` at the mapped line. The inverse of ctrl+click. |
| `stewbeet.goToSource` | StewBeet: Go to Python Source | From a generated `.mcfunction` position, open the Python source at the mapped line. |
| `stewbeet.reloadSourceMaps` | StewBeet: Reload Source Maps | Drop the decoded map cache. An escape hatch when a build finishes outside the watcher's view. |

## Settings

Added to the existing `StewBeet.*` configuration block:

| Setting | Type | Default | Meaning |
|---|---|---|---|
| `StewBeet.languageFeatures` | `boolean` | `true` | Master switch for the forwarded providers. |
| `StewBeet.buildOutput` | `string` | `""` | Glob or path to the generated datapack root. Empty means autodetect by searching the workspace for `pack.mcmeta` under a `build` directory. |
| `StewBeet.sourceMapDiagnostics` | `boolean` | `true` | Whether to relay generated-file diagnostics onto Python. |

## Backwards compatibility

The existing grammar injection, block decorations and their four `StewBeet.*` settings are untouched. A user who installs this version and nothing else sees exactly what they see today.
