# Quickstart

Three commands, from nothing to a datapack you can load. The last one writes a zip.

**Requires** [uv](https://docs.astral.sh/uv/). Nothing else, not even Python: uv installs the
3.14 the template asks for.

## 1. Install uv

Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Create a project

```bash
uvx stewbeet init
```

Type `basic` when it asks which template to use, then press Enter.<br>
`uvx` runs StewBeet straight from PyPI, so there is nothing to install first.

## 3. Build

```bash
uv run stewbeet build
```

The template ships a `pyproject.toml`, so this first run creates `.venv/`, fetches Python 3.14 if
you do not have it and installs StewBeet into the project. Every later run starts building right away.

## What you got

```
build/
├── BasicTemplate_datapack.zip          <- drop this in .minecraft/saves/<world>/datapacks/
├── BasicTemplate_resource_pack.zip     <- drop this in .minecraft/resourcepacks/
├── datapack/
│   └── data/basic_template/
│       ├── function/enjoy.mcfunction
│       ├── function/_give_all.mcfunction        every item, in named chests
│       └── function/v0.0.1/                     load, tick, second, minute, unload
└── resource_pack/
```

32 files, from the six you can see in `src/`. Load the world, run `/reload`, and
`/function basic_template:_give_all` puts everything the pack defines in front of you.

## Next steps

- [Tutorial: build your first datapack](../0_getting_started/en.md): the same ground at
  walking pace, adding a custom item and a custom block of your own.
