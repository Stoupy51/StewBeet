
# Garder les fonctions rapides

Les conventions que suivent les packs StewBeet dans le code exécuté à chaque tick. Chacune cite le helper qui l'applique quand il y en a un.
Mesurez avant et après avec `/perf start` puis `/perf stop` : le zip produit contient `server/profiling.txt`, le temps pris par chaque commande.

### Des entités persistantes plutôt que temporaires

`execute summon ... run function ...` suivi de `kill @s` crée et détruit une entité à chaque appel, ce qui coûte plus que la plupart de ce que fait ensuite la fonction.
Une commande qui n'a besoin d'une entité que comme support (un `item_display` dans lequel faire `loot replace entity @s contents`, puis lire `item`) utilise une entité persistante :

```python
from stewbeet import persistent_item_display, write_function

display: str = persistent_item_display("pulverizer_recipe")
write_function(f"{ns}:get_recipe", f"""
execute as {display} run function #{ns}:calls/recipes
data modify storage {ns}:main output set from entity {display} item
""")
```

`persistent_item_display(name)` ajoute à la fonction de load un `forceload add` du chunk de `FORCELOAD_BLOCK` (x -30000000, z 1600, partagé avec Bookshelf, Furnace NBT Recipes, et autres) et un `execute unless entity <uuid> run summon` de l'entité, une fois par nom.
L'UUID est dérivé de l'id du projet et du nom : il ne change pas d'un build à l'autre et deux projets n'en partagent jamais un. La fonction d'unload tue l'entité et laisse le forceload aux autres packs qui utilisent ce chunk.

La position d'exécution reste celle de l'appelant : `execute as <uuid>` change `@s`, pas `~ ~ ~`.

### N'écrire le NBT d'une entité que s'il change

`data modify entity` sérialise toute l'entité puis la recharge. Protégez-le par un test peu coûteux de la valeur qu'il écrirait :

```mcfunction
execute unless items entity @s contents *[minecraft:item_model="ns:machine_on"] run data modify entity @s item.components."minecraft:item_model" set value "ns:machine_on"
```

### Une valeur absente doit être absente

`data modify storage ... set value {}` avant un `set from` optionnel laisse `{}` quand la source manque, et `execute unless data` ne voit alors jamais l'absence. Videz plutôt avec `data remove`.

### Réutiliser un résultat tant que son entrée ne change pas

`data modify A set from B` ne réussit que s'il modifie `A`, donc `execute store success` en fait un test d'égalité qui enregistre aussi la nouvelle valeur :

```mcfunction
execute store success score #changed ns.data run data modify storage ns:temp previous_input set from storage ns:temp input
execute if score #changed ns.data matches 1 run function ns:expensive_lookup
```

Supprimez `previous_input` là où la réutilisation doit s'arrêter, par exemple au début du tick de chaque bloc.

### Ordonner une chaîne de returns par fréquence

Dans une fonction faite de lignes `execute if ... run return <valeur>`, mettez le cas le plus fréquent en premier, et vérifiez que chaque ligne teste la bonne cible (`block ~ ~ ~` ou `entity @s`) : une ligne qui ne peut jamais réussir fait parcourir toute la chaîne à chaque appel.

