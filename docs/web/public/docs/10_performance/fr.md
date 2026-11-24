
# Garder les functions rapides

Les conventions que suivent les packs StewBeet dans le code qui tourne à chaque tick. Chacune nomme le helper qui l'applique quand il y en a un.
Mesurez avant et après avec `/perf start`, puis `/perf stop` : le zip qu'il écrit contient `server/profiling.txt`, le temps pris par chaque commande.

### Des entités persistantes plutôt que temporaires

`execute summon ... run function ...` suivi de `kill @s` crée et détruit une entité à chaque appel, ce qui coûte plus que la plupart de ce que fait ensuite la function.
Une commande qui n'a besoin d'une entité que comme support (un `item_display` dans lequel faire `loot replace entity @s contents`, puis lire `item`) en utilise une persistante :

```python
from stewbeet import persistent_item_display, write_function

display: str = persistent_item_display("pulverizer_recipe")
write_function(f"{ns}:get_recipe", f"""
execute as {display} run function #{ns}:calls/recipes
data modify storage {ns}:main output set from entity {display} item
""")
```

`persistent_item_display(name)` ajoute à la function de chargement un `forceload add` du chunk à `FORCELOAD_BLOCK` (x -30000000, z 1600, partagé avec Bookshelf, Furnace NBT Recipes, et d'autres) et un `execute unless entity <uuid> run summon` de l'entité, une fois par nom.
L'UUID est dérivé de l'id du projet et du nom, donc il ne change jamais d'un build à l'autre et deux projets n'en partagent jamais un. La function unload tue l'entité, et laisse le forceload aux autres packs qui utilisent ce chunk.

La position d'exécution reste celle de l'appelant : `execute as <uuid>` change `@s`, pas `~ ~ ~`.

### N'écrire le NBT d'une entité ou d'un block que s'il change

`data modify entity` et `store result block` sérialisent toute l'entité ou le block entity puis la rechargent. Gardez-les derrière un test peu coûteux de la valeur qu'ils écriraient :

```mcfunction
execute unless items entity @s contents *[minecraft:item_model="ns:machine_on"] run data modify entity @s item.components."minecraft:item_model" set value "ns:machine_on"
```

Une valeur que le jeu fait bouger seul à chaque tick, comme le `cooking_time_spent` d'un four, n'est jamais égale à celle écrite au tick précédent. Écrivez-la quand ce que voit le joueur change, par exemple quand une flèche de progression montrerait un autre pixel.

### Tester les items avec `if items`

`data modify storage ... set from entity @s SelectedItem` sérialise tout le joueur, inventaire compris, pour lire un item. `execute if items` lit directement le slot :

```mcfunction
execute if items entity @s weapon.offhand *[custom_data~{"ns":{"multimeter":true}}] run function ns:multimeter
execute if items block ~ ~ ~ container.26 *[!custom_data~{"common_signals":{"temp":true}}] run function ns:drop_intruder
```

Copiez les `Items` d'un conteneur seulement sur le chemin qui a besoin de la pile complète, et au plus une fois par tick.

### Lire un block entity une fois par tick

`execute if data block ~ ~ ~ {lit_time_remaining:0}` sérialise tout le block entity, items compris, pour une seule valeur. Quand une function a besoin de plusieurs valeurs, copiez le block une fois avec `data modify storage ... set from block ~ ~ ~`, transformez en scores les valeurs testées plus d'une fois, et testez les slots avec `if items block`.
Testez ce que le block state dit déjà avant cette copie : `execute if block ~ ~ ~ #ns:furnaces[lit=true]` dit si un four brûle sans le sérialiser, donc un four inactif retourne en premier.

### Garder l'état par entité dans des scores et des tags

Une valeur qu'une entité lit et écrit à chaque tick (une progression, un flag de déblocage) coûte une sérialisation complète de l'entité dans chaque sens quand elle vit dans le NBT. Stockez-la comme score ou tag sur l'entité, et ne la déplacez vers et depuis le NBT qu'à la pose ou à la destruction du block, où l'item la porte.
Une valeur qui ne change jamais tant que l'entité suit le block, comme le type de four, est lue une fois, au premier tick où son score manque : `execute unless score @s ns.type matches 0.. run function ns:read_type`.

### Vider les valeurs optionnelles avec `data remove`

`data modify storage ... set value {}` avant un `set from` optionnel laisse `{}` quand la source manque, donc `execute unless data` ne voit jamais l'absence. Utilisez `data remove` pour la vider.

### Réutiliser un résultat tant que son entrée ne change pas

`data modify A set from B` ne réussit que s'il change `A`, donc `execute store success` en fait un test d'égalité qui enregistre aussi la nouvelle valeur :

```mcfunction
execute store success score #changed ns.data run data modify storage ns:temp previous_input set from storage ns:temp input
execute if score #changed ns.data matches 1 run function ns:expensive_lookup
```

Supprimez `previous_input` là où la réutilisation doit s'arrêter : au début du tick de chaque block, après que quelque chose a consommé le résultat, ou dans la function de chargement quand un `/reload` peut changer ce que renvoie la recherche.

Le même test compare exactement deux compounds : copiez-en un dans un chemin temporaire, puis `execute store success ... run data modify <temporary> set from <other>` donne 0 seulement quand ils sont égaux. Il remplace une macro qui exécute `if data` dans les deux sens, qu'un appel de macro réanalyse.

### Ordonner une chaîne de returns par fréquence

Dans une function faite de lignes `execute if ... run return <value>`, mettez le cas le plus fréquent en premier, et vérifiez que chaque ligne teste la bonne cible (`block ~ ~ ~` contre `entity @s`) : une ligne qui ne peut jamais correspondre fait exécuter toute la chaîne à chaque appel.

## Étapes suivantes

- [Functions et fichiers](../2_writing_to_files/fr.md) : `write_function` et les autres helpers qu'utilisent les exemples.
- [Tester avec Ward](../11_testing/fr.md) : vérifier un changement comme ceux-ci sur un serveur headless.

