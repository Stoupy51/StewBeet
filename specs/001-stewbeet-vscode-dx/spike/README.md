# Q2 spike: does Spyglass answer on virtual documents?

**Status: PASS**, run 2026-09-01 against VS Code 1.135.0 and Spyglass (`spgoding.datapack-language-server`) 4.11.0. Raw output in [result.json](./result.json).

This is the gate on phase A. Keep it as a regression test: it is the one thing that detects a future Spyglass release adding a `scheme` filter to its document selector, which would silently break every forwarded provider.

## Result

| Check | Result | Meaning |
|---|---|---|
| `control_realFileCompletions` | **83** | Spyglass is alive and answering on a real `.mcfunction`. Without this the rest proves nothing. |
| `virtualLanguageId` | `mcfunction` | The `.mcfunction` suffix on the virtual URI does assign the language id, so Spyglass's selector matches. |
| `offsetsIdentical` | `true` | The whitespace projection preserves document length exactly, so positions need no translation. |
| `unshown_virtualCompletions` | **83** | **The answer to Q2.** Spyglass answers on a document opened but never shown. No escalation needed. |
| `projectSymbolCompletions` | **2**, `["probe:alpha","probe:beta"]` | The virtual document sees the **project symbol table**, so generated function paths are completable from inside a Python string. |
| `hoverResults` | 1 | Hover forwards. |
| `definitionResults` | 1, to `alpha.mcfunction` | Definition forwards and resolves to the real generated file. |
| `spyglassReadyAfterSeconds` | 2 | With a warm cache. First ever run downloads mcmeta summaries and takes minutes. |

`projectSymbolCompletions` was the largest unknown in the whole design. A virtual document lives outside the project roots, so it was not obvious its completions would resolve against the project's symbols. They do, because `Project.symbols` is global rather than path-relative. That is what makes `function <tab>` inside a `write_function` string offer the pack's own functions.

## Running it

```powershell
$S = "<path to this spike folder>"
$env:Q2_OUT = "$S\out.json"
Start-Process -FilePath "<VS Code>\Code.exe" -Wait -PassThru -ArgumentList @(
  "--extensionDevelopmentPath=$S\ext",
  "--extensionTestsPath=$S\ext\test\index.js",
  "--extensions-dir=$env:USERPROFILE\.vscode\extensions",
  "--user-data-dir=$S\udd",
  "--new-window", "--disable-gpu", "--disable-workspace-trust",
  "$S\ws"
)
Get-Content "$S\out.json"
```

A VS Code window opens, runs the probe and closes itself. Takes about 20 seconds with a warm cache.

### Two traps worth knowing

**Clear the inherited environment first.** When launched from inside VS Code's own integrated terminal or an extension host, `ELECTRON_RUN_AS_NODE=1` is inherited, and `Code.exe` then behaves as plain Node and rejects every VS Code flag with `bad option:`. `VSCODE_IPC_HOOK` is worse: it makes the launch attach to the *running* editor instead of starting a new one. Clear both, plus the other `VSCODE_*` variables, before launching.

**The `code` CLI wrapper detaches**, so it returns exit 0 immediately and you never see the result. Launch `Code.exe` directly and wait on the process.

## What it does

`ext/test/index.js` runs inside the extension host and, in order:

1. Waits for the extension host to settle, then activates Spyglass.
2. Opens a real `.mcfunction` from the probe workspace and polls until Spyglass answers. This is the control, and the run reports `INCONCLUSIVE` rather than `FAIL` if it never does.
3. Registers a `TextDocumentContentProvider` for the `stewbeet-mcfunction` scheme.
4. Projects a fake Python buffer, replacing everything outside the mcfunction block with spaces, and serves it as a virtual document.
5. Asks for completions **without showing** the document.
6. Only if that returns nothing, shows it in a preserved-focus preview editor and retries. That branch did not fire.
7. Asks for completions mid resource-location, to test project symbol visibility.
8. Asks for hover and definition.

`openTextDocument` is wrapped in a retry, because it raises `Canceled` while the extension host is still wiring up.

## Probe workspace

`ws/` is a minimal datapack: `pack.mcmeta` at `pack_format` 48, plus `probe:alpha` and `probe:beta`, which exist so there is a project symbol table to complete against.
