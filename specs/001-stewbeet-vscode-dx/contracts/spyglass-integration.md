# Contract: Spyglass integration

**This is the priority deliverable.** It closes both halves of issue #41 and needs no build, no source map and no Sniffer.

Everything needed to implement this is in this file. It does not assume the Spyglass repository is available.

## Part 1: Spyglass facts sheet

Recorded from the Spyglass source at the time of writing, checkout `d:/advanced_desktop/Spyglass`. Re-verify before implementing if much time has passed.

### Identity

| Thing | Value |
|---|---|
| VS Code extension id | `SPGoding.datapack-language-server` |
| Marketplace name | Datapack Helper Plus |
| npm scope | `@spyglassmc/*` (`core`, `language-server`, `java-edition`, `mcfunction`, `json`, `nbt`, `mcdoc`, `locales`) |
| Standalone server | `npm install --global @spyglassmc/language-server` |
| Project config file | `spyglass.json` at the project root |
| Hard dependency | `MinecraftCommands.syntax-mcfunction`, which is what registers the `mcfunction` language id |
| Website | <https://spyglassmc.com/> |

### The client's document selector

`packages/vscode-extension/src/extension.mts`:

```ts
const documentSelector: lc.DocumentSelector = [
	{ language: 'mcfunction' },
	{ language: 'mcdoc' },
	{ language: 'snbt' },
	{ language: 'mcmeta' },
	{ language: 'json', pattern: '**/data/*/**/*.json' },
	{ language: 'json', pattern: '**/assets/*/**/*.json' },
]
```

**No `scheme` field on any entry.** This single fact is what makes the whole integration possible: `vscode-languageclient` matches a selector entry without a scheme against a document of *any* scheme, so a virtual document under our own scheme is synced to the Spyglass server exactly like a real file.

The client is started only when `vscode.workspace.workspaceFolders` is non-empty.

### Server capabilities advertised

`packages/language-server/src/server.ts`, around line 158:

```
codeActionProvider, colorProvider, completionProvider, declarationProvider,
definitionProvider, implementationProvider, referencesProvider, typeDefinitionProvider,
documentHighlightProvider, documentSymbolProvider, hoverProvider, inlayHintProvider,
semanticTokensProvider, signatureHelpProvider, workspaceSymbolProvider
```

Formatting is registered dynamically when the client advertises `textDocument.formatting.dynamicRegistration`.

`completionProvider.triggerCharacters` comes from `meta.getTriggerCharacters()`, the union over all registered languages. `signatureHelpProvider.triggerCharacters` is `[' ']`.

### The mcfunction language registration

`packages/java-edition/src/mcfunction/index.ts:46`:

```ts
meta.registerLanguage('mcfunction', {
	extensions: ['.mcfunction'],
	parser: mcf.entry(tree, parser.argument, mcfunctionOptions),
	completer: mcf.completer.entry(tree, completer.getMockNodes),
	triggerCharacters: [' ', '[', '=', '!', ',', '{', ':', '/', '.', '"', "'"],
})
```

Those eleven trigger characters are the exact set our forwarding provider must declare, or completion will not fire in the same places it fires in a real `.mcfunction` file.

`mcfunctionOptions` is version-gated: line continuation and macros from 1.20.2, a 2 MB command length cap from 1.20.5.

### Document intake

`packages/core/src/service/Project.ts:934`:

```ts
async onDidOpen(uri: string, languageID: string, version: number, content: string): Promise<void> {
	uri = this.normalizeUri(uri)
	if (uri.startsWith(ArchiveUriSupporter.Protocol)) {
		return // We do not accept `archive:` scheme for client-managed URIs.
	}
	if (this.shouldExclude(uri, languageID)) { return }
	const doc = TextDocument.create(uri, languageID, version, content)
	const node = this.parse(doc)
	this.#clientManagedUris.add(uri)
	this.#clientManagedDocAndNodes.set(uri, { doc, node })
	if (this.#isReady) {
		await this.bind(doc, node)
		await this.check(doc, node)
	}
}
```

Only `archive:` is rejected. Symbol resolution runs against `this.symbols`, which is **project-global rather than path-relative**, so a document that lives outside the project roots still completes against the project's full symbol table. That is why a virtual document can offer the real datapack's function paths.

### The extension points that exist, and the one that does not

`MetaRegistry` (`packages/core/src/service/MetaRegistry.ts`) is the real, documented extension surface:

```ts
export interface LanguageOptions {
	extensions: FileExtension[]        // must include the leading dot
	uriPredicate?: UriPredicate
	triggerCharacters?: string[]
	parser?: Parser<AstNode>
	completer?: Completer<any>
}

public registerLanguage(languageID: string, options: LanguageOptions): void
```

Plus `registerBinder`, `registerChecker`, `registerColorizer`, `registerCompleter`, `registerFormatter`, `registerLinter`, `registerParser`, `registerSymbolRegistrar`, `registerInlayHintProvider`, `registerSignatureHelpProvider`, `registerUriBinder`, `registerDependencyProvider`.

Registrations happen inside a `ProjectInitializer`, and **the set of initializers is hard-coded**:

- `packages/language-server/src/server.ts:114` -> `initializers: [mcdoc.initialize, je.initialize]`
- `packages/playground/src/index.ts:37` -> the same

`Config.env.plugins: string[]` exists (`packages/core/src/service/Config.ts:110`, defaulted to `[]` at line 354) and **is read by nothing in the repository**. The plugin API is advertised in the package description and in the config schema and does not exist. Verified by grepping the whole monorepo: the identifier appears exactly twice, both in `Config.ts`.

## Part 2: why StewBeet content is invisible today

Spyglass only ever sees documents whose language id is one of its five. A StewBeet author's commands live inside Python string literals in a `.py` file, language id `python`. The Spyglass client never syncs that document, the server never parses it, and no amount of Spyglass configuration changes that.

The current StewBeet extension colors those strings with a TextMate injection grammar (`syntaxes/mcfunction-injection.tmLanguage.json` injected into `source.python`) and draws a box around them. TextMate grammars are pure regex tokenisers with no semantic model, so they cannot produce completion, hover, navigation or diagnostics. That ceiling is why issue #41 exists.

What the extension already has and this feature reuses unchanged:

`extension/vscode/src/blocks.js` exports `findBlockOffsets(text)` returning `{ start, end }[]`, the offsets of every mcfunction string block in a Python document. `start` is the opening quote including any `f` or `r` prefix, `end` is just past the closing quote. It correctly handles triple-quoted strings, f-strings, nested interpolations containing their own strings, escapes, and the fact that `write_function` and `write_versioned_function` and `write_scheduled_function` take the content as the **second** argument while `write_load_file`, `write_unload_file` and `write_tick_file` take it as the **first**. It has no `vscode` import and is unit-tested by `test/blocks.test.js`.

## Part 3: the mechanism

**Request forwarding through virtual documents**, the technique VS Code documents at <https://code.visualstudio.com/api/language-extensions/embedded-languages> as one of the two supported approaches for embedded languages. The other, embedding a language service library in your own server, is rejected in [research.md](../research.md) Option B.

### The projection

For a Python document `D` and a target block `B`, the virtual document is **the entire text of `D` with every character outside `B` replaced by a space, newlines preserved**.

```python
write_function("test:demo", """
execute as @a run say hi
""")
```

becomes, in the virtual document:

```

execute as @a run say hi

```

with the first line's `write_function("test:demo", """` replaced by 32 spaces and the trailing `""")` replaced by 4.

This is the whole trick, and it earns its keep three times over:

1. **Offsets are identity.** Line `n` column `c` in the Python document is line `n` column `c` in the virtual document. No mapping table, no off-by-one, no translation on the way back. Every `Range` in every response, including `CompletionItem.textEdit` and `additionalTextEdits`, is already correct for the Python document.
2. **One block per virtual document.** Completions and symbols cannot leak between two blocks in the same file.
3. **Spyglass sees a valid file.** Blank lines are legal mcfunction, so the surrounding whitespace parses to nothing and the block parses normally.

### URI shape

```
stewbeet-mcfunction://<percent-encoded original uri>/<block index>/<basename>.mcfunction
```

The trailing `.mcfunction` is load-bearing: VS Code derives a document's language id from its path extension, the `MinecraftCommands.syntax-mcfunction` extension registers that extension as language id `mcfunction`, and that is what makes Spyglass's selector match. Everything before the basename is opaque and exists only to make the URI unique and reversible.

Registered with `vscode.workspace.registerTextDocumentContentProvider('stewbeet-mcfunction', provider)`. The provider fires `onDidChange` for a virtual URI whenever the underlying Python document changes, so Spyglass re-parses.

### F-string interpolation masking

`f"execute as @a run say {name}"` contains Python where mcfunction is expected. Left alone, Spyglass parses `{name}` as part of the command and may or may not accept it.

Mask it: replace each interpolation span, braces included, with a same-length run of `_`. So `{name}` becomes `______`. Length identity is preserved, which preserves offset identity, and `_` is a legal character in resource locations, selector values, scoreboard names, tags and objectives, so the masked token parses as a plausible word in most argument positions. It will not parse where a number is required. That is accepted.

`blocks.js` already contains `skipInterpolation(text, i)`, which walks an interpolation body handling nested brackets and nested strings. It needs one small addition: return the spans it skips rather than only the index past them, so the projection can mask them.

**Design rule that makes the imperfection harmless: diagnostics are never taken from the virtual document.** Only completion, hover, signature help, symbols and navigation are. A masked token that fails to parse costs a slightly worse completion list at that exact position and nothing else. Real diagnostics come from the built output, which contains the rendered string with the interpolation actually substituted, and are relocated onto Python through the source map. See [extension-api.md](./extension-api.md).

### Lifecycle

- Virtual documents are created lazily, on the first request that lands inside a block.
- Cache one virtual document per `(python uri, block index)`. Invalidate the cache entry on `onDidChangeTextDocument` for the underlying document, and fire `onDidChange` on the provider for the affected URIs.
- Close virtual documents for a Python document when it closes. VS Code garbage-collects unreferenced virtual documents, but Spyglass holds them in `#clientManagedDocAndNodes` until a `didClose` arrives.
- `await vscode.workspace.openTextDocument(virtualUri)` before every forwarded request. It is cheap when already open and it is what triggers the client's `didOpen`.

## Part 4: what to forward, and how

Every provider is registered on `{ language: 'python' }` and returns `undefined` immediately when the position is not inside a block, so Python tooling is never disturbed.

| Feature | Built-in command | Notes |
|---|---|---|
| Completion | `vscode.executeCompletionItemProvider` | Signature is `(uri, position, triggerCharacter?, itemResolveCount?)`. **Pass an `itemResolveCount`** (50 is reasonable) or items come back unresolved with no `documentation` and no `detail`, because VS Code will not call our provider's `resolveCompletionItem` for items we did not create. Declare the eleven mcfunction trigger characters listed in Part 1. |
| Hover | `vscode.executeHoverProvider` | Ranges pass through unchanged. |
| Signature help | `vscode.executeSignatureHelpProvider` | Trigger character is a space. |
| Definition | `vscode.executeDefinitionProvider` | Returns the generated `.mcfunction`. Useful on its own, and phase C rewrites the target to the Python origin. |
| References | `vscode.executeReferenceProvider` | Same. |
| Document symbols | `vscode.executeDocumentSymbolProvider` | Scoped to the one block, which is usually what you want in the outline. |
| Semantic tokens | `vscode.provideDocumentSemanticTokens` | Optional. The TextMate injection already colors these strings, so this is a refinement, not a requirement. Needs `vscode.provideDocumentSemanticTokensLegend` to decode. |
| Document highlight | `vscode.executeDocumentHighlights` | Cheap to add once the plumbing exists. |
| Diagnostics | none | **Deliberately not forwarded.** See the design rule above. |

### Sketch

```js
const provider = {
	async provideCompletionItems(doc, pos, token, context) {
		const virt = getVirtualUri(doc, pos);          // undefined when outside a block
		if (!virt) return undefined;
		await vscode.workspace.openTextDocument(virt);
		return vscode.commands.executeCommand(
			"vscode.executeCompletionItemProvider",
			virt, pos, context.triggerCharacter, 50,
		);
	},
};
vscode.languages.registerCompletionItemProvider(
	{ language: "python" }, provider,
	" ", "[", "=", "!", ",", "{", ":", "/", ".", '"', "'",
);
```

No position translation anywhere, because of the projection.

### Failure behaviour

If Spyglass is not installed, if it failed to start, or if the workspace has no folder so its client never launched, every forwarded command resolves to `undefined` or an empty array. The providers return that unchanged, the editor behaves exactly as it does today, and nothing is logged above debug level. Spyglass stays a soft dependency, never listed in `extensionDependencies`, per NFR-003.

## Part 5: the spike that gates everything

Open question Q2. **Do this before writing a single provider**, because a negative answer changes the shape of the whole phase.

The question is whether `vscode-languageclient` syncs a document that is opened programmatically but never shown in an editor. The client listens to `vscode.workspace.onDidOpenTextDocument` and forwards `didOpen` for documents matching its selector, and `workspace.openTextDocument(uri)` does fire that event, so the expected answer is yes. It is not worth assuming.

In the extension development host, with Spyglass installed and a datapack workspace open:

```js
// 1. a trivial content provider
vscode.workspace.registerTextDocumentContentProvider("stewbeet-mcfunction", {
	provideTextDocumentContent: () => "say hello",
	onDidChange: new vscode.EventEmitter().event,
});

// 2. open without showing
const uri = vscode.Uri.parse("stewbeet-mcfunction://x/0/probe.mcfunction");
const doc = await vscode.workspace.openTextDocument(uri);
console.log("languageId:", doc.languageId);           // expect "mcfunction"

// 3. ask for completions mid-command
const list = await vscode.commands.executeCommand(
	"vscode.executeCompletionItemProvider", uri, new vscode.Position(0, 4), undefined, 50);
console.log("items:", list?.items?.length);            // expect > 0
```

**Pass**: a non-empty list containing vanilla commands. Proceed.

**`languageId` is not `mcfunction`**: `MinecraftCommands.syntax-mcfunction` is missing. Install it and retry.

**Empty list**: escalate through these in order, and record which one worked in [research.md](../research.md).

1. Show the document in a preserved-focus preview editor, `vscode.window.showTextDocument(doc, { preserveFocus: true, preview: true })`, then retry. Confirms the client only syncs shown documents.
2. Check whether the workspace has a folder. Spyglass's `activate` returns early without starting the client when `workspaceFolders` is empty.
3. Fall back to Part 6.

## Part 6: fallback, a private language server

Only if the spike fails and cannot be worked around.

Depend on `@spyglassmc/language-server` directly, spawn it as a child process from the StewBeet extension, and drive it with `vscode-languageclient` over IPC, pointing its project root at the workspace. Then own the client end of the conversation and stop depending on the Spyglass extension's selector.

Cost: a second full Spyglass project in memory next to the user's own, with duplicate mcmeta downloads and a duplicate symbol table. Roughly 100 extra lines plus a real npm dependency and a bundling step. Do not do this preemptively.

## Part 7: the long-term shape, upstream

The correct end state, tracked as a stretch goal because its timeline is not ours. Two upstream PRs to Spyglass:

**PR 1: make `env.plugins` real.** Load each entry as a module and call its exported `initialize` as an additional `ProjectInitializer`, alongside the hard-coded `[mcdoc.initialize, je.initialize]`. The config field, its default and its documentation already exist, so this is wiring, not design.

**PR 2: make the VS Code client's document selector dynamic**, derived from the languages the server ends up with rather than a hard-coded array, so a plugin-registered language actually receives documents.

With both, StewBeet ships a small plugin and the virtual document machinery is deleted:

```ts
export const initialize: ProjectInitializer = (ctx) => {
	ctx.meta.registerLanguage('python', {
		extensions: ['.py'],
		// parse the Python file, emit an mcfunction sub-tree per write_* string block
		// at that block's real offsets, so every downstream processor works unchanged
		parser: stewbeetPythonParser,
		triggerCharacters: [' ', '[', '=', '!', ',', '{', ':', '/', '.', '"', "'"],
	})
}
```

One Spyglass instance, one symbol table, native offsets, and every feature including diagnostics and formatting works without special cases. It would also unlock Bolt and Mecha, which have the same problem, so it is plausibly welcome upstream rather than a favour being asked.

This is a stretch goal and **not a dependency**. Parts 3 and 4 deliver the same user-facing features now, and are deleted the day this lands.

## Part 8: risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Spyglass adds a `scheme` filter to its selector | Low. There is no reason to, and it would break nothing else. | Part 6. Detected instantly by the spike, which should be kept as a regression test. |
| The client only syncs shown documents | Medium. This is Q2. | Part 5 escalation, preserved-focus preview editor. |
| Completion items come back without documentation | High if `itemResolveCount` is forgotten | Pass it. Covered in Part 4. |
| Masked interpolations produce nonsense completions at that position | Certain, by construction | Accepted. Diagnostics are not taken from the virtual document, so the blast radius is one completion list. |
| Spyglass has no project context, so no function paths are offered | Low. Symbols are project-global, and the built datapack is normally in the workspace. | Document that `beet build` at least once makes generated paths completable. |
| Two Spyglass versions disagree about trigger characters | Low | Read them from Part 1 and re-verify on major Spyglass releases. |
