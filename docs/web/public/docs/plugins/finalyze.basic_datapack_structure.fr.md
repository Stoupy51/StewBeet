
# Tick, second and minute functions

Lance les functions que vous écrivez sous les noms `tick_2`, `second`, `second_5` et `minute` à leur intervalle, sans timer à écrire vous-même.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.finalyze.basic_datapack_structure`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py)

## Écrire une function minutée

Écrivez la function avec le helper versionné :

```python
write_versioned_function("second", """
scoreboard players add #seconds simplenergy.data 1
""")
```

Le plugin n'ajoute un timer que pour une function qui existe quand il tourne. Les functions écrites plus tard dans le pipeline sont manquées.

| Function | Tourne | Score auquel elle tourne |
|---|---|---|
| `tick_2` | Tous les 2 ticks | 3 |
| `second` | Tous les 20 ticks | 20 |
| `second_5` | Tous les 100 ticks | 90, après une remise à -10 |
| `minute` | Tous les 1200 ticks | 1201, après une remise à 1 |

Pour lancer quelque chose sur chaque exemplaire posé d'un block, utilisez plutôt [Block ticking](finalyze.custom_blocks_ticking.fr.md).

## Ce que ce plugin écrit

- Une ligne `Reset timer` en haut de chaque function minutée, qui remet `#<name>` de `<id>.data` à sa valeur de départ.
- Un paragraphe `Timers` en haut de la function `tick`. Il ajoute 1 à chaque timer, puis lance chaque function dont le score a atteint son seuil.

Les valeurs de départ de `tick_2` et `second_5` diffèrent des autres exprès, pour que les functions ne tournent pas toutes au même tick.

La function `tick` ne tourne qu'une fois le pack chargé.

## Limites

- Un timer compte des ticks du serveur. Un serveur qui lag lance une function `second` moins d'une fois par seconde réelle.
- Seuls ces quatre intervalles existent.

## Pour continuer

- [Écrire des functions et des fichiers](../2_writing_to_files/fr.md) : `write_versioned_function` et les autres helpers.

