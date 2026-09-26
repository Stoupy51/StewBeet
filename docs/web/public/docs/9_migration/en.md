# Migrate an existing pack

`stewbeet migrate` turns a datapack or resource pack you already have into a StewBeet project. Your files move into `src/`, a template adds `beet.yml` and the rest of a project around them, and `stewbeet build` gives you your pack back. Nothing you wrote is edited, only moved.

It is meant for packs made by hand or with other tools. A folder that already has a beet configuration is refused, since it is a beet project already.

New to beet? The diagram at the top of the [beet configuration page](../3_beet_config/en.md) shows who makes beet, bolt, mecha and StewBeet.

## Before you start

- **Commit the folder to git, or copy it.** The migration moves files.
- **Open a terminal in your pack's folder, or the folder above it.** A pack is a `pack.mcmeta` next to a `data/` folder, an `assets/` folder, or both, and it is looked for up to two folders deep.
- **One datapack and one resource pack at most.** A single folder holding both counts as one pack.

## 1. Preview the migration

```bash
uvx stewbeet migrate basic --dry-run
```

`--dry-run` prints everything the migration would do and changes nothing. Here the pack is `My Pack/`, a datapack and a resource pack sharing one `pack.mcmeta`:

```text
Found datapack and resource pack in My Pack
Migration plan:
  add     .gitignore
  add     definitions_debug.json
  add     pyproject.toml
  skip    assets/pack.png (replaced by your pack.png)
  add     assets/textures/README.md
  add     src/link.py
  add     src/setup_definitions.py
  skip    src/data/basic_template/function/enjoy.mcfunction (replaced by your datapack)
  add     src/definitions/additions.py
  add     src/definitions/ores.py
  write   beet.yml
            name: My Pack
            id: mypack
            description: from pack.mcmeta
  move    My Pack/data -> src/data
  move    My Pack/assets -> src/assets
  move    My Pack/pack.png -> assets/pack.png
  delete  My Pack/pack.mcmeta (beet.yml and StewBeet write it at build time)
  remove  My Pack/ (empty once moved)
WARNING Set author in beet.yml: it still names the template's author
Dry run: nothing was changed. Run the same command without --dry-run to apply this plan.
```

| Line | Meaning |
|------|---------|
| `add` | A template file, written because you have nothing at that path |
| `skip` | A template file left out, with the reason |
| `write` | `beet.yml`, with the values taken from your pack listed under it |
| `move` | One of your files or folders, moved as it is |
| `delete` | A `pack.mcmeta` that held only a description and a pack format |
| `remove` | A folder left empty by the moves |

### Which template

| Template | What you get |
|----------|--------------|
| `minimal` | beet with a single StewBeet plugin. The closest to the pack you had. |
| `basic` | Every StewBeet plugin configured and commented. The template the [tutorial](../0_getting_started/en.md) uses. |

Without a name, the command asks, and pressing Enter picks `minimal`. `extensive` is not offered, because its example items would mix with yours.

## 2. Migrate

```bash
uvx stewbeet migrate basic
```

It prints the same plan, then asks `Apply this plan? (y/n)`. Add `--yes` to skip the question, in a script for instance.

## 3. Check `beet.yml`, then build

The warnings under the plan list what is left to do by hand:

- **`author`** still holds the template's author. Put your name there.
- **`id`** is set from your namespace, the folder under `data/` other than `minecraft`. With several namespaces it is not set, so choose the one StewBeet should generate its functions under.

Then build:

```bash
uv run stewbeet build
```

`build/` now holds your datapack and resource pack, with a `pack.mcmeta` written for the `minecraft` version set in `beet.yml`. If you kept a `pyproject.toml` of your own, the template's was skipped: add `stewbeet` to its dependencies, or build with `uvx stewbeet build`.

## Before and after

The example above, migrated onto `basic`:

```text
Before                                  After
.                                       .
└── My Pack/                            ├── beet.yml           id, name and description from your pack
    ├── pack.mcmeta                     ├── pyproject.toml
    ├── pack.png                        ├── assets/
    ├── data/                           │   └── pack.png       your icon
    │   ├── minecraft/tags/...          └── src/
    │   └── mypack/function/...             ├── data/          your datapack, unchanged
    └── assets/                             ├── assets/        your resource pack, unchanged
        └── mypack/lang/en_us.json          ├── definitions/   from the template, no items yet
                                            ├── link.py
                                            └── setup_definitions.py
```

## What happens to each file

- **`data/` and `assets/`** move to `src/data/` and `src/assets/`, content untouched.
- **`pack.mcmeta`** holding only a description and a pack format is deleted: its description goes into `beet.yml`, and StewBeet writes a new `pack.mcmeta` on every build. One holding more, such as `overlays` or `filter`, moves to `src/pack.mcmeta`. StewBeet keeps its extra keys but still sets `pack_format` and `description`, so check the formats it lists against the versions you target.
- **`pack.png`** moves to where the template keeps its icon: `src/` for `minimal`, `assets/` for `basic`. When the datapack and the resource pack each have one, the datapack's is used and the other stays where it is.
- **Files the template ships that you already have**, like `.gitignore` or `pyproject.toml`, are kept. The template's copy is skipped.
- **A resource pack migrated onto `minimal`** gets a `resource_pack` section added to `beet.yml`, since that template only builds a datapack.
- **The folders your pack sat in** are removed once they are empty.

## When it refuses

Every check runs before the first file moves, so a refusal leaves the folder as it was.

| Message | What to do |
|---------|------------|
| `This folder already has a beet configuration` | The folder is a beet project already: there is nothing to migrate. |
| `No pack found` | The `pack.mcmeta` is missing, or more than two folders down. Run the command closer to it. |
| `Found 2 datapacks` | A project holds one datapack and one resource pack. Run the command from a folder that only contains the pack to migrate. |
| `Nothing was changed, because: src/data already exists` | Something is already where your files would go. Move it away and run again. |
| `Could not download the 'basic' template` | Templates are downloaded from GitHub for your StewBeet version, so this needs a connection. |

## Next steps

- [Definitions](../1_definitions_setup/en.md): turn the items you give with hand-written loot tables into definitions, one at a time. StewBeet then writes their loot tables, models and manual pages.
- [beet configuration](../3_beet_config/en.md): every option of the `beet.yml` you just got.
