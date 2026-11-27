
# Tutoriel : construire votre premier datapack

Dans ce tutoriel, vous créez un projet StewBeet, vous le compilez, vous le chargez dans Minecraft, puis vous ajoutez un item personnalisé et une gamme complète de minerai de rubis avec un custom block fonctionnel. Comptez environ 20 minutes. Vous avez déjà un datapack ? [Migrez-le](../9_migration/fr.md) plutôt.

Il vous faut trois choses :

- **uv**, [le gestionnaire de paquets Python d'Astral](https://docs.astral.sh/uv/). Il installe Python pour vous, c'est donc le seul élément de cette liste à installer à la main.
- **Un éditeur de texte.** [VS Code](https://code.visualstudio.com/) avec le pack d'extensions Python et l'[extension StewBeet](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) vous donne la complétion dans vos commandes.
- **Minecraft Java Edition**, pour tester le résultat.

Vous n'installez pas Python vous-même. StewBeet a besoin de la 3.14, chaque template l'indique dans son `pyproject.toml`, et uv télécharge une version adaptée au premier build.

## 1. Installer uv

```powershell tab="Windows"
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash tab="macOS et Linux"
curl -LsSf https://astral.sh/uv/install.sh | sh
```

D'autres moyens de l'installer (winget, Homebrew, pipx, un binaire autonome) sont listés sur la [page d'installation d'uv](https://docs.astral.sh/uv/getting-started/installation/).

Fermez et rouvrez votre terminal, puis vérifiez qu'uv est dans votre PATH :

```bash
uv --version
```

> Vous avez déjà Python 3.14 et préférez pip ? `pip install stewbeet` fonctionne aussi, et chaque `uv run stewbeet ...` ci-dessous devient simplement `stewbeet ...`. Le reste du tutoriel est identique.

## 2. Créer le projet

StewBeet fournit trois templates. Ce tutoriel utilise **Basic** : chaque plugin y est configuré et commenté, et il n'y a pas de contenu d'exemple à supprimer.

| Template | Pour | Ce que vous obtenez |
|----------|-----|--------------|
| Minimal | Apprendre beet seul | Un plugin StewBeet, rien d'autre |
| **Basic** | **La plupart des projets** | Chaque plugin, commenté, sans contenu d'exemple |
| Extensive | Lire de vrais exemples | Chaque fonctionnalité, avec des items, des minerais et un manuel qui fonctionnent |

1. Créez un dossier pour le projet, par exemple `C:/MyDatapacks/AwesomeOres/`.
2. Ouvrez-le dans VS Code (clic droit sur le dossier puis "Ouvrir avec Code", ou Fichier, Ouvrir un dossier).
3. Ouvrez un terminal avec Terminal, Nouveau terminal. Il démarre dans le dossier du projet.
4. Lancez :

   ```bash
   uvx stewbeet init basic
   ```

`uvx` télécharge StewBeet, l'exécute une fois et jette la copie, donc rien n'est installé globalement. Le dossier ressemble à ceci :

```bash
AwesomeOres/
├── .beet_cache/              # Build cache (generated)
├── build/                    # Output folder (generated)
├── .venv/                    # Project environment (created by uv on the first build)
├── assets/                   # Your textures and sounds
│   └── pack.png              # The icon of both packs
├── src/                      # Your source code
│   ├── data/                 # Datapack functions and data
│   │   └── basic_template/   # Your namespace (rename this)
│   ├── definitions/          # Definition modules
│   │   ├── additions.py      # Custom items and blocks
│   │   └── ores.py           # Ore and equipment tiers
│   ├── link.py               # Code that runs after the definitions
│   └── setup_definitions.py  # Entry point for the definitions
├── .gitignore
├── pyproject.toml            # Python dependencies (StewBeet and anything you add)
├── beet.yml                  # Main configuration file
└── definitions_debug.json    # What your definitions produced, for debugging
```

### Ce que fait `pyproject.toml`

Il rend le projet autonome :

```toml
[project]
name = "template"
version = "0.0.1"
requires-python = ">=3.14"
dependencies = [
	"stewbeet>=3.18.1",
]

[tool.uv]
package = false
```

`requires-python` indique à uv quel interpréteur récupérer.

Pour utiliser une autre bibliothèque dans vos définitions (`requests`, `pillow`), lancez `uv add requests`. Elle se retrouve dans ce fichier, dans votre `.venv`, et dans le lock file que vos collaborateurs réutilisent.

## 3. Nommer votre pack

Ouvrez `beet.yml`. Ces champs identifient le pack et sont réutilisés dans `pack.mcmeta`, le lore des items, les noms d'archives et le manuel :

```yaml
# Project identifier used for namespacing functions and tags. Should align with the namespace in the source folder.
id: "awesome_ores"

# Project name that will be used in messages, item lore, etc.
name: "Awesome Ores"

# Author(s) name(s) displayed in pack.mcmeta
author: "YourName"

# Project version in semantic versioning format
version: "1.0.0"

# Pack description for pack.mcmeta. Defaults to "{name} [{version}] by {author}" if empty.
description: ""
```

| Champ | Règle | Exemple |
|-------|------|---------|
| `id` | Minuscules et underscores, sans espaces. Doit correspondre au dossier de `src/data/` | `awesome_ores` |
| `name` | Texte libre | `"Awesome Ores & Gems"` |
| `version` | [Semantic versioning](https://semver.org/), major.minor.patch | `1.0.0` |

Renommez `src/data/basic_template/` en `src/data/awesome_ores/` pour qu'il corresponde à `id`.

## 4. Le compiler

Dans le terminal, lancez `uv run stewbeet` (ou `uv run stewbeet build`, qui est identique).

Le premier lancement fait la mise en place : uv lit `pyproject.toml`, télécharge Python 3.14 s'il manque, crée `.venv/` et installe StewBeet. Les lancements suivants compilent immédiatement.

Le build affiche le temps pris par chaque plugin. Un projet vide affiche aussi quelques avertissements, comme celui qui dit que le manuel n'a encore rien à lister.

`build/` contient :

| Chemin | Ce que c'est |
|------|------------|
| `datapack/` | Le datapack généré, décompressé |
| `resource_pack/` | Le resource pack généré, décompressé |
| `AwesomeOres_datapack.zip` | Le datapack, prêt à être déposé dans un monde |
| `AwesomeOres_resource_pack.zip` | Le resource pack, prêt à être activé |
| `sha1_hashes.json` | Les hashes des archives, pour les admins de serveur |

## 5. Le charger dans Minecraft

La boucle la plus rapide consiste à laisser chaque build copier les packs dans votre jeu. Ajoutez ceci sous `meta.stewbeet` dans `beet.yml`, avec vos propres chemins :

```yaml
build_copy_destinations:
  datapack: ["C:/Users/YourName/AppData/Roaming/.minecraft/saves/YourWorldName/datapacks"]
  resource_pack: ["C:/Users/YourName/AppData/Roaming/.minecraft/resourcepacks"]
```

Avec cela, `uv run stewbeet` copie les deux packs après chaque build.

Pour les copier à la main à la place :

1. Copiez `build/AwesomeOres_datapack.zip` dans le dossier datapacks du monde :
   - Windows : `%appdata%\.minecraft\saves\[WorldName]\datapacks\`
   - macOS : `~/Library/Application Support/minecraft/saves/[WorldName]/datapacks/`
2. Copiez `build/AwesomeOres_resource_pack.zip` dans le dossier des resource packs :
   - Windows : `%appdata%\.minecraft\resourcepacks\`
   - macOS : `~/Library/Application Support/minecraft/resourcepacks/`

Ensuite, en jeu :

1. Lancez `/reload`. Le message de chargement écrit par `src/link.py` apparaît dans le chat.
2. Activez le resource pack dans Options, Packs de ressources.
3. Lancez `/function awesome_ores:path/to/a/random/function/i/guess`. Cela affiche "Hello world!", depuis la function que `src/link.py` écrit.

## 6. Ajouter un item personnalisé

1. Créez `assets/textures/` et mettez-y un PNG 16x16, par exemple [`ruby.png`](./ruby.png), de sorte que le fichier soit `assets/textures/ruby.png`.
2. Ouvrez `src/definitions/additions.py` et déclarez l'item. L'`id` correspond au nom de la texture, c'est ainsi que StewBeet la trouve :

```python
# Imports
from stewbeet import *  # type: ignore


# Main entry point
def main():

	# Add items to the definitions
	Item(
		id="ruby",
		manual_category="material",
		components={
			"lore": [{"text":"A precious red gemstone","color":"gray","italic":False}]
		}
	)
```

3. Lancez `uv run stewbeet`.
4. En jeu, lancez `/reload`, puis `/loot give @s loot awesome_ores:i/ruby` ou `/function awesome_ores:_give_all`.

À partir de cette seule déclaration, StewBeet a écrit le model de l'item, ajouté la texture au resource pack, construit les components de l'item, et listé l'item dans le manuel sous sa `manual_category`.

## 7. Ajouter une gamme complète de minerai

Mettez ces textures dans `assets/textures/` :

| Fichier | Sert à |
|------|----------|
| [`ruby_ore.png`](./ruby_ore.png) | Le block de minerai |
| [`ruby_sword.png`](./ruby_sword.png) | L'épée |
| [`ruby_chestplate.png`](./ruby_chestplate.png) | L'item plastron |
| [`ruby_layer_1.png`](./ruby_layer_1.png) | Armure portée, couche du haut (la façon dont Minecraft dessine l'armure personnalisée) |
| [`ruby_layer_2.png`](./ruby_layer_2.png) | Armure portée, couche du bas, dessinée sur les jambières (lue seulement si un `ruby_leggings.png` existe) |

Ouvrez `src/definitions/ores.py` et décrivez le matériau. Tout ce que StewBeet trouve dans le dossier de textures sous le préfixe `ruby` est enregistré à partir de cette entrée :

```python
# Imports
from stewbeet import *  # type: ignore


# Main entry point
def main():

	# Configuration to generate everything about a material
	ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
		"ruby": EquipmentsConfig(
			# This ruby is equivalent to diamond,
			equivalent_to = DefaultOre.DIAMOND,

			# But, has more durability (1.2 times more)
			pickaxe_durability = 1.2 * VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]["durability"],

			# And, does 1 more damage per hit (mainhand), has 0.5 more armor, and adds 0.2 to the mining efficiency attribute of tools
			attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
		),
	}

	# Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
	generate_everything_about_these_materials(ORES_CONFIGS)
```

`src/setup_definitions.py` exécute `ores.py` avant `additions.py`. Avec un `ruby.png` dans le dossier de textures, l'item `ruby` vient du matériau, donc un `Item(id="ruby", ...)` dans `additions.py` est ignoré : un item déjà présent dans les définitions n'est pas remplacé. Définissez plutôt le lore sur l'item existant :

```python
Item.from_id("ruby").components["lore"] = [{"text":"A precious red gemstone","color":"gray","italic":False}]
```

Compilez, `/reload`, puis lancez `/loot give @s loot awesome_ores:i/ruby_ore` et posez le block. C'est un custom block fonctionnel : StewBeet a écrit son model, sa logique de pose et de destruction et ses drops, et l'a relié à la bibliothèque Smithed Custom Block. Sans Silk Touch il lâche un rubis, avec Silk Touch le minerai lui-même. L'épée et le plastron reçoivent des recipes de craft faites à partir de rubis.

## 8. Ouvrir le manuel en jeu

Le manuel utilise le système de dialogs de Minecraft, qui ne prend en compte les nouveaux dialogs qu'au redémarrage du serveur, donc quittez puis rejoignez d'abord le monde. Ensuite appuyez sur G (le raccourci d'action rapide), ou lancez `/loot give @s loot awesome_ores:i/manual` si vous êtes parti du template Extensive.

Le manuel liste vos items avec leurs recipes, tirés de vos définitions.

## Ce que contient `beet.yml`

`beet.yml` a deux parties à connaître avant d'aller plus loin.

Les dossiers que StewBeet lit, sous `meta.stewbeet` :

```yaml
# Directory containing all project textures
textures_folder: "assets/textures"
# Directory containing all custom sounds
sounds:
    folder: "assets/sounds"
    # Optional: glob patterns to exclude from processing
    exclude_patterns: ["some_sub_folder/*"]
# Directory containing all jukebox records
records_folder: "assets/records"
# Directory containing libraries that will be copied to the build destination, and merged using Smithed Weld if enabled.
libs_folder: "libs"
# Optional: glob patterns (relative to libs_folder) of library archives to leave out of the build
libs_exclude_patterns: []
```

Le `pipeline` liste chaque étape du build dans l'ordre. Chaque ligne `stewbeet.plugins` est un plugin, et retirer une ligne désactive sa fonctionnalité. [Comment StewBeet s'intègre à beet](../how_it_fits/fr.md) explique comment `require` et `pipeline` fonctionnent ensemble, et chaque option est décrite dans [Configurer le build](../3_beet_config/fr.md).

## Étapes suivantes

- [Items et blocks](../items_and_blocks/fr.md) : ajouter des recipes et un block posable à un item.
- [Définir des items et des blocks](../1_definitions_setup/fr.md) : chaque champ qu'accepte un `Item` ou un `Block`, recipes comprises.
- Le [template Extensive](https://github.com/Stoupy51/StewBeet/tree/main/templates/extensive/src) est un projet complet à lire.

Bloqué ? Demandez sur [Discord](https://discord.gg/anxzu6rA9F) ou ouvrez une [issue GitHub](https://github.com/Stoupy51/StewBeet/issues).

