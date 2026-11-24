
# Live reload

Recharge votre datapack dans le jeu après chaque build, sans `beet link` et sans `/reload` manuel.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.livereload`, dans `require`, et lit les dossiers de datapack de `build_copy_destinations`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/livereload/__init__.py)

## L'utiliser

```yaml
require:
  - "stewbeet.plugins.livereload"

meta:
  stewbeet:
    build_copy_destinations:
      datapack:
        - "C:/mc/saves/world/datapacks"
```

```bash
stewbeet watch
```

Chaque rebuild copie le datapack, et le jeu lance `/reload` de lui-même. Le chat affiche `livereload - Reloaded`. Un projet aussi lié avec `beet link` recharge également ce dossier.

## Ce que ce plugin écrit

- `livereload` : un petit datapack d'aide déposé dans chaque destination locale de datapack et dans le dossier de `beet link`. Il fait recharger le jeu quand il apparaît.
- `livereload.zip` : la même aide, envoyée à chaque destination `sftp://`.

L'aide du build précédent est retirée d'abord, puisque le jeu ne recharge que lorsqu'une aide apparaît. Elle est retirée de nouveau une fois le rechargement visible dans le `logs/latest.log` du client.

## Options

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `build_copy_destinations.datapack` | `[]` | Les dossiers de datapack à recharger, chemins locaux ou URL `sftp://` |
| `livereload.minecraft` | détecté | Le dossier qui contient le `logs/latest.log` du client sur lequel vous jouez |

Le dossier de logs est cherché dans cet ordre : `livereload.minecraft`, le dossier Minecraft de `beet link`, chaque destination `resource_pack` et ses parents, puis la première destination de datapack et ses parents.

Pour un serveur distant, pointez `livereload.minecraft` vers votre propre client, car seul votre client journalise le rechargement :

```yaml
meta:
  stewbeet:
    livereload:
      minecraft: "C:/Users/you/AppData/Roaming/.minecraft"
    build_copy_destinations:
      datapack:
        - "sftp://user@host/mc/datapacks"
```

Les identifiants SFTP sont lus comme pour [Copy to destination](copy_to_destination.fr.md).

## Limites

- Aucun dossier de logs trouvé : l'aide est quand même copiée, mais un avertissement signale que le nettoyage est désactivé, et elle reste dans la destination.
- Un dossier `datapacks` distant manquant avertit, et cette destination est ignorée. Un envoi raté avertit aussi.
- Chaque destination, locale et distante, reçoit l'aide.

