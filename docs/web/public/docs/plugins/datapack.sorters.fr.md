
# List sorting

Génère les functions qui trient une liste stockée dans un storage, à partir d'un petit fichier JSON.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.datapack.sorters`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/sorters/__init__.py)

## Déclarer un sorter

Écrivez `data/<namespace>/sorter/<name>.json` :

```json
{
  "algorithm": "selection_sort",
  "functions_location": "switch:stats/sort",
  "to_sort": {
    "storage": "switch:stats",
    "target": "all.played"
  },
  "key": "count",
  "scale": 100,
  "limit": 10
}
```

Appelez ensuite `/function switch:stats/sort/sort`. La liste à `target` est remplacée par sa copie triée, de la plus petite `key` à la plus grande. Un `scale` négatif donne la plus grande en premier.

Le fichier du sorter est retiré du pack une fois ses functions écrites.

## Ce que ce plugin écrit

Sous `functions_location` :

- `sort` est le point d'entrée.
- `selection_sort_loop`, `find_min`, `move_min_element`, et `append_remaining` quand `limit` est défini, pour `selection_sort`.
- `quick_sort`, `partition_main`, `partition_loop`, `partition_swap` et `partition_loop_swap`, pour `quick_sort`.

Les scores de tri sont sur l'objective `sorter.val` et les données temporaires dans `sorter:temp`.

## Options

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `algorithm` | `"selection_sort"` | `"selection_sort"` ou `"quick_sort"` |
| `functions_location` | obligatoire | Le chemin de function sous lequel les functions sont écrites |
| `to_sort.storage` | obligatoire | Le storage qui contient la liste |
| `to_sort.target` | obligatoire | Le chemin NBT de la liste dans ce storage |
| `key` | obligatoire | Le nombre, à l'intérieur de chaque élément, qui est comparé |
| `scale` | `1` | Entier par lequel la clé est multipliée avant d'être arrondie en score |
| `limit` | aucun | Ne trie que les premiers éléments, et garde le reste après eux. `selection_sort` seulement |

`selection_sort` est celui à choisir. `quick_sort` s'appelle lui-même par des macros, et dans un datapack cela coûte plus que la boucle quadratique.

## Limites

- Une clé est comparée comme un score entier. Utilisez `scale` pour garder des décimales : `1000` en garde 3.
- `limit` est ignoré par `quick_sort`.
- Un sorter dont `functions_location`, `key` ou `to_sort` manque fait échouer le build.

## Support de l'éditeur

Spyglass complète et vérifie les fichiers de sorter quand `sorter` est une custom resource. Dans la config de Spyglass, sous `env` :

```json
"customResources": {
  "sorter": { "category": "sorter" }
}
```

Ajoutez ensuite [`mod.mcdoc`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/sorters/mod.mcdoc) n'importe où dans le workspace et redémarrez VS Code.

## Pour continuer

- [Écrire des functions et des fichiers](../2_writing_to_files/fr.md) : appeler les functions générées depuis les vôtres.

L'implémentation du quick sort est de [Darukshock](https://github.com/Darukshock).

