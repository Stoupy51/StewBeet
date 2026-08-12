# playground

Real StewBeet projects that the website builds and shows.

## hero/

The project behind the landing page hero. It exists so that neither half of the hero is written
by hand: the snippet on the left is a region of `hero/src/definitions.py`, and the file tree on
the right is what building that file actually produces.

Two things read it:

| Consumer | Reads | Writes |
|---|---|---|
| `python_package/scripts/build_hero_output.py` | the whole project | `src/generated/heroOutput.json`, `src/generated/heroContents.json`, `public/generated/hero/*.png` |
| `docs/web/scripts/prehighlight.ts` | the `hero-snippet` region, then `heroContents.json` | `src/generated/heroCode.json`, `src/generated/heroContentsHtml.json` |

Run them in that order: the highlighter derives from the builder's output.

Nothing on the landing page loads a syntax highlighter. Both the snippet and the generated file
bodies are highlighted here at build time, and the bodies go to their own file that the panel
imports dynamically, so that markup only reaches a reader who clicked a file.

Shiki bundles no `mcfunction` grammar, so the site ships its own. `prehighlight.ts` registers it
from `src/langs/mcfunction.ts`, the same module `src/hooks/useShiki.ts` uses in the browser, with
the same theme and the same transformer. The build-time markup is byte-identical to what `useShiki`
produces at runtime, so a `.mcfunction` in the hero and one in the features section below it are
colored the same. Register the grammar in one place only; two would drift.

### Where it runs

`docs/web/Dockerfile` installs uv in its build stage and runs the builder there, before
`bun run build`, writing over whatever the repository had committed. uv brings its own interpreter,
read from `requires-python`, so the image still has no Python base and no system interpreter. The
deployed hero can therefore never show a build older than the code being deployed, which is why
nothing checks the committed copies for staleness.

They are still committed, and that is not redundancy: `Hero.tsx` imports `heroOutput.json`
statically, so without it in the repository `tsc -b` and `bun run dev` fail on a fresh clone and
every website contributor would need the Python toolchain to see the site at all. Treat the
committed copies as a local convenience and the Dockerfile as the source of truth.

### After editing the hero

```bash
cd python_package && uv run scripts/build_hero_output.py
cd docs/web       && bun scripts/prehighlight.ts
```

Commit what changed so local development keeps working. `--check` on the builder tells you whether
the committed copies still match, if you want to know before pushing; nothing enforces it, because
the image regenerates them anyway.

Commit what changed under `docs/web/src/generated/` and `docs/web/public/generated/`. CI runs
`build_hero_output.py --check` and fails if you forget.

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
