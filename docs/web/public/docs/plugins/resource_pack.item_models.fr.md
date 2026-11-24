
# Item models

Écrit le model et la définition `items/` de chaque item et block de vos définitions à partir des textures de votre dossier de textures, si bien qu'une texture nommée comme un item suffit à le dessiner.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.resource_pack.item_models`. Il a besoin de `textures_folder` dans la section `stewbeet` de `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/item_models/__init__.py)

## Nommer vos textures

Le plugin analyse `textures_folder` à la recherche de fichiers `.png` et trouve les textures d'un item par leur nom de fichier, quel que soit le sous-dossier. Les textures qui commencent par l'id de l'item sont ses variantes.

```text
steel_ingot.png
simplunium_block.png
super_furnace_front.png
super_furnace_side.png
super_furnace_top.png
super_furnace_on.png
```

- Un block avec une seule texture l'affiche sur toutes ses faces.
- Un block avec plusieurs textures prend la première de ces formes dont tous les côtés existent, sous la forme `<id>_<side>.png` :

| Forme | Côtés |
|---|---|
| `cake` | `bottom`, `side`, `top`, `inner` |
| `orientable_with_bottom` | `front`, `bottom`, `side`, `top` |
| `cube_bottom_top` | `bottom`, `side`, `top` |
| `orientable` | `front`, `side`, `top` |
| `cube_column` | `end`, `side` |

- Une texture qui finit par `_on` est l'état allumé. Le plugin en écrit un second model, que montre un hôte furnace en train de brûler.
- Un bow prend `<id>_pulling_0`, `<id>_pulling_1` et ainsi de suite. Une crossbow prend aussi `<id>_arrow` et `<id>_firework` pour ses états chargés.
- Un item en cuir prend `<id>_overlay` comme seconde couche.
- Une spear prend `<id>_in_hand` pour le model qu'elle montre hors de la GUI.

## Ce que ce plugin écrit

- `models/item/<id>.json` : le model, avec une copie par état de l'item (`_on`, les `_pulling_<n>` d'un bow).
- `items/<id>.json` : la définition d'item model.
- `textures/item/<texture>.png`, avec son `.mcmeta` quand la source en a un.
- Des entrées dans les atlas `minecraft` pour les textures de blocks vanilla qu'un model utilise : `items` à partir du pack format 73, `blocks` avant.
- Un model, un item model et une texture par stade de croissance d'une graine qui pousse, depuis `<texture_basename>_stage_<n>.png`.
- Des copies de model supplémentaires pour un block avec `uvlock` ou `half`, et pour un hôte stairs, que le display choisit selon l'état.

Seuls les items dont l'`item_model` est dans votre namespace sont écrits.

## Options

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `meta.stewbeet.textures_folder` | obligatoire | Le dossier analysé pour les fichiers `.png` |
| `Item.override_model` | `None` | Fusionné par-dessus le model généré. `{"textures": None}` retire ses textures, `{}` n'écrit aucun model |
| `Item.hand_model` | `None` | Le model montré en main, dans la GUI et au sol |
| `Item.override_model_contexts` | `["none", "fixed"]` | Les display contexts qui gardent le model normal quand `hand_model` est défini |

## Limites

- Une texture dont le model a besoin et que le dossier n'a pas journalise une erreur qui nomme `<name>.png`, et l'item n'a pas de model.
- Un block dont les textures ne remplissent aucune forme journalise une erreur qui liste les formes, sauf si son `override_model` définit des textures.
- Deux textures de même nom de fichier dans des sous-dossiers différents entrent en collision, et une seule est lue.

## Pour continuer

- [Définitions](../1_definitions_setup/fr.md#block-class) : les options de `VanillaBlock` qui ajoutent des copies de model.

