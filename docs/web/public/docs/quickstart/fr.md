
# Démarrage rapide

Trois commandes, de rien à un datapack chargeable. La dernière écrit un zip.

Nécessite [uv](https://docs.astral.sh/uv/), rien d'autre. uv installe le Python 3.14 demandé par le template. Vous avez déjà un datapack ? [Migrez-le](../9_migration/fr.md) au lieu de partir d'un template.

## 1. Installer uv

```powershell tab="Windows"
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash tab="macOS et Linux"
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Créer un projet

```bash
uvx stewbeet init
```

Tapez `basic` quand le template vous est demandé, puis Entrée. `uvx` lance StewBeet directement depuis PyPI, il n'y a donc rien à installer avant.

## 3. Compiler

```bash
uv run stewbeet build
```

Ce premier lancement crée `.venv/`, récupère Python 3.14 si vous ne l'avez pas et installe StewBeet dans le projet. Les lancements suivants compilent directement.

## Ce que vous obtenez

- `build/BasicTemplate_datapack.zip` va dans `.minecraft/saves/<monde>/datapacks/`.
- `build/BasicTemplate_resource_pack.zip` va dans `.minecraft/resourcepacks/`.

Chargez le monde et lancez `/reload`. `/function basic_template:_give_all` pose alors devant vous tous les items du pack, dans des coffres nommés. À côté des zips, `build/` contient les mêmes packs décompressés : 32 fichiers, écrits à partir des six visibles dans `src/`.

