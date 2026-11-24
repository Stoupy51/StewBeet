
# SimpleDrawer

Permet aux drawers compactants de SimpleDrawer de stocker vos ingots, nuggets et blocks de stockage, et de convertir de l'un à l'autre.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.compatibilities.simpledrawer`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/compatibilities/simpledrawer/__init__.py)

## Ce qu'il lit

Un item nommé `<material>_block` compte comme block de stockage quand son `custom_data` contient un `smithed.dict`, que les helpers de matériau des définitions écrivent pour vous. Le plugin cherche alors les autres formes par leur nom :

| Forme | Trouvée sous le nom |
|---|---|
| Ingot | `<material>_ingot`, sinon `<material>`, sinon `<material>_fragment` |
| Nugget | `<material>_nugget` |

Un block qui commence par `raw_` utilise `raw_<material>` comme ingot et n'a pas de nugget. Un block sans ingot ni nugget est ignoré.

Il lit aussi vos recipes. Une recipe de crafting qui a le block pour seul ingrédient donne le nombre d'ingots en lesquels un block se décompresse. La même avec l'ingot donne les nuggets par ingot. Sans une telle recipe, les deux nombres valent 9.

## Ce que ce plugin écrit

- `#simpledrawer:material` appelle `calls/simpledrawer/material`, qui compare l'item du drawer à chaque forme de chaque matériau.
- `calls/simpledrawer/<material>/block`, `ingot` et `nugget` donnent le type de la forme (0, 1 ou 2) et appellent `main`.
- `calls/simpledrawer/<material>/main` pose les nombres et le nom du matériau, et copie vos items depuis `<namespace>:items`.

## Limites

- Rien n'est écrit quand aucun block ne correspond, et le build n'avertit pas.
- Le nom affiché pour un matériau est son id avec des espaces et des majuscules, comme `Steel Alloy` pour `steel_alloy`. Il n'est pas traduit.

## Pour continuer

- [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md) : SimpleDrawer s'installe comme n'importe quelle autre bibliothèque.

