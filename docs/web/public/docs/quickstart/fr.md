# Démarrage rapide

Trois commandes, de rien à un datapack chargeable. La dernière écrit un zip.

**Nécessite** [uv](https://docs.astral.sh/uv/). Rien d'autre, pas même Python : uv installe le
3.14 demandé par le template.

## 1. Installer uv

Windows :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS et Linux :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Créer un projet

```bash
uvx stewbeet init
```

Tapez `basic` quand le template vous est demandé, puis Entrée.<br>
`uvx` lance StewBeet directement depuis PyPI, il n'y a donc rien à installer avant.

## 3. Compiler

```bash
uv run stewbeet build
```

Le template fournit un `pyproject.toml` : ce premier lancement crée `.venv/`, récupère Python 3.14 si
vous ne l'avez pas et installe StewBeet dans le projet. Les lancements suivants compilent directement.

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
