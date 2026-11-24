
# Load functions

Donne à votre pack les functions qui le chargent une seule fois, comparent sa version à celle d'autres copies de lui-même, et mettent vos items en storage.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.datapack.loading`, et a besoin de `version` et `id` dans `beet.yml`. La version doit s'écrire `major.minor.patch`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/loading/__init__.py)

Le chargement est terminé par `stewbeet.plugins.finalyze.dependencies`, qui tourne plus tard dans le même pipeline.

## Lire vos items depuis le storage

Chaque item de vos définitions est dans le storage `<id>:items` une fois le pack chargé, sous `all.<item id>` :

```mcfunction
data get storage simplenergy:items all.pulverizer
```

Les components portent le préfixe `minecraft:` et l'item model vient en premier.

## Ce que ce plugin écrit

Dans `function/v<version>/load/` :

- `enumerate` monte les scores `#<id>.major`, `#<id>.minor` et `#<id>.patch` de `load.status` à la version de ce pack.
- `resolve` lance `load/main` seulement quand ces scores égalent la version de ce pack, de sorte que la copie la plus récente du pack est celle qui se charge.
- `main` lance `secondary` sauf si `#<id>.loaded` vaut déjà 1.
- `set_items_storage` remplit le storage des items.

Les tags `#<id>:enumerate` et `#<id>:resolve` appellent `enumerate` et `resolve`.

Au chargement, les joueurs qui ont le tag `convention.debug` reçoivent `[Loaded <name> v<version>]` dans le chat.

Pour un pack qui supporte Minecraft 26.3 ou plus récent, la convention Smithed pack enabled : le tag de predicate `#<id>:installed` et les tags de context int provider `#<id>:major`, `#<id>:minor` et `#<id>:patch`, que les autres packs lisent quel que soit l'ordre de chargement.

Il écrit aussi l'enchantment caché de chaque item qui a un `ranged_weapon`, et une vérification qui rend ce qu'une crossbow avait chargé à la place de sa munition.

## Options

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `version` | obligatoire | `major.minor.patch`, comparé aux autres copies du pack |
| `id` | obligatoire | Le namespace de chaque function et storage écrits |
| `name` | l'`id` | Le nom affiché dans le message de chargement |
| `meta.stewbeet.items_storage` | `true` | Remplit `<id>:items` au chargement. `datapack.custom_blocks` et `compatibilities.simpledrawer` le lisent. Mettez `false` pour sauter la function et le storage |

## Limites

- Une version qui n'est pas `major.minor.patch`, ou un `id` ou une `version` manquants, fait échouer le build.
- Le storage des items contient les définitions telles que déclarées au build. Il n'est pas mis à jour pendant que le monde tourne.
- Un pack avec beaucoup d'items lance un `data modify` par item à chaque chargement, ce qui fait grossir `set_items_storage`.

## Pour continuer

- [Définir des items et des blocks](../1_definitions_setup/fr.md) : où sont déclarés les items stockés ici.

