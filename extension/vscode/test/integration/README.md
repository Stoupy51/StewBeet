# Integration test

End-to-end proof that the forwarded providers answer inside StewBeet mcfunction blocks, run against the real extension and the real Spyglass in a VS Code extension host.

```sh
npm run test:integration          # from extension/vscode/
```

A VS Code window opens, runs the checks and closes itself. Takes about 25 seconds with a warm Spyglass cache; the first ever run downloads mcmeta summaries and takes minutes. Set `VSCODE_EXE` if the launcher cannot find your VS Code.

## The probe

```sh
SB_TESTS=probe node test/integration/run.js
```

A measurement rather than a set of assertions, for questions the unit tests cannot answer: does a virtual document stay reachable, does the server report on one nobody asked about, and does loading generated files evict it. It is what found the two faults 1.5.0 fixes, and rerunning it is the fastest way to tell a dead relay from a slow one.

It types into `demo.py`, and VS Code saves a dirty document when the window closes, so `run.js` snapshots the fixture and puts it back afterwards.

## Why it exists

It is the regression guard for the assumption the whole design rests on: **Spyglass's document selector carries no scheme filter**, so it attaches to the virtual documents this extension serves. If a future Spyglass release adds one, every provider silently stops answering and nothing else notices.

## What it checks

| Check | Asserts |
|---|---|
| `control_realFileCompletions` | Spyglass answers on a real `.mcfunction`. Without this the rest proves nothing, so the run reports INCONCLUSIVE rather than FAIL. |
| US1 completion inside a block | Completions arrive mid-command inside a `write_function` string. |
| US1 offers vanilla commands | `say` is among them. |
| US1 offers the project's own function paths | `probe:alpha` is offered mid resource location, proving the virtual document sees the project symbol table. |
| US1 no mcfunction items outside a block | Providers stay out of the way in ordinary Python. |
| US2 hover | Hover answers on a selector. |
| US3 definition | Resolves to the generated `alpha.mcfunction`. |
| Setting gate | `StewBeet.languageFeatures: false` stops all forwarding. |

### The trap in the outside-a-block check

VS Code's word-based suggestions collect words from the open document, and `say` and `execute` both appear inside the fixture's mcfunction string. Asserting on those made the check fail with the extension behaving perfectly. It now turns word-based suggestions off and asserts on commands that are **not** words in `demo.py` (`advancement`, `bossbar`, `ban-ip`, ...), with a paired positive control confirming those same tokens do appear inside a block.

## Launch traps

`run.js` exists to avoid two of them:

1. Launched from VS Code's own terminal or an extension host, `ELECTRON_RUN_AS_NODE=1` is inherited and `Code.exe` behaves as plain Node, rejecting every flag with `bad option:`. `VSCODE_IPC_HOOK` is worse: the launch attaches to the running editor instead of starting a new one. Both are stripped.
2. The `code` CLI wrapper detaches, returning 0 immediately with no result. The Electron binary is invoked directly.

## Fixture

**The throwaway VS Code profile lives in the OS temp dir, never in the repo.** A profile inside the workspace puts the git extension's askpass sockets under a directory Spyglass' file watcher cannot `scandir`; the resulting EPERM restarts the language server until it stops retrying. Gitignoring it is not enough, because Spyglass watches the project root and does not read `.gitignore`.

`fixture/` is a minimal datapack (`pack.mcmeta`, `probe:alpha`, `probe:beta`) plus `demo.py` containing one `write_function` block. The datapack exists so there is a project symbol table to complete against.

## What this run establishes

Two assumptions the design rests on, neither of which is guaranteed by any API, both re-checked
on every run:

- **Spyglass attaches to our virtual documents.** Its document selector carries no scheme filter.
  If a release ever adds one, every forwarded provider goes quiet and only this test notices.
- **`vscode.executeDefinitionProvider` resolves to `Location`, not `LocationLink`.** Recorded as
  `us3_answerShape` in `result.json`. Both shapes are handled in `src/navigation.js`, because
  which one arrives depends on the answering provider rather than on us, but the observed value
  is the one the rewriting is exercised against.

Deleting `fixture/data/probe/function/alpha.mcfunction.map` turns the US3 checks into the step A
behaviour: definition falls back to the generated `.mcfunction` and completion is unaffected.
That is the degradation path for a workspace with no build, and it has been verified by hand.
