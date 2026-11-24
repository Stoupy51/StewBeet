
# Equations

`ScoreboardEquation` et `StorageEquation` sont des constructeurs d'équations chaînables qui transforment une expression Python lisible en commandes Minecraft. Les deux écrivent l'équation complète en `# comment` sur la première ligne, suivie des commandes qui la calculent.

Utilisez les equations pour l'arithmétique entière en plusieurs étapes dans une function de datapack. Construisez l'expression en Python et appelez `str()` pour obtenir le bloc mcfunction complet, plutôt que d'écrire à la main des commandes `scoreboard players operation`.

- Fichier d'exemple : [extensive/src/link.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py)
- Code source : [stewbeet/core/utils/equation.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/core/utils/equation.py)

Ce qu'elles font :

- Construire de l'arithmétique de scoreboard avec la syntaxe Python ordinaire.
- Écrire un en-tête `# comment` qui reprend l'équation complète.
- Chaîner des méthodes (`.set()`, `.add()`, `.multiply()`) ou utiliser les opérateurs Python (`+`, `-`, `*`, `/`, `//`, `%`, `-` unaire).
- `ScoreboardEquation` laisse son résultat dans un objective de scoreboard.
- `StorageEquation` écrit son résultat dans le storage NBT, avec un facteur d'échelle.
- Prendre une autre equation comme opérande, dont les commandes sont insérées en ligne.
- Gérer les arguments de macro (`$(name)`), qui reçoivent un préfixe `$` sur les lignes qui les utilisent.

Importez-les avec `from stewbeet import *`, et passez la sortie à `write_function()` pour intégrer les commandes dans une function de datapack. Avant la 26.3, les constantes entières qu'une equation utilise (`#5`, `#100`) sont initialisées par le plugin `stewbeet.plugins.auto.scoreboard_constants`, qui cherche chaque `#<integer> <project_id>.data` dans vos functions.

## Depuis Minecraft 26.3 : une seule commande `/compute`

Quand le projet cible la 26.3 ou plus, une equation est rendue en une seule commande `execute store result ... run compute default integer <provider>`, le provider étant un arbre de number providers `add`, `sub`, `mul`, `floor_div` et `floor_mod` qui arrondit exactement comme les opérations de scoreboard. Les exemples ci-dessous montrent les opérations de scoreboard, ce que contient `.ops` et ce qui est écrit avant la 26.3.

```python
equation = ScoreboardEquation("#value", f"{ns}.data").set(10).add(5).multiply(2)
```
```mcfunction
# scoreboard #value <ns>.data = 10 + 5 * 2
execute store result score #value <ns>.data run compute default integer {type:"mul",inputs:[{type:"add",inputs:[10,5]},2]}
```

- Un opérande qu'un number provider ne sait pas nommer, un sélecteur autre que `@s`, garde toute l'equation en opérations de scoreboard.
- Une equation combinée est calculée en ligne : son propre score cible n'est pas écrit.
- Aucune constante `#5` n'est nécessaire, donc `auto.scoreboard_constants` n'a rien à initialiser pour ces equations.

## ScoreboardEquation

### Constructeur

```python
ScoreboardEquation(player: str, scoreboard: str | None = None)
```

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `player` | `str` | - | Joueur cible ou fake-player (ex. `"@s"`, `"#value"`) |
| `scoreboard` | `str \| None` | `{project_id}.data` | Objective de scoreboard cible |

### Exemple de base

Tiré du [template extensive](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py) :

```python
ns: str = ctx.project_id

equation  = ScoreboardEquation("#value", f"{ns}.data").set(10).add(5).multiply(2).divide(3).modulo(100)
equation2 = (ScoreboardEquation("#value2", f"{ns}.data").set(20) - 6 + 7) * 8 // 4 % 5

write_function(f"{ns}:equation/test", str(equation) + "\n" + str(equation2))
```

Mcfunction généré avant la 26.3 :

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

Quand `scoreboard` est omis, il vaut `{project_id}.data`. Les opérandes entiers sont des fake players comme `#5`, que le plugin `auto.scoreboard_constants` définit dans la function de load.

### Utiliser le scoreboard d'un joueur comme opérande

Passez n'importe quel nom de joueur ou sélecteur comme source. Donnez un scoreboard explicite en second argument s'il diffère de l'objective de l'equation :

```python
# Copy @s's score from another objective, then divide by 100
equation = ScoreboardEquation("@s", f"{ns}.data").set("@s", f"{ns}.base").divide(100)
```

Mcfunction généré :

```mcfunction
# scoreboard @s <ns>.data = @s <ns>.base / 100
scoreboard players operation @s <ns>.data  = @s <ns>.base
scoreboard players operation @s <ns>.data /= #100 <ns>.data
```

### Combiner deux equations

Toute instance d'equation peut être passée directement comme opérande. Ses commandes sont insérées en premier, et son joueur et son scoreboard finaux servent de valeur source :

```python
eq_a = ScoreboardEquation("@s").set(10) * 5
eq_b = ScoreboardEquation("#toto", "some_score").set(20) * 2
write_function(f"{ns}:equation/combined", str(eq_a * eq_b))
```

Mcfunction généré avant la 26.3 :

```mcfunction
# scoreboard @s <ns>.data = 10 * 5 * (scoreboard #toto some_score = 20 * 2)
scoreboard players set @s <ns>.data 10
scoreboard players operation @s <ns>.data *= #5 <ns>.data
scoreboard players set #toto some_score 20
scoreboard players operation #toto some_score *= #2 <ns>.data
scoreboard players operation @s <ns>.data *= #toto some_score
```

---

## StorageEquation

`StorageEquation` fonctionne comme `ScoreboardEquation` pour les étapes d'arithmétique, mais `str()` stocke aussi le résultat dans le storage NBT.

### Constructeur

```python
StorageEquation(storage: str, path: str, scale: float = 1.0, storage_type: str = "double")
```

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `storage` | `str` | - | Resource location du storage (ex. `"my_ns:my_storage"`) |
| `path` | `str` | - | Chemin NBT dans le storage (ex. `"result"`) |
| `scale` | `float` | `1.0` | Multiplicateur appliqué à l'écriture dans le storage : utilisez de petites valeurs (ex. `0.000001`) pour convertir des entiers en flottants |
| `storage_type` | `str` | `"double"` | Type de nombre NBT : `"double"`, `"float"`, `"int"`, `"long"`, `"short"`, `"byte"` |

Avant la 26.3, l'arithmétique s'exécute sur le fake player `#temp_result` de l'objective `{project_id}.data`, et une commande `execute store result storage ...` est ajoutée pour l'écrire. Depuis la 26.3, toute l'equation est une seule commande `/compute` qui stocke dans le storage.

### Exemple avec des arguments de macro

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

Mcfunction généré avant la 26.3 :

```mcfunction
# storage some_namespace:some_path result_path = (-$(amount) * 1000000 / $(max_damage) - #toto) * 0.000005
$scoreboard players set #temp_result <ns>.data -$(amount)
scoreboard players operation #temp_result <ns>.data *= #1000000 <ns>.data
$scoreboard players set #temp_divide <ns>.data $(max_damage)
scoreboard players operation #temp_result <ns>.data /= #temp_divide <ns>.data
scoreboard players operation #temp_result <ns>.data -= #toto <ns>.data
execute store result storage some_namespace:some_path result_path double 0.000005 run scoreboard players get #temp_result <ns>.data
```

Les lignes qui commencent par `$` sont des commandes macro Minecraft, générées dès qu'un argument de macro (`$(name)`) apparaît comme opérande. Depuis la 26.3, la ligne unique `execute store` commence elle aussi par `$`.

---

## Référence des opérations

### Méthodes et opérateurs Python

| Méthode | Opérateur Python | Opération scoreboard | Description |
|---------|------------------|----------------------|-------------|
| `.set(value)` | aucun | `scoreboard players set` | Affectation initiale, à appeler en premier |
| `.add(value)` | `+` | `+=` | Addition |
| `.subtract(value)` | `-` | `-=` | Soustraction |
| `.multiply(value)` | `*` | `*=` | Multiplication |
| `.divide(value)` | `/` ou `//` | `/=` | Division entière (`//` se comporte comme `/`) |
| `.modulo(value)` | `%` | `%=` | Modulo |
| Négation unaire | `-equation` | `*= #-1` | Multiplie la valeur courante par -1 |

Chaque méthode accepte un second argument optionnel `scoreboard` pour cibler un autre objective pour la valeur source.

### Types de `value` acceptés

| Type | Exemple | Comportement |
|------|---------|--------------|
| `int` | `42` | Génère une constante fake-player `#42` sur l'objective `{project_id}.data` |
| `str` : joueur ou sélecteur | `"@s"`, `"#other"` | Opération de scoreboard directe, sur l'objective de l'equation sauf si `scoreboard` est fourni |
| `str` : argument de macro | `"$(amount)"` | Ajoute en tête `$scoreboard players set #temp_... ...` pour gérer la macro avant l'opération |
| Equation | une autre `ScoreboardEquation` ou `StorageEquation` | Insère d'abord les commandes de l'equation source, puis utilise son joueur et son scoreboard finaux comme source |

L'arithmétique de scoreboard ne gère que les entiers. Utilisez le paramètre `scale` de `StorageEquation` pour transformer le résultat entier en valeur NBT à virgule flottante lors de l'écriture dans le storage.

## Étapes suivantes

- [Écrire dans des fichiers](../2_writing_to_files/fr.md) : intégrer les commandes qu'une equation produit.
- [auto.scoreboard_constants](../plugins/auto.scoreboard_constants.fr.md) : comment les constantes dont les equations ont besoin sont initialisées.

