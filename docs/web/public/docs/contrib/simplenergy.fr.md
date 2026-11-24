
# SimplEnergy

Des helpers pour un pack dont les machines tournent sur [DatapackEnergy](https://github.com/ICY105/DatapackEnergy), la bibliothèque d'énergie qu'utilise SimplEnergy : des batteries qui gardent leur charge, de l'énergie partagée entre appareils voisins, des câbles et des servos qui changent de forme en se connectant, des écrans de machine dessinés par le resource pack, et des blocks que la wrench fait tourner.

Importez-les depuis `stewbeet.contrib.simplenergy` et appelez chacun depuis votre `beet_default`, comme le fait SimplEnergy dans [`src/link.py`](https://github.com/Stoupy51/SimplEnergy/blob/main/src/link.py). [Source](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/contrib/simplenergy)

## L'énergie vient du block

Un block rejoint le réseau d'énergie par l'`energy` de son `custom_data`. Le plugin [Custom blocks](../plugins/datapack.custom_blocks.fr.md) le lit, sans aucun appel de votre part :

```python title="src/definitions/additions/energy.py"
Block(
  id="wind_turbine",
  ...
  components={"custom_data": {"energy": {
    "generation": 20,
    "max_storage": 800,
    "blocked_faces": ["top"],
  }}},
)
```

| Clé | Ce qu'elle fait du block |
|---|---|
| `generation` | Un générateur, qui produit autant de kW |
| `usage` | Une machine, qui consomme autant de kW |
| `transfer` | Un câble, avec ce débit de transfert |
| `max_storage` | Le maximum qu'il contient, en kJ. Sans aucune des trois clés ci-dessus, le block est une batterie |
| `storage` | La charge d'une batterie quand l'item est posé, en kJ |
| `blocked_faces` | Les faces auxquelles un câble ne peut pas se connecter : `top`, `bottom`, `front`, `back`, `left`, `right` |

## Les batteries gardent leur charge

```python
keep_energy_for_batteries([
  "simple_battery",
  "advanced_battery",
])
```

Une batterie cassée lâche un item qui contient sa charge, affichée dans son lore, et la retrouve une fois reposée. Deux batteries chargées ne s'empilent jamais.

Il ajoute au `destroy` et au `replace_item` de chaque batterie, et écrit `utils/keep_energy` et `calls/update_energy_lore/`, ce dernier dans le tag `#energy:v1/update_energy_lore/main`.

## Les voisins partagent leur énergie

```python
setup_energy_balancing([
  "solar_panel",
  "simple_battery",
])
```

Toutes les 5 secondes, les blocks qui se touchent, de même type et de même `max_storage`, répartissent leur énergie à parts égales. Un block déclenche un partage dès qu'il contient 20 kJ, et l'énergie qu'un block plein ne peut pas absorber est perdue.

Il écrit `balancing/`, un appel dans `second_5`, et le tag `<namespace>.can_balance` donné à chaque block à la pose.

## Câbles d'énergie

```python
energy_cables_models([
  "simple_cable",
  "elite_cable",
])
```

Chaque câble a besoin de `<textures_folder>/<cable>.png`, disposé comme le [`simple_cable.png`](https://github.com/Stoupy51/SimplEnergy/blob/main/assets/textures/simple_cable.png) de SimplEnergy. Il reçoit 64 models, un par ensemble de côtés connectés, et DatapackEnergy en choisit un à chaque changement d'un voisin.

Il écrit `calls/energy/cable_update`, dans le tag `#energy:v1/cable_update`.

## Câbles d'items

```python
item_cables_models({
  "basic_item_cable": None,
})
```

Avec `None`, les textures sont `<cable>/center`, `<cable>/pillon` et `<cable>/glass` sous le dossier de textures. Un dictionnaire des clés de texture du model `"0"`, `"1"` et `"2"` vers d'autres chemins les remplace.

Un câble posé rejoint le réseau [ItemIO](https://github.com/edayot/ItemIO) et le quitte quand il est cassé. Le pack écrit `calls/itemio/cable_update`, dans le tag `#itemio:event/cable_update`.

## Mécanismes servo

```python
servo_mechanisms_models({
  "servo_extractor": {"type": "extract"},
  "servo_inserter": {"type": "insert"},
})
```

Un servo déplace des items entre des conteneurs ItemIO. Ses textures sont par défaut `<type>_default` et `<type>_connected`, et sa texture "off" est une copie grise assombrie de celle par défaut. Un joueur éteint un servo en le faisant tourner dans son item frame, et le rallume d'un tour de plus.

Il écrit `utils/servo/`, une advancement sur `player_interacted_with_entity`, et `calls/itemio/network_update`, dans le tag `#itemio:event/network_update`.

## Écrans de machine

```python
gui = setup_gui_in_resource_packs({
  "electric_furnace":
    GuiTranslation.furnace_bottom,
})
```

Chaque PNG de `<textures_folder>/gui/` devient un item model. Celui dont le nom contient une clé du dictionnaire est dessiné sur tout l'écran du conteneur, depuis le slot que nomme sa `GuiTranslation` :

| Translation | Slot qui porte le model |
|---|---|
| `furnace_bottom` | Le slot de combustible d'un furnace |
| `furnace_top` | Le slot d'ingrédient d'un furnace |
| `brewing_stand` | Le slot de combustible d'un brewing stand |
| `barrel_bottom_right` | Le 27e slot d'un barrel |

Tout autre PNG devient un item plat. La function renvoie le model de chaque fichier, comme `{"gui/electric_furnace.png": "simplenergy:gui/electric_furnace"}`, pour l'item que vous mettez dans ce slot.

## La wrench fait tourner vos machines

```python
setup_wrench([
  "electric_furnace",
  "pulverizer",
])
```

Tague chaque block `simplenergy.rotatable` à la pose. Une chaîne à la place de la liste, comme `"all"`, prend chaque block posé face au joueur, et chaque block à interaction dont le display fait face au joueur. La wrench de Mechanization le fait alors tourner avec `simplenergy:utils/wrench/rotate`, une function de SimplEnergy : le pack tourne donc à côté de SimplEnergy. `tag_ns="<namespace>"` utilise à la place votre propre tag et votre propre function.

La wrench casse aussi n'importe lequel de vos blocks custom, par `#mechanization:wrench_break`.

Utiliser un block à [interaction](../1_definitions_setup/fr.md#interaction) n'utilise jamais l'item en main. Les outils de SimplEnergy entendent ce clic d'eux-mêmes, et ceux de Mechanization le reçoivent par `#<namespace>:calls/mechanization/right_click` quand votre pack a un tel block.

## Limites

- DatapackEnergy, et ItemIO pour les câbles d'items et les servos, doivent faire partie des [bibliothèques](../5_dependencies/fr.md) du pack.
- `insert_lib_calls()` ne fait rien : le plugin Custom blocks enregistre les blocks d'énergie. Retirez l'appel.

## Pour continuer

- [Custom blocks](../plugins/datapack.custom_blocks.fr.md) : toutes les options d'un block posable.

