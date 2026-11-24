
# Zip archives

Zippe votre datapack et votre resource pack dans le dossier de build, avec les mêmes octets sur chaque machine pour les mêmes sources.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.archive`, et a besoin de `output` dans `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/archive/__init__.py)

## Ce que ce plugin écrit

Dans le dossier `output`, pour un projet nommé `Stardust Fragment` :

- `StardustFragment_datapack.zip` : le datapack. Le nom est celui du projet sans ses espaces.
- `StardustFragment_resource_pack.zip` : le resource pack.

Les deux zips sont écrits en parallèle, et chaque entrée suit les mêmes règles :

- Sa date est celle du dernier commit git de `beet.yml`, en UTC, si bien que chaque clone la date pareil. Hors d'un dépôt git, la date est celle du dossier de cache de beet, et quand il manque, le 2025-01-01.
- Un fichier texte (`.json`, `.mcfunction`, `.mcmeta`, `.properties`, `.lang`, `.md` et quelques autres) est stocké avec des fins de ligne Unix, même si vous compilez sous Windows.
- Une entrée dont le contenu n'a pas changé depuis le build précédent est recopiée encore compressée, ce qui garde un rebuild rapide.
- `pack.png` est remplacé par l'icône du projet, quand votre projet en a une.

Quand les source maps sont activées, leurs fichiers sont ajoutés aux packs avant d'être zippés : le plugin n'a donc besoin d'aucune entrée `source_maps.emit` avant lui.

## Limites

- Tout ce qui lit les zips (le [Smithed Weld merge](merge_smithed_weld.fr.md), le [copy to destination](copy_to_destination.fr.md), les [SHA-1 hashes](compute_sha1.fr.md)) doit venir après lui dans le `pipeline`.
- Un zip verrouillé par un autre programme, comme un jeu qui lit le fichier, est retenté 10 fois, à 0,5 seconde d'intervalle. Passé ce délai, le build signale l'erreur.
- `stewbeet.plugins.archive.silent` lance le même plugin et masque sa sortie de log.

## Pour continuer

- [Configurer le build](../3_beet_config/fr.md#pipeline) : où se place un plugin dans le `pipeline`.

