
# Smithed Weld merge

Fusionne votre pack avec les bibliothèques dont il a besoin dans un `_with_libs.zip` par type de pack, prêt à publier ou à déposer dans un monde.

Le template `basic` lance `stewbeet.plugins.merge_smithed_weld` et le template `extensive` lance ses deux moitiés, `stewbeet.plugins.merge_smithed_weld.datapack` et `stewbeet.plugins.merge_smithed_weld.resource_pack`. Il lit les zips de [Zip archives](archive.fr.md). [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/merge_smithed_weld/__init__.py)

## Choisir ce qui est fusionné

Le welding coûte quelques secondes à chaque build. Ne listez que les types de pack que vous livrez :

```yaml
pipeline:
  - stewbeet.plugins.archive
  - stewbeet.plugins.merge_smithed_weld.datapack
```

L'entrée simple fusionne les deux, comme si vous listiez les deux moitiés.

## Ce que ce plugin écrit

Dans le dossier `output` :

- `StardustFragment_datapack_with_libs.zip` : votre datapack, les zips de `libs/datapack/`, puis les [bibliothèques officielles](../5_dependencies/fr.md#bibliotheques-officielles) que vos functions utilisent.
- `StardustFragment_resource_pack_with_libs.zip` : la même chose pour le resource pack, avec `libs/resource_pack/`.

Smithed Weld résout les fichiers que deux packs fournissent tous les deux. Votre propre pack vient en dernier, donc son `pack.mcmeta` et son `pack.png` l'emportent. Quand une fusion a les mêmes sources que le dernier build, le zip sur le disque est gardé tel quel.

## Options

À définir dans `meta.stewbeet`.

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `libs_folder` | `"libs"` | Le dossier qui contient `datapack/*.zip` et `resource_pack/*.zip` |
| `libs_exclude_patterns` | `[]` | Motifs glob, relatifs à `libs_folder`, des zips de bibliothèques à écarter, comme `"resource_pack/*ARAM*.zip"` |

Un zip exclu est écarté du build entier : il n'est ni fusionné ni copié vers une destination.

## Limites

- Un type de pack a besoin de votre propre zip et d'au moins une bibliothèque. Sans rien à fusionner, le build avertit `No datapacks or libs to merge` et n'écrit aucun `_with_libs.zip`.
- Un type de pack qu'aucune entrée du `pipeline` ne fusionne voit son `_with_libs.zip` supprimé de `output`. Un zip laissé par un ancien build serait sinon haché et envoyé comme s'il était à jour.
- Quand un weld échoue, le build affiche l'erreur et le `_with_libs.zip` est celui du dernier bon build.
- Le resource pack fusionné retire l'entrée `__smithed__` de ses fichiers de langue, qui empêcherait Minecraft de charger la langue.

## Pour continuer

- [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md) : comment les bibliothèques officielles sont détectées et téléchargées.
- [Configurer le build](../3_beet_config/fr.md#metastewbeet) : `meta.stewbeet`.

