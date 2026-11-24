
# Source maps

Écrit un fichier `.mcfunction.map` à côté de chaque function générée, pour qu'un éditeur ou [Sniffer](https://github.com/mcbookshelf/sniffer) puisse sauter d'une commande à la ligne Python qui l'a écrite.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.source_maps`, avec `stewbeet.plugins.source_maps.emit` dans le pipeline. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/source_maps/__init__.py)

## L'utiliser

Les deux vont dans `beet.yml` :

```yaml
require:
  - "stewbeet"
  - "stewbeet.plugins.source_maps"

pipeline:
  # after the plugins writing functions
  - "stewbeet.plugins.source_maps.emit"
  - "stewbeet.plugins.archive"
```

`source_maps` enregistre les écritures : il vient donc dans `require` avant tout ce qui écrit une function. `emit` écrit les maps, après le dernier plugin qui réécrit des functions et avant celui qui zippe le pack.

Pour un seul build sans modifier `beet.yml` : `beet -s "require[]=stewbeet.plugins.source_maps" build`.

Un projet bolt ou mecha sans aucun appel StewBeet n'a besoin que de `source_maps`, dans `require`.

## Ce que ce plugin écrit

Pour chaque function d'origine connue, `<name>.mcfunction.map`, un fichier Source Map v3 à côté de la function. La function n'est pas modifiée.

```json
{
  "version": 3,
  "file": "root.mcfunction",
  "sources": ["src/link.py"],
  "names": [],
  "mappings": "AAKA;AACA;AACA"
}
```

Les `sources` sont des chemins depuis la racine du projet. Il n'y a ni `sourcesContent` ni `sourceRoot` : l'éditeur lit donc vos fichiers sur le disque.

Les functions que mecha a compilées portent aussi `x_stewbeet_bolt` et `x_stewbeet_opaque`, des champs que les autres consommateurs ignorent.

## Ce qui est mappé

- Vos propres appels à `write_function` et les lignes qu'ils construisent, y compris une commande construite dans une boucle.
- Ce que mecha a compilé : un module `.bolt`, ou un `.mcfunction` qui contient du bolt.
- Ce qu'un plugin génère à partir de l'une de vos déclarations, mappé vers cet appel `Block(...)` ou `Item(...)`. Cela couvre `datapack.custom_blocks` et les functions de recipe de `custom_recipes` (smithed, furnace, pulverizer, awakened forge).

Tout le reste de ce qu'un plugin génère reste non mappé, tout comme les functions écrites une seule fois pour tout le pack (`custom_blocks/get_rotation`) et les définitions chargées depuis du JSON ou `external_definitions`. Une map ne pointe jamais à l'intérieur de StewBeet, beet, bolt, mecha ou stouputils.

## Limites

- Sans `source_maps` dans `require`, aucune map n'est écrite. Un build qui n'a rien capturé avertit.
- Sans `emit` dans le pipeline, les maps sont écrites tout à la fin du build. Quand un plugin qui empaquette le pack a déjà tourné (`archive`, `merge_smithed_weld`, `copy_to_destination`, `compute_sha1`), un avertissement dit qu'il ne les a pas vues.
- `archive` écrit lui-même les maps avant de zipper, si bien que le zip et le dossier de build portent les mêmes fichiers.

## Pour continuer

- [Écrire des functions et des fichiers](../2_writing_to_files/fr.md) : les appels que ce plugin enregistre.

