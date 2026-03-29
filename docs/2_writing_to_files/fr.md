
# 📝 Guide d'écriture dans les fichiers StewBeet

## 📖 Définitions
- **Chargement de fichiers statiques** : Chargement pré-plugin des fichiers déclarés dans `beet.yml` (`data_pack.load` et `resource_pack.load`).
- **Écriture via API native Beet** : Création de fichiers via les objets `ctx.data`/`ctx.assets` dans le code plugin.
- **Écriture via helpers StewBeet** : Fonctions utilitaires comme `write_function`, `write_tag` et helpers associés pour générer plus vite.

## 🧪 Exemples
📄 **Fichier d'exemple** : [extensive/src/link.py](../../templates/extensive/src/link.py) 🔗<br>
📄 **Exemple réel** : [SimplEnergy/src/utils/machines.py](https://github.com/Stoupy51/SimplEnergy/blob/main/src/utils/machines.py) 🔗<br>
📄 **Exemple réel** : [StardustFragment/src/utils/remaining.py](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py) 🔗<br>

## 🔗 Dépendances
- **✅ Requis** : Utilitaires I/O StewBeet (`from stewbeet import write_function, write_load_file, ...`)
- **📍 Position** : Appelé après la configuration des définitions, typiquement au milieu du pipeline
- **🔄 Intégration** : Fonctionne avec tous les types de fichiers (fonctions, advancements, tags, etc.)

## 📋 Vue d'ensemble
L'écriture dans les fichiers est essentielle pour générer des datapacks et resource packs. StewBeet propose trois approches pour l'écriture de fichiers, chacune avec différents cas d'usage et niveaux de complexité. Ce guide couvre le chargement de fichiers statiques via configuration, l'API native beet, et les fonctions helper simplifiées de StewBeet.

**L'écriture de fichiers se produit typiquement dans les plugins utilisateur après que les définitions soient configurées mais avant la finalisation.**

> **📝 Note sur Bolt** : [Bolt](https://github.com/mcbeet/beet/tree/beta/packages/bolt) est un autre moyen puissant d'écrire des fonctions de datapack en utilisant une syntaxe similaire à Python. Bien qu'il existe et soit un excellent outil, il n'est pas couvert dans ce guide. Consultez le [dépôt Bolt](https://github.com/mcbeet/beet/tree/beta/packages/bolt) pour en savoir plus.

## 🎯 Objectif
- 📁 Charger des fichiers statiques depuis des répertoires (pré-plugin via `beet.yml`)
- ✍️ Générer dynamiquement des fonctions, advancements et tags par programme
- 🔄 Ajouter, préfixer ou écraser le contenu de fichiers
- 📦 Organiser la logique de datapack à travers plusieurs fichiers
- 🏷️ Gérer les tags de fonctions et autres types de tags
- ⏰ Configurer les fonctions d'horloge (tick, second, minute)

## 🎨 Trois approches pour écrire des fichiers

### 📖 Comparaison rapide

| Approche | Cas d'usage | Complexité | Flexibilité |
|----------|----------|------------|-------------|
| **Fichiers statiques (beet.yml)** | Fichiers pré-écrits | ⭐ Simple | ⭐ Faible |
| **API native Beet** | Contrôle total | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |
| **Helpers StewBeet** | Génération dynamique | ⭐⭐ Moyenne | ⭐⭐ Moyenne-Élevée |

---

### 📁 Approche 1 : Chargement de fichiers statiques (beet.yml)

L'approche la plus simple - charger des fichiers pré-écrits depuis des répertoires **avant que les plugins ne s'exécutent**.

```yaml
# Dans beet.yml
data_pack:
    name: "datapack"
    load: ["src"]  # Charge tous les fichiers .mcfunction et .json depuis src/

resource_pack:
    name: resource_pack
    load: ["src"]  # Charge tous les fichiers de textures, modèles et sons depuis src/
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
- 📦 **data/** - Tout le contenu du datapack (fonctions, advancements, recettes, tags, etc.)
- ⚙️ **function/** - Commandes Minecraft (fichiers .mcfunction)
- 🏆 **advancement/** - Succès joueurs et déclencheurs techniques (.json)
- 🍳 **recipe/** - Recettes de craft, cuisson et autres (.json)
- 🎨 **assets/** - Tout le contenu du resource pack (textures, modèles, sons)
- 🖼️ **textures/** - Fichiers PNG pour objets, blocs, etc.
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

### 🔧 Approche 2 : API native Beet

Utilisez l'API native orientée objet de beet pour écrire des fichiers par programme dans les plugins.

```python
from beet import Context, Function, Advancement, FunctionTag
from beet.core.utils import JsonDict

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

### 🚀 Approche 3 : Fonctions helper StewBeet (Recommandé)

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

## 📚 Référence des fonctions helper StewBeet

### 🏆 Écriture de fonctions

#### `write_function()`
Écrire du contenu dans un fichier de fonction.

```python
def write_function(
    path: str,                      # Chemin de la fonction (ex., "namespace:folder/function_name")
    content: str,                   # Le contenu à écrire
    overwrite: bool = False,        # Écraser au lieu d'ajouter
    prepend: bool = False,          # Préfixer au lieu d'ajouter
    tags: list[str] | None = None   # Tags de fonction à ajouter (ex., ["minecraft:load"])
) -> None:
```

**Exemple :**
```python
write_function(f"{ns}:utils/teleport_spawn", """
# Téléporter le joueur au spawn
tp @s 0 64 0
""", tags=[f"{ns}:tp_spawn"])
```
La fonction sera écrite dans `data/your_namespace/functions/utils/teleport_spawn.mcfunction`, et ajoutée au tag de fonction `your_namespace:tp_spawn`.

---

#### `read_function()`
Lire le contenu d'une fonction existante.

```python
def read_function(
    path: str  # Chemin de la fonction (ex., "namespace:folder/function_name")
) -> str:
```

**Exemple :**
```python
existing_content = read_function(f"{ns}:my_function")
modified_content = existing_content.replace("say Bonjour", "say Au revoir")
write_function(f"{ns}:my_function", modified_content, overwrite=True)
```

---

#### `write_load_file()`
Écrire du contenu dans la fonction de chargement principale (s'exécute au chargement du datapack).

```python
def write_load_file(
    content: str,                   # Le contenu à écrire
    overwrite: bool = False,        # Écraser au lieu d'ajouter
    prepend: bool = False,          # Préfixer au lieu d'ajouter
    tags: list[str] | None = None   # Tags supplémentaires à ajouter
) -> None:
```

**Chemin :** `namespace:v{version}/load/confirm_load`

**Exemple :**
```python
# Préfixer le code d'initialisation (s'exécute en premier)
write_load_file("""
# Initialiser les scoreboards de base
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)

# Ajouter le code de configuration (s'exécute après le contenu préfixé)
write_load_file("""
# Définir les valeurs par défaut
scoreboard players set #2 data 2
scoreboard players set #100 data 100
""")
```

---

#### `write_tick_file()`
Écrire du contenu dans la fonction tick principale (s'exécute à chaque tick du jeu - 20 fois par seconde).

```python
def write_tick_file(
    content: str,                   # Le contenu à écrire
    overwrite: bool = False,        # Écraser au lieu d'ajouter
    prepend: bool = False,          # Préfixer au lieu d'ajouter
    tags: list[str] | None = None   # Tags supplémentaires à ajouter
) -> None:
```

**Chemin :** `namespace:v{version}/tick`

**Exemple :**
```python
write_tick_file("""
# Incrémenter le timer
scoreboard players add #global_timer data 1

# Réinitialiser toutes les minutes
execute if score #global_timer data matches 1200.. run scoreboard players set #global_timer data 0
""")
```

---

#### `write_versioned_function()`
Écrire du contenu dans une fonction d'horloge versionnée.

```python
def write_versioned_function(
    path: str,                      # Chemin de fonction SANS namespace (ex., "second", "tick_2")
    content: str,                   # Le contenu à écrire
    overwrite: bool = False,        # Écraser au lieu d'ajouter
    prepend: bool = False,          # Préfixer au lieu d'ajouter
    tags: list[str] | None = None   # Tags supplémentaires à ajouter
) -> None:
```

**Chemin :** `namespace:v{version}/{path}`

**Fonctions d'horloge courantes :** (les autres noms ne seront pas appelés automatiquement par défaut)
| Chemin | Fréquence | Ticks | Description |
|------|-----------|-------|-------------|
| `tick` | Chaque tick | 1 | S'exécute avec le fichier tick principal |
| `tick_2` | Tous les 2 ticks | 2 | Vitesse demi-tick (10 fois/seconde) |
| `second` | Toutes les secondes | 20 | Une fois par seconde |
| `second_5` | Toutes les 5 secondes | 100 | Bon pour les vérifications périodiques |
| `minute` | Toutes les minutes | 1200 | Pour les mises à jour rares |

**Exemple :**
```python
# S'exécute toutes les secondes
write_versioned_function("second", """
# Régénérer la santé pour les joueurs avec effet de régénération
execute as @a[nbt={active_effects:[{id:"minecraft:regeneration"}]}] run effect give @s instant_health 1 0 true
""")

# S'exécute toutes les 5 secondes
write_versioned_function("second_5", """
# Faire apparaître des particules aux entités marker
execute at @e[type=marker,tag=particle_source] run particle flame ~ ~ ~ 0.5 0.5 0.5 0.01 10
""")

# S'exécute toutes les minutes
write_versioned_function("minute", """
# Nettoyer les vieux objets
kill @e[type=item,nbt={Age:5400s}]
""")
```

---

### 🏅 Écriture d'advancements

#### `write_advancement()`
Écrire un fichier d'advancement.

```python
def write_advancement(
    path: str,                              # Chemin de l'advancement (ex., "namespace:folder/name")
    advancement: Advancement | JsonDict,    # Données ou objet advancement
    overwrite: bool = False,                # Écraser au lieu de fusionner
    max_level: int = -1                     # Profondeur d'indentation JSON (-1 = illimitée)
) -> None:
```

**Exemple :**
```python
# Advancement technique (caché des joueurs)
write_advancement(f"{ns}:technical/inventory_changed", {
    "criteria": {
        "requirement": {
            "trigger": "minecraft:inventory_changed"
        }
    },
    "rewards": {
        "function": f"{ns}:advancements/check_inventory"
    }
})

# Advancement visible
write_advancement(f"{ns}:story/craft_ruby_sword", {
    "display": {
        "icon": {"id": "minecraft:diamond_sword", "components": {"item_model": f"{ns}:ruby_sword"}},
        "title": {"text": "Lame Légendaire", "color": "red"},
        "description": {"text": "Fabriquer une Épée de Rubis"},
        "frame": "challenge",
        "show_toast": True,
        "announce_to_chat": True
    },
    "parent": f"{ns}:story/mine_ruby",
    "criteria": {
        "requirement": {
            "trigger": "minecraft:recipe_unlocked",
            "conditions": {
                "recipe": f"{ns}:ruby_sword"
            }
        }
    }
})
```

---

### 🏷️ Écriture de tags

#### `write_tag()`
Écrire un fichier de tag (générique pour tous types de tags).

```python
def write_tag(
    path: str,                                  # Chemin du tag (ex., "namespace:my_tag")
    tag_type: NamespaceProxy | NamespaceContainer,  # Type de tag (ex., ctx.data.function_tags)
    values: list[Any] | None = None,           # Valeurs à ajouter au tag
    prepend: bool = False,                      # Préfixer au lieu d'ajouter
    max_level: int | None = None                # Profondeur d'indentation JSON
) -> None:
```

**Exemple :**
```python
# Tags de fonctions
write_tag(f"{ns}:custom_load", Mem.ctx.data.function_tags, [
    f"{ns}:init/scoreboards",
    f"{ns}:init/teams"
])

# Tags de types d'entités
write_tag(f"{ns}:hostile_mobs", Mem.ctx.data.entity_type_tags, [
    "minecraft:zombie",
    "minecraft:skeleton",
    "minecraft:spider"
])

# Tags de blocs
write_tag(f"{ns}:mineable/pickaxe", Mem.ctx.data.block_tags, [
    "stone",
    "emerald_block"
])
```

---

#### `write_function_tag()`
Écrire un tag de fonction (wrapper de commodité pour `write_tag`).

```python
def write_function_tag(
    path: str,                      # Chemin du tag (ex., "namespace:my_tag")
    functions: list[Any] | None = None,  # Chemins de fonctions à ajouter
    prepend: bool = False,          # Préfixer au lieu d'ajouter
    max_level: int | None = None    # Profondeur d'indentation JSON
) -> None:
```

**Exemple :**
```python
# Ajouter des fonctions à minecraft:load
write_function_tag("minecraft:load", [
    f"{ns}:load/main"
])

# Ajouter des fonctions à minecraft:tick
write_function_tag("minecraft:tick", [
    f"{ns}:tick/main"
])

# Tag de fonction personnalisé
write_function_tag(f"{ns}:custom_blocks/tick", [
    f"{ns}:custom_blocks/furnace/tick",
    f"{ns}:custom_blocks/machine/tick"
])
```

---

### 🛠️ Fonctions utilitaires

#### `super_merge_dict()`
Fusionner récursivement deux dictionnaires sans modifier les originaux.

```python
def super_merge_dict(
    dict1: JsonDict,  # Premier dictionnaire
    dict2: JsonDict   # Deuxième dictionnaire (remplace dict1)
) -> JsonDict:
```

**Exemple :**
```python
base_config = {
    "settings": {"power": 100, "speed": 5},
    "enabled": True
}

override_config = {
    "settings": {"power": 150},  # Remplacer power, garder speed
    "debug": True                 # Ajouter nouveau champ
}

merged = super_merge_dict(base_config, override_config)
# Résultat : {"settings": {"power": 150, "speed": 5}, "enabled": True, "debug": True}
```

---

#### `set_json_encoder()`
Définir un encodeur JSON personnalisé pour un affichage formaté.

```python
def set_json_encoder(
    obj: JsonFileT,              # Objet JsonFile (Advancement, FunctionTag, etc.)
    max_level: int | None = None,  # Profondeur d'indentation max (None = illimitée)
    indent: str | int = '\t'      # Caractère d'indentation ou espaces
) -> JsonFileT:
```

**Exemple :**
```python
from stewbeet import set_json_encoder
from beet import Advancement

advancement = Advancement({
    "criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}}
})

# Utiliser des tabulations pour l'indentation (défaut)
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement)

# Utiliser 2 espaces
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement, indent=2)

# Limiter la profondeur d'indentation
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement, max_level=3)
```

---

#### `convert_to_serializable()`
Convertir les objets avec méthode `to_dict()` en formes sérialisables JSON.

```python
def convert_to_serializable(
    obj: Any  # Objet à convertir
) -> Any:
```

**Exemple :**
```python
from stewbeet import Item, convert_to_serializable

item = Item.from_id("ruby_sword")
serializable_data = convert_to_serializable(item)
# Peut maintenant être écrit en JSON
```

---

#### `texture_mcmeta()`
Créer un objet Texture avec fichier mcmeta s'il existe.

```python
def texture_mcmeta(
    source_path: str  # Chemin vers fichier texture (ex., "assets/textures/my_texture.png")
) -> Texture:
```

**Exemple :**
```python
from stewbeet import texture_mcmeta

# Charge automatiquement animated_block.png.mcmeta s'il existe
texture = texture_mcmeta("assets/textures/animated_block.png")
Mem.ctx.assets["my_namespace"].textures["block/animated_block"] = texture
```

---

## 💡 Exemples concrets

### 📦 Exemple 1 : Ticking de blocs personnalisés

Générer des fonctions tick pour blocs personnalisés avec différents comportements.

```python
from stewbeet import write_function, write_versioned_function, Mem

def setup_custom_blocks(ctx: Context):
    ns = ctx.project_id
    
    # Panneau solaire génère de l'énergie pendant la journée
    write_versioned_function("custom_blocks/solar_panel/second", """
# Vérifier le niveau de lumière du jour et générer de l'énergie
execute if predicate simplenergy:check_daylight_power run scoreboard players operation @s energy.storage += @s simplenergy.energy_rate
execute if score @s energy.storage > @s energy.max_storage run scoreboard players operation @s energy.storage = @s energy.max_storage
""")
    
    # Four électrique fait fondre des objets en utilisant de l'énergie
    write_versioned_function("custom_blocks/electric_furnace/second", f"""
# Empêcher la cuisson vanilla
data modify block ~ ~ ~ cooking_total_time set value -200s

# Vérifier si a de l'énergie et des objets
execute if score @s energy.storage matches 20.. if data block ~ ~ ~ Items[{{Slot:0b}}] run function {ns}:custom_blocks/electric_furnace/process
""")
    
    write_function(f"{ns}:custom_blocks/electric_furnace/process", """
# Consommer de l'énergie
scoreboard players remove @s energy.storage 20

# Cuire l'objet (se terminera à la prochaine vérification)
data modify block ~ ~ ~ CookTime set value 199s
""")
```

---

### ⚡ Exemple 2 : Gestion d'états de machines

Gérer les états de machines avec plusieurs fonctions.

```python
def setup_machine_states(ctx: Context):
    ns = ctx.project_id
    
    # Tick principal de la machine
    write_function(f"{ns}:machines/processor/tick", f"""
# Vérifier si la machine doit fonctionner
execute if score @s {ns}.power matches 100.. run function {ns}:machines/processor/running
execute unless score @s {ns}.power matches 100.. run function {ns}:machines/processor/idle
""")
    
    # État en marche
    write_function(f"{ns}:machines/processor/running", f"""
# Consommer de l'énergie
scoreboard players remove @s {ns}.power 10

# Afficher des particules en marche
particle electric_spark ~ ~0.5 ~ 0.2 0.2 0.2 0.01 5

# Traiter les objets
execute if predicate {ns}:has_input_item run function {ns}:machines/processor/process_item
""")
    
    # État inactif
    write_function(f"{ns}:machines/processor/idle", """
# Afficher des particules inactives
particle smoke ~ ~0.5 ~ 0.1 0.1 0.1 0.01 1
""")
    
    # Logique de traitement
    write_function(f"{ns}:machines/processor/process_item", f"""
# Retirer l'entrée
item replace block ~ ~ ~ container.0 with air

# Donner la sortie
loot spawn ~ ~ ~ loot {ns}:items/processed_material
""")
```

---

### 🎯 Exemple 3 : Déclencheurs d'advancements

Configurer un système de détection basé sur les advancements.

```python
def setup_advancement_triggers(ctx: Context):
    ns = ctx.project_id
    
    # Déclencheur de changement d'inventaire
    write_advancement(f"{ns}:technical/inventory_changed", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/check_inventory"
        }
    })
    
    write_function(f"{ns}:advancements/check_inventory", f"""
# Révoquer l'advancement
advancement revoke @s only {ns}:technical/inventory_changed

# Vérifier les objets personnalisés
execute if items entity @s container.* *[custom_data~{{{ns}:{{}}}}] run function {ns}:items/handle_custom_item
""", prepend=True)
    
    # Déclencheur d'utilisation d'objet (pour détection de clic droit)
    write_advancement(f"{ns}:technical/used_item", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:using_item",
                "conditions": {
                    "item": {
                        "predicates": {
                            "custom_data": {ns: {}}
                        }
                    }
                }
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/item_used"
        }
    })
    
    write_function(f"{ns}:advancements/item_used", f"""
advancement revoke @s only {ns}:technical/used_item
function {ns}:items/right_click_handler
""")
```

---

### 🔄 Exemple 4 : Génération programmatique de fonctions

Générer automatiquement plusieurs fonctions similaires.

```python
def generate_tier_functions(ctx: Context):
    ns = ctx.project_id
    
    # Générer des fonctions pour chaque tier
    tiers = {
        "basic": {"power": 10, "speed": 100, "color": "gray"},
        "advanced": {"power": 25, "speed": 50, "color": "blue"},
        "elite": {"power": 50, "speed": 25, "color": "purple"}
    }
    
    for tier_name, tier_data in tiers.items():
        # Générer fonction d'amélioration
        write_function(f"{ns}:machines/{tier_name}/upgrade", f"""
# Définir les stats du tier
scoreboard players set @s {ns}.power {tier_data['power']}
scoreboard players set @s {ns}.speed {tier_data['speed']}

# Afficher message d'amélioration
tellraw @s {{"text":"Amélioré au Tier {tier_name.title()} !","color":"{tier_data['color']}"}}
""")
        
        # Générer fonction d'opération
        write_function(f"{ns}:machines/{tier_name}/operate", f"""
# Vérifier le besoin en énergie
execute if score @s {ns}.energy matches {tier_data['power']}.. run function {ns}:machines/{tier_name}/process

# Afficher le statut
title @s actionbar {{"text":"Énergie : ","color":"gray","extra":[{{"score":{{"name":"@s","objective":"{ns}.energy"}}}}]}}
""")
```

---

### 📊 Exemple 5 : Configuration complexe du chargement

Initialiser des systèmes de datapack complets au chargement.

```python
def setup_load_system(ctx: Context):
    ns = ctx.project_id
    
    # Préfixer l'initialisation précoce (s'exécute en premier)
    write_load_file("""
# Créer les scoreboards de base
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)
    
    # Initialisation principale
    write_load_file(f"""
# Créer les scoreboards spécifiques au jeu
scoreboard objectives add {ns}.energy dummy
scoreboard objectives add {ns}.power dummy
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick

# Définir les constantes
scoreboard players set #2 data 2
scoreboard players set #10 data 10
scoreboard players set #100 data 100
scoreboard players set #1000 data 1000

# Créer les équipes
team add {ns}.green
team add {ns}.gold
team add {ns}.aqua
team modify {ns}.green color green
team modify {ns}.gold color gold
team modify {ns}.aqua color aqua

# Initialiser le stockage
data modify storage {ns}:main config set value {{}}
data modify storage {ns}:main temp set value {{}}
""")
    
    # Charger les modules personnalisés
    write_load_file(f"""
# Charger les systèmes de modules
function {ns}:modules/energy/load
function {ns}:modules/machines/load
function {ns}:modules/items/load
""")
```

---

### 🎮 Exemple 6 : Système de détection de clic droit

Système complet de détection de clic droit utilisant des objets personnalisés.

```python
def setup_right_click_detection(ctx: Context):
    ns = ctx.project_id
    
    # Créer le scoreboard de détection au chargement
    write_load_file(f"""
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick
""")
    
    # Vérifier les clics droits à chaque tick
    write_tick_file(f"""
# Détecter les clics droits
execute as @a[scores={{{ns}.right_click=1..}}] run function {ns}:items/right_click_handler
""")
    
    # Gestionnaire principal de clic droit
    write_function(f"{ns}:items/right_click_handler", f"""
# Réinitialiser le score
scoreboard players set @s {ns}.right_click 0

# Vérifier quel objet a été utilisé
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{wrench:true}}}}] run function {ns}:items/wrench/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{teleporter:true}}}}] run function {ns}:items/teleporter/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{scanner:true}}}}] run function {ns}:items/scanner/use
""")
    
    # Gestionnaires d'objets individuels
    write_function(f"{ns}:items/wrench/use", """
# Faire pivoter le bloc regardé par le joueur
execute anchored eyes positioned ^ ^ ^1 align xyz positioned ~0.5 ~ ~0.5 as @e[type=item_display,tag=custom_block,distance=..1,limit=1,sort=nearest] run function simplenergy:items/wrench/rotate_block
""")
```

---

### 🌟 Exemple 7 : Système de cultures en croissance

Implémenter des mécaniques de croissance personnalisées.

```python
def setup_growing_system(ctx: Context):
    ns = ctx.project_id
    
    # Vérifier la croissance toutes les 5 secondes
    write_versioned_function("second_5", f"""
# Mettre à jour les cultures en croissance
execute as @e[type=item_display,tag={ns}.growing_crop] at @s run function {ns}:crops/check_growth
""")
    
    # Fonction de vérification de croissance
    write_function(f"{ns}:crops/check_growth", f"""
# Incrémenter le timer de croissance
scoreboard players add @s {ns}.growth_time 5

# Vérifier si complètement cultivé
execute if score @s {ns}.growth_time >= @s {ns}.growth_required run function {ns}:crops/fully_grown

# Retour visuel (particule aléatoire)
execute if predicate {ns}:random/0.3 run particle happy_villager ~ ~0.3 ~ 0.2 0.2 0.2 0 1
""")
    
    # Gestionnaire de culture complètement cultivée
    write_function(f"{ns}:crops/fully_grown", f"""
# Mettre à jour le modèle à l'état cultivé
data modify entity @s item.components."minecraft:item_model" set value "{ns}:block/crop_grown"

# Ajouter le tag cultivé
tag @s add {ns}.crop_grown
tag @s remove {ns}.growing_crop

# Jouer le son
playsound minecraft:block.crop.break block @a ~ ~ ~ 1 1.2
""")
    
    # Récolte
    write_function(f"{ns}:crops/harvest", f"""
# Lâcher les objets
loot spawn ~ ~ ~ loot {ns}:crops/harvest_crop

# Retirer l'entité
kill @s

# Jouer le son
playsound minecraft:block.crop.break block @a ~ ~ ~ 1 0.8
""")
```

---

### 📜 Exemple 8 : Gestion des tags

Organiser les fonctions et entités avec des tags.

```python
def setup_tags(ctx: Context):
    ns = ctx.project_id
    
    # Ajouter à minecraft:load
    write_function_tag("minecraft:load", [
        f"{ns}:v{ctx.project_version}/load/main"
    ])
    
    # Ajouter à minecraft:tick
    write_function_tag("minecraft:tick", [
        f"{ns}:v{ctx.project_version}/load/tick_verification"
    ])
    
    # Tags de fonctions personnalisés pour l'organisation
    write_function_tag(f"{ns}:custom_blocks/tick", [
        f"{ns}:custom_blocks/solar_panel/tick",
        f"{ns}:custom_blocks/electric_furnace/tick",
        f"{ns}:custom_blocks/battery/tick"
    ])
    
    write_function_tag(f"{ns}:machines/process", [
        f"{ns}:machines/crusher/process",
        f"{ns}:machines/smelter/process",
        f"{ns}:machines/assembler/process"
    ])
    
    # Tags de types d'entités
    write_tag("mob_grinder_blacklist", Mem.ctx.data.entity_type_tags, [
        "minecraft:warden",
        "minecraft:ender_dragon",
        "minecraft:wither"
    ])
    
    write_tag("machines", Mem.ctx.data.entity_type_tags, [
        "minecraft:item_display",
        "minecraft:interaction"
    ])
    
    # Tags de blocs
    write_tag(f"{ns}:machines", Mem.ctx.data.block_tags, [
        "minecraft:furnace",
        "minecraft:barrel",
        "minecraft:dropper"
    ])
```

---

## 🚨 Bonnes pratiques

### ✅ À faire

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

### ❌ À ne pas faire

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

## 🎯 Exemple complet

Voici un exemple complet combinant toutes les approches (exemple de [Stardust Fragment](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py)) :

```python
# Imports
import json

from stewbeet import *  # type: ignore
from stouputils import get_root_path

# Constantes
ROOT: str = get_root_path(__file__)

# Configuration des utilitaires restants
def setup_remaining() -> None:
	ns: str = Mem.ctx.project_id

	# Obtenir la loot table de tête de joueur
	json_content: JsonDict = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":"minecraft:player_head","functions":[{"function":"minecraft:fill_player_head","entity":"this"}]}]}]}
	Mem.ctx.data[ns].loot_tables["player_head"] = set_json_encoder(LootTable(json_content), max_level=-1)

	# Musique de boss
	write_load_file(f"\n# Boss music timers\nscoreboard objectives add {ns}.boss_music dummy", prepend=True)

	# Changement d'inventaire
	write_advancement(f"{ns}:technical/inventory_changed", {
		"criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}},
		"rewards": {"function": f"{ns}:advancements/inventory_changed"}
	})
	write_function(f"{ns}:advancements/inventory_changed", f"""
# Révoquer l'advancement
advancement revoke @s only {ns}:technical/inventory_changed
""", prepend=True)


	# Détection de clic droit
	write_load_file(f"\n# Right click detection\nscoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick\nscoreboard objectives add {ns}.cooldown dummy\n", prepend=True)
	write_advancement(f"{ns}:technical/right_click", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_scores",
							"entity": "this",
							"scores": {f"{ns}.right_click": {"min": 1}}
						}
					]
				}
			}
		},
		"rewards": {
			"function": f"{ns}:advancements/right_click"
		}
	})
	write_function(f"{ns}:advancements/right_click", f"""
# Révoquer l'advancement et réinitialiser le score
advancement revoke @s only {ns}:technical/right_click
scoreboard players set @s {ns}.right_click 0
""", prepend=True)

	# Compteur global
	write_tick_file(f"\n# Global counter for various features\nscoreboard players add #global_tick {ns}.data 1\n", prepend=True)
	write_versioned_function("second", f"\n# Global counter for various features\nscoreboard players add #global_second {ns}.data 1\n", prepend=True)

	# Calculer le mouvement vers
	write_function(f"{ns}:utils/compute_motion_towards", """
# Calculer le mouvement vers
scoreboard players set @s bs.vel.x 0
scoreboard players set @s bs.vel.y 0
$scoreboard players set @s bs.vel.z $(towards)
function #bs.move:local_to_canonical

# Appliquer le mouvement
$function #bs.move:set_motion {scale:$(scale)}
""")

	# Utiliser la durabilité
	write_function(f"{ns}:utils/use_durability/main", f"""
# Calculer l'utilisation de durabilité (précision 6 chiffres)
scoreboard players set #1000000 {ns}.data 1000000
$scoreboard players set #temp_durability {ns}.data -$(amount)
scoreboard players operation #temp_durability {ns}.data *= #1000000 {ns}.data
$scoreboard players set #temp_divider {ns}.data $(max_damage)
scoreboard players operation #temp_durability {ns}.data /= #temp_divider {ns}.data
execute store result storage {ns}:temp use_durability double 0.000001 run scoreboard players get #temp_durability {ns}.data
$data modify storage {ns}:temp slot set value "$(slot)"
function {ns}:utils/use_durability/item_modifier with storage {ns}:temp

# Si l'objet est cassé, le détruire
execute store result score #current_damage {ns}.data run data get entity @s SelectedItem.components."minecraft:damage"
$execute if score #current_damage {ns}.data matches $(max_damage).. anchored eyes run particle item{{item:{{id:"minecraft:stone",components:{{"minecraft:item_model":"$(item_model)"}}}}}} ^ ^ ^0.5 0 0 0 0.1 10
$execute if score #current_damage {ns}.data matches $(max_damage).. run playsound minecraft:item.shield.break ambient @a[distance=..16]
$execute if score #current_damage {ns}.data matches $(max_damage).. run item replace entity @s $(slot) with minecraft:air
""")
	write_function(f"{ns}:utils/use_durability/item_modifier", r"""
$item modify entity @s $(slot) {"function": "minecraft:set_damage","damage": $(use_durability),"add": true}
""")

	## Consommation de Life Crystal
	# Ajouter l'instrument life crystal
	Mem.ctx.data[ns].instruments["life_crystal"] = set_json_encoder(Instrument({
		"description": item_id_to_text_component("life_crystal"),
		"range": 16.0,
		"sound_event": {"sound_id": f"{ns}:life_crystal"},
		"use_duration": 1.0
	}))
	# Détecter l'utilisation de life crystal
	write_load_file(f"\n# Life Crystal tracker\nscoreboard objectives add {ns}.life_crystal dummy\n", prepend=True)
	write_advancement(f"{ns}:technical/use_life_crystal", {
		"criteria": {
			"requirements": {
				"trigger": "minecraft:using_item",
				"conditions": {"item": {"predicates": {"minecraft:custom_data": {ns: {"life_crystal": True}}}}}
			}
		},
		"rewards": {"function": f"{ns}:advancements/use_life_crystal"}
	})
	write_function(f"{ns}:advancements/use_life_crystal", f"""
# Révoquer l'advancement
advancement revoke @s only {ns}:technical/use_life_crystal

# Arrêter si exécuté il y a un tick (pour éviter la double consommation)
scoreboard players operation #cooldown {ns}.data = @s {ns}.cooldown
execute if score #cooldown {ns}.data > #global_tick {ns}.data run return fail
scoreboard players operation @s {ns}.cooldown = #global_tick {ns}.data
scoreboard players add @s {ns}.cooldown 20

# Arrêter si déjà au maximum de life crystals
execute if score @s {ns}.life_crystal matches 20 run return run tellraw @s {{"text":"[Stardust Fragment] Vous avez déjà atteint le nombre maximum de Life Crystals !","color":"red"}}

# Mettre à jour le compteur de life crystal et l'attribut
scoreboard players add @s {ns}.life_crystal 1
particle minecraft:heart ~ ~1 ~ .5 .5 .5 1 10 normal
attribute @s minecraft:max_health modifier remove {ns}:life_crystal
{'\n'.join([f'execute if score @s {ns}.life_crystal matches {i+1} run attribute @s minecraft:max_health modifier add {ns}:life_crystal {i+1} add_value' for i in range(20)])}

# Retirer un life crystal
clear @s *[custom_data~{{{ns}:{{"life_crystal":true}}}}] 1

# Accorder l'advancement life crystal
advancement grant @s only {ns}:visible/stuff/life_crystal
execute if score @s {ns}.life_crystal matches 20 run advancement grant @s only {ns}:visible/stuff/life_crystal_max
""")

	# Production d'excréments de chien
	Mem.ctx.data[ns].predicates["random/0.05"] = set_json_encoder(Predicate({"condition":"minecraft:random_chance","chance": 0.05}))
	write_versioned_function("minute", f"""
# Production d'excréments de chien (environ 1 toutes les 20 minutes par loup)
execute at @e[type=minecraft:wolf,{Conventions.AVOID_ENTITY_TAGS},predicate={ns}:random/0.05] run loot spawn ~ ~ ~ loot {ns}:i/dog_excrement
""")

	# Bâton de voyage
	max_damage: int = Mem.definitions["home_travel_staff"]["max_damage"]
	write_load_file(f"""
# Logique du bâton de voyage
scoreboard objectives add {ns}.travel_staff_cooldown dummy
scoreboard objectives add {ns}.travel_x dummy
scoreboard objectives add {ns}.travel_y dummy
scoreboard objectives add {ns}.travel_z dummy
""", prepend=True)
	write_function(f"{ns}:advancements/right_click", f"""
# Si tient un bâton de voyage, le gérer
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{home_travel_staff:true}}}}] run function {ns}:utils/home_travel_staff/right_click
""")
	write_function(f"{ns}:utils/home_travel_staff/right_click", f"""
# Arrêter si déjà cliqué récemment
execute if score @s {ns}.travel_staff_cooldown > #global_tick {ns}.data run return fail

# Main principale ou secondaire ?
data modify storage {ns}:temp slot set value "weapon.mainhand"
execute unless items entity @s weapon.mainhand *[custom_data~{{{ns}:{{home_travel_staff:true}}}}] run data modify storage {ns}:temp slot set value "weapon.offhand"

# Temps de téléportation (100 ticks)
scoreboard players operation @s {ns}.travel_staff_cooldown = #global_tick {ns}.data
scoreboard players add @s {ns}.travel_staff_cooldown 100
schedule function {ns}:utils/home_travel_staff/schedule_teleport 100t append
schedule function {ns}:utils/home_travel_staff/schedule_particles 50t append

# Copier la position actuelle (pour détecter si déplacé)
execute store result score @s {ns}.travel_x run data get entity @s Pos[0] 100
execute store result score @s {ns}.travel_y run data get entity @s Pos[1] 100
execute store result score @s {ns}.travel_z run data get entity @s Pos[2] 100

# Utiliser 1 de durabilité
data modify storage {ns}:temp amount set value 1
data modify storage {ns}:temp max_damage set value {max_damage}
data modify storage {ns}:temp item_model set value "{ns}:home_travel_staff"
function {ns}:utils/use_durability/main with storage {ns}:temp

# Retour
playsound minecraft:block.portal.trigger ambient @s ~ ~ ~ 0.5
effect give @s minecraft:nausea 8 255 true
""")
	write_function(f"{ns}:utils/home_travel_staff/schedule_teleport", f"execute as @a if score @s {ns}.travel_staff_cooldown = #global_tick {ns}.data at @s run function {ns}:utils/home_travel_staff/check")
	write_function(f"{ns}:utils/home_travel_staff/schedule_particles", f"""
# Effet de particules quand il reste 50 ticks
scoreboard players operation #plus_50 {ns}.data = #global_tick {ns}.data
scoreboard players add #plus_50 {ns}.data 50
execute as @a if score @s {ns}.travel_staff_cooldown = #plus_50 {ns}.data at @s run particle minecraft:portal ~ ~1 ~ 1 1 1 3 2500
""")
	write_function(f"{ns}:utils/home_travel_staff/check", f"""
# Vérifier si le joueur s'est déplacé
scoreboard players reset @s {ns}.travel_staff_cooldown
execute store result score #new_x {ns}.data run data get entity @s Pos[0] 100
execute store result score #new_y {ns}.data run data get entity @s Pos[1] 100
execute store result score #new_z {ns}.data run data get entity @s Pos[2] 100
execute unless score @s {ns}.travel_x = #new_x {ns}.data run return run function {ns}:utils/home_travel_staff/fail
execute unless score @s {ns}.travel_y = #new_y {ns}.data run return run function {ns}:utils/home_travel_staff/fail
execute unless score @s {ns}.travel_z = #new_z {ns}.data run return run function {ns}:utils/home_travel_staff/fail

# Téléporter
advancement grant @s only {ns}:visible/stuff/home_travel_staff
function {ns}:dimensions/teleport_home
""")
	write_function(f"{ns}:utils/home_travel_staff/fail", """tellraw @s {"text":"[Stardust Fragment] Téléportation annulée car vous avez bougé !","color":"red"}\nplaysound entity.villager.no ambient @s""")

	# Potion de trou de ver
	title: str = json.dumps(item_id_to_text_component("wormhole_potion"))
	write_function(f"{ns}:advancements/right_click", f"""
# Si tient une potion de trou de ver, la gérer
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{wormhole_potion:true}}}}] run function {ns}:utils/wormhole_potion/right_click
""")
	write_function(f"{ns}:utils/wormhole_potion/right_click", f"""
# Préparer le dialogue pour choisir vers quel joueur se téléporter
tag @s add {ns}.temp
data modify storage {ns}:temp dialog set value {{"actions":[],"title":{title}}}
execute as @a[tag=!{ns}.temp] run function {ns}:utils/wormhole_potion/add_to_actions
tag @s remove {ns}.temp

# Message si aucun autre joueur connecté
execute unless data storage {ns}:temp dialog.actions[1] run playsound minecraft:entity.villager.no ambient @s
execute unless data storage {ns}:temp dialog.actions[1] run return run tellraw @s {{"text":"[Stardust Fragment] Aucun autre joueur n'est actuellement connecté pour se téléporter.","color":"red"}}

# Afficher le dialogue
function {ns}:utils/wormhole_potion/show_dialog with storage {ns}:temp dialog
""")
	write_function(f"{ns}:utils/wormhole_potion/add_to_actions", f"""
# Obtenir le nom d'utilisateur du joueur pour la macro
tag @e[type=item] add {ns}.temp
execute at @s run loot spawn ~ ~ ~ loot {ns}:player_head
data modify storage {ns}:temp player_name set from entity @e[type=item,tag=!{ns}.temp,limit=1] Item.components."minecraft:profile".name
kill @e[type=item,tag=!{ns}.temp]
tag @e[type=item,tag={ns}.temp] remove {ns}.temp

# Préparer l'action
data modify storage {ns}:temp element set value {{"label":[],"action":{{}}}}
data modify storage {ns}:temp element.label append value {{"player":{{"name":""}},"hat":true}}
data modify storage {ns}:temp element.label[-1].player.name set from storage {ns}:temp player_name
data modify storage {ns}:temp element.label append value " "
data modify storage {ns}:temp element.label append from storage {ns}:temp player_name
data modify storage {ns}:temp element.label append value " "
data modify storage {ns}:temp element.label append from storage {ns}:temp element.label[0]
data modify storage {ns}:temp element.action set value {{"type":"minecraft:run_command","command":""}}
function {ns}:utils/wormhole_potion/set_teleport_command with storage {ns}:temp

# Ajouter l'action au dialogue
data modify storage {ns}:temp dialog.actions append from storage {ns}:temp element
""")
	write_function(f"{ns}:utils/wormhole_potion/set_teleport_command", f"""
$data modify storage {ns}:temp element.action.command set value 'function {ns}:utils/wormhole_potion/teleport_to {{"name":"$(player_name)"}}'
""")
	write_function(f"{ns}:utils/wormhole_potion/show_dialog", r"""
$dialog show @s {"type":"minecraft:multi_action","columns":3,"exit_action":{"label":{"translate":"gui.back"},"width":200},"title":$(title),"actions":$(actions)}
""")
	write_function(f"{ns}:utils/wormhole_potion/teleport_to", f"""
# Effet de chute lente pour éviter les dégâts de chute
effect give @s minecraft:slow_falling 3 255 true

# Téléporter vers le joueur sélectionné
$tp @s $(name)

# Retour
execute at @s run particle minecraft:portal ~ ~1 ~ 1 1 1 0 2500
execute at @s run playsound {ns}:wormhole_potion ambient @a[distance=..16]

# Consommer une potion de trou de ver
clear @s *[custom_data~{{{ns}:{{"wormhole_potion":true}}}}] 1
""")

	## Perles de dragon et d'ender dragon
	write_load_file(f"\n# Détection de perle d'ender\nscoreboard objectives add {ns}.ender_pearl minecraft.used:minecraft.ender_pearl\n", prepend=True)
	write_advancement(f"{ns}:technical/ender_pearl", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_scores",
							"entity": "this",
							"scores": {f"{ns}.ender_pearl": {"min": 1}}
						}
					]
				}
			}
		},
		"rewards": {
			"function": f"{ns}:advancements/ender_pearl"
		}
	})
	dragon_data: str = f"""{{{ns}:{{"dragon_pearl":true}}}}"""
	ender_dragon_data: str = f"""{{{ns}:{{"ender_dragon_pearl":true}}}}"""
	def line_pearl(data: str, scale: int) -> str:
		return f"""execute if items entity @s weapon.mainhand *[custom_data~{data}] as @n[type=ender_pearl,tag=!{ns}.motion_applied,nbt={{Item:{{components:{{"minecraft:custom_data":{data}}}}}}}] run function {ns}:utils/multiply_motion {{scale:{scale}}}"""
	write_function(f"{ns}:advancements/ender_pearl", f"""
# Révoquer l'advancement et réinitialiser le score
advancement revoke @s only {ns}:technical/ender_pearl
scoreboard players set @s {ns}.ender_pearl 0

# Si Perle de Dragon (Mouvement x1.5), si perle d'ender dragon (Mouvement x2)
{line_pearl(dragon_data, 1500)}
{line_pearl(ender_dragon_data, 2000)}
""", prepend=True)
	write_function(f"{ns}:utils/multiply_motion", f"""
# Impossible de multiplier directement le mouvement (bug Minecraft), donc stocker dans les scoreboards d'abord
$execute store result score #motion_x {ns}.data run data get entity @s Motion[0] $(scale)
$execute store result score #motion_y {ns}.data run data get entity @s Motion[1] $(scale)
$execute store result score #motion_z {ns}.data run data get entity @s Motion[2] $(scale)
execute store result entity @s Motion[0] double 0.001 run scoreboard players get #motion_x {ns}.data
execute store result entity @s Motion[1] double 0.001 run scoreboard players get #motion_y {ns}.data
execute store result entity @s Motion[2] double 0.001 run scoreboard players get #motion_z {ns}.data
tag @s add {ns}.motion_applied
""")

	# Multiplicateur de dégâts des arcs
	write_load_file(f"\n# Détection de tir d'arc\nscoreboard objectives add {ns}.bow_shoot minecraft.used:minecraft.bow\n", prepend=True)
	write_advancement(f"{ns}:technical/bow_shoot", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_scores",
							"entity": "this",
							"scores": {f"{ns}.bow_shoot": {"min": 1}}
						}
					]
				}
			}
		},
		"rewards": {
			"function": f"{ns}:advancements/bow_shoot"
		}
	})

	# Créer le predicate pour s'accroupir
	Mem.ctx.data[ns].predicates["player/sneaking"] = set_json_encoder(Predicate({"condition":"minecraft:entity_properties","entity":"this","predicate":{"flags":{"is_sneaking":True}}}))

	sb_data: str = f"""{{{ns}:{{"stardust_bow":true}}}}"""
	asb_data: str = f"""{{{ns}:{{"awakened_stardust_bow":true}}}}"""
	ub_data: str = f"""{{{ns}:{{"ultimate_bow":true}}}}"""
	def line_bow(data: str, scale: float) -> str:
		return f"""execute if items entity @s weapon.mainhand *[custom_data~{data}] as @n[type=arrow,tag=!{ns}.damage_multiplied,nbt={{weapon:{{components:{{"minecraft:custom_data":{data}}}}}}}] run function {ns}:utils/modify_arrow {{scale:{scale}}}"""
	write_function(f"{ns}:advancements/bow_shoot", f"""
# Révoquer l'advancement et réinitialiser le score
advancement revoke @s only {ns}:technical/bow_shoot
scoreboard players set @s {ns}.bow_shoot 0

# Définir le flag accroupi si le joueur est accroupi
scoreboard players set #is_sneaking {ns}.data 0
execute if predicate {ns}:player/sneaking run scoreboard players set #is_sneaking {ns}.data 1

# Si Arc de Stardust (x2.0), si Arc de Stardust Éveillé (x3.0), si Arc Ultime (x4.0)
{line_bow(sb_data, 2.0)}
{line_bow(asb_data, 3.0)}
{line_bow(ub_data, 4.0)}
""", prepend=True)
	write_function(f"{ns}:utils/modify_arrow", f"""
# Multiplier les dégâts de la flèche
$execute store result entity @s damage double $(scale) run data get entity @s damage 1.0

# Définir NoGravity si accroupi
execute if score #is_sneaking {ns}.data matches 1 run data modify entity @s NoGravity set value 1b

# Marquer comme modifié
tag @s add {ns}.damage_multiplied
""")

	# Toujours un œuf de dragon à la mort
	write_versioned_function("second_5", f"""
# Toujours lâcher un œuf de dragon à la mort
execute unless score #dragon_in_end {ns}.data matches 1.. in minecraft:the_end if entity @e[type=minecraft:ender_dragon,x=0,y=0,z=0,distance=..320,nbt={{Brain:{{}}}}] run function {ns}:utils/dragon_egg_on_death/has_dragon
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/has_dragon", f"""
# On sait qu'il y a un dragon, définir le flag
scoreboard players set #dragon_in_end {ns}.data 1

# Commencer à surveiller la mort du dragon
schedule function {ns}:utils/dragon_egg_on_death/monitor 1s append
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/monitor", f"""
# Vérifier si le dragon est mort
execute in minecraft:the_end unless entity @e[type=minecraft:ender_dragon,x=0,y=0,z=0,distance=..320,nbt={{Brain:{{}}}}] run function {ns}:utils/dragon_egg_on_death/schedule_place_egg

# Replanifier la vérification
execute if score #dragon_in_end {ns}.data matches 1.. run schedule function {ns}:utils/dragon_egg_on_death/monitor 1s replace
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/schedule_place_egg", f"""
# Planifier le drop de l'œuf de dragon après 10 secondes (pour s'assurer que la séquence de mort du dragon est terminée)
schedule function {ns}:utils/dragon_egg_on_death/place_egg_start 10s append
scoreboard players reset #dragon_in_end {ns}.data
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/place_egg_start", f"""
# Lâcher l'œuf de dragon au centre de l'End
execute in minecraft:the_end positioned 0 100 0 run function {ns}:utils/dragon_egg_on_death/place_egg_loop
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/place_egg_loop", f"""
# Si le bloc actuel est de la bedrock, arrêter et placer l'œuf
execute unless loaded ~ ~ ~ run return fail
execute if block ~ ~ ~ bedrock run return run setblock ~ ~1 ~ minecraft:dragon_egg

# Sinon, descendre et répéter jusqu'à trouver de la bedrock ou atteindre le fond
execute positioned ~ ~-1 ~ run function {ns}:utils/dragon_egg_on_death/place_egg_loop
""")

	# Fonctionnalité d'aimant
	write_function(f"{ns}:advancements/inventory_changed", f"""
# Si a un aimant d'objets, ajouter le tag et le score
execute if entity @s[tag={ns}.has_item_magnet] unless items entity @s weapon.offhand *[custom_data~{{{ns}:{{"item_magnet":true}}}}] run function {ns}:utils/magnet/removed
execute if entity @s[tag=!{ns}.has_item_magnet] if items entity @s weapon.offhand *[custom_data~{{{ns}:{{"item_magnet":true}}}}] run function {ns}:utils/magnet/added
""", prepend=True)
	write_function(f"{ns}:utils/magnet/added", f"""
# Ajouter le tag et le score
tag @s add {ns}.has_item_magnet
scoreboard players add #has_item_magnet {ns}.data 1
""")
	write_function(f"{ns}:utils/magnet/removed", f"""
# Retirer le tag et le score
tag @s remove {ns}.has_item_magnet
scoreboard players remove #has_item_magnet {ns}.data 1
""")
	write_versioned_function("tick_2", f"""
# Fonctionnalité d'aimant d'objets
execute if score #has_item_magnet {ns}.data matches 1.. at @a[tag={ns}.has_item_magnet] run tp @e[type=item,distance=..4] ~ ~ ~
""")

	# Sac d'artefacts chanceux
	write_function(f"{ns}:advancements/right_click", f"""
# Si tient un sac d'artefacts chanceux, le gérer
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{"lucky_artifact_bag":true}}}}] run function {ns}:utils/lucky_artifact_bag
""")
	write_function(f"{ns}:utils/lucky_artifact_bag", f"""
# Donner un artefact aléatoire
loot give @s loot {ns}:random_artifact

# Son et particules
particle minecraft:happy_villager ~ ~1 ~ 0.5 0.5 0.5 0 20
playsound minecraft:entity.player.levelup ambient @s ~ ~ ~ 0.5

# Consommer un sac d'artefacts chanceux
clear @s *[custom_data~{{{ns}:{{lucky_artifact_bag:true}}}}] 1
""")
	Mem.ctx.data[ns].loot_tables["random_artifact"] = set_json_encoder(LootTable({
		"pools": [{
			"rolls": 1,
			"bonus_rolls": 0,
			"entries": [
				{"type": "minecraft:loot_table", "weight": 5, "value": "stardust:i/health_artifact_lv1"},
				{"type": "minecraft:loot_table", "weight": 5, "value": "stardust:i/damage_artifact_lv1"},
				{"type": "minecraft:loot_table", "weight": 5, "value": "stardust:i/speed_artifact_lv1"},
				{"type": "minecraft:loot_table", "value": "stardust:i/health_artifact_lv2"},
				{"type": "minecraft:loot_table", "value": "stardust:i/damage_artifact_lv2"},
				{"type": "minecraft:loot_table", "value": "stardust:i/speed_artifact_lv2"},
			]
		}]
	}), max_level=4)
```

---

## 📖 Résumé

### **Comparaison des trois approches**

| Approche | Cas d'usage | Complexité | Flexibilité |
|----------|----------|------------|-------------|
| **Fichiers statiques (beet.yml)** | Fichiers pré-écrits | ⭐ Simple | ⭐ Faible |
| **API native Beet** | Contrôle total | ⭐⭐⭐ Complexe | ⭐⭐⭐ Élevée |
| **Helpers StewBeet** | Génération dynamique | ⭐⭐ Moyenne | ⭐⭐ Moyenne-Élevée |

### **Quand utiliser chacune**

- 📁 **Fichiers statiques** : Fichiers de configuration, recettes statiques, fonctions simples
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

