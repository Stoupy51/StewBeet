
# Block ticking

Lance une function de votre block sur chaque exemplaire posé, à chaque tick, seconde ou minute, ou quand un joueur clique dessus. Écrivez la function et ce plugin la trouve.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.finalyze.custom_blocks_ticking`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/finalyze/custom_blocks_ticking/__init__.py)

## Faire tick un block

Écrivez l'une de ces functions dans le dossier du block, `custom_blocks/<block>/` :

| Function | Tourne |
|---|---|
| `tick` | À chaque tick, 20 fois par seconde |
| `tick_2` | Tous les 2 ticks |
| `second` | Chaque seconde |
| `second_5` | Toutes les 5 secondes |
| `minute` | Chaque minute |

Prenez son chemin depuis le block plutôt que de le taper :

```python
obj = Block.from_id("solar_panel")
write_function(obj.functions.second, """
scoreboard players add @s energy.storage 5
""")
```

La function tourne en tant qu'item display du block, à sa position.

## Réagir à un clic

Un block dont l'hôte a une [Interaction](../1_definitions_setup/fr.md#interaction) peut aussi avoir ces functions :

| Function | Tourne | Le joueur |
|---|---|---|
| `right_click` | Quand un joueur utilise le block | Tagué `<namespace>.user` |
| `left_click` | À chaque coup, avant qu'il compte dans `hits`, y compris celui qui le casse | Tagué `<namespace>.breaker` |

```python
obj = Block.from_id("control_panel")
write_function(obj.functions.right_click, """
tellraw @p[tag=my_pack.user] "Panel switched on"
""")
```

Elles tournent aussi en tant qu'item display du block, à sa position. Un siège assoit toujours le joueur, et lance aussi son `right_click`.

## Ce que ce plugin écrit

Pour chaque nom de function qu'un block utilise, ici `second` :

- Le `place_secondary` du block donne à son display le tag `<namespace>.second` et le compte dans `#second_entities`.
- Son `destroy` le retire du compte.
- La function `second` du pack appelle `custom_blocks/second` tant que le compte est supérieur à 0.
- `custom_blocks/second` envoie chaque display tagué vers la function de son block :

```mcfunction title="custom_blocks/second.mcfunction"
execute if entity @s[tag=simplenergy.solar_panel] run function simplenergy:custom_blocks/solar_panel/second
execute if entity @s[tag=simplenergy.pulverizer] run function simplenergy:custom_blocks/pulverizer/second
```

`/function <namespace>:_stats_custom_blocks` liste aussi combien de blocks posés lancent chaque function.

## Limites

- Le tag est donné quand un block est posé. Un block posé avant l'existence de sa function ne la lance pas tant qu'il n'est pas cassé puis reposé.
- Seule compte une function nommée exactement comme dans le tableau, directement dans le dossier du block.
- Une function de clic sur un block sans `Interaction` fait échouer le build, car aucun autre hôte ne dit qu'un joueur a cliqué dessus.
- Utiliser une interaction n'utilise jamais l'item en main : un joueur ne peut donc pas poser de block contre elle.
- Mille blocks sur `tick` lancent leur function 20 000 fois par seconde. Le guide [Performance](../10_performance/fr.md) montre ce qu'il faut passer sur `second`.

## Pour continuer

- [Performance](../10_performance/fr.md) : garder de nombreux blocks qui tickent peu coûteux.

