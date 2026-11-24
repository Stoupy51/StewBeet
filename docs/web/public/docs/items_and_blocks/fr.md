
# Items et blocks

Déclarez un item ou un block une fois, en Python. Chaque build écrit son model, sa loot table, ses recipes, ses traductions et sa page de manuel à partir de cette déclaration.

Il vous faut un projet : lancez d'abord le [Quickstart](../quickstart/fr.md) si vous n'en avez pas. Vos déclarations vont dans `src/definitions/additions.py`, le fichier que chaque template garde pour elles.

## 1. Ajouter les textures

Mettez un PNG par item dans `assets/textures/`, nommé d'après son id. StewBeet trouve une texture par son nom : `steel_ingot.png` est la texture de l'item dont l'id est `steel_ingot`.

Un block prend une texture pour toutes les faces, ou une par face comme `steel_block_top.png` et `steel_block_side.png`. Les [texture patterns reconnus](../1_definitions_setup/fr.md#patterns-de-textures-reconnus) listent chaque suffixe que StewBeet lit.

## 2. Déclarer l'item

```python title="src/definitions/additions.py"
from stewbeet import *


def main():
	Item(
		id="steel_ingot",
		manual_category="material",
		components={
			"item_name": "Steel Ingot",
		},
	)
```

Créer l'`Item` l'enregistre : il n'y a pas de liste où l'ajouter. `components` accepte n'importe quel component d'item Minecraft, écrit sans `minecraft:`. `manual_category` est une chaîne libre, et le manuel fait une page par valeur exacte : le générateur de matériaux écrit `material` pour les ingrédients et les blocks et `equipment` pour les outils et armures, donc `materials` et `material` font deux pages.

## 3. Ajouter une recipe de four

Une recipe va dans la liste `recipes` de l'item qu'elle fabrique :

```python
iron = Ingr("minecraft:iron_ingot")
Item(
	id="steel_ingot",
	manual_category="material",
	components={
		"item_name": "Steel Ingot",
	},
	recipes=[
		SmeltingRecipe(ingredient=iron),
		BlastingRecipe(ingredient=iron),
	],
)
```

Un four transforme un lingot de fer en lingot d'acier, et un haut fourneau le fait deux fois plus vite. `cookingtime` fixe la durée en ticks, 200 dans un four et 100 dans un haut fourneau par défaut, et `experience=0.7` donne l'expérience d'un minerai vanilla. `SmokingRecipe` prend les mêmes arguments.

## 4. Déclarer un block

Un `Block` est un item qui peut être posé. Son `vanilla_block` tient sa place dans le monde, donc il décide du son du block, du temps qu'il faut pour le miner et de l'outil qui le mine :

```python
steel = Ingr("steel_ingot")
Block(
	id="steel_block",
	vanilla_block=VanillaBlock(
		id="minecraft:iron_block",
	),
	manual_category="material",
	components={
		"item_name": "Steel Block",
	},
	recipes=[
		CraftingShapedRecipe(
			shape=["XXX", "XXX", "XXX"],
			ingredients={"X": steel},
		),
	],
)
```

`Ingr("steel_ingot")` est un de vos items, `Ingr("minecraft:iron_ingot")` un item vanilla. Une recipe fabrique un exemplaire de l'item auquel elle appartient : fixez `result_count` pour en avoir plus, ou `result=Ingr(...)` pour fabriquer autre chose. La page [Custom blocks](../plugins/datapack.custom_blocks.fr.md) liste chaque fichier qu'un block reçoit et chaque option de `VanillaBlock`.

## 5. Compiler et les obtenir en jeu

```bash
uv run stewbeet build
```

Dans votre monde, lancez `/reload`, puis `/function <namespace>:_give_all` pour obtenir chaque item, ou `/loot give @s loot <namespace>:i/steel_block` pour un seul. Le namespace est l'`id` de votre `beet.yml`.

## Où finit chaque recipe

| Ingrédients | Ce que le build écrit |
|---|---|
| Items vanilla seulement | Un fichier de recipe dans `data/<namespace>/recipe/` |
| Un de vos items, craft | Une recipe pour la bibliothèque Smithed Crafter |
| Un de vos items, cuisson | Une recipe pour la bibliothèque Furnace NBT Recipes |

Les recipes vanilla ne peuvent pas vérifier les custom data, c'est pourquoi vos propres items passent par une bibliothèque. Le build ajoute chaque bibliothèque au pack quand une recipe en a besoin.

## Charger vos modules de définitions

beet exécute les plugins listés sous `pipeline` dans `beet.yml`, dans l'ordre. Un projet liste ses fichiers d'entrée de définitions en premier, avant les plugins qui les lisent :

```yaml title="beet.yml"
pipeline:
    - "src.definitions.setup_main"
    - "src.definitions.setup_external"
```

Le fichier d'entrée importe les autres modules de définitions et les appelle. Le `src/definitions/setup_main.py` de SimplEnergy le fait dans cet ordre :

```python title="src/definitions/setup_main.py"
def beet_default(ctx: Context) -> None:
	generate_everything_about_these_materials(ORES_CONFIGS)
	add_recipes_for_all_dusts(DUSTS_CONFIGS)
	generate_custom_records("auto")

	material_additions()
	gear_additions()
	energy_additions()
	misc_additions()

	add_item_model_component(black_list = ["simple_cable", "advanced_cable", "elite_cable"])
	add_item_name_and_lore_if_missing()
	add_private_custom_data_for_namespace()
	add_smithed_ignore_vanilla_behaviours_convention()
	set_manual_components(white_list=["item_name", "lore", "custom_name", "attribute_modifiers"])
```

Les cinq derniers appels complètent chaque définition existant au moment où ils s'exécutent, donc ils viennent après le dernier module qui en déclare une. Les générateurs viennent avant les modules qui ajustent ce qu'ils ont fait, parce que `Item.from_id` échoue sur un id que rien n'a encore déclaré.

Un item sans `manual_category` n'a pas de page de manuel. Le template donne `"miscellaneous"` aux autres dans une boucle sur `Mem.definitions` avant les appels finaux.

## Générer toute une gamme de matériau à partir d'un lingot

Une entrée d'un dictionnaire, et les textures de `assets/textures/` décident de ce qui existe. `simplunium_ingot` a pour base `simplunium`, donc `simplunium_pickaxe.png` fait une pioche, `simplunium_helmet.png` un casque, `raw_simplunium_block.png` un block de matière brute :

```python title="src/definitions/additions/gear.py"
SIMPLUNIUM_EQUIPMENTS: EquipmentsConfig = EquipmentsConfig(
	DefaultOre.IRON,
	3 * VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"],
	{"attack_damage": 1, "armor": 0.5, "mining_efficiency": 2},
)
```

```python
generate_everything_about_these_materials({"simplunium_ingot": SIMPLUNIUM_EQUIPMENTS})

Block.from_id("simplunium_block").vanilla_block = VanillaBlock(id="minecraft:iron_block")
Block.from_id("raw_simplunium_block").vanilla_block = VanillaBlock(id="minecraft:raw_iron_block")
```

Les outils et armures prennent les stats du fer, trois fois sa durabilité, et les attributs qui leur sont ajoutés. L'armure n'est générée que si une config est donnée. Le générateur choisit l'hôte des minerais, mais pas celui des blocks de stockage, donc les lignes après l'appel le fixent.

## Donner à un block des états allumé et éteint, ou une orientation

Un block tire son model des noms de ses textures. Le générateur à four de SimplEnergy a `furnace_generator_front.png`, `furnace_generator_side.png` et `furnace_generator_top.png`, qui sont les faces du model `orientable`, et un `furnace_generator_front_on.png` pour quand il travaille :

```python
Block(
	id="furnace_generator",
	vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player"),
	manual_category="energy",
)
```

`block_facing="player"` fait pivoter l'hôte four comme le fait vanilla, et le model suit. Une texture qui finit par `_on` fait écrire au build un model `_on`, qu'un hôte four, fumoir ou haut fourneau affiche pendant qu'il brûle. Un block dont les textures ne remplissent aucun pattern arrête le build et liste les patterns qu'il connaît, tous dans [Texture patterns reconnus](../1_definitions_setup/fr.md#patterns-de-textures-reconnus).

## Ajouter un arc avec des animations de tension

Donnez à un item `minecraft:bow` comme `base_item`, et numérotez à partir de 0 les textures de ses étapes :

```python
Item(
	id="stardust_bow",
	base_item="minecraft:bow",
	manual_category="equipment",
	components={"max_damage": 768},
)
```

Avec `stardust_bow.png`, `stardust_bow_pulling_0.png`, `stardust_bow_pulling_1.png` et `stardust_bow_pulling_2.png` dans le dossier de textures, le build écrit un model par texture de tension et un model d'item qui bascule entre eux pendant que l'arc est bandé. Une arbalète fait de même à partir de `_pulling_<n>`, et montre une flèche ou une fusée de feu d'artifice chargée à partir de `<id>_arrow.png` et `<id>_firework.png`. `RangedWeapon` règle le temps de charge, les dégâts et les munitions d'une arbalète, comme dans [RangedWeapon](../1_definitions_setup/fr.md#rangedweapon).

## Modifier un item qu'un autre module a déclaré

`Item.from_id(id)` renvoie l'objet qu'un module a enregistré, quel que soit le module qui l'appelle, donc un module suivant en fixe des champs au lieu de déclarer l'item de nouveau :

```python
simplunium = Item.from_id("simplunium_ingot")
simplunium.wiki_buttons = [WikiButton({"text": "Found as simplunium ore, or made from its raw form.", "color": "yellow"})]
simplunium.recipes.append(CraftingShapelessRecipe(category="misc", ingredients=[Ingr("simplunium_block")], result_count=9))
```

`Item(id="simplunium_ingot")` pour un id déjà déclaré ne change rien : le premier objet reste enregistré, et le build avertit que le second est ignoré. Assigner une nouvelle liste à `recipes` remplace les recipes générées, `append` les garde.

## Exécuter des commandes quand un custom block est posé

Chaque function d'un block a un nom sur `Block.functions`, donc aucun chemin n'est tapé à la main. `place_secondary` s'exécute en tant que l'entité display que le block invoque quand il est posé :

```python title="src/link.py"
solar_panel = Block.from_id("solar_panel")
solar_panel.functions.place_secondary.obj.append("""
data modify entity @s transformation.scale[1] set value 1.005f
data modify entity @s transformation.translation[1] set value 0.002f
""")
```

`.obj` est la function beet, qui existe une fois que `stewbeet.plugins.datapack.custom_blocks` a tourné, donc cela va dans un plugin listé après lui dans `pipeline`, comme le `src/link.py` du template. Avant, cela lève `KeyError`, là où `write_function` placerait les commandes avant la mise en place propre du block. `BlockFunctions("solar_panel")` donne les mêmes chemins sans recherche de définition. Les autres noms, comme `second` et `destroy`, sont dans [Resource locations et BlockFunctions](../1_definitions_setup/fr.md#resource-locations-et-blockfunctions).

## Étapes suivantes

- [Définitions](../1_definitions_setup/fr.md) : chaque champ d'`Item` et de `Block`, et chaque type de recipe.
- [Tutoriel, étape 7](../0_getting_started/fr.md#7-ajouter-une-gamme-complete-de-minerai) : un minerai, ses outils et son armure à partir d'une seule entrée de matériau.

