# Démarrage rapide

Trois commandes, de rien à un datapack chargeable. La dernière écrit un zip.

**Nécessite** Python 3.14 ou plus récent

## 1. Installer

```bash
pip install stewbeet
```

## 2. Créer un projet

```bash
stewbeet init
```

Tapez `basic` quand le template vous est demandé, puis Entrée.

## 3. Compiler

```bash
stewbeet build
```

## Ce que vous obtenez

```
build/
├── BasicTemplate_datapack.zip          <- à déposer dans .minecraft/saves/<monde>/datapacks/
├── BasicTemplate_resource_pack.zip     <- à déposer dans .minecraft/resourcepacks/
├── datapack/
│   └── data/basic_template/
│       ├── function/enjoy.mcfunction
│       ├── function/_give_all.mcfunction        tous les objets, dans des coffres nommés
│       └── function/v0.0.1/                     load, tick, second, minute, unload
└── resource_pack/
```

32 fichiers, à partir des six visibles dans `src/`. Chargez le monde, lancez `/reload`, puis
`/function basic_template:_give_all` pose devant vous tout ce que le pack définit.

## Prochaines étapes

- [Tutoriel : votre premier datapack](../0_getting_started/fr.md): le même terrain au pas,
  en ajoutant votre propre objet et votre propre bloc.
