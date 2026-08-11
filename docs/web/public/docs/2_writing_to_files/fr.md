# Écrire fonctions et fichiers

L'écriture dans les fichiers est essentielle pour générer des datapacks et resource packs. StewBeet propose trois approches pour l'écriture de fichiers, chacune avec différents cas d'usage et niveaux de complexité. Ce guide couvre le chargement de fichiers statiques via configuration, l'API native beet, et les fonctions helper simplifiées de StewBeet.

**L'écriture de fichiers se produit typiquement dans les plugins utilisateur après que les définitions soient configurées mais avant la finalisation.**

> **Note sur Bolt** : [Bolt](https://github.com/mcbeet/beet/tree/beta/packages/bolt) est un autre moyen puissant d'écrire des fonctions de datapack en utilisant une syntaxe similaire à Python. Bien qu'il existe et soit un excellent outil, il n'est pas couvert dans ce guide. Consultez le [dépôt Bolt](https://github.com/mcbeet/beet/tree/beta/packages/bolt) pour en savoir plus.

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

## Trois approches pour écrire des fichiers

### Comparaison rapide

| Approche | Cas d'usage | Complexité | Flexibilité |
|----------|----------|------------|-------------|
| **Fichiers statiques (beet.yml)** | Fichiers pré-écrits | ⭐ Simple | ⭐ Faible |
| **API native Beet** | Contrôle total | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |
| **Helpers StewBeet** | Génération dynamique | ⭐⭐ Moyenne | ⭐⭐ Moyenne-Élevée |

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

### **Comparaison des trois approches**

| Approche | Cas d'usage | Complexité | Flexibilité |
|----------|----------|------------|-------------|
| **Fichiers statiques (beet.yml)** | Fichiers pré-écrits | ⭐ Simple | ⭐ Faible |
| **API native Beet** | Contrôle total | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |
| **Helpers StewBeet** | Génération dynamique | ⭐⭐ Moyenne | ⭐⭐ Moyenne-Élevée |

### **Quand utiliser chacune**

- 📁 **Fichiers statiques** : Fichiers de configuration, recipes statiques, fonctions simples
- 🔧 **API native Beet** : Structures imbriquées complexes, types de fichiers personnalisés, contrôle avancé
- 🚀 **Helpers StewBeet** : La plupart de la logique de datapack, fonctions dynamiques, motifs standards

### **Points clés à retenir**

✅ Commencez avec des fichiers statiques pour du contenu simple<br>
✅ Utilisez les helpers StewBeet pour la logique dynamique de datapack<br>
✅ Utilisez l'API native beet uniquement quand les helpers ne couvrent pas vos besoins<br>
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

## Prochaines étapes

- [Référence des fonctions utilitaires](reference/fr.md): chaque fonction et ses arguments.
- [Cookbook](cookbook/fr.md): des exemples complets et fonctionnels.
- [Équations](../4_equations/fr.md): construire l'arithmétique de scoreboard.
- [Configurer le build](../3_beet_config/fr.md): contrôler quand votre code s'exécute.
