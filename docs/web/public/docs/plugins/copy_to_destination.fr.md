
# Copy to destination

Copie les packs compilés dans vos dossiers de jeu ou sur un serveur après chaque build, pour que le jeu fasse toujours tourner le dernier.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.copy_to_destination`. Il ne fait rien tant que `build_copy_destinations` n'est pas défini. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/copy_to_destination/__init__.py)

## Définir les destinations

```yaml
meta:
  stewbeet:
    build_copy_destinations:
      datapack:
        - "D:/world/datapacks"
        - "sftp://bob@host/dp"
      resource_pack:
        - "D:/minecraft/resourcepacks"
```

Un dossier local doit déjà exister, sinon le build avertit et l'ignore.

Pour `sftp://user@host/path`, le mot de passe vient de l'URL (`sftp://user:password@host/path`), puis de `~/stewbeet/credentials.yml`. Sans mot de passe, les clés SSH locales et l'agent sont essayés.

```yaml
sftp:
  bob@host:
    password: "..."
```

## Ce que ce plugin écrit

Dans chaque destination `datapack` :

- `StardustFragment_datapack.zip` : votre datapack, sans ses bibliothèques.
- Chaque zip de `libs/datapack/`, sous son propre nom.
- Chaque bibliothèque officielle que vos functions utilisent, sous le nom `<library>.zip`.

Dans chaque destination `resource_pack` :

- `StardustFragment_resource_pack_with_libs.zip` quand le [Smithed Weld merge](merge_smithed_weld.fr.md) l'a écrit, sinon `StardustFragment_resource_pack.zip`.

## Options

À définir dans `meta.stewbeet`.

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `build_copy_destinations.datapack` | `[]` | Dossiers ou URL `sftp://` qui reçoivent le datapack et ses bibliothèques |
| `build_copy_destinations.resource_pack` | `[]` | Dossiers ou URL `sftp://` qui reçoivent le resource pack |
| `libs_folder` | `"libs"` | D'où sont lus les zips de bibliothèques |
| `libs_exclude_patterns` | `[]` | Zips de bibliothèques à écarter, voir le [Smithed Weld merge](merge_smithed_weld.fr.md#options) |

## Limites

- Un fichier local est supprimé, puis copié. Quand le jeu le retient, la copie retente 10 fois, à une seconde d'intervalle.
- Deux destinations qui mènent au même dossier, par un lien par exemple, reçoivent le fichier une seule fois.
- Un fichier déjà présent sur un serveur SFTP avec les mêmes SHA-1 et taille que le dernier envoi n'est pas renvoyé.
- Un dossier distant qui n'existe pas n'est jamais créé : le build avertit et l'ignore.
- Les bibliothèques de `libs/resource_pack/` ne sont pas copiées seules. Elles n'atteignent une destination de resource pack que par le pack fusionné.

## Pour continuer

- [Configurer le build](../3_beet_config/fr.md#build_copy_destinations) : la clé en contexte.
- [Live reload](livereload.fr.md) : recharge le jeu quand un build arrive dans ces dossiers.

