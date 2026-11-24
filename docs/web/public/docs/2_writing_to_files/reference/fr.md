
# Référence des fonctions d'aide

Tous les helpers que StewBeet ajoute à beet pour écrire des fichiers de datapack, avec les arguments
que prend chacun.

[Écrire des functions et des fichiers](../fr.md) aide à choisir entre les trois approches, et [le cookbook](../cookbook/fr.md) contient des exemples pratiques.

### Écriture de functions

#### `write_function()`
Écrit du contenu dans un fichier de function.

```python
def write_function(
    path: str,                                      # Function path (e.g., "namespace:folder/function_name")
    content: str,                                   # The content to write
    overwrite: bool = False,                        # Overwrite instead of appending
    prepend: bool = False,                          # Prepend instead of appending, ignored with overwrite
    tags: list[str] | None = None,                  # Function tags to add (e.g., ["minecraft:load"])
    condition: Callable[[str], bool] | None = None  # Receives the existing content, writes nothing when it returns False
) -> Function | None:                               # The written function, None when the condition refused
```

**Exemple :**
```python
write_function(f"{ns}:utils/teleport_spawn", """
# Teleport player to spawn
tp @s 0 64 0
""", tags=[f"{ns}:tp_spawn"])
```
La function est écrite dans `data/<namespace>/function/utils/teleport_spawn.mcfunction`, et ajoutée au tag de function `<namespace>:tp_spawn`.

`condition` rend une écriture idempotente : `condition=lambda existing: "tp @s 0 64 0" not in existing` ajoute les commandes une seule fois, quel que soit le nombre d'exécutions du code. Les autres fonctions d'écriture prennent aussi un `condition`, appelé avec les valeurs ou les données existantes.

---

#### `read_function()`
Lit le contenu d'une function existante, ou une chaîne vide si elle n'existe pas.

```python
def read_function(
    path: str  # Function path (e.g., "namespace:folder/function_name")
) -> str:
```

**Exemple :**
```python
existing_content = read_function(f"{ns}:my_function")
modified_content = existing_content.replace("say Hello", "say Goodbye")
write_function(f"{ns}:my_function", modified_content, overwrite=True)
```

---

#### Préférer les accesseurs Resource aux chemins en dur

Dès que le chemin appartient à une définition, prenez-le dans l'`Item` ou le `Block` au lieu de retaper la convention.
Une `Resource` est une chaîne, elle s'insère donc directement dans chacune de ces fonctions :

```python
furnace = Block.from_id("electric_furnace")

# Hardcoded: breaks silently if the convention changes
write_function(f"{ns}:custom_blocks/electric_furnace/tick", "...")

# Derived from the definition
write_function(furnace.functions.tick, "...")

# Equivalent, without the definition lookup (BlockFunctions builds the same paths)
write_function(BlockFunctions("electric_furnace").tick, "...")

# To append to a function that already exists, take the beet Function with .obj:
furnace.functions.place_secondary.obj.append("tag @s add my_ns.active")
# (raises KeyError if the function hasn't been generated yet: a loud failure
#  instead of your commands silently landing before the block setup)

# Works the same for loot tables, models, textures, advancements
write_function(f"{ns}:give_furnace", f"loot give @s loot {furnace.loot_table}")
```

Voir [Resource locations et BlockFunctions](../../1_definitions_setup/fr.md#resource-locations-et-blockfunctions) pour la liste complète des accesseurs.

---

#### `write_load_file()`
Écrit du contenu dans la function de load principale (exécutée au chargement du datapack).

```python
def write_load_file(
    content: str,                                   # The content to write
    overwrite: bool = False,                        # Overwrite instead of appending
    prepend: bool = False,                          # Prepend instead of appending
    tags: list[str] | None = None,                  # Additional tags to add
    condition: Callable[[str], bool] | None = None  # Writes nothing when it returns False for the existing content
) -> Function | None:
```

**Chemin :** `namespace:v{version}/load/confirm_load`

**Exemple :**
```python
# Prepend initialization code (runs first)
write_load_file("""
# Initialize core scoreboards
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)

# Append setup code (runs after prepended content)
write_load_file("""
# Set default values
scoreboard players set #2 data 2
scoreboard players set #100 data 100
""")
```

---

#### `persistent_item_display()`
Ajoute à la function de load un `item_display` conservé dans le chunk forceloadé à `FORCELOAD_BLOCK`, et renvoie son UUID pour le cibler avec `execute as`. Voir [Garder les functions rapides](../../10_performance/fr.md).

```python
def persistent_item_display(name: str) -> str:   # name: unique within the project
```

---

#### `write_tick_file()`
Écrit du contenu dans la function de tick principale (exécutée à chaque tick du jeu, 20 fois par seconde).

```python
def write_tick_file(
    content: str,                                   # The content to write
    overwrite: bool = False,                        # Overwrite instead of appending
    prepend: bool = False,                          # Prepend instead of appending
    tags: list[str] | None = None,                  # Additional tags to add
    condition: Callable[[str], bool] | None = None  # Writes nothing when it returns False for the existing content
) -> Function | None:
```

**Chemin :** `namespace:v{version}/tick`

**Exemple :**
```python
write_tick_file("""
# Increment timer
scoreboard players add #global_timer data 1

# Reset every minute
execute if score #global_timer data matches 1200.. run scoreboard players set #global_timer data 0
""")
```

---

#### `write_versioned_function()`
Écrit du contenu dans une function d'horloge versionnée.

```python
def write_versioned_function(
    path: str,                                      # Function path without namespace (e.g., "second", "tick_2")
    content: str,                                   # The content to write
    overwrite: bool = False,                        # Overwrite instead of appending
    prepend: bool = False,                          # Prepend instead of appending
    tags: list[str] | None = None,                  # Additional tags to add
    condition: Callable[[str], bool] | None = None  # Writes nothing when it returns False for the existing content
) -> Function | None:
```

**Chemin :** `namespace:v{version}/{path}`

**Functions d'horloge courantes :** (les autres noms ne sont pas appelés automatiquement par défaut)
| Chemin | Fréquence | Ticks | Description |
|--------|-----------|-------|-------------|
| `tick` | À chaque tick | 1 | S'exécute avec le fichier tick principal |
| `tick_2` | Tous les 2 ticks | 2 | Demi-vitesse (10 fois par seconde) |
| `second` | Chaque seconde | 20 | Une fois par seconde |
| `second_5` | Toutes les 5 secondes | 100 | Pratique pour les vérifications périodiques |
| `minute` | Chaque minute | 1200 | Pour les mises à jour rares |

**Exemple :**
```python
# Runs every second
write_versioned_function("second", """
# Regenerate health for players with regen effect
execute as @a[nbt={active_effects:[{id:"minecraft:regeneration"}]}] run effect give @s instant_health 1 0 true
""")

# Runs every 5 seconds
write_versioned_function("second_5", """
# Spawn particles at marker entities
execute at @e[type=marker,tag=particle_source] run particle flame ~ ~ ~ 0.5 0.5 0.5 0.01 10
""")

# Runs every minute
write_versioned_function("minute", """
# Clean up old items
kill @e[type=item,nbt={Age:5400s}]
""")
```

---

#### `write_unload_file()`
Écrit du contenu dans la function exécutée au déchargement du datapack, `namespace:v{version}/unload`, qui est ajoutée au tag de function `namespace:unload`.

```python
def write_unload_file(
    content: str,                                   # The content to write
    overwrite: bool = False,                        # Overwrite instead of appending
    prepend: bool = False,                          # Prepend instead of appending
    tags: list[str] | None = None,                  # Additional tags, `namespace:unload` is always added
    condition: Callable[[str], bool] | None = None  # Writes nothing when it returns False for the existing content
) -> Function | None:
```

---

#### `write_scheduled_function()`
Écrit une function qui se reprogramme elle-même, et programme sa première exécution depuis le fichier load.

```python
def write_scheduled_function(
    duration: int | str,            # Delay before each run, a digit-only string is read as an int
    content: str,                   # The commands run each time
    unit: str = "t",                # Time unit, used only when duration is an int
    path: str | None = None,        # Defaults to "namespace:v{version}/scheduled/{delay}"
    overwrite: bool = False,        # Overwrite instead of appending
    prepend: bool = False,          # Prepend instead of appending, ignored with overwrite
    condition: Callable[[str], bool] = lambda existing_content: True  # Receives the existing content of the scheduled function
) -> Function | None:
```

**Exemple :**
```python
write_scheduled_function(10, f"scoreboard players add #timer {ns}.data 1", unit="s")
```
Cela écrit `{ns}:v{version}/scheduled/10s`, qui se termine par `schedule function ... 10s` pour s'exécuter toutes les 10 secondes, et ajoute au fichier load le premier `schedule function ... 10s replace`. Une durée en chaîne comme `"5s"` est utilisée telle quelle comme délai.

---

### Écriture d'advancements

#### `write_advancement()`
Écrit un fichier d'advancement.

```python
def write_advancement(
    path: str,                              # Advancement path (e.g., "namespace:folder/name")
    advancement: Advancement | JsonDict,    # Advancement data or object
    overwrite: bool = False,                # Overwrite instead of merging into the existing one
    max_level: int = -1,                    # Maximum depth of the JSON dump (-1 = default)
    condition: Callable[[JsonDict], bool] = lambda existing_data: True  # Receives the existing data, writes nothing when it returns False
) -> Advancement | None:                    # None when the condition refused
```

**Exemple :**
```python
# Technical advancement (hidden from players)
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

# Visible advancement
write_advancement(f"{ns}:story/craft_ruby_sword", {
    "display": {
        "icon": {"id": "minecraft:diamond_sword", "components": {"item_model": f"{ns}:ruby_sword"}},
        "title": {"text": "Legendary Blade", "color": "red"},
        "description": {"text": "Craft a Ruby Sword"},
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

#### `write_predicate()` and `write_enchantment()`
Même signature et même fusion que `write_advancement()` (les données existantes sont fusionnées avec `super_merge_dict()`), pour les predicates et les enchantments.

```python
write_predicate(f"{ns}:is_sneaking", {
    "condition": "minecraft:entity_properties",
    "entity": "this",
    "predicate": {"flags": {"is_sneaking": True}}
})
```

#### `write_json_resource()`
La même chose pour tout autre registre JSON : passez le registre et sa classe beet.

```python
def write_json_resource(
    registry: MutableMapping[str, T],   # Where the resource goes (e.g., Mem.ctx.data.item_modifiers)
    file_type: type[T],                 # Its beet class (e.g., ItemModifier)
    path: str,                          # Resource location, with or without ".json"
    data: T | JsonDict,                 # Resource data or object
    overwrite: bool = False,            # Overwrite instead of merging into the existing one
    max_level: int = -1,                # Maximum depth of the JSON dump (-1 = default)
    condition: Callable[[JsonDict], bool] = lambda existing_data: True  # Receives the existing data, writes nothing when it returns False
) -> T | None:
```

**Exemple :**
```python
from beet import ItemModifier
write_json_resource(Mem.ctx.data.item_modifiers, ItemModifier, f"{ns}:set_count_4", {"function": "minecraft:set_count", "count": 4})
```

---

### Écriture de tags

#### `write_tag()`
Écrit un fichier de tag (générique pour tout type de tag).

```python
def write_tag(
    path: str,                                  # Tag path (e.g., "namespace:my_tag")
    tag_type: NamespaceProxy | NamespaceContainer,  # Tag type (e.g., ctx.data.function_tags)
    values: list[Any] | None = None,           # Values to add to the tag, merged without duplicates
    prepend: bool = False,                      # Prepend instead of appending
    max_level: int | None = None,               # Maximum depth of the JSON dump (None = default)
    condition: Callable[[list[Any]], bool] = lambda existing_values: True  # Receives the existing values, writes nothing when it returns False
) -> TagFile | None:                            # None when the condition refused
```

**Exemple :**
```python
# Function tags
write_tag(f"{ns}:custom_load", Mem.ctx.data.function_tags, [
    f"{ns}:init/scoreboards",
    f"{ns}:init/teams"
])

# Entity type tags
write_tag(f"{ns}:hostile_mobs", Mem.ctx.data.entity_type_tags, [
    "minecraft:zombie",
    "minecraft:skeleton",
    "minecraft:spider"
])

# Block tags
write_tag(f"{ns}:mineable/pickaxe", Mem.ctx.data.block_tags, [
    "stone",
    "emerald_block"
])
```

---

### Fonctions utilitaires

#### `super_merge_dict()`
Fusionne récursivement deux dictionnaires sans modifier les originaux. Les listes sont concaténées, sans doublons sauf si elles contiennent des dictionnaires.

```python
def super_merge_dict(
    dict1: JsonDict,  # First dictionary
    dict2: JsonDict   # Second dictionary (overrides dict1)
) -> JsonDict:
```

**Exemple :**
```python
base_config = {
    "settings": {"power": 100, "speed": 5},
    "enabled": True
}

override_config = {
    "settings": {"power": 150},  # Override power, keep speed
    "debug": True                 # Add new field
}

merged = super_merge_dict(base_config, override_config)
# Result: {"settings": {"power": 150, "speed": 5}, "enabled": True, "debug": True}
```

---

#### `set_json_encoder()`
Définit un encodeur JSON personnalisé pour la mise en forme.

```python
def set_json_encoder(
    obj: JsonFileT,              # JsonFile object (Advancement, FunctionTag, etc.)
    max_level: int | None = None,  # Maximum depth of the JSON dump (None = default)
    indent: str | int = '\t'      # Indentation character or spaces
) -> JsonFileT:
```

**Exemple :**
```python
from stewbeet import Mem, set_json_encoder
from beet import Advancement

advancement = Advancement({
    "criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}}
})

# Use tabs for indentation (default)
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement)

# Use 2 spaces
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement, indent=2)

# Limit indentation depth
Mem.ctx.data.advancements["my_advancement"] = set_json_encoder(advancement, max_level=3)
```

---

#### `convert_to_serializable()`
Convertit en données sérialisables en JSON les objets avec une méthode `to_dict()`, les dataclasses, les mappings et les itérables. Elle vient de stouputils, dont StewBeet dépend.

```python
def convert_to_serializable(
    obj: Any  # Object to convert
) -> Any:
```

**Exemple :**
```python
import stouputils as stp
from stewbeet import Item

item = Item.from_id("simplunium_ingot")
serializable_data = stp.convert_to_serializable(item)
```

---

#### `texture_mcmeta()`
Crée un objet Texture avec son fichier mcmeta s'il existe.

```python
def texture_mcmeta(
    source_path: str  # Path to texture file (e.g., "assets/textures/my_texture.png")
) -> Texture:
```

**Exemple :**
```python
from stewbeet import Mem, texture_mcmeta

# Automatically loads animated_block.png.mcmeta if it exists
texture = texture_mcmeta("assets/textures/animated_block.png")
Mem.ctx.assets["my_namespace"].textures["block/animated_block"] = texture
```

---

## Étapes suivantes

- [Écrire des functions et des fichiers](../fr.md) : quelle approche choisir, et pourquoi.
- [Cookbook](../cookbook/fr.md) : ces helpers utilisés dans des fichiers complets qui fonctionnent.
- [Equations](../../4_equations/fr.md) : construire de l'arithmétique de scoreboard à intégrer dans ce que vous écrivez.

