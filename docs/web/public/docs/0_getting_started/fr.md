# Tutoriel : votre premier datapack

Dans ce tutoriel, vous créez un projet StewBeet, vous le compilez, vous le chargez dans Minecraft, puis vous ajoutez un custom item et tout un palier de rubis avec un custom block fonctionnel. Comptez une vingtaine de minutes.

Il vous faut trois choses :

- **uv**, [le gestionnaire de paquets Python d'Astral](https://docs.astral.sh/uv/). Il installe Python pour vous, c'est donc la seule chose de cette liste à installer à la main.
- **Un éditeur de texte.** [VS Code](https://code.visualstudio.com/) avec le pack d'extensions Python et l'[extension StewBeet](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) vous donne la complétion dans vos commandes.
- **Minecraft Java Edition**, pour tester le résultat.

Vous n'installez pas Python vous-même. StewBeet demande 3.14, chaque template l'indique dans son `pyproject.toml`, et uv télécharge une version compatible à la première compilation.

## 1. Installer uv

Lancez la ligne correspondant à votre système :

```powershell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS et Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Les autres façons de l'installer (winget, Homebrew, pipx, un binaire autonome) sont listées sur la [page d'installation de uv](https://docs.astral.sh/uv/getting-started/installation/).

Fermez et rouvrez votre terminal, puis vérifiez que uv est dans votre PATH :

```bash
uv --version
```

> Vous avez déjà Python 3.14 et préférez pip ? `pip install stewbeet` fonctionne aussi, et chaque `uv run stewbeet ...` ci-dessous devient simplement `stewbeet ...`. Le reste du tutoriel ne change pas.

## 2. Créer le projet

StewBeet fournit trois templates. Ce tutoriel utilise **Basic** : chaque plugin est configuré et commenté, et il n'y a aucun contenu d'exemple à supprimer.

| Template | Pour | Ce que vous obtenez |
|----------|------|---------------------|
| Minimal | Apprendre beet seul | Un seul plugin StewBeet, rien d'autre |
| **Basic** | **La plupart des projets** | Tous les plugins, commentés, sans contenu d'exemple |
| Extensive | Lire de vrais exemples | Toutes les fonctionnalités, avec items, minerais et manuel fonctionnels |

1. Créez un dossier pour le projet, par exemple `C:/MyDatapacks/AwesomeOres/`.
2. Ouvrez-le dans VS Code (clic droit sur le dossier puis "Ouvrir avec Code", ou Fichier, Ouvrir le dossier).
3. Ouvrez un terminal avec Terminal, Nouveau terminal. Il démarre dans le dossier du projet.
4. Lancez :

   ```bash
   uvx stewbeet init basic
   ```

`uvx` télécharge StewBeet, l'exécute une fois et jette la copie, rien n'est donc installé globalement. Le dossier ressemble maintenant à ceci :

```bash
AwesomeOres/
├── .beet_cache/              # Cache de compilation (généré)
├── build/                    # Dossier de sortie (généré)
├── .venv/                    # Environnement du projet (créé par uv à la première compilation)
├── assets/                   # Vos textures et sons
├── src/                      # Votre code source
│   ├── data/                 # Fonctions et données du datapack
│   │   └── basic_template/   # Votre namespace (à renommer)
│   ├── definitions/          # Modules de définitions
│   │   ├── additions.py      # Custom items et custom blocks
│   │   └── ores.py           # Paliers de minerais et d'équipements
│   ├── link.py               # Code exécuté après les définitions
│   └── setup_definitions.py  # Point d'entrée des définitions
├── .gitignore
├── pyproject.toml            # Dépendances Python (StewBeet et ce que vous ajoutez)
├── beet.yml                  # Fichier de configuration principal
└── definitions_debug.json    # Ce que vos définitions ont produit, pour le débogage
```

### Le rôle de `pyproject.toml`

Il rend le projet autonome :

```toml
[project]
name = "template"
version = "0.0.1"
requires-python = ">=3.14"
dependencies = [
	"smithed",
	"stewbeet>=3.9.0",
]

[tool.uv]
package = false

[tool.uv.sources]
smithed = { git = "https://github.com/Stoupy51/smithed-python.git" }
```

`requires-python` indique à uv quel interpréteur récupérer.

La section `[tool.uv.sources]` est temporaire : la version de `smithed` publiée sur PyPI mélange des modèles Pydantic V1 et V2, ce qui fait échouer la fusion Smithed Weld sur les Python récents. Supprimez cette section et la dépendance `smithed` une fois le problème corrigé en amont.

Pour utiliser une autre bibliothèque dans vos définitions (`requests`, `pillow`), lancez `uv add requests`. Elle atterrit dans ce fichier, dans votre `.venv`, et dans le fichier de lock que vos collaborateurs réutilisent.

## 3. Nommer votre pack

Ouvrez `beet.yml`. Ces champs identifient le pack et sont réutilisés dans `pack.mcmeta`, le lore des items, le nom des archives et le manuel :

```yaml
# Identifiant du projet - DOIT correspondre à votre namespace dans src/data/
id: "awesome_ores"

# Nom du projet pour l'affichage
name: "Awesome Ores"

# Votre nom (apparaît dans pack.mcmeta et le lore des items)
author: "VotreNom"

# Version utilisant le versioning sémantique
version: "1.0.0"

# Brève description
description: "Mon premier datapack StewBeet avec des custom ores !"
```

| Champ | Règle | Exemple |
|-------|-------|---------|
| `id` | Minuscules et underscores, sans espaces. Doit correspondre au dossier de `src/data/` | `awesome_ores` |
| `name` | Texte libre | `"Awesome Ores & Gems"` |
| `version` | [Versioning sémantique](https://semver.org/), majeur.mineur.patch | `1.0.0` |

Renommez `src/data/basic_template/` en `src/data/awesome_ores/` pour qu'il corresponde à `id`.

## 4. Compiler

Dans le terminal, lancez `uv run stewbeet` (ou `uv run stewbeet build`, qui revient au même).

La première exécution fait la mise en place : uv lit `pyproject.toml`, télécharge Python 3.14 s'il manque, crée `.venv/` et installe StewBeet. Comptez une minute. Les exécutions suivantes compilent immédiatement.

La sortie ressemble à ceci. Les avertissements sont normaux sur un projet vide :

```bash
Building project...

[WARNING 19:05:57] Error during generate_custom_records(): (FileNotFoundError) [WinError 3] The system cannot find the path specified: 'assets/records' 
[DEBUG 19:05:58] Mem.definitions exported to 'definitions_debug.json' 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.sounds': 0.070ms (69900ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.item_models': 0.246ms (245700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.resource_pack.check_power_of_2': 0.250ms (249700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.custom_recipes': 0.021ms (20700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.custom_paintings': 0.007ms (7400ns) 
[WARNING 19:05:58] Database is empty, skipping manual generation. 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.ingame_manual': 0.075ms (74600ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.loading': 0.150ms (150300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.custom_blocks': 0.108ms (108200ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.loot_tables': 0.187ms (187300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.datapack.sorters': 0.031ms (31300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compatibilities.simpledrawer': 0.003ms (2700ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compatibilities.neo_enchant': 0.003ms (2800ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking': 0.045ms (45100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.basic_datapack_structure': 0.062ms (61600ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.dependencies': 0.875ms (874900ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.check_unused_textures': 0.125ms (124800ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.finalyze.last_final': 0.154ms (154500ns) 
Generating lang file: 100%|████████████████████████████████████████████████| 21/21 [4481.78it/s, 00:00<00:00]
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.auto.lang_file': 73.613ms (73613100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.auto.headers': 0.561ms (561000ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.archive': 23.592ms (23592200ns) 
[WARNING 19:05:58] No datapacks or libs to merge for build\AwesomeOres_datapack_with_libs.zip. Skipping weld. 
[WARNING 19:05:58] No resource packs or libs to merge for build\AwesomeOres_resource_pack_with_libs.zip. Skipping weld. 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.merge_smithed_weld': 0.593ms (593100ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.copy_to_destination': 0.007ms (7300ns) 
[PROGRESS 19:05:58] Execution time of 'stewbeet.plugins.compute_sha1': 25.546ms (25546400ns) 
[DEBUG 19:05:58] Total execution time: 0.56934s 
Done!
```

`build/` contient maintenant :

| Chemin | Ce que c'est |
|--------|--------------|
| `datapack/` | Le datapack généré, décompressé |
| `resource_pack/` | Le resource pack généré, décompressé |
| `AwesomeOres_datapack.zip` | Le datapack, prêt à déposer dans un monde |
| `AwesomeOres_resource_pack.zip` | Le resource pack, prêt à activer |
| `sha1_hashes.json` | Les hashes des archives, pour les administrateurs de serveur |

## 5. Le charger dans Minecraft

Le plus rapide est de laisser chaque compilation copier les packs dans votre jeu. Ajoutez ceci à `beet.yml`, avec vos propres chemins :

```yaml
meta:
  stewbeet:
    build_copy_destinations:
      datapack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/saves/NomDuMonde/datapacks"]
      resource_pack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/resourcepacks"]
```

Désormais, `uv run stewbeet` copie les deux packs après chaque compilation.

Pour les copier à la main :

1. Copiez `build/AwesomeOres_datapack.zip` dans le dossier datapacks du monde :
   - Windows : `%appdata%\.minecraft\saves\[NomDuMonde]\datapacks\`
   - macOS : `~/Library/Application Support/minecraft/saves/[NomDuMonde]/datapacks/`
2. Copiez `build/AwesomeOres_resource_pack.zip` dans le dossier des resource packs :
   - Windows : `%appdata%\.minecraft\resourcepacks\`
   - macOS : `~/Library/Application Support/minecraft/resourcepacks/`

Puis, en jeu :

1. Lancez `/reload`.
2. Activez le resource pack dans Options, Packs de ressources.
3. Si vous avez gardé la fonction d'exemple dans `src/data/awesome_ores/function/`, lancez-la avec `/function awesome_ores:path/to/a/random/function/i/guess`.

## 6. Ajouter un custom item

1. Créez `assets/textures/` et placez-y un PNG 16x16, par exemple [`ruby.png`](./ruby.png), pour obtenir `assets/textures/ruby.png`.
2. Ouvrez `src/definitions/additions.py` et déclarez l'item. L'`id` correspond au nom de la texture, c'est comme ça que StewBeet la trouve :

```python
# Imports
from stewbeet import *


# Point d'entrée principal
def main():

    # Ajouter des items aux définitions
    Mem.definitions["ruby"] = Item(
        id="ruby",
        components={
            "lore": [{"text":"Une précieuse pierre précieuse rouge","color":"gray","italic":False}]
        }
    )

    # Voir extensive_template/src/definitions/additions.py pour des exemples
    pass
```

3. Lancez `uv run stewbeet`. La première compilation qui dessine les item models prend un peu plus de temps.
4. En jeu, lancez `/reload`, puis `/loot give @s loot awesome_ores:i/ruby` ou `/function awesome_ores:_give_all`.

À partir de cette seule déclaration, StewBeet a écrit l'item model et sa référence, ajouté la texture au resource pack, construit les components de l'item et ajouté une page au manuel.

## 7. Ajouter tout un palier de minerai

Placez ces textures dans `assets/textures/` :

| Fichier | Utilisé pour |
|---------|--------------|
| [`ruby_ore.png`](./ruby_ore.png) | Le bloc de minerai |
| [`ruby_sword.png`](./ruby_sword.png) | L'épée |
| [`ruby_chestplate.png`](./ruby_chestplate.png) | L'item plastron |
| [`ruby_layer_1.png`](./ruby_layer_1.png) | L'armure portée, couche supérieure (c'est ainsi que Minecraft dessine les custom armors) |
| [`ruby_layer_2.png`](./ruby_layer_2.png) | L'armure portée, couche inférieure |

Ouvrez `src/definitions/ores.py` et décrivez le matériau. Tout ce que StewBeet trouve dans le dossier des textures avec le préfixe `ruby` est enregistré à partir de cette entrée :

```python
# Imports
from stewbeet import *


# Point d'entrée principal
def main():

    # Configuration pour tout générer à propos d'un matériau
    ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
        "ruby": EquipmentsConfig(
            # Ce rubis est équivalent au diamant,
            equivalent_to = DefaultOre.DIAMOND,

            # Mais, a plus de durabilité (1.2 fois plus)
            pickaxe_durability = 1.2 * VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]["durability"],

            # Et, fait 1 dégât de plus par coup (main), et a 0.5 armure de plus, et mine 20% plus vite (pioche)
            attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
        ),
    }

    # Générer les minerais dans les définitions (ajoute tout ce qui est trouvé (dans le dossier textures) lié aux matériaux donnés, aux définitions)
    generate_everything_about_these_materials(ORES_CONFIGS)
    return
```

Compilez, `/reload`, puis lancez `/loot give @s loot awesome_ores:i/ruby_ore` et posez le bloc. C'est un custom block complet : StewBeet a écrit son model, sa logique de pose et de cassage, ses drops et ses conditions de minage, son comportement avec Fortune et Silk Touch, et l'a branché sur la bibliothèque Smithed Custom Blocks.

## 8. Ouvrir le manuel en jeu

Le manuel utilise le système de dialogues de Minecraft, qui ne prend en compte les nouveaux dialogues qu'au redémarrage du serveur : quittez et rejoignez le monde d'abord. Appuyez ensuite sur G (le raccourci d'action rapide), ou lancez `/loot give @s loot awesome_ores:i/manual` si vous êtes parti du template Extensive.

Le manuel liste vos items avec leurs recipes, dessinées à partir des définitions que vous venez d'écrire.

## Ce que contient `beet.yml`

Vous avez parcouru toute la boucle. Deux autres parties de `beet.yml` sont utiles à connaître avant d'aller plus loin.

Les dossiers que StewBeet lit, et où il copie le résultat :

```yaml
meta:
  stewbeet:
    # Répertoire contenant toutes les textures du projet
    textures_folder: "assets/textures"

    # Répertoire contenant tous les custom sounds
    sounds_folder: "assets/sounds"

    # Répertoire contenant tous les jukebox records
    records_folder: "assets/records"

    # Répertoire contenant les bibliothèques qui seront copiées vers la destination de build, et fusionnées avec Smithed Weld si activé.
    libs_folder: "libs"

    # Optionnel : motifs glob (relatifs à libs_folder) des archives de bibliothèque à exclure du build
    libs_exclude_patterns: []

    # Liste optionnelle de chemins de destination où les fichiers générés seront copiés
    build_copy_destinations:
      datapack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/saves/NomDuMonde/datapacks"]
      resource_pack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/resourcepacks"]
```

Le pipeline, qui liste chaque étape de la compilation dans l'ordre. Retirez une ligne pour désactiver une fonctionnalité :

```yaml
# Plugins à exécuter en premier
require:
    - "stewbeet"  # Équivalent à "stewbeet.plugins.initialize"
    - "bolt"      # Initialiser bolt

# Une liste de chaînes représentant des "plugins".
# - Ces plugins s'exécuteront après le chargement du pack (tous les contenus src/data et src/assets sont chargés en premier)
pipeline:
    - "src.setup_definitions"                           # Votre code utilisateur pour définir items/blocs
    - "stewbeet.plugins.resource_pack.sounds"           # Générer les fichiers sons
    - "stewbeet.plugins.resource_pack.item_models"      # Générer les item models
    - "stewbeet.plugins.resource_pack.check_power_of_2" # Vérifier les dimensions des textures
    - "stewbeet.plugins.custom_recipes"                 # Générer les custom recipes
    - "stewbeet.plugins.custom_paintings"               # Générer les custom paintings
    - "stewbeet.plugins.ingame_manual"                  # Générer le manuel en jeu
    - "stewbeet.plugins.datapack.loading"               # Configurer les fonctions load/tick
    - "stewbeet.plugins.datapack.custom_blocks"         # Configurer les mécaniques de blocs
    - "stewbeet.plugins.datapack.loot_tables"           # Générer les loot tables
    - "stewbeet.plugins.datapack.sorters"               # Configurer les item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"   # Compatibilité SimpleDrawer
    - "stewbeet.plugins.compatibilities.neo_enchant"    # Compatibilité NeoEnchant
    - "src.link"                                        # Code utilisateur pour lier les fonctionnalités
    - "mecha"                                           # Compilation Bolt/Mecha
    - "stewbeet.plugins.finalyze.custom_blocks_ticking" # Finaliser le ticking des blocs
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # Finalisation de la structure
    - "stewbeet.plugins.finalyze.dependencies"          # Vérification des dépendances
    - "stewbeet.plugins.finalyze.check_unused_textures" # Trouver les textures inutilisées
    - "stewbeet.plugins.finalyze.last_final"            # Nettoyage final
    - "stewbeet.plugins.auto.lang_file"                 # Générer les fichiers de langue
    - "stewbeet.plugins.auto.headers"                   # Générer les en-têtes de fonctions
    - "stewbeet.plugins.archive"                        # Créer les fichiers zip
    - "stewbeet.plugins.merge_smithed_weld"             # Fusionner avec Smithed Weld
    - "stewbeet.plugins.copy_to_destination"            # Copier vers les chemins configurés
    - "stewbeet.plugins.compute_sha1"                   # Calculer les hashes de fichiers
```

Chaque option est décrite dans [Configurer le build](../3_beet_config/fr.md).

## Étapes suivantes

- [Définir des items et des blocs](../1_definitions_setup/fr.md) : chaque champ qu'acceptent un `Item` ou un `Block`, recipes comprises.
- [Écrire des fonctions et des fichiers](../2_writing_to_files/fr.md) : ajouter vos propres commandes au pack.
- [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md) : Smithed, Bookshelf et les vérifications de version que StewBeet écrit pour vous.
- Le [template Extensive](https://github.com/Stoupy51/StewBeet/tree/main/templates/extensive/src) est un projet complet à lire.

Bloqué ? Demandez sur [Discord](https://discord.gg/anxzu6rA9F) ou ouvrez une [issue GitHub](https://github.com/Stoupy51/StewBeet/issues).
