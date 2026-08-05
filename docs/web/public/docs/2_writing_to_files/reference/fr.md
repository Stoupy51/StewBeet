# Référence des fonctions utilitaires

Chaque fonction que StewBeet ajoute par-dessus beet pour écrire des fichiers de datapack, avec
les arguments que chacune accepte.

**Voir aussi** [Écrire fonctions et fichiers](../fr.md) pour choisir entre les trois
approches, et [les recettes](../cookbook/fr.md) pour des exemples complets.

### Écriture de fonctions

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

#### Préférez les accesseurs Resource aux chemins codés en dur

Dès que le chemin appartient à une définition, récupérez-le depuis l'`Item`/`Block` plutôt que de retaper la convention.
Un objet `Resource` est une chaîne, il s'utilise donc directement dans toutes ces fonctions :

```python
furnace = Block.from_id("electric_furnace")

# ❌ Codé en dur — casse silencieusement si la convention change
write_function(f"{ns}:custom_blocks/electric_furnace/tick", "...")

# ✅ Dérivé de la définition
write_function(furnace.functions.tick, "...")

# ✅ Équivalent, sans passer par la définition (BlockFunctions construit les mêmes chemins)
write_function(BlockFunctions("electric_furnace").tick, "...")

# ✅ Ajouter à une fonction qui existe déjà ? Récupérez la Function beet via .obj :
furnace.functions.place_secondary.obj.append("tag @s add my_ns.active")
# (lève KeyError si la fonction n'a pas encore été générée — un échec bruyant
# plutôt que vos commandes placées silencieusement avant le setup du bloc)

# Fonctionne pareil pour les loot tables, modèles, textures, progrès
write_function(f"{ns}:give_furnace", f"loot give @s loot {furnace.loot_table}")
```

Voir [Emplacements de ressources](../../1_definitions_setup/fr.md#-emplacements-de-ressources) pour la liste complète des accesseurs.

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

### Écriture d'advancements

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

### Écriture de tags

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

### Fonctions utilitaires

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

## Prochaines étapes

- [Écrire fonctions et fichiers](../fr.md) — quelle approche choisir, et pourquoi.
- [Recettes](../cookbook/fr.md) — ces fonctions dans des fichiers complets et fonctionnels.
- [Équations](../../4_equations/fr.md) — construire l'arithmétique de scoreboard à intégrer.
