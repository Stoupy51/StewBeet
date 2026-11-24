
# Recipes

Transforme les `recipes` de chaque item de vos définitions en fichiers et functions de recipe, pour que les joueurs puissent fabriquer, cuire, découper ou forger vos items.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.custom_recipes`, et lit les définitions d'items sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/custom_recipes/__init__.py)

## Déclarer une recipe

```python
Item(
  id="super_stone",
  base_item="minecraft:stone",
  recipes=[
    CraftingShapedRecipe(
      category="building",
      shape=["XXX", "XXX", "XXX"],
      ingredients={
        "X": Ingr("minecraft:stone"),
      },
    ),
  ],
)
```

L'item est le résultat, sauf si la recipe définit `result`. `Ingr("minecraft:stone")` est un item vanilla, `Ingr("steel_ingot")` un item de votre projet.

## Ce que ce plugin écrit

Un ingrédient qui est un simple item vanilla donne un fichier de recipe vanilla. Un ingrédient qui est l'un de vos items ne peut pas figurer dans un fichier de recipe : la recipe passe alors par une bibliothèque.

- `recipe/<item>.json` : un par recipe de crafting, smelting, blasting, smoking, campfire, stonecutting et smithing dont tous les ingrédients sont des items vanilla. Une deuxième recipe de l'item s'appelle `<item>_2`.
- `function/utils/get_all_recipes` : donne au joueur toutes les recipes ci-dessus.
- `advancement/unlock_recipes` : donne une recipe quand le joueur tient l'un de ses ingrédients ou son résultat. Elle appelle `function/advancements/unlock_recipes`.
- `function/calls/smithed_crafter/shapeless_recipes` et `shaped_recipes` : toutes les recipes de crafting, taguées pour [Smithed Crafter](https://wiki.smithed.dev/libraries/crafter/), qui donne le résultat depuis la loot table de l'item. Un ingrédient custom ajoute la bibliothèque au pack.
- `function/calls/furnace_nbt_recipes/<type>_recipes` : toutes les recipes de smelting, blasting et smoking, pour [Furnace NBT Recipes](https://github.com/Stoupy51/FurnaceNbtRecipes), avec leur expérience dans `recipes_used`. C'est ainsi qu'un four accepte un ingrédient custom.
- `function/calls/simplenergy/pulverizer_recipes` : les `PulverizingRecipe` du pulverizer de SimplEnergy.
- `function/calls/stardust/awakened_forge_recipes` : les `AwakenedForgeRecipe` de la forge de Stardust Fragment, avec un `timer` et une function `craft` pour chaque résultat.

Un item avec `remainder` reçoit aussi le component `use_remainder`, qui contient ce conteneur.

## Options

Chaque recipe accepte :

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `result` | l'item | Ce que la recipe donne, sous forme d'`Ingr` |
| `result_count` | `1` | Combien elle en donne |
| `category` | `None` | L'onglet du recipe book |
| `group` | `None` | Le groupe du recipe book |
| `smithed_crafter_command` | `None` | La commande lancée à la place du don de la loot table, pour les recipes de crafting |

Les recipes de cuisson ajoutent `experience` (`0.0`) et `cookingtime` en ticks : `200` pour le smelting, `100` pour le blasting et le smoking. `CampfireCookingRecipe` exige les deux. À partir de la 26.3, les fichiers de recipe de blasting et de smoking stockent le double de votre `cookingtime`, que le block divise par deux.

## Limites

- Un type de recipe que le plugin ne connaît pas lève `Invalid recipe type` quand la définition est construite.
- Une recipe shaped contient au plus 3 lignes de 3 colonnes, toutes les lignes de même largeur.
- Une recipe de stonecutting ou de smithing avec un ingrédient custom est ignorée, sans fichier ni function.
- Une recipe de campfire avec un ingrédient custom est ignorée aussi.
- Une recipe de four ajoute la bibliothèque Furnace NBT Recipes au pack.
- Le premier ingrédient d'une recipe de awakened forge contient au plus 64 items.

## Pour continuer

- [Définitions](../1_definitions_setup/fr.md#recipe-system) : chaque classe de recipe avec ses champs.

