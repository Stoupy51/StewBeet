
# Tester son pack avec Ward

[Ward](https://github.com/mcbookshelf/ward) lance des tests `.mcfunction` dans un serveur sans interface et signale chaque `assert` qui échoue avec son fichier et sa ligne.
Un projet StewBeet range ses tests dans un dossier `tests/` à côté de `src/`, comme un second datapack chargé à côté du zip construit : les tests portent sur ce que les joueurs téléchargent, bibliothèques comprises.

### Organisation

```
tests/
	pack.mcmeta
	data/
		minecraft/tags/function/load.json           -> {"values": ["<ns>_test:load"]}
		<ns>_test/
			function/load.mcfunction                 -> scoreboard objectives add <ns>_test.data dummy
			function/spawn_loader.mcfunction         -> dummy loader spawn
			structure/room.nbt                       -> une structure vide de 5x5x5
			test_environment/loaded.json
			test/<comportement>.mcfunction           -> un fichier par test
```

Donnez-leur un namespace à part, `<ns>_test`, pour que la commande plus bas ne lance que vos tests : des bibliothèques comme ItemIO embarquent leurs propres tests Ward dans le zip, et ils tournent aussi quand le sélecteur les inclut.

### Un pack qui attend un joueur

Un pack StewBeet ne se charge qu'une fois un joueur connecté : `valid_dependencies` lit la version du jeu sur `@p` et se replanifie tant qu'il n'y a personne.
Un monde Ward n'a aucun joueur, donc `#<ns>.loaded` ne passe jamais à 1, sauf si un environnement de test fait apparaître un [dummy](https://github.com/mcbookshelf/ward/blob/main/docs/dummies.md) qui reste pendant toute l'exécution :

```json
{
	"type": "minecraft:function",
	"setup": "<ns>_test:spawn_loader"
}
```

Chaque test nomme alors cet environnement et attend le pack avant toute chose :

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

`dummy @s use block` pose un bloc custom comme le ferait un joueur, donc Smithed Custom Block et les fonctions `place` s'exécutent pour de vrai.
Donnez au dummy une pile de deux : il est en survie, et un bloc posé avec le dernier objet d'une pile trouve `SelectedItem` déjà vide, si bien que ce que ses fonctions `place` copient de l'objet (énergie stockée, slots sauvegardés) est perdu.

`room.nbt` existe parce que la version de Ward pour 26.3 n'a pas les templates `ward:empty/*`, et son template par défaut est un seul bloc d'air, trop bas pour un dummy. Écrivez-le une fois avec le nbtlib qu'installe beet :

```python
from nbtlib import File, Compound, List, Int
room = Compound({"size": List[Int]([5, 5, 5]), "entities": List([]), "blocks": List([]), "palette": List([]), "DataVersion": Int(5023)})
File({"": room}, gzipped=True).save("tests/data/<ns>_test/structure/room.nbt")
```

### Construire et lancer

Construisez sans la copie vers votre monde : `build_copy_destinations` écraserait sinon le datapack du monde où vous jouez.

```sh
beet -s "meta.stewbeet.build_copy_destinations.datapack=null" -s "meta.stewbeet.build_copy_destinations.resource_pack=null" build
uvx "mcward[cli]" test -p build/<Name>_datapack_with_libs.zip -p tests -v 26.3 "<ns>_test:*"
```

Ajoutez `--verbose` pour lister chaque test. La première exécution démarre un serveur qui reste lancé, les suivantes prennent quelques secondes ; `uvx "mcward[cli]" stop --all` l'arrête.
N'utilisez pas `beet test` : il teste le pack source, sans les bibliothèques que Smithed Weld fusionne dans le zip.

Une fonction qui ne se parse pas n'est pas chargée, et Ward la liste avant les résultats, sous la forme `[minecraft:function] <ns>:<chemin>` : une faute de frappe dans une commande générée apparaît même si aucun test n'appelle cette fonction.

### Pièges

- Les tests d'un même lot tournent en même temps, dans des zones à quelques blocs les unes des autres. Sélectionnez vos blocs avec `distance=`, comme dans `execute positioned ~2.5 ~.5 ~2.5 run assert entity @e[tag=<ns>.pulverizer,distance=..0.5]`, jamais avec un tag seul.
- `~ ~ ~` est le coin bas nord-ouest du template, et un test s'exécute en tant que son dummy mais à ce coin.
- `tp @s ~.5 ~ ~.5 facing <pos>` vise depuis les pieds, pas les yeux. Donnez une rotation explicite (`tp @s ~.5 ~ ~.5 -45 22`) pour que le dummy regarde un bloc lors d'un raycast.
- `loot replace block` refuse le slot de sortie d'un four. Mettez l'objet dans l'inventaire du dummy avec `loot replace entity @s hotbar.8`, puis `item replace block <pos> container.2 from entity @s hotbar.8`.
- Un item modifier inline prend `type` en 26.x, pas `function` : `item modify block <pos> container.0 {type:"minecraft:set_count",count:64}`.
- Furnace NBT Recipes commence à traiter les fours deux secondes après son chargement. Un test de four attend d'abord sa shulker box : `await block -30000000 14 1610 minecraft:yellow_shulker_box`.
- Un test qui relance la fonction de chargement, ou qui modifie quelque chose de partagé, reçoit son propre environnement, un `all_of` autour du même setup, pour tourner seul dans son lot.
- La version de Ward pour 26.3 n'a pas de commande `log`. Pour voir une valeur, rangez-la dans un storage et terminez le test par `fail {"storage":"dbg","nbt":"{}"}`.
- Les échecs `@optional` comptent comme réussis dans le résumé : laissez échouer un test qui reproduit un bug connu.

### Vérifier qu'un test attrape quelque chose

Un test ne prouve quelque chose qu'une fois qu'il a échoué. Cassez la ligne qu'il protège dans le zip construit (une copie, le projet reste intact), lancez la suite sur ce zip, et vérifiez que ce test, et aucun autre sans rapport, passe au rouge.

