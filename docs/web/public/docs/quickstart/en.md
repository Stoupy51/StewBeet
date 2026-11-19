
# Quickstart

Three commands, from nothing to a datapack you can load. The last one writes a zip.

Requires [uv](https://docs.astral.sh/uv/), nothing else. uv installs the Python 3.14 the template asks for. Already have a datapack? [Migrate it](../9_migration/en.md) instead of starting from a template.

## 1. Install uv

```powershell tab="Windows"
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash tab="macOS and Linux"
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Create a project

```bash
uvx stewbeet init
```

Type `basic` when it asks which template to use, then press Enter. `uvx` runs StewBeet straight from PyPI, so there is nothing to install first.

## 3. Build

```bash
uv run stewbeet build
```

The first run creates `.venv/`, fetches Python 3.14 if you do not have it and installs StewBeet into the project. Every later run starts building right away.

## What you got

- `build/BasicTemplate_datapack.zip` goes in `.minecraft/saves/<world>/datapacks/`.
- `build/BasicTemplate_resource_pack.zip` goes in `.minecraft/resourcepacks/`.

Load the world and run `/reload`. `/function basic_template:_give_all` then puts every item of the pack in front of you, in named chests. Beside the zips, `build/` holds the same packs unzipped: 32 files, written from the six you can see in `src/`.

