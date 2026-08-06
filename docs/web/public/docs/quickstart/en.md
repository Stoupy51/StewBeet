# Quickstart

Three commands, from nothing to a datapack you can load. The last one writes a zip.

**Requires** Python 3.14 or newer

## 1. Install

```bash
pip install stewbeet
```

## 2. Create a project

```bash
stewbeet init
```

Type `basic` when it asks which template to use, then press Enter.

## 3. Build

```bash
stewbeet build
```

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
