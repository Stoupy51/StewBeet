# playground

Real StewBeet projects that the website builds and shows.

| Directory | What it is |
|---|---|
| `hero/` | The project behind the landing page hero, built at website build time |
| `sandbox/` | The container that builds submitted code for `/playground`, on demand |

## hero/

The project behind the landing page hero. It exists so that neither half of the hero is written
by hand: the snippet on the left is a region of `hero/src/definitions.py`, and the file tree on
the right is what building that file actually produces.

Two things read it:

| Consumer | Reads | Writes |
|---|---|---|
| `python_package/scripts/build_hero_output.py` | the whole project | `src/generated/heroOutput.json`, `src/generated/heroContents.json`, `public/generated/hero/*.png` |
| `docs/web/scripts/prehighlight.ts` | the `hero-snippet` region, then `heroContents.json` | `src/generated/heroCode.json`, `src/generated/heroContentsHtml.json` |

Run them in that order: the highlighter derives from the builder's output. Both `bun run dev` and
`bun run build` do it for you, so there is nothing to run by hand and nothing to keep in sync.

Nothing on the landing page loads a syntax highlighter. Both the snippet and the generated file
bodies are highlighted here at build time, and the bodies go to their own file that the panel
imports dynamically, so that markup only reaches a reader who clicked a file.

Shiki bundles no `mcfunction` grammar, so the site ships its own. `prehighlight.ts` registers it
from `src/langs/mcfunction.ts`, the same module `src/hooks/useShiki.ts` uses in the browser, with
the same theme and the same transformer. The build-time markup is byte-identical to what `useShiki`
produces at runtime, so a `.mcfunction` in the hero and one in the features section below it are
colored the same. Register the grammar in one place only; two would drift.

### Where it runs

The `hero` script in `package.json` is the first prebuild step of both `dev` and `build`, so the
hero is rebuilt from source every time the site is. `docs/web/src/generated/` is therefore
gitignored: every file in it carries a fresh timestamp, and committing that would be a diff on
every build for no gain.

It runs through `uv run --project ../../python_package`, which reads `requires-python` and
downloads that interpreter on its own. That is the whole reason `docs/web/Dockerfile` can install
uv into a `oven/bun` stage and still have no Python base and no system interpreter, and it is why
building the site needs uv installed but nothing else.

### After editing the hero

Nothing. Start the dev server and it rebuilds.

`uv run scripts/build_hero_output.py --check` from `python_package` reports whether the files on
disk still match a fresh build, which is useful while editing the builder itself.

### The rules it enforces

- **Every leaf of `src/components/heroTree.json` must exist in the build.** The tree is curated,
  because the real paths are three times too long to read in half a hero panel, but each leaf
  carries the real path it stands for and the generator fails, naming the closest real paths, when
  one goes missing.
- **Lines in the region must fit 66 columns once dedented.** Past that a 1280px screen cuts the
  snippet mid-string, which reads as a rendering bug. `prehighlight.ts` fails with the line number.
- **Both region markers must be present.** A renamed marker fails the build rather than shipping a
  hero with no code in it.

### Why it needs no GPU and no network

`iso_renders/` is committed. `core/utils/fonts/item_images.py` skips every item whose PNG is
already there when `manual.cache_assets` is true, so the model resolver queue comes back empty and
the lazy `from model_resolver.render import Render` behind it never executes. The same cache
short-circuits the vanilla texture downloads.

The one thing that breaks this is an item with no committed render. That is why
`manual.use_dialog` is `2`: a book item would need a `manual.png` and a render for it, and it
would be the one item that drags OpenGL back into the build. If you add an item to the hero,
commit its render into `iso_renders/<namespace>/` at the same time.

`build_hero_output.py` also passes `cache=True` to `run_beet`. With the default `cache=False`,
beet runs the whole build inside a temporary directory and the project's relative
`textures_folder` resolves against the wrong place.

## sandbox/

The container behind `/playground`. It runs code submitted by strangers, so it is built to be the
thing that gets attacked.

```bash
docker build -t stewbeet-playground docs/web/playground/sandbox
docker run -d --name pg --network none --read-only --init \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=128m,mode=1777 \
  --memory 1g --memory-swap 1g --cpus 1 --pids-limit 96 \
  --cap-drop ALL --security-opt no-new-privileges:true \
  -p 127.0.0.1:8001:8000 stewbeet-playground
python docs/web/playground/sandbox/tests/test_sandbox.py http://127.0.0.1:8001
```

`docker-compose.example.yml` beside this file is what the deployment host copies. The flags above
are not decoration: see the comments in it for what each one is actually stopping.

### Why the container is the boundary

StewBeet executes submitted Python by design. Pipeline entries are `importlib.import_module` with
the project directory on `sys.path`, and bolt hands the code every non-underscore builtin,
including `exec`, `eval` and `open`. Beet's `ProjectConfig.whitelist` guards beet's own require and
inject resolution, not what a whitelisted module then imports, so **it is not a security control**.
There is no in-process sandbox that makes this safe, which is why the worker is a separate service
on a network with no gateway. Everything in `worker.py` is the second layer, there so one abusive
request degrades into an error message rather than into an outage for the next visitor.

### uv is a build-time tool here

The image installs uv and builds `/srv/.venv` with it, the same way `docs/web/Dockerfile` does, so
there is no Python base image and no system interpreter. At request time the worker execs
`/srv/.venv/bin/python` directly and never `uv run`, which would try to sync the project and write
to the venv and its cache on a read-only rootfs.

StewBeet comes from the cloned repository at `REPO_REF`, not from PyPI, so the playground cannot
disagree with the documentation deployed beside it.

### What keeps OpenGL out

This is the part to be careful with, because it is not where you would expect.

`generate_all_iso_renders` is only called by `ingame_manual`, which is left out of the pipeline.
But `auto.text_renders` reaches model_resolver by a second route:
`emit.source_images` -> `ensure_item_images` -> `run_model_resolver`. The
`if source is None: continue` in `emit()` runs *after* that call, so it does not save you.

`src/placeholders.py` is what closes it. Between the submitted module and
`resource_pack.item_models` it seeds a render for every definition, and
`build_model_resolver_queue` skips an item whose PNG already exists when `cache_assets` is true, so
the queue is always empty. `runner.py` also refuses to import `model_resolver.render` at all, which
turns a future pipeline change into an immediate error instead of a fifteen second hang, and
`worker.py --selftest` builds a render node at image build time so that change fails the image
rather than a visitor.

The same plugin writes a magenta checkerboard for any item id the bundled packs have no texture
for. Without it, `resource_pack.item_models` raises `Texture '<id>.png' not found in source
textures` and the build dies, which is the first thing a visitor hits after renaming an item.

### Why `init: true` is not optional

The worker is PID 1 in the container, so every process a build orphans is reparented to it and
stays a zombie until something waits on it. A zombie still holds a pid. One fork bomb was enough to
fill `pids_limit`, after which the worker could no longer spawn a thread for an incoming
connection: the next request got a dropped connection with no response, and it never recovered.
Containing a fork bomb is worthless if the service cannot answer afterwards, which is why
`tests/test_sandbox.py` builds normally straight after the bomb.

`init: true` puts a real init in front of the worker to reap them. `Build.reap` does it too, after
every build, so the worker is not one deployment flag away from that failure. `Build.kill` also
signals the process group repeatedly rather than once, because killpg only reaches what exists at
the instant it is delivered and a fork landing a microsecond later inherits the group unsignalled.

### Two things that look like details and are not

`stdin=subprocess.DEVNULL`: `stouputils.print.message.error` prints "Press enter to ignore error
and continue" and calls `input()` before exiting. With a real stdin, every build error would block
until the 20 second wall timeout, and at one build slot that is the whole playground.

The texture and render folders are per request and writable, filled with symlinks into
`/srv/assets`. `src/placeholders.py` has to write into both, the image is read only, and copying
32 MB per request would spend a quarter of the tmpfs on bytes that never change.

### Textures a visitor can use

`merge_assets.py` merges the textures and renders of SimplEnergy, Stardust Fragment and the
extensive template at image build time, sparse-cloned so only those folders are fetched. Measured:
452 textures, 2.9 MB, against a 32 MB budget that fails the image build.

Names collide across three real packs, so the last source in `SOURCES` wins and the count is
reported. Measured at 2 colliding textures and 89 colliding renders, almost all of the latter being
the vanilla `minecraft/` items every project caches. Failing the build over that, as an earlier
draft of this planned to do, would have meant it never built.
