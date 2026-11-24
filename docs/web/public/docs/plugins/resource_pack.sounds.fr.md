
# Sounds

Transforme les fichiers `.ogg` de votre dossier de sons en sounds qu'une commande peut jouer, et écrit leur `sounds.json`.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.resource_pack.sounds`. Il a besoin de `sounds.folder` dans la section `stewbeet` de `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/sounds/__init__.py)

## Configurer et nommer vos fichiers

```yaml
meta:
  stewbeet:
    sounds:
      folder: assets/sounds
      exclude_patterns: ["debug/*"]
```

Les fichiers qui finissent par un nombre sont des variantes d'un même sound, et Minecraft en choisit une au hasard à chaque lecture.

```text
dirt_bullet_impact_01.ogg
dirt_bullet_impact_02.ogg
dirt_bullet_impact_03.ogg
fireselect.ogg
```

```mcfunction
playsound simplenergy:dirt_bullet_impact master @s
```

`name_01` et `name1` se regroupent tous deux sous `name`. Un sous-dossier fait partie du nom : `guns/shot_1.ogg` se joue sous `simplenergy:guns/shot`.

## Ce que ce plugin écrit

- `sounds/<file>.ogg` : chaque fichier, son nom en minuscules avec les espaces en `_`.
- `sounds.json` : un event par nom, qui liste ses variantes. Le sous-titre est le nom de fichier sans son nombre final.

Un fichier de plus de 10 secondes est réglé sur `stream`, pour que le jeu ne le charge pas en entier.

## Options

| Option | Défaut | Ce qu'elle fait |
|---|---|---|
| `sounds.folder` | obligatoire | Le dossier analysé pour les fichiers `.ogg`, sous-dossiers compris |
| `sounds.exclude_patterns` | `[]` | Motifs glob, relatifs au dossier, des fichiers à ignorer |

## Limites

- Seuls les fichiers `.ogg` sont lus. Un dossier qui n'en a aucun n'écrit rien.
- Un nom d'event ne garde que les lettres, chiffres, `.`, `_` et `/`, donc `Gun Shot.ogg` se joue sous `gun_shot`.
- Depuis votre propre code, `add_sound(ctx, sound, name)` dans `stewbeet.core.utils.sounds` ajoute un sound au même `sounds.json`.

## Pour continuer

- [Définitions](../1_definitions_setup/fr.md#music-discs) : des music discs à partir de fichiers de sons.

