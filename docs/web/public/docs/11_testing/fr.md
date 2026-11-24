
# Tester votre pack avec Ward

[Ward](https://github.com/mcbookshelf/ward) exécute des tests `.mcfunction` sur un serveur headless et signale chaque `assert` qui échoue avec son fichier et sa ligne.
Un projet StewBeet garde ses tests dans un dossier `tests/` à côté de `src/`, comme un second datapack chargé à côté du zip compilé, donc les tests tournent sur exactement ce que les joueurs téléchargent, bibliothèques comprises.

### Organisation

```
tests/
	pack.mcmeta
	data/
		minecraft/tags/function/load.json           -> {"values": ["<ns>_test:load"]}
		<ns>_test/
			function/load.mcfunction                 -> scoreboard objectives add <ns>_test.data dummy
			function/spawn_loader.mcfunction         -> dummy loader spawn
			structure/room.nbt                       -> an empty 5x5x5 structure
			test_environment/loaded.json
			test/<behaviour>.mcfunction              -> one file per test
```

Utilisez un namespace à part, `<ns>_test`, pour que la commande ci-dessous n'exécute que vos tests : des bibliothèques comme ItemIO embarquent leurs propres tests Ward dans le zip, et ceux-ci tournent aussi quand le sélecteur les correspond.

### Un pack qui attend un joueur

Un pack StewBeet qui a des dépendances ne se charge qu'une fois un joueur en ligne : `valid_dependencies` lit la version du jeu depuis `@p` et se reprogramme tant que personne n'est là.
Un monde Ward n'a pas de joueur, donc `#<ns>.loaded` n'atteint jamais 1 sauf si un environnement de test fait apparaître un [dummy](https://github.com/mcbookshelf/ward/blob/main/docs/dummies.md) qui reste pendant toute l'exécution :

```json
{
	"type": "minecraft:function",
	"setup": "<ns>_test:spawn_loader"
}
```

Chaque test nomme alors cet environnement et attend le pack avant de faire quoi que ce soit :

```mcfunction
# @template <ns>_test:room
# @environment <ns>_test:loaded
# @dummy ~ ~ ~
# @timeout 200
await score #<ns>.loaded load.status matches 1

loot replace entity @s weapon.mainhand loot <ns>:i/pulverizer
item modify entity @s weapon.mainhand {type:"minecraft:set_count",count:2}
dummy @s use block ~2 ~-1 ~2
execute positioned ~2.5 ~.5 ~2.5 run await entity @e[tag=<ns>.pulverizer,distance=..0.5]
```

`dummy @s use block` pose un custom block comme le fait un joueur, donc Smithed Custom Block et les functions `place` tournent pour de vrai.
Donnez au dummy une pile de deux. Son action s'exécute dans une commande, donc le jeu met en file la récompense d'advancement de Smithed Custom Block jusqu'à la fin de cette commande, après que l'item du dummy en survie a été retiré. Posé depuis le dernier item d'une pile, le block trouve alors `SelectedItem` vide et tout ce que ses functions `place` copient depuis l'item (énergie stockée, slots sauvegardés) est perdu. La récompense d'un vrai joueur s'exécute avant le retrait de l'item, donc cela n'arrive que dans les tests.

`room.nbt` existe parce que le build 26.3 de Ward n'a pas de templates `ward:empty/*`, et que son template par défaut est un block d'air, trop bas pour un dummy. Écrivez-le une fois avec le nbtlib que beet installe :

```python
from nbtlib import File, Compound, List, Int
room = Compound({"size": List[Int]([5, 5, 5]), "entities": List([]), "blocks": List([]), "palette": List([]), "DataVersion": Int(5023)})
File({"": room}, gzipped=True).save("tests/data/<ns>_test/structure/room.nbt")
```

### Compiler et exécuter

Compilez sans la copie vers votre monde : `build_copy_destinations` écraserait sinon le datapack du monde dans lequel vous jouez.

```sh
uv run stewbeet -s "meta.stewbeet.build_copy_destinations.datapack=null" -s "meta.stewbeet.build_copy_destinations.resource_pack=null" build
uvx "mcward[cli]" test -p build/<Name>_datapack_with_libs.zip -p tests -v 26.3 "<ns>_test:*"
```

Ajoutez `--verbose` pour lister chaque test. Le premier lancement démarre un serveur qui reste actif, donc les suivants prennent quelques secondes ; `uvx "mcward[cli]" stop --all` l'arrête.
N'utilisez pas `beet test` : il teste le pack source, sans les bibliothèques que Smithed Weld fusionne dans le zip.

Une function qui ne s'analyse pas n'est pas chargée, et Ward la liste avant les résultats, sous la forme `[minecraft:function] <ns>:<path>`, donc une faute de frappe dans une commande générée apparaît même si aucun test n'appelle cette function.

### Pièges

- Les tests d'un même lot tournent en même temps dans des zones à quelques blocks d'écart. Sélectionnez vos blocks avec `distance=`, comme dans `execute positioned ~2.5 ~.5 ~2.5 run assert entity @e[tag=<ns>.pulverizer,distance=..0.5]`, jamais avec un tag seul.
- `~ ~ ~` est le coin bas nord-ouest du template, et un test s'exécute en tant que son dummy mais à ce coin.
- `tp @s ~.5 ~ ~.5 facing <pos>` vise depuis les pieds, pas les yeux. Donnez une rotation explicite (`tp @s ~.5 ~ ~.5 -45 22`) pour que le dummy regarde un block pour un raycast.
- `loot replace block` refuse l'emplacement de sortie d'un four. Mettez l'item dans l'inventaire du dummy avec `loot replace entity @s hotbar.8`, puis `item replace block <pos> container.2 from entity @s hotbar.8`.
- Un item modifier en ligne prend `type` en 26.x, pas `function` : `item modify block <pos> container.0 {type:"minecraft:set_count",count:64}`.
- Furnace NBT Recipes commence à faire tourner les fours deux secondes après son chargement. Un test de four attend d'abord sa shulker box : `await block -30000000 14 1610 minecraft:yellow_shulker_box`.
- Un test qui relance la function de chargement, ou change quoi que ce soit de partagé, reçoit un environnement à lui, un `all_of` autour du même setup, pour qu'il tourne seul dans un lot.
- Le build 26.3 de Ward n'a pas de commande `log`. Pour voir une valeur, stockez-la dans un storage et terminez le test par `fail {"storage":"dbg","nbt":"{}"}`.
- Les échecs `@optional` comptent comme réussis dans le résumé : gardez en échec un test qui reproduit un bug connu.

### Vérifier qu'un test attrape quelque chose

Un test ne prouve quelque chose qu'une fois qu'il a échoué. Cassez la ligne qu'il garde dans le zip compilé (une copie, le projet reste intact), lancez la suite sur ce zip, et vérifiez que ce test, et aucun autre sans rapport, passe au rouge.

## Étapes suivantes

- [Bibliothèques de datapack](../5_dependencies/fr.md#comportement-a-lexecution) : la séquence de chargement qu'un test attend.
- [Publier des releases](../6_continuous_delivery/fr.md) : livrer le zip sur lequel vos tests ont tourné.

