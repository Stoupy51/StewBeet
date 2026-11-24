
# Tout ce à quoi vous n'avez pas à penser

Un datapack est surtout de la paperasse : des tags qui le démarrent, des scores qui comparent les versions, un fichier model par item, un pack.mcmeta qui correspond au jeu, un zip utilisable pour une release. StewBeet écrit tout cela à partir de vos définitions et de votre `beet.yml`. Cette page le liste par domaine, avec un lien vers le plugin derrière chaque point.

## Chargement et ticking

- Votre pack reçoit la séquence de chargement de la convention Lantern Load : le tag `minecraft:load`, les tags `load:` auxquels d'autres packs se branchent, et un objective `load.status` remis à zéro à chaque `/reload`. Les load tags de vos bibliothèques passent avant les vôtres.
- Deux copies du même pack dans un monde ne se chargent pas toutes les deux. Chaque copie élève les scores `#<id>.major`, `#<id>.minor` et `#<id>.patch` à sa propre version, et seule la copie qui relit sa propre version se charge. Les functions se trouvent sous `<id>:v<version>/`, donc les versions n'écrasent jamais les fichiers des autres. Voir [Load functions](../plugins/datapack.loading.fr.md).
- La function de chargement ne peut pas tourner deux fois, et la function `tick` ne tourne qu'une fois le pack chargé.
- Les joueurs dont le nom est dans `author` reçoivent le tag `convention.debug`, et reçoivent `[Loaded <name> v<version>]` dans le chat au chargement du pack.
- Pour un pack qui supporte Minecraft 26.3 ou plus récent, d'autres packs peuvent détecter le vôtre grâce aux tags Smithed `#<id>:installed`, `#<id>:major`, `#<id>:minor` et `#<id>:patch`.
- Chaque item de vos définitions est placé dans le storage `<id>:items` au chargement.
- Une function nommée `tick`, `tick_2`, `second`, `second_5` ou `minute` reçoit son timer. La function tick compte un score par timer et appelle la function quand le seuil est atteint. Voir [Tick, second and minute functions](../plugins/finalyze.basic_datapack_structure.fr.md).
- Un custom block qui a une function `second` ou `tick` dans son dossier reçoit le tag, le compteur et le dispatcher qui l'exécutent pour chaque copie posée, ainsi qu'une ligne dans la function de stats. Voir [Block ticking](../plugins/finalyze.custom_blocks_ticking.fr.md).
- Chaque constante `#<n> <id>.data` utilisée par vos functions est définie au chargement. Vous écrivez le nombre là où vous en avez besoin. Voir [Scoreboard constants](../plugins/auto.scoreboard_constants.fr.md).
- Une function `unload` est construite en lisant vos functions : elle supprime chaque objective de scoreboard que vous ajoutez, supprime chaque champ d'un storage `<id>:` que vous modifiez, tue les entités que vous invoquez avec un tag personnalisé ou un UUID, et retire vos items aux joueurs. Elle appelle aussi la function `unload` d'une bibliothèque quand son archive en a une.

## Des fichiers à partir d'une seule définition

- Un item défini une fois reçoit son model, sa définition dans `items/` et sa texture dans le resource pack, trouvée par nom de fichier dans votre dossier de textures. Un block prend le bon model parent selon les faces qu'il trouve (`_front`, `_top`, `_side`), un arc ses états de tension, une machine allumée son model `_on`. Voir [Item models](../plugins/resource_pack.item_models.fr.md).
- Les textures déposées à la racine du dossier de textures sont renommées sur le disque avec les noms que cherchent les models : minuscules, `_up` devient `_top`, `_north` devient `_front`, et ainsi de suite. Le build avertit pour chaque renommage.
- Le même item reçoit une loot table, une de plus pour chaque quantité qu'une recipe donne, une loot table créative, et une function `_give_all` qui donne des coffres contenant chaque item, 27 par coffre. Voir [Loot tables](../plugins/datapack.loot_tables.fr.md).
- Les quatre appels de setup des templates remplissent le reste d'un item : son `item_model`, son nom tiré de son id, le lore de votre pack, une entrée `custom_data` sous votre namespace, et les flags d'ignore de Smithed.
- Le texte brut devient du texte traduisible. Chaque `{"text": "..."}` d'un fichier de votre datapack se transforme en component `translate` avec le texte comme fallback, et `en_us.json` est écrit avec les clés. La clé est l'id du projet plus le texte, et deux textes différents qui partageraient une clé reçoivent un suffixe numérique. Voir [Lang file](../plugins/auto.lang_file.fr.md).
- Vos fichiers de sons deviennent `sounds.json`. Les fichiers qui ne diffèrent que par un nombre final sont regroupés comme variantes d'un même événement, chaque variante reçoit son sous-titre, et un son de plus de 10 secondes est streamé. Voir [Sounds](../plugins/resource_pack.sounds.fr.md).
- Une clé `render` dans un text component est remplacée par un glyphe de cet item, dessiné par une font que le build génère. Voir [Item images in text](../plugins/auto.text_renders.fr.md).
- Chaque function reçoit un en-tête indiquant quelles functions, tags ou advancements l'appellent et dans quel contexte, et quels arguments de macro elle prend. Voir [Function headers](../plugins/auto.headers.fr.md).
- Votre `pack.png` est copié dans le datapack et le resource pack.

## Versions

- Les deux packs reçoivent le pack format de la version de Minecraft indiquée dans `beet.yml`, y compris les versions que beet ne connaît pas encore.
- `pack.mcmeta` est écrit pour vous : format, `min_format` et `max_format` là où le jeu les lit, `supported_formats` pour les anciennes versions, la description tirée de votre nom, version et auteur, et l'id de votre projet.
- La première et la dernière entrée de [`mc_supports`](../3_beet_config/fr.md#mc_supports) fixent la plage de formats, et `"infinite"` désigne la dernière version connue.
- Les overlays s'accordent sur leurs clés de format, puisque le jeu refuse un pack.mcmeta dont les overlays divergent.
- La plus basse release de `mc_supports` devient la version du jeu que demande le pack. Sur un jeu plus ancien, le pack affiche une erreur rouge dans le chat au lieu de fonctionner à moitié.

## Bibliothèques

- Vos functions sont scannées à la recherche des marqueurs des bibliothèques officielles, comme Smithed Custom Block ou un module Bookshelf. Chacune trouvée est téléchargée pour votre version de Minecraft depuis Smithed ou Modrinth, gardée dans le cache de beet, et ajoutée aux load tags. [Bibliothèques de datapack](../5_dependencies/fr.md) les liste.
- Pour chaque bibliothèque, et chacune que vous déclarez sous `load_dependencies`, le pack compare les scores de version de la bibliothèque avec celle contre laquelle il a été construit. Une bibliothèque absente ou périmée affiche une ligne cliquable avec son nom, la version requise et un lien. Voir [Library version checks](../plugins/finalyze.dependencies.fr.md).

## Sortie

- Les deux packs sont zippés en `<Name>_datapack.zip` et `<Name>_resource_pack.zip`, où `<Name>` est le nom de votre projet sans espaces. Chaque entrée porte la date du dernier commit de votre `beet.yml` (une date fixe hors de git), les entrées texte utilisent des fins de ligne Unix, et une entrée inchangée est copiée depuis le zip précédent. Les mêmes sources donnent le même zip sur n'importe quelle machine. Voir [Zip archives](../plugins/archive.fr.md).
- Chaque pack peut être fusionné avec vos bibliothèques dans un `_with_libs.zip`. Un `_with_libs.zip` d'un type de pack que votre pipeline ne weld pas est sorti du dossier de sortie, pour qu'une release ne reprenne jamais un zip périmé. Voir [Smithed Weld merge](../plugins/merge_smithed_weld.fr.md).
- `sha1_hashes.json` liste le SHA1 de chaque zip. Voir [SHA-1 hashes](../plugins/compute_sha1.fr.md).
- Les zips vont dans chaque dossier de `build_copy_destinations`, en local ou par SFTP. Un fichier distant qui contient déjà les mêmes octets n'est pas envoyé de nouveau. Voir [Copy to destination](../plugins/copy_to_destination.fr.md).

## Vérifications

Le build avertit ou échoue là où le jeu resterait silencieux.

- Une texture dont la taille n'est pas une puissance de 2 dans `item/` ou `block/` est listée avec sa taille. Voir [Texture size check](../plugins/resource_pack.check_power_of_2.fr.md).
- Un fichier de texture qu'aucun fichier JSON du resource pack ne référence est listé. Voir [Unused textures](../plugins/check_unused_textures.fr.md).
- Une ligne de function qui commence par `$` sans macro, ou une ligne qui utilise `$(name)` sans le `$` initial, est signalée avec sa function et son numéro de ligne, puisque le jeu n'exécuterait ni l'une ni l'autre telle quelle.
- Un id d'item qui contient `:` fait l'objet d'un avertissement et perd son namespace.
- Une texture dont un model a besoin et que le dossier n'a pas, ou un block dont les textures ne correspondent à aucune forme, est consigné comme erreur nommant le fichier manquant.
- Une `version` de projet qui n'est pas `major.minor.patch`, ou un `id`, `name`, `version` ou `author` manquant, arrête le build avant que quoi que ce soit ne soit écrit.

## Étapes suivantes

- [Plugins](../plugins/README.fr.md) : tout le pipeline, avec ce qu'écrit chaque plugin et comment le configurer.
- [Bibliothèques de datapack](../5_dependencies/fr.md) : les bibliothèques que le build télécharge et vérifie pour vous.
- [Publier des releases](../6_continuous_delivery/fr.md) : envoyer les zips sur GitHub, Modrinth et Smithed.

