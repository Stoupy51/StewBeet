
# Écrire des functions et des fichiers

Quatre façons d'ajouter vos propres functions, advancements et tags au pack : des fichiers statiques chargés par `beet.yml`, l'API native de beet, les fonctions d'aide de StewBeet, et Bolt.
Votre code s'exécute dans un plugin utilisateur, après la mise en place des définitions et avant la finalisation.

> Chaque approche ci-dessous finit avec des commandes dans une chaîne Python, dans un module `.bolt`, ou les deux. L'[extension StewBeet pour VSCode](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) les lit pour ce qu'elles sont : complétion, erreurs, ctrl+clic, et un lien de chaque bloc vers la function que votre build en a tirée. Voir [Éditeur VS Code](../8_editor/fr.md).

<video src="/vscode_extension.mp4" controls loop muted playsinline preload="auto">
</video>

Des fichiers complets à lire en parallèle de cette page :

- [extensive/src/link.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py), le template
- [SimplEnergy/src/utils/machines.py](https://github.com/Stoupy51/SimplEnergy/blob/main/src/utils/machines.py), un pack publié
- [StardustFragment/src/utils/remaining.py](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py), un pack publié

## Quelle approche choisir

| Approche | Idéale pour | Effort |
|----------|-------------|--------|
| Fichiers statiques (`beet.yml`) | Des functions et du JSON écrits à la main qui ne changent jamais | Le plus faible |
| API native de beet | Des types de fichiers inhabituels, un contrôle total sur chaque objet | Le plus élevé |
| Helpers StewBeet (recommandé) | La logique générée depuis vos définitions, les functions de load et d'horloge | Faible |
| Bolt | Une logique riche en commandes, des boucles et de l'arithmétique autour des commandes | Moyen, un second langage |

### Approche 1 : chargement de fichiers statiques (beet.yml)

Beet charge les fichiers écrits à la main depuis un dossier avant l'exécution de tout plugin.

```yaml
# In beet.yml
data_pack:
    name: "datapack"
    load: ["src"]  # Loads all .mcfunction and .json files from src/

resource_pack:
    name: resource_pack
    load: ["src"]  # Loads all texture, model, and sound files from src/
```

Fonctionnement :

- Placez les fichiers `.mcfunction` dans `src/data/<namespace>/function/`.
- Placez les fichiers `.json` dans `src/data/<namespace>/advancement/`, `src/data/<namespace>/recipe/`, et ainsi de suite.
- Beet les charge aux emplacements correspondants du pack.
- Les fichiers sont chargés avant l'exécution de tout code de plugin.

Un exemple de structure :

```text
src/
├── data/
│   └── simplenergy/
│       ├── function/
│       │   ├── load.mcfunction
│       │   └── tick.mcfunction
│       ├── advancement/
│       │   └── first_machine.json
│       └── recipe/
│           └── wrench.json
└── assets/
    └── simplenergy/
        └── textures/
            └── item/
                └── wrench.png
```

| Dossier | Contient |
|---------|----------|
| `data/` | Tout le contenu du datapack : functions, advancements, recipes, tags |
| `function/` | Les commandes Minecraft, en fichiers `.mcfunction` |
| `advancement/` | Les succès et les déclencheurs techniques, en `.json` |
| `recipe/` | Les recipes de craft, de cuisson et autres, en `.json` |
| `assets/` | Tout le contenu du resource pack : textures, models, sons |
| `textures/` | Les images PNG des items, des blocks et du reste |

À utiliser quand :

- Vous avez des fichiers statiques qui n'ont pas besoin d'être générés.
- Vous organisez des commandes et des données déjà écrites.

À éviter quand :

- Vous devez générer du contenu depuis vos définitions.
- Vous devez combiner plusieurs sources de données.
- Vous devez générer des fichiers sous condition.

---

### Approche 2 : API native de beet

L'API d'objets de beet, utilisée directement depuis un plugin.

```python
from beet import Context, Function, Advancement, FunctionTag
from stouputils.typing import JsonDict

def beet_default(ctx: Context):
    # Writing a function
    ctx.data["simplenergy"].functions["machines/charge"] = Function("""
# Charge every machine
say Charging machines
scoreboard players add @a energy 1
""")

    # Writing an advancement
    advancement_data: JsonDict = {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": "simplenergy:rewards/first_machine"
        }
    }
    ctx.data["simplenergy"].advancements["first_machine"] = Advancement(advancement_data)

    # Writing a function tag
    tag_data: JsonDict = {
        "values": [
            "simplenergy:machines/charge",
            "simplenergy:machines/discharge"
        ]
    }
    ctx.data.function_tags["minecraft:load"] = FunctionTag(tag_data)
```

À utiliser quand :

- Vous avez besoin d'un contrôle total sur les objets fichier.
- Vous travaillez avec des structures imbriquées complexes.

À éviter quand :

- Vous voulez écrire des fichiers rapidement.
- Vous écrivez beaucoup de petites functions.
- Vous avez besoin d'une gestion automatique des chemins.

---

### Approche 3 : fonctions d'aide de StewBeet (recommandé)

Les helpers StewBeet prennent un chemin et une chaîne, créent le fichier ou y ajoutent du contenu, et savent où se trouvent les functions de load, de tick et d'horloge.

```python
from beet import Context
from stewbeet import write_function, write_load_file, write_tick_file, write_versioned_function

def beet_default(ctx: Context):
    ns = ctx.project_id

    # Write a simple function
    write_function(f"{ns}:machines/charge", """
# Charge every machine
say Charging machines
scoreboard players add @a energy 1
""")

    # Append to the load file (runs when the datapack loads: "your_namespace:v{version}/load/confirm_load")
    write_load_file("""
# Initialize scoreboards
scoreboard objectives add energy dummy
scoreboard objectives add data dummy
""")

    # Append to the tick file (runs every game tick: "your_namespace:v{version}/tick")
    write_tick_file(f"""
# Check for players with a full battery
execute as @a[scores={{energy=100..}}] run function {ns}:machines/discharge
""")

    # Write a clock function ("your_namespace:v{version}/second")
    write_versioned_function("second", """
# Runs every second (20 ticks)
execute as @a run title @s actionbar {"score":{"name":"@s","objective":"energy"}}
""")

    write_versioned_function("minute", """
# Runs every minute (1200 ticks)
say One minute has passed!
""")
```

La function de tick appelle les functions d'horloge `tick_2`, `second`, `second_5` et `minute` quand vous les écrivez : un fichier écrit avec `write_versioned_function` sous l'un de ces noms s'exécute donc à cet intervalle.

À utiliser quand :

- Vous voulez un code lisible avec une gestion automatique des chemins.
- Vous suivez les conventions de StewBeet (functions versionnées, fichiers load et tick).
- Vous voulez ajouter du contenu à la fin ou au début.

À éviter quand :

- Vous avez besoin d'une organisation de fichiers non standard.
- Le projet n'utilise pas StewBeet.

---

### Approche 4 : Bolt

[Bolt](https://github.com/mcbeet/beet/tree/main/packages/bolt) est la couche de scripting de mecha.
Les trois approches ci-dessus mettent les commandes dans une chaîne Python. Dans un fichier `.bolt`, les commandes font partie de la syntaxe : `item = 3` est du Python et `item modify entity @s weapon.mainhand set value ...` est une commande, à la même indentation, dans la même portée.

Tout s'exécute au moment du build. Rien de Python n'arrive dans le datapack.

Le template Basic liste déjà `bolt` dans `require` et `mecha` dans `pipeline`. Seul `entrypoint` est à ajouter :

```yaml
# In beet.yml
require:
    - "stewbeet"
    - "bolt"

pipeline:
    - "mecha"       # bolt needs mecha to compile what it produced

meta:
    bolt:
        entrypoint: "*"     # let any function file use bolt, not only modules
```

Deux sortes de fichiers :

- Les **modules**, des `.bolt` sous `data/<namespace>/module/`. Ils sont importables, et n'écrivent une function que là où ils en demandent une.
- Les **fichiers function**, des `.mcfunction` couverts par `entrypoint`. Le fichier *est* une function, écrite en bolt.

#### Écrire une function

```python
# src/data/voltaic/module/gui.bolt
MACHINES = ["pulverizer", "furnace", "smelter"]

for machine in MACHINES:
    function f"voltaic:gui/{machine}/open":
        playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
        data modify entity @s equipment.head set from storage voltaic:gui Icon
        tag @s add voltaic.watching
```

Trois functions issues d'une seule boucle. La f-string est le chemin, et le bloc indenté est le corps.

Un chemin est une valeur comme une autre : il peut être nommé, importé et passé en argument. Deux raccourcis évitent d'y écrire le namespace :

| Écrit    | Se résout en                                              |
|----------|-----------------------------------------------------------|
| `./load` | `<namespace>:<module path>/load`                           |
| `~/init` | Un enfant de la function en cours d'écriture à cet endroit |

```python
SERVER_LOAD = ./load

prepend function_tag minecraft:load {"values": [SERVER_LOAD]}

function SERVER_LOAD:
    forceload add 0 0
    scoreboard objectives add voltaic.energy dummy
```

#### Imbrication et execute implicite

Un `execute` qui finit par deux-points écrit sa propre function et l'appel qui y mène :

```python
execute as @a[tag=voltaic.using] at @s:
    particle minecraft:electric_spark ~ ~1 ~
    playsound minecraft:block.beacon.ambient block @s ~ ~ ~ 0.4 2.0
```

Les conditions se lisent comme des conditions, avec `if`, `else` et les formes `run return` intégrés :

```python
if score @s voltaic.energy matches 1..:
    scoreboard players remove @s voltaic.energy 1
else:
    function voltaic:machines/shutdown
```

#### Ajouter à une function qui appartient à un autre module

```python
from voltaic:core import SERVER_LOAD

append function SERVER_LOAD:
    team add builder "Builder"
    team modify builder color black
```

`function`, `append function` et `prepend function` sont les trois façons pour un module de contribuer à un chemin.
Plusieurs modules peuvent ajouter à la même function de load sans se connaître, ce qui permet un fichier par feature.

#### Les fonctionnalités Python dans bolt

Les imports prennent une resource location là où Python prend un chemin pointé :

```python
from lib:helpers import ticks            # a module in another namespace
from ./items import team_flag            # a sibling module
from dataclasses import dataclass        # plain Python, from your environment
from functools import cache
```

Les classes et les décorateurs fonctionnent, et une méthode peut écrire des functions :

```python
from functools import cached_property

class Gui:
    """ One machine's interface, opened by right clicking it. """

    def __init__(self, machine):
        self.path = f"voltaic:gui/{machine}"

    @cached_property
    def open(self):
        function f"{self.path}/open":
            playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
            tag @s add voltaic.watching
        return f"{self.path}/open"


gui = Gui("pulverizer")
function voltaic:gui/pulverizer/tick:
    execute as @a[tag=voltaic.using] run function gui.open
```

Avec `cached_property`, la function est écrite la première fois que quelque chose demande son chemin, et jamais deux fois.

Les fichiers JSON sont des littéraux, où l'on glisse directement des valeurs Python :

```python
ON_KILL = ./on_kill

advancement ON_KILL {
    "criteria": {"kill": {"trigger": "minecraft:player_killed_entity"}},
    "rewards": {"function": ON_KILL}
}

function ON_KILL:
    advancement revoke @s only ON_KILL
```

#### Scoreboards et storage comme variables

[`bolt_expressions`](https://github.com/mcbeet/bolt-expressions) (`pip install bolt-expressions`, puis ajoutez-le à `require`) transforme l'arithmétique en commandes qui l'exécutent :

```python
from bolt_expressions import Scoreboard, Data

Energy = Scoreboard("voltaic.energy")
Temp = Data.storage("voltaic:temp")

Energy["@s"] -= 20
Energy["#total"] = Energy["@s"] * 3 + Energy["#buffer"]
Temp.display.text = Energy["#total"]
```

Chaque ligne compile vers la séquence de `scoreboard players operation` dont elle a besoin, temporaires compris.
C'est le même travail que les [Equations](../4_equations/fr.md) côté StewBeet, exprimé dans le fichier qui l'utilise.

#### Bolt et StewBeet dans le même pack

Un pack peut déclarer ses items avec `Item(...)`, laisser les plugins générer les recipes et le manual, écrire l'essentiel de sa logique avec `write_function`, et garder un module `.bolt` pour la partie où les commandes sont le plus difficile.
Le [pack de démo](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode/demo) dont l'extension tire ses démonstrations est exactement cela : un petit pack écrit de trois façons.

À utiliser quand :

- Les commandes sont la partie compliquée, pas les données qui les sous-tendent.
- Vous voulez des boucles, des conditions et des classes autour des commandes sans f-string entre elles et vous.
- Vous faites de l'arithmétique sur des scoreboards ou du storage et voulez la lire comme de l'arithmétique.
- Vous voulez de l'imbrication (`execute ...:`) plutôt que de découper les functions à la main.

À éviter quand :

- Le travail consiste à générer beaucoup de functions quasi identiques depuis vos définitions. `write_function` dans un plugin voit `Mem.definitions` et c'est le chemin le plus court.
- Un plugin StewBeet listé avant `mecha` dans le pipeline doit voir ce que vous avez écrit. Ces plugins s'exécutent avant que mecha compile le bolt.
- Vos collaborateurs ne veulent pas d'un second langage dans le projet.

#### Dans l'éditeur

L'[extension StewBeet](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) donne à `.bolt` son propre langage, avec complétion et ctrl+clic sur les commandes et une lens par function que le module écrit.
Elle empêche aussi Spyglass de souligner un `.mcfunction` qui contient du bolt, que Spyglass lit comme du mcfunction vanilla. Voir [Éditeur VS Code](../8_editor/fr.md).

## Bonnes pratiques

### À faire

Qualité du code :

- Utilisez des f-strings pour les chemins dynamiques : `f"{ns}:folder/{item}"`.
- Utilisez des chaînes entre triples guillemets pour le contenu des commandes.
- Utilisez `prepend=True` pour le code d'initialisation dans les fichiers qui doivent s'exécuter en premier.

Performance :

- Utilisez les functions d'horloge (`second`, `second_5`, `minute`) plutôt que le tick quand c'est possible.
- Utilisez des predicates plutôt que des conditions execute complexes.

Conventions StewBeet :

- Prenez le namespace dans `Mem.ctx.project_id`.
- Utilisez `write_load_file()` pour l'initialisation.
- Utilisez `write_versioned_function()` pour les functions d'horloge.
- Appelez les helpers StewBeet plutôt que l'API beet quand il en existe un.

### À ne pas faire

Gestion des fichiers :

- Ne codez pas le namespace en dur (utilisez `ctx.project_id` ou une variable `ns`).
- Ne mélangez pas fichiers statiques et génération pour le même chemin.
- N'écrasez pas de fichiers sans le vouloir.
- Ne créez pas d'appels circulaires entre functions.

Qualité du code :

- N'utilisez pas `ctx.data["namespace"].functions["path"]` quand un helper StewBeet existe.

Performance :

- Ne créez pas de functions qui s'appellent elles-mêmes récursivement sans limite.

## Étapes suivantes

- [Référence des fonctions d'aide](reference/fr.md) : chaque helper et les arguments qu'il prend.
- [Equations](../4_equations/fr.md) : construire de l'arithmétique de scoreboard au lieu de l'écrire à la main.
- [Éditeur VS Code](../8_editor/fr.md) : l'extension qui vérifie chaque bloc de cette page.

