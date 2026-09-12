# Écrire fonctions et fichiers

L'écriture dans les fichiers est essentielle pour générer des datapacks et resource packs. StewBeet propose quatre approches pour l'écriture de fichiers, chacune avec différents cas d'usage et niveaux de complexité. Ce guide couvre le chargement de fichiers statiques via configuration, l'API native beet, les fonctions helper simplifiées de StewBeet, et Bolt.

**L'écriture de fichiers se produit typiquement dans les plugins utilisateur après que les définitions soient configurées mais avant la finalisation.**

> **Écrivez tout cela avec les commandes vérifiées à la frappe.** Chaque approche ci-dessous finit par des commandes dans une chaîne Python, dans un module `.bolt`, ou les deux. L'[extension StewBeet pour VSCode](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) les lit pour ce qu'elles sont : complétion, erreurs, ctrl+clic, et un lien de chaque bloc vers la fonction que votre build en a tirée. Voir [Support éditeur](../8_editor/fr.md).

<video src="/vscode_extension.mp4" controls loop muted playsinline preload="auto">
</video>

**Fichier d'exemple** : [extensive/src/link.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py) <br>  
**Exemple réel** : [SimplEnergy/src/utils/machines.py](https://github.com/Stoupy51/SimplEnergy/blob/main/src/utils/machines.py) <br>  
**Exemple réel** : [StardustFragment/src/utils/remaining.py](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py) <br>  
**Requis** : Utilitaires I/O StewBeet (`from stewbeet import write_function, write_load_file, ...`)  
**Position** : Appelé après la configuration des définitions, typiquement au milieu du pipeline  
**Intégration** : Fonctionne avec tous les types de fichiers (fonctions, advancements, tags, etc.)

- Charger des fichiers statiques depuis des répertoires (pré-plugin via `beet.yml`)
- Générer dynamiquement des fonctions, advancements et tags par programme
- Ajouter, préfixer ou écraser le contenu de fichiers
- Organiser la logique de datapack à travers plusieurs fichiers
- Gérer les tags de fonctions et autres types de tags
- Configurer les fonctions d'horloge (tick, second, minute)

## Quatre approches pour écrire des fichiers

### Comparaison rapide

| Approche | Cas d'usage | Complexité | Flexibilité |
|----------|----------|------------|-------------|
| **Fichiers statiques (beet.yml)** | Fichiers pré-écrits | ⭐ Simple | ⭐ Faible |
| **API native Beet** | Contrôle total | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |
| **Helpers StewBeet** | Génération dynamique | ⭐⭐ Moyenne | ⭐⭐ Moyenne-Élevée |
| **Bolt** | Les commandes comme syntaxe | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |

---

### Approche 1 : Chargement de fichiers statiques (beet.yml)

L'approche la plus simple - charger des fichiers pré-écrits depuis des répertoires **avant que les plugins ne s'exécutent**.

```yaml
# Dans beet.yml
data_pack:
    name: "datapack"
    load: ["src"]  # Charge tous les fichiers .mcfunction et .json depuis src/

resource_pack:
    name: resource_pack
    load: ["src"]  # Charge tous les fichiers de textures, models et sons depuis src/
```

**Comment ça marche :**
- Placez les fichiers `.mcfunction` dans `src/data/<namespace>/function/`
- Placez les fichiers `.json` dans `src/data/<namespace>/advancement/`, `src/data/<namespace>/recipe/`, etc.
- Beet les charge automatiquement aux emplacements corrects du pack
- Les fichiers sont chargés **avant** que le code des plugins ne s'exécute

**Exemple de structure :**
```
src/
├── 📦 data/
│   └── my_namespace/
│       ├── ⚙️ function/
│       │   ├── load.mcfunction
│       │   └── tick.mcfunction
│       ├── 🏆 advancement/
│       │   └── my_advancement.json
│       └── 🍳 recipe/
│           └── my_recipe.json
└── 🎨 assets/
    └── my_namespace/
        └── textures/
            └── item/
                └── my_item.png
```

**Que mettre où :**
- 📦 **data/** - Tout le contenu du datapack (fonctions, advancements, recipes, tags, etc.)
- ⚙️ **function/** - Commandes Minecraft (fichiers .mcfunction)
- 🏆 **advancement/** - Succès joueurs et déclencheurs techniques (.json)
- 🍳 **recipe/** - Recipes de craft, cuisson et autres (.json)
- 🎨 **assets/** - Tout le contenu du resource pack (textures, models, sons)
- 🖼️ **textures/** - Fichiers PNG pour items, blocs, etc.
- ...

**✅ À utiliser quand :**
- Vous avez des fichiers statiques qui n'ont pas besoin de génération dynamique
- Vous organisez des commandes et données pré-écrites
- Vous voulez une structure de fichiers simple et directe

**❌ À ne pas utiliser quand :**
- Vous devez générer du contenu basé sur des définitions
- Vous devez combiner plusieurs sources de données
- Vous avez besoin de génération conditionnelle de fichiers

---

### Approche 2 : API native Beet

Utilisez l'API native orientée objet de beet pour écrire des fichiers par programme dans les plugins.

```python
from beet import Context, Function, Advancement, FunctionTag
from stouputils.typing import JsonDict

def beet_default(ctx: Context):
    # Écrire une fonction
    ctx.data["my_namespace"].functions["my_folder/my_function"] = Function("""
# Ceci est ma fonction
say Bonjour le monde !
scoreboard players add @a points 1
""")
    
    # Écrire un advancement
    advancement_data: JsonDict = {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": "my_namespace:rewards/give_item"
        }
    }
    ctx.data["my_namespace"].advancements["my_advancement"] = Advancement(advancement_data)
    
    # Écrire un tag de fonction
    tag_data: JsonDict = {
        "values": [
            "my_namespace:my_folder/my_function",
            "my_namespace:another_function"
        ]
    }
    ctx.data["my_namespace"].function_tags["minecraft:load"] = FunctionTag(tag_data)
```

**✅ À utiliser quand :**
- Vous avez besoin d'un contrôle total sur les objets fichiers
- Vous travaillez avec des structures imbriquées complexes
- Vous voulez la sécurité de type avec le modèle d'objets de beet

**❌ À ne pas utiliser quand :**
- Vous voulez des écritures de fichiers simples et rapides
- Vous gérez beaucoup de petites fonctions
- Vous avez besoin de gestion automatique des chemins

---

### Approche 3 : Fonctions helper StewBeet (Recommandé)

StewBeet fournit des fonctions helper simplifiées qui facilitent l'écriture de fichiers avec gestion automatique des motifs courants.

```python
from stewbeet import write_function, write_load_file, write_tick_file, Mem

def beet_default(ctx: Context):
    ns = ctx.project_id
    
    # Écrire une fonction simple
    write_function(f"{ns}:my_folder/my_function", """
# Ceci est ma fonction
say Bonjour le monde !
scoreboard players add @a points 1
""")
    
    # Ajouter au fichier de chargement (s'exécute au chargement du datapack : "your_namespace:v{version}/load/confirm_load")
    write_load_file("""
# Initialiser les scoreboards
scoreboard objectives add points dummy
scoreboard objectives add data dummy
""")
    
    # Ajouter au fichier tick (s'exécute à chaque tick : "your_namespace:v{version}/tick")
    write_tick_file("""
# Vérifier les joueurs avec scores élevés
execute as @a[scores={points=100..}] run function my_namespace:rewards/high_score
""")
    
    # Écrire des fonctions versionnées (horloge automatique : "your_namespace:v{version}/second", etc.)
    write_versioned_function("second", """
# S'exécute toutes les secondes (20 ticks)
execute as @a run title @s actionbar {"score":{"name":"@s","objective":"points"}}
""")
    
    write_versioned_function("minute", """
# S'exécute toutes les minutes (1200 ticks)
say Une minute s'est écoulée !
""")
```

**✅ À utiliser quand :**
- Vous voulez un code simple et lisible
- Vous avez besoin de gestion automatique des chemins
- Vous utilisez les conventions de StewBeet (fonctions versionnées, fichiers load/tick)
- Vous voulez ajouter/préfixer du contenu facilement

**❌ À ne pas utiliser quand :**
- Vous avez besoin d'une organisation de fichiers non standard
- Vous n'utilisez pas le framework StewBeet

---

### Approche 4 : Bolt

[Bolt](https://github.com/mcbeet/beet/tree/main/packages/bolt) est la couche de script de mecha, et elle inverse les trois approches précédentes.
Au lieu que du Python écrive une chaîne qui contient des commandes, les commandes **sont** la syntaxe : dans un fichier `.bolt`, `item = 3` est du Python et `item modify entity @s weapon.mainhand set value ...` est une commande, à la même indentation, dans la même portée.

Tout s'exécute au build. Rien du Python n'atteint le datapack.

```yaml
# Dans beet.yml
require:
    - "stewbeet"
    - "bolt"

pipeline:
    - "mecha"       # bolt a besoin de mecha pour compiler ce qu'il a produit

meta:
    bolt:
        entrypoint: "*"     # autorise bolt dans n'importe quel fichier de fonction, pas seulement les modules
```

Deux types de fichiers :

- **Les modules**, `.bolt` sous `data/<namespace>/module/`. Importables, ils n'écrivent une fonction que là où ils le demandent.
- **Les fichiers de fonction**, `.mcfunction` couverts par `entrypoint`. Le fichier **est** une fonction, écrite en bolt.

#### Écrire une fonction

```python
# src/data/voltaic/module/gui.bolt
MACHINES = ["pulverizer", "furnace", "smelter"]

for machine in MACHINES:
    function f"voltaic:gui/{machine}/open":
        playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
        data modify entity @s equipment.head set from storage voltaic:gui Icon
        tag @s add voltaic.watching
```

Trois fonctions issues d'une boucle. La f-string est le chemin, le bloc indenté est le corps.

Un chemin est une valeur comme une autre : il se nomme, s'importe et se passe en argument. Deux raccourcis évitent d'écrire le namespace :

| Écrit    | Résout en                                                  |
|----------|------------------------------------------------------------|
| `./load` | `<namespace>:<chemin du module>/load`                       |
| `~/init` | Un enfant de la fonction en cours d'écriture à cet endroit  |

```python
SERVER_LOAD = ./load

prepend function_tag minecraft:load {"values": [SERVER_LOAD]}

function SERVER_LOAD:
    forceload add 0 0
    scoreboard objectives add voltaic.energy dummy
```

#### Imbrication et execute implicite

Un `execute` qui se termine par deux-points écrit sa propre fonction et l'appel qui y mène :

```python
execute as @a[tag=voltaic.using] at @s:
    particle minecraft:electric_spark ~ ~1 ~
    playsound minecraft:block.beacon.ambient block @s ~ ~ ~ 0.4 2.0
```

Les conditions se lisent comme des conditions, avec `if`, `else` et les formes `run return` repliées dedans :

```python
if score @s voltaic.energy matches 1..:
    scoreboard players remove @s voltaic.energy 1
else:
    function voltaic:machines/shutdown
```

#### Compléter une fonction qui appartient à un autre module

```python
from voltaic:core import SERVER_LOAD

append function SERVER_LOAD:
    team add builder "Builder"
    team modify builder color black
```

`function`, `append function` et `prepend function` sont les trois façons pour un module de contribuer à un chemin.
Plusieurs modules peuvent compléter la même fonction de load sans se connaître, et c'est ce qui rend viable un fichier par fonctionnalité.

#### C'est du Python, donc tout le langage est là

Les imports prennent une resource location là où Python prend un chemin pointé :

```python
from lib:helpers import ticks            # un module d'un autre namespace
from ./items import team_flag            # un module voisin
from dataclasses import dataclass        # du Python normal, depuis votre environnement
from functools import cache
```

Classes et décorateurs fonctionnent, et une méthode peut écrire des fonctions :

```python
from functools import cached_property

class Gui:
    """ L'interface d'une machine, ouverte par un clic droit dessus. """

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

`cached_property` fait un vrai travail ici : la fonction est écrite la première fois que quelqu'un demande son chemin, et jamais deux fois.

Les fichiers JSON sont des littéraux, avec les valeurs Python déposées directement dedans :

```python
ON_KILL = ./on_kill

advancement ON_KILL {
    "criteria": {"kill": {"trigger": "minecraft:player_killed_entity"}},
    "rewards": {"function": ON_KILL}
}

function ON_KILL:
    advancement revoke @s only ON_KILL
```

#### Scoreboards et storage comme des variables

[`bolt_expressions`](https://github.com/mcbeet/bolt-expressions) (`pip install bolt-expressions`, puis à ajouter dans `require`) transforme l'arithmétique en les commandes qui l'exécutent :

```python
from bolt_expressions import Scoreboard, Data

Energy = Scoreboard("voltaic.energy")
Temp = Data.storage("voltaic:temp")

Energy["@s"] -= 20
Energy["#total"] = Energy["@s"] * 3 + Energy["#buffer"]
Temp.display.text = Energy["#total"]
```

Chaque ligne compile vers la séquence de `scoreboard players operation` nécessaire, temporaires compris.
C'est le même travail que les [Équations](../4_equations/fr.md) côté StewBeet, exprimé dans le fichier qui s'en sert.

#### Bolt et StewBeet dans le même pack

Rien n'oblige à choisir. Un pack peut déclarer ses items avec `Item(...)`, laisser les plugins générer les recipes et le manuel, écrire l'essentiel de sa logique avec `write_function`, et garder un module `.bolt` pour la partie où les commandes sont le point difficile.
Le [pack de démonstration](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode/demo) dont l'extension tire ses enregistrements est exactement cela : un petit pack écrit de trois façons.

**✅ Utilisez quand :**
- Ce sont les commandes qui sont compliquées, pas les données derrière
- Vous voulez des boucles, des conditions et des classes autour des commandes sans f-string entre vous et elles
- Vous faites de l'arithmétique de scoreboard ou de storage et voulez la lire comme de l'arithmétique
- Vous voulez l'imbrication (`execute ...:`) plutôt que de découper les fonctions à la main

**❌ N'utilisez pas quand :**
- Le travail consiste à générer beaucoup de fonctions quasi identiques depuis vos définitions. `write_function` dans un plugin voit `Mem.definitions` et c'est la route la plus courte
- Un plugin StewBeet doit voir ce que vous avez écrit. Les plugins tournent sur le pack, et mecha compile après eux
- Vos collaborateurs ne veulent pas d'un second langage dans le projet

#### Deux choses à configurer une fois

- **Spyglass souligne un `.mcfunction` contenant du bolt**, parce que ce n'est pas du mcfunction vanilla. [`stewbeet.plugins.spyglass`](../plugins/spyglass.md) retire ces fichiers de sa liste, à partir de ce que le build a réellement compilé.
- **L'[extension StewBeet](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) donne au `.bolt` son propre langage**, avec complétion et ctrl+clic sur les commandes et un lens par fonction que le module écrit. Voir [Support éditeur](../8_editor/fr.md).

---
## Bonnes pratiques

### À faire

**Organisation des fichiers :**
- Utilisez des structures de dossiers significatives (ex., `machines/`, `items/`, `utils/`)
- Groupez les fonctions liées ensemble
- Séparez la logique en petites fonctions réutilisables

**Qualité du code :**
- Utilisez des f-strings pour les chemins dynamiques : `f"{ns}:folder/{item}"`
- Utilisez des chaînes multi-lignes (guillemets triples) pour le contenu des commandes
- Ajoutez des commentaires descriptifs dans les fonctions générées
- Utilisez `prepend=True` pour le code d'initialisation dans les fichiers qui doivent s'exécuter en premier

**Performance :**
- Utilisez des fonctions versionnées (second, second_5, minute) au lieu de tick quand possible
- Regroupez les opérations dans des fonctions uniques
- Utilisez des predicates au lieu de conditions execute complexes
- Évitez les appels de fonction inutiles en tick

**Conventions StewBeet :**
- Utilisez toujours `Mem.ctx.project_id` pour le namespace
- Utilisez `write_load_file()` pour l'initialisation
- Utilisez `write_versioned_function()` pour les fonctions d'horloge
- Appelez les helpers StewBeet au lieu de l'API beet directe quand disponible

### À ne pas faire

**Gestion des fichiers :**
- Ne codez pas en dur les chaînes de namespace (utilisez `ctx.project_id` ou variable `ns`)
- Ne mélangez pas fichiers statiques et génération dynamique pour le même chemin
- N'écrasez pas les fichiers sauf si intentionnel
- Ne créez pas d'appels circulaires de fonctions (boucles infinies)

**Qualité du code :**
- N'utilisez pas `ctx.data["namespace"].functions["path"]` quand des helpers StewBeet existent
- N'oubliez pas de gérer les cas limites (vérifications vides, limites de score)
- N'écrivez pas de fonctions monolithiques (divisez en morceaux plus petits)
- Ne dupliquez pas le code à travers plusieurs fonctions

---
## Résumé

### **Comparaison des quatre approches**

| Approche | Cas d'usage | Complexité | Flexibilité |
|----------|----------|------------|-------------|
| **Fichiers statiques (beet.yml)** | Fichiers pré-écrits | ⭐ Simple | ⭐ Faible |
| **API native Beet** | Contrôle total | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |
| **Helpers StewBeet** | Génération dynamique | ⭐⭐ Moyenne | ⭐⭐ Moyenne-Élevée |
| **Bolt** | Les commandes comme syntaxe | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |

### **Quand utiliser chacune**

- 📁 **Fichiers statiques** : Fichiers de configuration, recipes statiques, fonctions simples
- 🔧 **API native Beet** : Structures imbriquées complexes, custom file types, contrôle avancé
- 🚀 **Helpers StewBeet** : La plupart de la logique de datapack, fonctions dynamiques, motifs standards
- 🧪 **Bolt** : Logique dense en commandes, arithmétique de scoreboard, imbrication plutôt que découpage manuel

### **Points clés à retenir**

✅ Commencez avec des fichiers statiques pour du contenu simple<br>
✅ Utilisez les helpers StewBeet pour la logique dynamique de datapack<br>
✅ Utilisez l'API native beet uniquement quand les helpers ne couvrent pas vos besoins<br>
✅ Passez à Bolt là où ce sont les commandes, et non les données, qui sont difficiles<br>
✅ Organisez les fonctions dans des dossiers logiques<br>
✅ Utilisez les fonctions versionnées pour les tâches périodiques<br>
✅ Suivez les conventions de nommage pour la cohérence<br>

**🎉 Maîtrisez ces approches d'écriture de fichiers pour créer des datapacks efficaces et maintenables avec StewBeet !**<br>
Consultez les exemples réels en haut de cette page pour voir ces motifs en action ! 🚀
## Glossaire

| Terme | Signification |
|-------|---------------|
| **Chargement de fichiers statiques** | Chargement pré-plugin des fichiers déclarés dans `beet.yml` (`data_pack.load` et `resource_pack.load`). |
| **Écriture via API native Beet** | Création de fichiers via les objets `ctx.data`/`ctx.assets` dans le code plugin. |
| **Écriture via helpers StewBeet** | Fonctions utilitaires comme `write_function`, `write_tag` et helpers associés pour générer plus vite. |
| **Bolt** | La couche de script de mecha. Python et commandes partagent une syntaxe, compilée au build. |
| **Module** | Un fichier `.bolt` sous `data/<namespace>/module/`, importé par d'autres et n'écrivant des fonctions que là où il le demande. |
| **Imbrication** | Un `execute` ou un `if` finissant par deux-points, que mecha transforme en sa propre fonction et l'appel qui y mène. |

## Prochaines étapes

- [Référence des fonctions utilitaires](reference/fr.md): chaque fonction et ses arguments.
- [Support éditeur](../8_editor/fr.md): l'extension qui vérifie chaque bloc de cette page.
- [Cookbook](cookbook/fr.md): des exemples complets et fonctionnels.
- [Équations](../4_equations/fr.md): construire l'arithmétique de scoreboard.
- [Configurer le build](../3_beet_config/fr.md): contrôler quand votre code s'exécute.
