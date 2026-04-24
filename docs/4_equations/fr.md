
# ⚡ Guide des Équations StewBeet

## 📖 Définitions
- **ScoreboardEquation** : Un constructeur chaînable qui génère des commandes `scoreboard players operation` Minecraft et stocke le résultat final dans un objectif de scoreboard.
- **StorageEquation** : Un constructeur chaînable qui calcule via un scoreboard caché `#temp_result`, puis envoie le résultat vers un storage NBT avec une commande `execute store result` et un scale factor configurable.
- **Chaînage de méthodes** : Chaque méthode d'opération retourne `self`, permettant de chaîner les appels : `.set(10).add(5).multiply(2)`.
- **Commentaire d'en-tête d'équation** : La première ligne de chaque équation rendue est un `# commentaire` lisible qui reflète l'expression mathématique complète, rendant les fonctions générées auto-documentées.
- **Argument macro** : Un paramètre de macro de fonction Minecraft sous la forme `$(nom)`. Utilisé comme opérande, une ligne `$scoreboard players set` est automatiquement préfixée.
- **Fake-player** : Joueur fictif utilisé par Minecraft pour stocker des valeurs dans un scoreboard (ex. `#value`, `#temp_result`).
- **Scale factor** : Multiplicateur appliqué lors de l'écriture d'un entier vers le storage NBT, permettant de le convertir en valeur flottante.

## 🧪 Exemples
📄 **Fichier d'exemple** : [extensive/src/link.py](../../templates/extensive/src/link.py) 🔗<br>
📄 **Code source** : [stewbeet/core/utils/equation.py](../../python_package/stewbeet/core/utils/equation.py) 🔗<br>

## 🔗 Dépendances
- **✅ Requis** : Framework StewBeet (`from stewbeet import *`)
- **✅ Requis** : `stewbeet.plugins.auto.scoreboard_constants` — initialise toutes les constantes entières (ex. `#5`) générées par les équations
- **📍 Position** : Appelé dans un hook de plugin `beet_default`, après la configuration des définitions
- **🔄 Intégration** : La sortie est passée à `write_function()` pour intégrer les commandes dans les fonctions de datapack

## 📋 Vue d'ensemble
`ScoreboardEquation` et `StorageEquation` sont des constructeurs d'équations chaînables qui traduisent une expression Python lisible en une série de commandes Minecraft `scoreboard players operation`. Les deux classes génèrent une sortie auto-documentée : la première ligne est toujours un `# commentaire` montrant l'équation complète, suivi de toutes les commandes de scoreboard nécessaires pour la calculer.

**Utilisez les équations chaque fois que vous avez besoin d'arithmétique entière multi-étapes dans une fonction de datapack** — au lieu d'écrire manuellement des commandes `scoreboard players operation` brutes, vous construisez l'expression en Python et appelez `str()` pour obtenir le bloc mcfunction complet.

## 🎯 Objectif
- 🔢 Construire des arithmétiques de scoreboard complexes avec une syntaxe Python claire et lisible
- 📝 Générer automatiquement un `# commentaire` d'en-tête reflétant l'équation complète pour des fonctions auto-documentées
- ⛓ Chaîner les opérations via des méthodes (`.set()`, `.add()`, `.multiply()`, …) ou des opérateurs Python (`+`, `-`, `*`, `/`, `//`, `%`, `-` unaire)
- 🎯 `ScoreboardEquation` — le résultat reste dans un objectif de scoreboard
- 💾 `StorageEquation` — le résultat est envoyé vers un storage NBT avec un scale factor flottant
- 🧩 Passer une autre instance d'équation comme opérande — ses commandes sont automatiquement intégrées
- 📦 Les arguments macro (`$(nom)`) sont gérés automatiquement avec un préfixe `$scoreboard players set`

---

## ⚙️ ScoreboardEquation

### Constructeur

```python
ScoreboardEquation(player: str, scoreboard: str | None = None)
```

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `player` | `str` | — | Joueur cible ou fake-player (ex. `"@s"`, `"#value"`) |
| `scoreboard` | `str \| None` | `{project_id}.data` | Objectif de scoreboard cible |

### 🎯 Exemple de base

Depuis le [template extensive](../../templates/extensive/src/link.py) :
```python
ns: str = ctx.project_id

equation  = ScoreboardEquation("#value", f"{ns}.data").set(10).add(5).multiply(2).divide(3).modulo(100)
equation2 = (ScoreboardEquation("#value2", f"{ns}.data").set(20) - 6 + 7) * 8 // 4 % 5

write_function(f"{ns}:equation/test", str(equation) + "\n" + str(equation2))
```

**mcfunction généré :**
```mcfunction
# scoreboard #value <ns>.data = 10 + 5 * 2 / 3 % 100
scoreboard players set #value <ns>.data 10
scoreboard players operation #value <ns>.data += #5 <ns>.data
scoreboard players operation #value <ns>.data *= #2 <ns>.data
scoreboard players operation #value <ns>.data /= #3 <ns>.data
scoreboard players operation #value <ns>.data %= #100 <ns>.data
# scoreboard #value2 <ns>.data = 20 - 6 + 7 * 8 / 4 % 5
scoreboard players set #value2 <ns>.data 20
scoreboard players operation #value2 <ns>.data -= #6 <ns>.data
scoreboard players operation #value2 <ns>.data += #7 <ns>.data
scoreboard players operation #value2 <ns>.data *= #8 <ns>.data
scoreboard players operation #value2 <ns>.data /= #4 <ns>.data
scoreboard players operation #value2 <ns>.data %= #5 <ns>.data
```

> **Note** : Quand `scoreboard` est omis, il prend par défaut la valeur `{project_id}.data`. Les opérandes entiers sont automatiquement enregistrés comme constantes de scoreboard (ex. `#5`) et initialisés par le plugin `auto.scoreboard_constants`.

### 🔀 Utiliser un scoreboard de joueur comme opérande
Passez n'importe quel nom de joueur ou sélecteur comme source — fournissez un scoreboard explicite en second argument s'il diffère de l'objectif propre à l'équation :
```python
# Copier le score de @s depuis un autre objectif, puis diviser par 100
equation = ScoreboardEquation("@s", f"{ns}.data").set("@s", f"{ns}.base").divide(100)
```

**mcfunction généré :**
```mcfunction
# scoreboard @s <ns>.data = @s <ns>.base / 100
scoreboard players operation @s <ns>.data  = @s <ns>.base
scoreboard players operation @s <ns>.data /= #100 <ns>.data
```

### 🧩 Combiner deux équations
N'importe quelle instance d'équation peut être passée directement comme opérande. Ses commandes sont intégrées en premier, et son joueur/scoreboard final est utilisé comme valeur source :
```python
eq_a = ScoreboardEquation("@s").set(10) * 5
eq_b = ScoreboardEquation("#toto", "some_score").set(20) * 2
write_function(f"{ns}:equation/combined", str(eq_a * eq_b))
```

**mcfunction généré :**
```mcfunction
# scoreboard @s <ns>.data = 10 * 5 * (scoreboard #toto some_score = 20 * 2)
scoreboard players set @s <ns>.data 10
scoreboard players operation @s <ns>.data *= #5 <ns>.data
scoreboard players set #toto some_score 20
scoreboard players operation #toto some_score *= #2 <ns>.data
scoreboard players operation @s <ns>.data *= #toto some_score
```

---

## ⚙️ StorageEquation

`StorageEquation` fonctionne exactement comme `ScoreboardEquation` pour les étapes arithmétiques, mais lors de l'appel à `str()`, une commande `execute store result storage …` est ajoutée pour persister le résultat dans le stockage NBT.

### Constructeur

```python
StorageEquation(storage: str, path: str, scale: float = 1.0, storage_type: str = "double")
```

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `storage` | `str` | — | Resource location du storage (ex. `"my_ns:my_storage"`) |
| `path` | `str` | — | Chemin NBT dans le storage (ex. `"result"`) |
| `scale` | `float` | `1.0` | Scale factor appliqué lors de l'écriture — utilisez de petites valeurs (ex. `0.000001`) pour convertir des entiers en flottants |
| `storage_type` | `str` | `"double"` | Type de nombre NBT : `"double"`, `"float"`, `"int"`, `"long"`, `"short"`, `"byte"` |

Toute l'arithmétique s'exécute sur un fake-player caché `#temp_result`. Le `execute store result` final est ajouté automatiquement lors de l'appel à `str()`.

### 🎯 Exemple avec des arguments macro
```python
equation = (
    StorageEquation("some_namespace:some_path", "result_path", 0.000005, "double")
    .set("-$(amount)")
    .multiply(1000000)
    .divide("$(max_damage)")
    .subtract("#toto")
)
write_function(f"{ns}:compute/result", str(equation))
```

**mcfunction généré :**
```mcfunction
# storage some_namespace:some_path result_path = (-$(amount) * 1000000 / $(max_damage) - #toto) * 0.000005
$scoreboard players set #temp_result <ns>.data -$(amount)
scoreboard players operation #temp_result <ns>.data *= #1000000 <ns>.data
$scoreboard players set #temp_divide <ns>.data $(max_damage)
scoreboard players operation #temp_result <ns>.data /= #temp_divide <ns>.data
scoreboard players operation #temp_result <ns>.data -= #toto <ns>.data
execute store result storage some_namespace:some_path result_path double 0.000005 run scoreboard players get #temp_result <ns>.data
```

> **Note** : Les lignes commençant par `$` sont des commandes macro Minecraft, générées automatiquement lorsqu'un argument macro (`$(nom)`) apparaît comme opérande.

---

## 🔧 Référence des opérations

### Méthodes et opérateurs Python

| Méthode | Opérateur Python | Op. scoreboard | Description |
|---------|-----------------|----------------|-------------|
| `.set(value)` | — | `scoreboard players set` | Affectation initiale — **doit être appelée en premier** |
| `.add(value)` | `+` | `+=` | Addition |
| `.subtract(value)` | `-` | `-=` | Soustraction |
| `.multiply(value)` | `*` | `*=` | Multiplication |
| `.divide(value)` | `/` ou `//` | `/=` | Division entière (`//` se comporte de façon identique à `/`) |
| `.modulo(value)` | `%` | `%=` | Modulo |
| Négation unaire | `-equation` | `*= #-1` | Multiplie la valeur courante par −1 |

> Toutes les méthodes acceptent un second argument optionnel `scoreboard` pour cibler un objectif différent pour la valeur source.

### Types de `value` acceptés

| Type | Exemple | Comportement |
|------|---------|--------------|
| `int` | `42` | Génère une constante fake-player `#42` ; utilise `scoreboard players operation` avec `{project_id}.data` |
| `str` — joueur / sélecteur | `"@s"`, `"#other"` | Opération directe sur scoreboard ; utilise l'objectif propre à l'équation sauf si `scoreboard` est fourni |
| `str` — argument macro | `"$(amount)"` | Préfixe `$scoreboard players set #temp_… …` pour gérer la macro avant l'opération |
| `BaseEquation` | autre équation | Intègre d'abord les commandes de l'équation source, puis utilise son joueur/scoreboard final comme source |

> **Important** : Toute l'arithmétique de scoreboard Minecraft est **entière uniquement**. Utilisez le paramètre `scale` de `StorageEquation` pour convertir le résultat entier en valeur NBT flottante lors de l'écriture dans le storage.
