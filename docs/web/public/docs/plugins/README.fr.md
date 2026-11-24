
# Plugins

Chaque ligne du `pipeline` d'un projet dans `beet.yml` est un plugin : il lit vos définitions et les packs que beet détient, et écrit les fichiers dont ils ont besoin. Cette page les liste selon ce qu'ils écrivent.

## Activer ou désactiver un plugin

Les templates `basic` et `extensive` lancent tous les plugins ci-dessous. Retirez de la liste un plugin dont vous n'avez pas besoin, et le build suivant n'écrit aucun de ses fichiers. Le template `minimal` ne lance que [Function headers](auto.headers.fr.md).

```yaml
pipeline:
    - "src.setup_definitions"
    - "stewbeet.plugins.resource_pack.item_models"
    - "stewbeet.plugins.custom_recipes.silent"
    - "stewbeet.plugins.datapack.custom_blocks"
    - "mecha"
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"
```

- L'ordre compte : un plugin voit les fichiers de ceux qui le précèdent. Les plugins `finalyze` tournent après `mecha`, une fois que toutes les functions existent.
- Ajoutez `.silent` à n'importe quel plugin StewBeet pour masquer ce qu'il affiche pendant le build.
- [Live reload](livereload.fr.md) va sous `require`, puisqu'il agit sur le build entier. [Source maps](source_maps.fr.md) y va aussi, avec son étape `source_maps.emit` près de la fin du `pipeline`.

[Comment StewBeet s'articule avec beet](../how_it_fits/fr.md) explique `require` et `pipeline`, et la [référence de beet.yml](../3_beet_config/fr.md) liste toutes les options.

## Items et blocks

- [Custom blocks](datapack.custom_blocks.fr.md) : rend chaque `Block` de vos définitions posable.
- [Block ticking](finalyze.custom_blocks_ticking.fr.md) : lance une function de votre block sur chaque exemplaire posé, à chaque tick, seconde ou minute.
- [Loot tables](datapack.loot_tables.fr.md) : une loot table pour chaque item, et une function qui donne tous les items dans des coffres.
- [Paintings](custom_paintings.fr.md) : transforme chaque `Painting` en variante que les joueurs peuvent poser.
- [Manuel en jeu](../7_ingame_manual/fr.md) : un livre qui liste vos items et leurs recipes.

## Recipes

- [Recipes](custom_recipes.fr.md) : transforme les `recipes` de chaque item en fichiers et functions de recipe, pour le fabriquer, le cuire, le découper ou le forger.

## Resource pack

- [Item models](resource_pack.item_models.fr.md) : le model et la définition `items/` de chaque item et block, à partir d'une texture nommée comme lui.
- [Sounds](resource_pack.sounds.fr.md) : transforme les fichiers `.ogg` de votre dossier de sons en sounds et en `sounds.json`.
- [Texture size check](resource_pack.check_power_of_2.fr.md) : signale les textures dont les côtés ne sont pas des puissances de 2.
- [Unused textures](check_unused_textures.fr.md) : signale les textures que rien n'utilise.

## Texte et traductions

- [Lang file](auto.lang_file.fr.md) : déplace le texte de vos commandes et loot tables dans `lang/en_us.json`.
- [Item images in text](auto.text_renders.fr.md) : permet à un text component d'afficher l'image d'un item.

## Functions

- [Load functions](datapack.loading.fr.md) : charge votre pack une seule fois et compare sa version à celle d'autres copies de lui-même.
- [Tick, second and minute functions](finalyze.basic_datapack_structure.fr.md) : lance `tick_2`, `second`, `second_5` et `minute` à leur intervalle.
- [Scoreboard constants](auto.scoreboard_constants.fr.md) : déclare chaque nombre que vous utilisez comme score holder.
- [List sorting](datapack.sorters.fr.md) : des functions qui trient une liste dans un storage.
- [Function headers](auto.headers.fr.md) : un commentaire en tête de chaque function, qui dit ce qui l'appelle et avec quels arguments de macro.

## Zips et copies

- [Zip archives](archive.fr.md) : zippe les deux packs, avec les mêmes octets sur chaque machine.
- [Smithed Weld merge](merge_smithed_weld.fr.md) : un `_with_libs.zip` par type de pack, bibliothèques comprises.
- [SHA-1 hashes](compute_sha1.fr.md) : le SHA-1 de chaque zip dans un seul fichier JSON.
- [Copy to destination](copy_to_destination.fr.md) : copie les packs compilés dans vos dossiers de jeu ou sur un serveur.

## Développement

- [Project setup](initialize.fr.md) : le `pack.mcmeta` des deux packs et une ligne de lore source sur chaque item.
- [Live reload](livereload.fr.md) : recharge votre datapack dans le jeu après chaque build.
- [Source maps](source_maps.fr.md) : relie chaque commande générée à la ligne Python qui l'a écrite.

## Compatibilité

- [Library version checks](finalyze.dependencies.fr.md) : refuse de se charger quand une bibliothèque ou la version de Minecraft est trop ancienne.
- [SimpleDrawer](compatibilities.simpledrawer.fr.md) : des drawers compactants pour vos ingots, nuggets et blocks.
- [NeoEnchant](compatibilities.neo_enchant.fr.md) : Veinminer mine vos minerais custom.

