
# Référence des definitions

Une definition est un objet Python enregistré dans `Mem.definitions` à sa création. Les plugins de build lisent ce dictionnaire pour écrire les models, loot tables, recipes, traductions et le manual en jeu. Pour un pas à pas, voir [Items et blocks](../items_and_blocks/fr.md).

## Mem.definitions

`Mem.definitions` est un `dict[str, Item]` indexé par id, sans namespace. Créer un `Item`, ou une sous-classe de `Item`, enregistre l'objet sous son `id`.

```python
item = Item(id="life_crystal")
assert Item.from_id("life_crystal") is item
assert "life_crystal" in Mem.definitions
```

| Appel | Effet |
|---|---|
| `Item.from_id(id)` | Renvoie l'objet enregistré, quelle que soit la classe avec laquelle il a été créé. Lève `KeyError` s'il n'y en a pas. |
| `Item.from_id(id, strict=False)` | Pareil, et crée puis enregistre un `Item(id=id)` s'il n'y en a pas. |
| `Mem.definitions[id]` | Le même objet, sans vérification de classe. |

Un item créé avec un `id` déjà présent dans `Mem.definitions` n'est pas enregistré : le build avertit, l'objet enregistré garde tous ses champs et `Item.from_id(id)` continue de renvoyer le premier. Un `id` vide n'est jamais enregistré. Pour modifier une definition existante, récupérez-la avec `from_id` et changez ses champs.

`Mem.external_definitions` contient les objets `ExternalItem`, indexés par `namespace:id`. Un `Ingr` qui nomme un item d'un autre datapack les lit.

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `id` | `str` | requis | `namespace:id` de l'item, comme dans `simplenergy:machine_block`. |
| `custom_data_predicate` | `JsonDict \| str` | requis | Ce que le `custom_data` de l'item doit contenir pour qu'une recipe le reconnaisse. |
| `components` | `JsonDict` | `{}` | Components de l'item, écrits sans `minecraft:`. |
| `loot_table` | `str \| Resource[LootTable] \| None` | `None` | Loot table de l'autre datapack qui donne l'item. Une recipe qui donne l'item en résultat en a besoin. |
| `base_item` | `str` | `CUSTOM_ITEM_VANILLA` | Item vanilla sur lequel l'item externe est basé. |

## Item

`Item` est une dataclass à arguments nommés uniquement.

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `id` | `str` | requis | Id unique. Un `:` dedans affiche un avertissement et garde la partie après le dernier `:`. |
| `base_item` | `str` | `CUSTOM_ITEM_VANILLA` (`minecraft:recovery_compass`) | Item vanilla sur lequel l'item custom est construit. `minecraft:` est ajouté s'il manque. |
| `manual_category` | `str \| None` | `None` | Catégorie de l'item dans le manual en jeu. Sans catégorie, l'item n'a pas de page de manual. Voir [Catégories du manual](#categories-du-manual). |
| `recipes` | `list[RecipeBase]` | `[]` | Recipes qui donnent cet item. Chaque recipe sans `group` reçoit l'id de l'item. Un ingrédient tag comme `#minecraft:eggs` est remplacé par une recipe par item du tag. |
| `override_model` | `JsonDict \| None` | `None` | Fusionné par-dessus le model généré depuis les textures. `{}` n'écrit aucun fichier de model. |
| `hand_model` | `JsonDict \| None` | `None` | Model affiché dans tous les display contexts sauf ceux de `override_model_contexts`. |
| `override_model_contexts` | `list[str] \| None` | `None` | Display contexts qui gardent le model normal quand `hand_model` est défini. `None` vaut `Item.DEFAULT_OVERRIDE_MODEL_CONTEXTS` : `["none", "fixed"]`, les item display entities et les item frames. |
| `wiki_buttons` | `list[WikiButton] \| TextComponent \| None` | `None` | Boutons de la page de manual de l'item. Le définir sans `manual_category` affiche un avertissement. Voir [Wiki buttons et item manual](#wiki-buttons-et-item-manual). |
| `components` | `JsonDict` | `{}` | Components de l'item. Un préfixe `minecraft:` sur une clé est retiré. Une clé qui commence par `!` retire le component et sa valeur est remise à `{}`. |
| `skip_gives` | `bool` | `False` | Laisse l'item hors des loot tables et de la function give-all. |
| `remainder` | `str \| None` | `None` | Id de la definition laissée une fois l'item mangé ou bu. Elle devient le component `use_remainder`, qui porte l'`item_name`, l'`item_model` et le `custom_data` du récipient, et le manual relie les deux pages. |
| `ranged_weapon` | `RangedWeapon \| None` | `None` | Réglages d'un arc ou d'une arbalète. Voir [RangedWeapon](#rangedweapon). |

La classe porte aussi `origin`, un champ défini par le plugin `source_maps` qui n'est pas un argument du constructeur.

```python
Item(
	id="stardust_ingot",
	manual_category="material",
	components={"item_name": {"text": "Stardust Ingot", "color": "aqua"}, "max_stack_size": 99},
)
```

## Block class

`Block` étend `Item` avec les champs ci-dessous. Son `base_item` vaut par défaut `CUSTOM_BLOCK_VANILLA` (`minecraft:furnace`), ce qui donne à l'item un component `container` portant les données du custom block Smithed et le masque du tooltip.

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `vanilla_block` | `VanillaBlock \| None` | `None` | Block vanilla placé dans le monde comme hôte du block. |
| `no_silk_touch_drop` | `NoSilkTouchDrop \| LootTable \| str \| None` | `None` | Ce qui tombe quand le block est cassé sans silk touch. Un `str` est un id d'item, dont un exemplaire tombe. Une `LootTable` est tirée telle quelle. |
| `mining` | `Mining \| None` | `None` | Outil nécessaire pour obtenir l'item. Voir [Mining](#mining). |
| `growing_seed` | `GrowingSeed \| None` | `None` | Fait du block une graine qui pousse avec le temps. Voir [GrowingSeed](#growingseed). |
| `on_place` | `str \| None` | `None` | Commandes ajoutées aux functions de placement. Affiche un avertissement au build, `functions.place_secondary.obj.append(...)` fait la même chose sans lui. |

`BlockAlternative` est un `Block` dont le `base_item` est `minecraft:item_frame` : le block est placé comme une item frame, et son `vanilla_block` est `VanillaBlock(contents=True)`. `BlockHead` est un `Block` dont le `base_item` est `minecraft:player_head` : le block est placé comme une tête de joueur, et l'id de son `vanilla_block` porte le profil de la tête.

```python
BlockHead(
	id="stardust_cable",
	manual_category=ENERGY,
	vanilla_block=VanillaBlock(id="minecraft:player_head{profile:" + str(stardust_cable_profile) + "}"),
	components={"custom_data": {"energy": {"transfer": 480}}, "profile": stardust_cable_profile},
)
```

Un `Block` normal n'a pas d'advancement de placement propre, puisque la bibliothèque Smithed custom block le détecte. `BlockAlternative` et `BlockHead` en ont un, `Block.advancement`.

### Configuration de VanillaBlock

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `id` | `str \| None` | `""` | Id du block vanilla avec états optionnels, comme `minecraft:furnace[lit=false]`. `minecraft:` est ajouté s'il manque. `None` avec `contents=True`. |
| `contents` | `bool` | `False` | Le block n'a pas de block vanilla et est tenu par une item frame. Met `id` à `None`. Incompatible avec `block_facing`. |
| `block_facing` | `False \| "player"` | `False` | `"player"` oriente le block hôte placé comme le fait vanilla : vers le joueur pour un furnace, dans le sens du regard du joueur pour les escaliers et les fence gates. Met `visual_facing` à `"player"` quand il est resté à `"none"`. |
| `visual_facing` | `"none" \| "player" \| "item_frame"` | `"none"` | Orientation du model affiché. `"player"` donne quatre directions horizontales, `"item_frame"` les six du `Facing` de la frame. |
| `apply_facing` | `False \| True \| "entity" \| None` | `None` | Raccourci pour les deux champs ci-dessus. `True` met les deux à `"player"`, `"entity"` met `visual_facing` à `"player"`. |
| `half` | `"click" \| None` | `None` | Un hôte dalle, escalier ou trapdoor prend sa moitié selon l'endroit où le joueur a cliqué. Lève `ValueError` pour un autre hôte. |
| `interaction` | `Interaction \| None` | `None` | Interaction entity qui casse le block quand on la frappe. Pour un hôte sans collision. |
| `uvlock` | `bool` | `False` | Affiche une copie du model tournée pour chaque orientation au lieu de tourner le display, pour que ses textures suivent la grille du monde. Demande `visual_facing="player"`. |
| `margin` | `float` | `1.002` | Échelle de chaque élément du model affiché autour de son propre centre, pour qu'aucune face ne repose sur une face de l'hôte. `1.0` garde la taille. Ignoré avec `contents=True`. |
| `machine_speed` | `float \| None` | `None` | Un furnace, smoker, blast furnace ou brewing stand cuit ou infuse autant de fois plus vite. Lève `ValueError` pour un autre hôte. |

`half="click"` lit l'endroit cliqué par le joueur dans `{ns}:custom_blocks/_aim/main`. Le `type` d'une dalle et le `half` des escaliers et trapdoors prennent le résultat. `#floor {ns}.data` est aussi laissé à 1 quand le joueur a cliqué le dessus du block du dessous.

Un hôte escalier prend un `shape` d'angle selon ses voisins, et son display le suit chaque seconde avec une copie du model découpée dans ses éléments, dessinée face au sud. Un hôte furnace, smoker ou blast furnace avec un model `_on` l'affiche pendant qu'il brûle. Les deux basculent via la chaîne `custom_model_data` du display, et seulement pour un model que StewBeet dessine.

### Interaction

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `width` | `float` | `1.01` | Largeur de l'interaction entity. |
| `height` | `float` | `1.01` | Hauteur, depuis le bas du block. Un peu plus qu'un block pour qu'elle soit visée avant l'hôte. |
| `seat` | `float \| None` | `None` | Hauteur au-dessus du bas du block à laquelle l'utiliser assoit le joueur. `None` veut dire pas de siège. |
| `hits` | `int` | `1` | Coups nécessaires pour casser le block. Chacun ne compte que s'il arrive moins de `hit_timeout` ticks après le précédent. |
| `hit_timeout` | `int` | `20` | Ticks entre deux coups comptés. |
| `sound` | `str` | `minecraft:block.stone` | Groupe de sons, joué en `<sound>.hit` à chaque coup et en `<sound>.break` à la casse. |

Les hôtes sans collision ou impossibles à miner sont `minecraft:barrier`, `minecraft:structure_void` et `minecraft:light[level=N]`. Frapper l'entity casse le block et fait tomber son item, sauf si celui qui casse est en creative. Les commandes lancées quand un joueur utilise l'interaction vont dans `{ns}:custom_blocks/_interaction/use`, exécutées par l'interaction avec le joueur taggé `{ns}.user`.

```python
Block(
	id="chair",
	vanilla_block=VanillaBlock(id="minecraft:barrier", visual_facing="player", interaction=Interaction(seat=0.5, hits=3, sound="minecraft:block.wood")),
)
```

### Mining

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `tool` | `"pickaxe" \| "axe" \| "shovel" \| "hoe"` | `"pickaxe"` | Type d'outil qui obtient l'item. |
| `level` | `"wood" \| "stone" \| "iron" \| "diamond" \| "netherite"` | `"wood"` | Niveau d'outil le plus faible qui obtient l'item. Chaque outil d'un niveau mine aussi tous les niveaux inférieurs. |

Un outil plus faible casse le block sans faire tomber son item. La classe a trois propriétés en lecture seule : `tools`, les outils vanilla du niveau ou d'un niveau supérieur, `item_tag`, le tag `{ns}:mining/<tool>_<level>` qui les liste, et `hosts`, les blocks vanilla qui font exiger le niveau à vanilla lui-même, vide pour tout outil autre que la pickaxe et pour `netherite`.

| Hôte du block | Comportement |
|---|---|
| Aucun donné | Le premier de `Mining.hosts`, par exemple `minecraft:diamond_block` pour `iron`. Les règles de drop vanilla décident alors, vitesse de minage et animation comprises. Sans `hosts`, le build lève `ValueError`. |
| Un de `Mining.hosts` | Utilisé tel quel. Tout autre vrai hôte lève `ValueError`. |
| Un hôte `Interaction` | La main principale de celui qui casse est comparée à `Mining.item_tag`. Marche pour tous les types d'outil. |
| `VANILLA_BLOCK_FOR_ORES` (`minecraft:polished_deepslate`) | Avec un niveau au-dessus de `wood`, le joueur le plus proche dans un rayon de 8 blocks, ni en creative ni en spectator, est comparé à `Mining.item_tag`. |

```python
Block(id="ruby_ore", vanilla_block=VANILLA_BLOCK_FOR_ORES, mining=Mining(level="iron"))
```

### NoSilkTouchDrop

Définissez exactement un parmi `id` et `loot_table`, sinon le constructeur lève `AssertionError`.

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `id` | `str` | `""` | Id de l'item à faire tomber, par exemple `raw_simplunium`. |
| `loot_table` | `LootTable \| str \| None` | `None` | Une loot table, ou sa resource location, qui tombe à la place de `id` et `count`, tirée avec l'outil de celui qui casse. |
| `count` | `int \| dict` | `1` | Quantité qui tombe, un entier ou `{"min": 1, "max": 3}`. |
| `experience` | `float \| dict` | `0.0` | Expérience qui tombe, sous forme de nombre ou de `{"min": 3, "max": 7}`. La partie décimale d'un nombre est la chance d'un point de plus : `2.5` donne 2 points, et un troisième une fois sur deux. Le manual l'affiche au survol de la recipe de minage. |

Un dict pour `count` ou `experience` demande `min` et `max`.

```python
Block(
	id="simplunium_ore",
	vanilla_block=VANILLA_BLOCK_FOR_ORES,
	no_silk_touch_drop=NoSilkTouchDrop(id="raw_simplunium", count={"min": 2, "max": 4}, experience={"min": 1, "max": 3}),
)
```

### RangedWeapon

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `charge_time` | `float \| None` | `None` | Secondes que met une arbalète à se charger. Vanilla vaut 1.25. |
| `damage_multiplier` | `float` | `1.0` | Multiplie les dégâts des flèches tirées. |
| `ammunition` | `str \| None` | `None` | Id de la seule definition qu'une arbalète charge. Tout le reste est rendu. |
| `name` | `str` | `"Heavy Draw"` | Nom, dans le tooltip, de l'enchantement caché qui l'applique. |

L'item reçoit l'enchantement `Item.ranged_weapon_enchantment` au niveau 1, tagué comme malédiction pour qu'une grindstone le garde, et sans lueur d'enchantement. Une arbalète avec des textures `_pulling_<n>`, `_arrow` et `_firework` reçoit l'item model d'arbalète vanilla : dessiné selon sa charge, et montrant ce qu'elle contient une fois chargée.

```python
Item(id="crossbow", base_item="minecraft:crossbow", ranged_weapon=RangedWeapon(charge_time=2.5, damage_multiplier=1.5, ammunition="bolt"))
```

### GrowingSeed

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `texture_basename` | `str` | requis | Base des textures de stades, nommées `<texture_basename>_stage_<n>.png`. |
| `seconds` | `int` | requis | Temps pour atteindre le dernier stade. |
| `planted_on` | `str` | requis | Block sur lequel la graine doit reposer. `minecraft:` est retiré. |
| `loots` | `list[GrowingSeedLoot] \| str` | requis | Loot de la récolte, ou resource location d'une loot table. |

`GrowingSeedLoot` :

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `id` | `str` | requis | Id de l'item à faire tomber. |
| `rolls` | `JsonDict \| int` | `1` | Un nombre, ou un number provider comme `{"type": "minecraft:uniform", "min": 3, "max": 9}`. |
| `fortune` | `JsonDict \| None` | `None` | Bonus de fortune, comme `{"extra": 0, "probability": 0.5}`. |

```python
BlockAlternative(
	id="diamond_seed",
	vanilla_block=VanillaBlock(contents=True),
	growing_seed=GrowingSeed(texture_basename="diamond", seconds=1200, planted_on="stone", loots=[
		GrowingSeedLoot(id="minecraft:diamond", rolls={"type": "minecraft:uniform", "min": 0, "max": 2}, fortune={"extra": 0, "probability": 0.1}),
	]),
)
```

## Painting

`Painting` étend `Item` avec `base_item="minecraft:painting"` et un champ de plus. Le component `painting/variant` est mis à `<namespace>:<id>` quand il est absent.

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `painting_data` | `PaintingData` | requis | Taille, texture et texte du painting. |

`PaintingData` :

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `width` | `int` | requis | Largeur en blocks. |
| `height` | `int` | requis | Hauteur en blocks. |
| `texture` | `str \| None` | l'id de l'item | Nom du fichier de texture sans `.png`, cherché dans le dossier des textures. |
| `author` | `TextComponent \| None` | `ctx.project_author` | Auteur affiché dans le tooltip. |
| `title` | `TextComponent \| None` | l'id avec espaces et majuscules | Titre affiché dans le tooltip. |

```python
Painting(
	id="stewbeet_painting",
	painting_data=PaintingData(texture="stewbeet_painting_2x2", author={"text": "Stoupy", "color": "yellow"}, width=2, height=2),
)
```

## Recipe system

Toute classe de recipe dérive de `RecipeBase`. Ses champs sont valables pour chaque classe ci-dessous.

| Champ | Type | Défaut | Effet |
|---|---|---|---|
| `result_count` | `int` | `1` | Quantité du résultat. |
| `category` | `str \| None` | `None` | Catégorie du recipe book écrite dans la recipe vanilla. |
| `group` | `str \| None` | l'id de l'item | Groupe du recipe book. |
| `result` | `Ingr \| None` | l'item auquel la recipe appartient | Ce que la recipe donne. |
| `manual_priority` | `int \| None` | `None` | Poids du bouton de la recipe sur la page de manual. Quand il y a trop de boutons, le poids le plus faible saute en premier. `None` pèse 1. |
| `smithed_crafter_command` | `str \| None` | `None` | Commande lancée par une recipe Smithed Crafter. Sans elle, la recipe donne la loot table du résultat. |

Un ingrédient est vérifié à la construction : il lui faut une clé `item` ou `components`, sinon la classe lève `ValueError`.

| Classe | Champs ajoutés | Notes |
|---|---|---|
| `CraftingShapedRecipe` | `shape: list[str]`, `ingredients: dict[str, Ingr]` | Au plus 3 lignes de 3 colonnes, toutes les lignes de même longueur. Chaque symbole de `ingredients` doit apparaître dans `shape`. |
| `CraftingShapelessRecipe` | `ingredients: list[Ingr]` | |
| `SmeltingRecipe` | `ingredient: Ingr`, `experience: float = 0.0`, `cookingtime: int = 200` | `cookingtime` en ticks. |
| `BlastingRecipe` | `ingredient: Ingr`, `experience: float = 0.0`, `cookingtime: int = 100` | La durée dans un blast furnace. La valeur écrite est doublée à partir de 26.3, où un blast furnace tire sa vitesse de son combustible. |
| `SmokingRecipe` | `ingredient: Ingr`, `experience: float = 0.0`, `cookingtime: int = 100` | Doublée à partir de 26.3 comme celle du blasting. |
| `CampfireCookingRecipe` | `ingredient: Ingr`, `experience: float`, `cookingtime: int` | Pas de défauts : les deux sont requis. |
| `StonecuttingRecipe` | `ingredient: Ingr` | |
| `SmithingTransformRecipe` | `template`, `base`, `addition`: `Ingr` | |
| `SmithingTrimRecipe` | `template`, `base`, `addition`: `Ingr`, `pattern: str` | `pattern` est l'id du trim pattern. |
| `PulverizingRecipe` | `ingredient: Ingr` | Une recipe de pulverizer SimplEnergy. |
| `AwakenedForgeRecipe` | `ingredients: list[Ingr]`, `particle: str \| None = None` | Une recipe d'awakened forge de Stardust Fragment. La page de forge du manual a une grille 3x3 pour jusqu'à 9 ingrédients et une grille 3x4 au-delà. |
| `HardcodedRecipe` | `type` | Une recipe spéciale vanilla, comme `crafting_special_armordye` ou `crafting_transmute`. `type` est requis et doit être l'un des types de recipe spéciale vanilla. |

`experience` et `cookingtime` sont vérifiés comme un nombre et un entier.

```python
CraftingShapedRecipe(shape=["II", "CC", "CC"], ingredients={"I": Ingr("minecraft:iron_ingot"), "C": Ingr("simplunium_ingot")})
```

### Ingr

`Ingr(id, ns=None, count=None, **kwargs)` construit le dictionnaire qui nomme un ingrédient. `Ingredient` et `IngrRepr` en sont des alias.

| Argument | Effet |
|---|---|
| `id` | Un id avec un `:` est un item vanilla ou un item d'un datapack : `{"item": id}`. Sans `:`, c'est un item d'un namespace, reconnu par son custom data : `{"components": {"minecraft:custom_data": {ns: {id: True}}}}`. Un dict est copié tel quel. |
| `ns` | Namespace d'un id sans `:`. L'id du projet par défaut. |
| `count` | Ajouté comme `count`. Utilisé pour un résultat, ou par un type de recipe qui gère les quantités. |
| `kwargs` | Ajoutés au dictionnaire. |

```python
Ingr("minecraft:stick")                     # {'item': 'minecraft:stick'}
Ingr("steel_ingot")                         # {'components': {'minecraft:custom_data': {'<project id>': {'steel_ingot': True}}}}
Ingr("tin_ingot", ns="mechanization")       # the same, in the namespace mechanization
Ingr("#minecraft:eggs")                     # an item tag, expanded in recipes into one recipe per item
```

Méthodes utilisées par les plugins : `to_id()`, `to_name()`, `to_item()`, `to_predicate()`, `to_vanilla_item_id()`, `item_to_id()` et `register_loot_table()`.

## Material generation

`generate_everything_about_these_materials(ores, ignore_recipes=False)` appelle `generate_everything_about_this_material(material, equipments_config=None, ignore_recipes=False)` pour chaque entrée de `ores`, un `dict[str, EquipmentsConfig | None]`. Elle lit `meta.stewbeet.textures_folder` et définit un item pour chaque texture trouvée.

Le nom du matériau fixe la base utilisée par tous les ids générés. Un nom avec un underscore est coupé avant le dernier (`steel_ingot` donne `steel`, `minecraft:copper_ingot` donne `copper`). Un nom qui finit par `!` est sa propre base (`awakened_stardust!` donne `awakened_stardust`), tout comme un nom sans underscore (`minecraft:stone` donne `stone`).

| Texture | Définie comme |
|---|---|
| `<base>`, `<base>_fragment`, `<base>_ingot`, `<base>_nugget`, `raw_<base>`, `<base>_dust`, `<base>_stick`, `<base>_rod` | Un `Item` avec `manual_category="material"`. |
| `<base>_block`, `raw_<base>_block` | Un `Block` avec `manual_category="material"` et sans `vanilla_block` : définissez-le ensuite. |
| `<base>_ore`, `deepslate_<base>_ore` | Un `Block` avec `manual_category="material"`, `vanilla_block=VANILLA_BLOCK_FOR_ORES`, et `no_silk_touch_drop` mis à `raw_<base>` quand cette texture existe, sinon au matériau lui-même. |
| `<base>_helmet`, `_chestplate`, `_leggings`, `_boots` | Un `Item` d'armure avec `manual_category="equipment"`. Demande une config. Son `base_item` est l'armure vanilla de l'`equivalent_to` de la config. |
| `<base>_sword`, `_pickaxe`, `_axe`, `_shovel`, `_hoe`, `_spear` | Un `Item` d'outil avec `manual_category="equipment"`. Son `base_item` est l'outil vanilla de `equivalent_to` quand une config est donnée. |
| `<base>_layer_1`, `<base>_layer_2` | L'equipment asset qui dessine l'armure sur un joueur : layer 1 pour le casque, le plastron et les bottes, layer 2 pour le pantalon. L'armure reçoit alors un component `equippable`. |

Les recipes viennent avec les items : un block depuis 9 du matériau et inversement, un lingot depuis 9 nuggets, du smelting et du blasting (200 et 100 ticks, 0.8 d'expérience) depuis l'item brut, la poudre ou les ores, des recipes de pulverizing pour la poudre, 4 bâtons depuis 2 matériaux, les formes vanilla habituelles pour les outils et armures, et un nugget en faisant fondre une pièce d'équipement. `ignore_recipes`, ou celui de la config, les saute toutes. Les recipes d'équipement ont `manual_priority=0`.

Le `max_damage` de chaque pièce est sa durabilité vanilla pour `equivalent_to`, multipliée par `pickaxe_durability` divisé par la durabilité de la pickaxe vanilla. Le `custom_data` de chaque item généré porte une entrée `smithed.dict` qui nomme son type et sa base.

`add_recipes_for_dust(material, pulverize, smelt_to)` définit `<material>_dust` depuis sa texture. Elle ajoute des recipes de smelting et de blasting qui donnent `smelt_to`, la recipe de pulverizing inverse, et une recipe de pulverizing qui donne 2 poudres pour chaque entrée de `pulverize`. Une entrée `str` est l'item vanilla de ce nom. `add_recipes_for_all_dusts(dusts_configs)` prend un dict qui associe un matériau à `(pulverize, smelt_to)`.

### EquipmentsConfig

`EquipmentsConfig` est une classe simple qui prend ces arguments.

| Argument | Type | Défaut | Effet |
|---|---|---|---|
| `equivalent_to` | `DefaultOre` | `DefaultOre.DIAMOND` | Tier vanilla dont viennent les stats de base. |
| `pickaxe_durability` | `float \| int` | `0` | Durabilité de la pickaxe, dont chaque pièce découle. `0` utilise la durabilité de la pickaxe vanilla de `equivalent_to`. |
| `attributes` | `dict[str, float] \| None` | `{}` | Attribute modifiers ajoutés aux stats vanilla, avec l'opération `add_value`. |
| `ignore_recipes` | `bool` | `False` | Saute les recipes de ce matériau. |

Les attributes sont nommés sans préfixe : une clé qui contient `player.` ou `generic.` affiche un avertissement, comme un `knockback_resistance` de 1 ou plus, que Minecraft multiplie par 10 sur l'équipement. `attack_damage` et `mining_efficiency` vont sur les outils seulement, `armor`, `armor_toughness` et `knockback_resistance` sur l'armure seulement, et tout autre attribute, comme `movement_speed` ou `burning_time`, sur les deux. Un `attack_damage` de 1 sur une pickaxe en diamant la fait passer à 6. Tout le reste appartient à l'item une fois généré : définissez-le sur `Item.from_id(...).components`.

### DefaultOre

| Membre | Tier vanilla |
|---|---|
| `NETHERITE` | netherite |
| `DIAMOND` | diamond |
| `IRON` | iron |
| `GOLD` | golden |
| `COPPER` | copper |
| `CHAINMAIL` | outils en pierre, armure en chainmail |
| `LEATHER` | outils en bois, armure en cuir |

`VanillaEquipments` contient les stats vanilla de chaque tier : `VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"]` vaut 250. Ses membres sont `HELMET`, `CHESTPLATE`, `LEGGINGS`, `BOOTS`, `SWORD`, `PICKAXE`, `AXE`, `SHOVEL`, `HOE` et `SPEAR`.

## Wiki buttons et item manual

`WikiButton(content)` enveloppe un text component, affiché au survol d'un bouton d'info sur la page de manual de l'item.

`Item.wiki_buttons` accepte une liste qui contient au moins un `WikiButton`, un bouton chacun. Toute autre valeur, un text component ou une liste simple de text components, est un seul bouton.

```python
Item.from_id("steel_ingot").wiki_buttons = [
	WikiButton([{"text": "Steel is a stronger variant of iron.\n"}, {"text": "It provides better durability.", "color": "yellow"}]),
	WikiButton({"text": "This is another button.", "color": "aqua"}),
]
```

Le plugin manual crée l'item `manual` : `base_item` `minecraft:written_book`, l'item model `<ns>:manual`, `item_name` mis à `meta.stewbeet.manual.name`, une taille de stack de 16, pas de lueur et le lore `by <author>`. Une definition avec l'id `manual` y est fusionnée : ses components l'emportent, et ses recipes sont celles de l'item. Avec `use_dialog: 2` et sans definition `manual`, aucun item n'est créé.

```python
Item(
	id="manual",
	manual_category="miscellaneous",
	recipes=[
		CraftingShapelessRecipe(category="misc", ingredients=[Ingr("minecraft:book"), Ingr("steel_ingot")]),
		CraftingShapelessRecipe(category="misc", ingredients=[Ingr("manual")]),
	],
)
```

## Music discs

`generate_custom_records(records="auto", category=None, attenuation_distance=None)` définit un disque par son. Elle lit `meta.stewbeet.records_folder`, et le build s'arrête quand cette clé manque.

| Argument | Type | Défaut | Effet |
|---|---|---|---|
| `records` | `dict[str, str] \| str \| None` | `"auto"` | Un dict qui associe un id de disque à un nom de fichier du dossier, ou `"auto"`, `"all"` et `None` pour chaque `.ogg` du dossier. |
| `category` | `str \| None` | `None` | `manual_category` des disques. |
| `attenuation_distance` | `int \| None` | `None` | Distance en blocks au-delà de laquelle le disque est silencieux. `None` vaut les 16 vanilla. |

Avec `"auto"`, l'id d'un disque est son nom de fichier nettoyé : lettres minuscules et chiffres, espaces et tirets changés en `_`. Un fichier qui n'est pas un `.ogg` affiche un avertissement et est ignoré.

Chaque disque est un `Item` avec `jukebox_playable` mis à `<ns>:<id>`, `item_name` `Music Disc`, `max_stack_size` 1 et `rarity` `rare`. Le nom du fichier sans extension est la description de la chanson. La durée lue dans le fichier donne `length_in_seconds` comme la durée plus une seconde, et `comparator_output` comme la durée modulo 16. Le son est streamé sous l'id du disque.

## Catégories du manual

`manual_category` est une chaîne libre. Le manual regroupe les items par sa valeur exacte, affiche chaque groupe sur une page titrée avec la valeur en title case, et ne liste aucun item sans catégorie. Une catégorie qui contient plus d'items que `max_items_per_row * max_rows_per_page` est découpée en pages numérotées, et plus de catégories que ce qui tient sur une page fait échouer le build.

Deux orthographes font deux catégories. Les helpers de matériaux écrivent `"material"` pour les ingrédients et les blocks et `"equipment"` pour les outils et armures, donc un item écrit à la main partage leur page en utilisant les mêmes valeurs.

## Resource locations et BlockFunctions

Chaque emplacement que StewBeet dérive d'un id est une propriété qui renvoie une `Resource`. Une `Resource` est un `str` qui contient `namespace:path`, donc elle marche dans les f-strings, comme chemin de `write_function` et comme clé de dict. Elle donne aussi le fichier beet.

| Propriété ou méthode | Valeur pour `Item(id="steel_ingot")` |
|---|---|
| `loot_table` | `ns:i/steel_ingot` |
| `loot_table_for(n)` | `ns:i/steel_ingot_x4`, ou `_x4to6` pour `{"min": 4, "max": 6}` |
| `item_model` | `ns:steel_ingot`, ou le component `item_model` quand il est défini |
| `generated_item_model` | `ns:steel_ingot`, toujours le fichier que StewBeet écrit |
| `model` | `ns:item/steel_ingot` |
| `texture` | `ns:item/steel_ingot` |
| `recipe(index=1)` | `ns:steel_ingot`, `ns:steel_ingot_2` pour l'index 2 |
| `ranged_weapon_enchantment` | `ns:ranged_weapon/steel_ingot` |

`Block` ajoute `functions`, `no_silk_touch_loot_table` (`ns:custom_blocks/no_silk_touch_drop/<id>`), `seed_loot_table` (`ns:seeds/<id>`), `advancement` (un `ValueError` pour un `Block` normal), `alternative_advancement`, `head_advancement`, `head_search` (`ns:custom_blocks/_player_head/search_<id>`), et `seed_stage_name`, `seed_stage_item_model`, `seed_stage_model` et `seed_stage_texture` pour un stade de croissance, nommés d'après `texture_basename`. `Painting` ajoute `variant`, `painting_texture` et `asset_id`.

| Méthode de `Resource` | Effet |
|---|---|
| `obj` | Le fichier beet. Lève `KeyError` quand il n'existe pas encore. Lui assigner une valeur écrit le fichier. |
| `get(default=None)` | Le fichier beet, ou `default`. |
| `exists()` | Si le fichier est dans le pack. |
| `setdefault(default=None)` | Le fichier, en insérant `default` ou un fichier vide quand il est absent. |
| `write(value)` | Écrit le fichier et le renvoie. |
| `delete()` | Retire le fichier quand il est présent. |
| `child(name)`, `suffixed(suffix)`, `sibling(name)` | Resources dérivées : `<path>/<name>`, `<path><suffix>`, `<folder>/<name>`. |
| `namespace`, `relative_path`, `file_type` | Les parties de l'emplacement. |

`Block.functions` renvoie un `BlockFunctions`, qu'on peut aussi construire directement : `BlockFunctions(block_id, namespace=None)` n'a pas besoin de definition. `functions["name"]` donne n'importe quelle function du dossier du block, `functions.folder` le dossier, et l'itérer liste les functions déjà dans le pack.

| Propriété | Function dans `ns:custom_blocks/<id>/` | Exécutée |
|---|---|---|
| `place_main` | `place_main` | À la position du block quand il est placé. |
| `place_secondary` | `place_secondary` | Par l'item display ou l'item frame invoqué, quand le block est placé. |
| `place_check` | `place_check` | Vérifie que le block placé est bien celui-ci avant `place_main`. |
| `search` | `search` | Cherche l'entity placée d'un block à item frame. |
| `get_facing` | `get_facing` | Calcule l'orientation depuis celle du joueur. |
| `destroy` | `destroy` | Quand le block est détruit. |
| `replace_item` | `replace_item` | Remplace l'item tombé par l'item du block. |
| `update_seed_model` | `update_seed_model` | Met le model d'une graine qui pousse à son stade. |
| `is_fully_grown` | `is_fully_grown` | Quand une graine qui pousse atteint son dernier stade. |
| `tick`, `tick_2`, `second`, `second_5`, `minute` | les mêmes noms | À chaque tick, 2 ticks, seconde, 5 secondes, minute, par l'entity du block. |

```python
steel_block = Block.from_id("steel_block")
write_function(steel_block.functions.tick, "particle heart ~ ~1 ~ 0.5 0.5 0.5 0.01 1")
write_function(BlockFunctions("steel_block").second, "particle angry_villager ~ ~1 ~ 0.2 0.2 0.2 0.01 10")
```

## Patterns de textures reconnus

Une texture est associée à une definition par son nom de fichier : `<id>.png`, ou `<id>_<suffix>.png` pour une variante. Une variante est cherchée parmi les fichiers du dossier des textures qui commencent par l'id et qui ont au plus deux underscores de plus que l'id.

Les patterns de block s'appliquent à un `Block` dont le `base_item` est celui par défaut, ou dont l'`override_model` nomme un parent de block. Une seule texture donne `block/cube_all`. Sinon, le premier pattern dont tous les côtés ont une texture l'emporte.

| Parent | Textures |
|---|---|
| `block/cake` | `<id>_bottom`, `<id>_side`, `<id>_top`, `<id>_inner` |
| `block/orientable_with_bottom` | `<id>_front`, `<id>_bottom`, `<id>_side`, `<id>_top` |
| `block/cube_bottom_top` | `<id>_bottom`, `<id>_side`, `<id>_top` |
| `block/orientable` | `<id>_front`, `<id>_side`, `<id>_top` |
| `block/cube_column` | `<id>_end`, `<id>_side` |

Un block qui ne correspond à aucun arrête le build, sauf si son `override_model` donne les textures.

| Pattern d'item | Textures et condition |
|---|---|
| Overlay | `<id>_overlay` devient la deuxième couche du model. |
| Armure en cuir | Un `base_item` qui commence par `leather_` reçoit aussi sa texture en deuxième couche, pour la teinture. |
| Bow | Un `base_item` qui finit par `bow` et des textures `<id>_pulling_0`, `<id>_pulling_1`, et ainsi de suite, dessinées dans l'ordre pendant que l'arc se tend. Une arbalète lit aussi `<id>_arrow` et `<id>_firework`. |
| Spear | Un id qui finit par `_spear` et une texture `<id>_in_hand` affichent cette texture hors du gui, au sol, dans les frames et sur les shelves. |
| Powered | Une texture qui finit par `_on` donne à l'item et au block un model `_on`. Un hôte furnace, smoker ou blast furnace l'affiche pendant qu'il brûle. |

## Fonctions helpers de setup

Chaque fonction lit `Mem.definitions` au moment où elle est appelée, donc elle s'exécute après la création de toutes les definitions.

| Fonction | Effet |
|---|---|
| `add_item_model_component(black_list=None)` | Met `item_model` au item model généré sur chaque definition qui n'en a pas, sauf les ids de `black_list`. |
| `add_item_name_and_lore_if_missing(is_external=False, black_list=None)` | Met `item_name` à l'id en title case quand il est absent, et ajoute la ligne `meta.stewbeet.source_lore` à `lore`. |
| `add_private_custom_data_for_namespace(is_external=False, black_list=None)` | Met `custom_data.<ns>.<id>` à `true`, ainsi que `custom_data.smithed.id` et `origin`. C'est ainsi que les items sont détectés dans les recipes et les functions. |
| `add_smithed_ignore_vanilla_behaviours_convention()` | Met `custom_data.smithed.ignore.functionality` et `crafting` à `true`. |
| `set_manual_components(white_list)` | Components affichés au survol d'un item dans le manual. Une liste vide ne change rien. |
| `export_all_definitions_to_json(file_name, is_external=False, verbose=True)` | Écrit chaque definition dans un seul fichier JSON, sans `override_model`. |
| `resolve_use_remainders()` | Écrit `use_remainder` sur chaque item qui a un `remainder`. Les plugins de recipes, de loading et de loot tables l'appellent. |

`is_external=True` s'exécute sur `Mem.external_definitions` à la place.

## Pour continuer

- [Items et blocks](../items_and_blocks/fr.md) : déclarez un item, un block et leurs recipes pas à pas.
- [Helpers](../2_writing_to_files/reference/fr.md) : les functions qui écrivent les fichiers vers lesquels une definition pointe.
- [Custom blocks](../plugins/datapack.custom_blocks.fr.md) : chaque fichier que le plugin écrit pour un `Block`.

