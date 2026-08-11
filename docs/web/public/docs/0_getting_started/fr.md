# Tutoriel : votre premier datapack


Bienvenue sur **StewBeet** ! 🎉 Ce guide complet vous accompagnera du statut de débutant complet à la création de votre premier datapack Minecraft utilisant le framework StewBeet. Que vous soyez nouveau dans le développement de datapacks ou que vous veniez des datapacks vanilla, ce guide contient tout ce dont vous avez besoin pour démarrer.

## Ce que vous allez apprendre

À la fin de ce guide, vous serez capable de :
- ✅ Installer uv et configurer StewBeet sur votre ordinateur
- 🎯 Choisir le bon template pour votre projet
- ⚙️ Configurer votre premier projet StewBeet
- 🔨 Compiler et tester votre datapack
- 📝 Ajouter vos premiers items et blocs personnalisés
- 🎮 Charger votre datapack dans Minecraft

## Qu'est-ce que StewBeet ?

StewBeet est un puissant **framework d'automatisation** pour créer des datapacks Minecraft. Considérez-le comme un assistant intelligent qui :

- 🤖 **Automatise les tâches répétitives** - Plus besoin de créer manuellement les models, textures ou fichiers de fonctions
- 📦 **Génère les resource packs** - Crée automatiquement tous les assets visuels dont votre datapack a besoin
- 📚 **Intègre les bibliothèques** - Fonctionne parfaitement avec les bibliothèques de datapacks populaires comme Smithed
- 📖 **Crée la documentation** - Génère les manuels en jeu et les en-têtes de fonctions
- 🔧 **Gère la complexité** - Gère automatiquement les dépendances, le versioning et la compatibilité

Au lieu d'écrire des centaines de fichiers manuellement, vous définissez ce que vous voulez et StewBeet crée tout pour vous !

## Prérequis

Avant de commencer, assurez-vous d'avoir :

### Logiciels requis
- **uv** 📦 - [Le gestionnaire de paquets Python d'Astral](https://docs.astral.sh/uv/). Il installe Python à votre place, c'est donc la seule chose de cette liste que vous avez à mettre en place.
- **Éditeur de texte ou IDE** 📝 - Nous recommandons [VS Code](https://code.visualstudio.com/) avec le pack d'extensions Python et l'extension [StewBeet](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet)
- **Minecraft Java Edition** 🎮 - Pour tester vos datapacks

Vous n'avez **pas** besoin d'installer Python vous-même. StewBeet demande la 3.14, chaque template le déclare dans son `pyproject.toml`, et uv télécharge une version compatible à la première compilation.

## Étape 1 : Installer uv

Ouvrez votre terminal/invite de commande et exécutez la ligne correspondant à votre système :

```powershell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS et Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Les autres méthodes d'installation (winget, Homebrew, pipx, binaire autonome) sont listées sur la [page d'installation de uv](https://docs.astral.sh/uv/getting-started/installation/).

### Vérifier l'installation
Fermez puis rouvrez votre terminal, et vérifiez que uv est bien dans votre PATH :
```bash
uv --version
```

> 💡 Vous avez déjà Python 3.14 et préférez pip ? `pip install stewbeet` fonctionne toujours, et chaque `uv run stewbeet ...` ci-dessous devient simplement `stewbeet ...`. Le reste du guide est identique.

## Étape 2 : Choisir votre template

StewBeet propose trois templates pour bien démarrer.<br>
**Nous recommandons fortement le Template Basic** pour les débutants :

### Comparaison des templates

| Template | Pour qui | Fonctionnalités | Complexité |
|----------|----------|----------|------------|
| **🔹 Minimal** | Apprendre les bases de beet | Fonctionnalités beet de base uniquement | ⭐ Débutant |
| **⭐ Basic** | **La plupart des utilisateurs** | Toutes les fonctionnalités StewBeet, configuration propre | ⭐⭐ Intermédiaire |
| **🌟 Extensive** | Utilisateurs avancés | Toutes les fonctionnalités + exemples | ⭐⭐⭐ Avancé |

### Pourquoi choisir le Template Basic ?

Le **Template Basic** est parfait car il :
- ✅ Inclut **toutes les fonctionnalités StewBeet** mais avec une configuration propre et vide
- 📝 Contient des **commentaires détaillés** expliquant chaque option
- 🎯 Fournit une **base solide** sans exemples écrasants
- 🔧 Est **facilement personnalisable** pour vos besoins spécifiques

## Étape 3 : Créer votre projet

### Initialiser un nouveau projet

1. **Créez** un nouveau dossier pour votre projet (par ex., `C:/MyDatapacks/AwesomeOres/`)
2. **Ouvrez le dossier dans VS Code** :
   - Clic droit sur le dossier -> "Ouvrir avec Code"
   - Ou lancez VS Code et utilisez Fichier -> Ouvrir un dossier
3. **Ouvrez un terminal dans VS Code** :
   - Utilisez Terminal -> Nouveau terminal depuis le menu
   - Le terminal s'ouvrira automatiquement dans votre dossier de projet
4. **Exécutez la commande init** :
   ```bash
   uvx stewbeet init basic
   ```

`uvx` télécharge StewBeet, le lance une fois puis jette la copie : vous n'installez donc jamais rien globalement. La commande crée tous les fichiers et dossiers nécessaires pour votre projet !

La structure de votre projet ressemblera à ceci :
```bash
AwesomeOres/
├── 📁 .beet_cache/              # Cache de compilation (auto-généré)
├── 📁 build/                    # Dossier de sortie (auto-généré)
├── 📁 .venv/                    # Environnement du projet (créé par uv à la première compilation)
├── 📁 assets/                   # Dossier assets (important pour textures et sons)
├── 📁 src/                      # Votre code source
│   ├── 📁 data/                 # Fonctions et données du datapack
│   │   └── 📁 basic_template/  # Votre namespace (renommez-le !)
│   ├── 📁 definitions/          # Modules de définitions
│   │   ├── 📄 additions.py      # Définitions personnalisées supplémentaires
│   │   └── 📄 ores.py           # Configurations d'équipements de minerais
│   ├── 📄 link.py               # Code utilisateur pour lier les fonctionnalités
│   └── 📄 setup_definitions.py  # Configuration principale des définitions
├── 📁 assets/                   # Vos textures et sons
├── 📄 .gitignore                # Fichier d'ignore Git
├── 📄 pyproject.toml            # Dépendances Python (StewBeet et ce que vous ajoutez)
├── 📄 beet.yml                  # Fichier de configuration principal
└── 📄 definitions_debug.json    # Fichier de débogage des définitions
```

### À propos de `pyproject.toml`

Chaque template en fournit un, et c'est lui qui rend le projet autonome :

```toml
[project]
name = "template"
version = "0.0.1"
requires-python = ">=3.14"
dependencies = [
	"smithed",
	"stewbeet>=3.6.1",
]

[tool.uv]
package = false

[tool.uv.sources]
smithed = { git = "https://github.com/Stoupy51/smithed-python.git" }
```

C'est `requires-python` qui indique à uv quel interpréteur récupérer, Python n'a donc jamais à être installé à la main.

La section `[tool.uv.sources]` est temporaire : la version de `smithed` publiée sur PyPI mélange des modèles Pydantic V1 et V2, ce qui fait échouer la fusion Smithed Weld sur les Python récents. Supprimez cette section et la dépendance `smithed` une fois le problème corrigé en amont.

Besoin d'une autre bibliothèque dans vos définitions (`requests`, `pillow`, n'importe laquelle) ? Lancez `uv add requests` : elle atterrit dans ce fichier, dans votre `.venv`, et dans le fichier de lock que vos collaborateurs réutilisent.

## Étape 4 : Configurer votre projet

Ouvrez `beet.yml` dans votre éditeur de texte. C'est votre fichier de configuration principal. Personnalisons-le :

### Paramètres de base du projet

Ce sont les champs de métadonnées minimum qui identifient votre pack et sont réutilisés dans les fichiers générés, l'archivage et l'affichage en jeu.

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
description: "Mon premier datapack StewBeet avec des minerais personnalisés !"
```

### Notes importantes :
- **ID** : Utilisez des minuscules, underscores uniquement, pas d'espaces (ex., `awesome_ores`)
- **Name** : Peut avoir des espaces et caractères spéciaux (ex., `"Awesome Ores & Gems"`)
- **Version** : Suivez le [versioning sémantique](https://semver.org/) (majeur.mineur.patch)

## Étape 5 : Compiler votre premier projet

Testons que tout fonctionne :

### Ouvrez le terminal dans le dossier du projet et exécutez votre première compilation

🖥️ Ouvrez le terminal dans le dossier du projet et exécutez `uv run stewbeet` ou `uv run stewbeet build`

Cette première exécution fait tout le travail de mise en place : uv lit `pyproject.toml`, télécharge Python 3.14 s'il manque, crée `.venv/` et installe StewBeet. Comptez une minute ; les exécutions suivantes compilent immédiatement.

Vous devriez voir une sortie comme :
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

### Vérifiez les résultats

Regardez dans votre dossier `build/`. Vous devriez voir :
- 📁 `datapack/` - Votre datapack généré
- 📁 `resource_pack/` - Votre resource pack généré
- 📦 `AwesomeOres_datapack.zip` - Datapack prêt à l'emploi
- 📦 `AwesomeOres_resource_pack.zip` - Resource pack prêt à l'emploi
- 📄 `sha1_hashes.json` - Peut être utile pour les administrateurs de serveur

**Félicitations !** 🎉 Vous avez compilé avec succès votre premier projet StewBeet !

## Étape 6 : Tester dans Minecraft

### Installer le datapack

#### Option 1 : Copie automatique (Recommandé)

Configurez StewBeet pour copier automatiquement les fichiers vers vos dossiers Minecraft en éditant `beet.yml` :

```yaml
meta:
  stewbeet:
    build_copy_destinations:
      datapack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/saves/NomDuMonde/datapacks"]
      resource_pack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/resourcepacks"]
```

Remplacez les chemins par vos vrais dossiers Minecraft. Maintenant quand vous exécutez `uv run stewbeet`, les fichiers sont automatiquement copiés !

#### Option 2 : Copie manuelle

1. **Ouvrez Minecraft** et créez un nouveau monde (ou ouvrez-en un existant)
2. **Copiez** `build/AwesomeOres_datapack.zip` dans le dossier datapacks de votre monde :
   - Windows : `%appdata%\.minecraft\saves\[NomDuMonde]\datapacks\`
   - Mac : `~/Library/Application Support/minecraft/saves/[NomDuMonde]/datapacks/`
3. **Copiez** `build/AwesomeOres_resource_pack.zip` dans votre dossier resource packs :
   - Windows : `%appdata%\.minecraft\resourcepacks\`
   - Mac : `~/Library/Application Support/minecraft/resourcepacks/`

### Activer dans le jeu

1. **Dans Minecraft**, tapez `/reload` dans le chat
2. Allez dans **Options** -> **Resource Packs** et activez votre resource pack
3. Testez la fonctionnalité de base avec `/function awesome_ores:chemin/vers/une/fonction/au/hasard` (si vous n'avez pas supprimé la fonction d'exemple dans `src/data/awesome_ores/function/`)

## Étape 7 : Ajouter votre premier item personnalisé

Ajoutons maintenant un item personnalisé pour voir la puissance de StewBeet en action !

### Ajouter une texture

1. Créez la structure de dossiers : `assets/textures/`
2. Ajoutez un fichier de texture PNG 16x16, par exemple : [`ruby.png`](./ruby.png)
3. Votre structure devrait être : `assets/textures/ruby.png`

### Définir l'item

Ouvrez `src/definitions/additions.py` et ajoutez la définition pour votre nouvel item :

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

### Compiler et tester

1. Exécutez `uv run stewbeet` dans votre terminal et attendez qu'il termine (le premier rendu des item models peut prendre un peu plus de temps)
2. Rechargez votre monde avec `/reload`
3. Obtenez votre item avec `/loot give @s loot awesome_ores:i/ruby` ou `/function awesome_ores:_give_all`

**Incroyable !** 🎉 StewBeet a automatiquement :
- ✅ Créé l'item model et la référence
- ✅ Ajouté au resource pack
- ✅ Créé les components d'item appropriés
- ✅ Ajouté au manuel (si activé)

## Étape 8 : Ajouter votre premier bloc personnalisé

Créons un bloc personnalisé :

### Ajouter les textures de bloc

Ajoutez ces textures à `assets/textures/` :
- [`ruby_ore.png`](./ruby_ore.png) - La texture principale
- [`ruby_sword.png`](./ruby_sword.png) - Une texture d'épée
- [`ruby_chestplate.png`](./ruby_chestplate.png) - Une texture de plastron de rubis
- [`ruby_layer_1.png`](./ruby_layer_1.png) - Une texture de couche pour la couche supérieure (c'est ainsi que Minecraft gère les armures personnalisées)
- [`ruby_layer_2.png`](./ruby_layer_2.png) - Une texture de couche pour la couche inférieure

### Configurer le bloc

Pour simplifier, nous utiliserons la section `ORES_CONFIGS` dans `src/definitions/ores.py` :

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

### Compiler et tester

1. Exécutez `uv run stewbeet`, attendez qu'il termine
2. Rechargez dans Minecraft
3. Obtenez votre bloc avec `/loot give @s awesome_ores:i/ruby_ore`
4. Placez-le dans le monde - c'est un bloc personnalisé entièrement fonctionnel !

StewBeet a automatiquement :
- ✅ Créé les block models avec les faces appropriées
- ✅ Configuré les mécaniques de placement et de cassage
- ✅ Ajouté les propriétés de minage (nécessite une pioche, drops, etc.)
- ✅ Intégré avec la bibliothèque Smithed Custom Blocks
- ✅ Ajouté le support de fortune et silk touch

## Étape 9 : Consultez votre manuel en jeu

L'une des fonctionnalités les plus cool de StewBeet est la génération automatique de manuel.<br>
D'abord, assurez-vous de redémarrer votre monde car le manuel en jeu nécessite un redémarrage du serveur (système de dialogues Minecraft), puis :

1. Dans Minecraft, appuyez sur "G" (raccourci d'action rapide) ou exécutez `/loot give @s loot awesome_ores:i/manual` si vous avez commencé avec le Template Extensive
2. Ouvrez le livre pour voir votre **manuel généré automatiquement**
3. Il inclut tous vos items, recipes et informations de craft !

## Étape 10 : Comprendre la configuration

Explorons quelques options de configuration clés dans `beet.yml` :

### Dossiers importants

Ces chemins définissent où StewBeet lit les sources et où il copie les sorties générées pour les tests.

```yaml
meta:
  stewbeet:
    # Répertoire contenant toutes les textures du projet
    textures_folder: "assets/textures"

    # Répertoire contenant tous les sons personnalisés
    sounds_folder: "assets/sounds"

    # Répertoire contenant tous les jukebox records
    records_folder: "assets/records"

    # Répertoire contenant les bibliothèques qui seront copiées vers la destination de build, et fusionnées avec Smithed Weld si activé.
    libs_folder: "libs"

    # Liste optionnelle de chemins de destination où les fichiers générés seront copiés
    build_copy_destinations:
      datapack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/saves/NomDuMonde/datapacks"]
      resource_pack: ["C:/Users/VotreNom/AppData/Roaming/.minecraft/resourcepacks"]
```

### Pipeline des plugins

La section `pipeline` contrôle ce que fait StewBeet :

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
    - "stewbeet.plugins.custom_recipes"                 # Générer les recipes personnalisées
    - "stewbeet.plugins.custom_paintings"               # Générer les paintings personnalisées
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

## Prochaines étapes

Félicitations ! Vous avez maintenant un projet StewBeet fonctionnel. Voici ce qu'il faut explorer ensuite :

Pour des guides plus approfondis et des fonctionnalités avancées, consultez la **📖 [Documentation](https://stewbeet.paralya.fr/documentation)** avec des guides complets et des références.

### Essayez ces fonctionnalités

1. **Ajoutez plus d'items** avec différentes textures et propriétés
2. **Créez des sets d'armure** en utilisant la configuration d'équipement
3. **Ajoutez des recipes personnalisées** dans les définitions de recipes
4. **Configurez la copie automatique** vers vos dossiers Minecraft
5. **Explorez le template extensive** pour des exemples avancés

### Configuration avancée

Une fois à l'aise, explorez ces fonctionnalités puissantes :

- **🔄 Auto-génération** de minerais, outils et sets d'armure
- **📦 Intégration de bibliothèques** avec Smithed, Bookshelf, et plus
- **🎨 Overrides de models personnalisés** pour items spéciaux
- **📝 Génération de fonctions** avec en-têtes appropriés
- **🌐 Internationalisation** avec fichiers de langue automatiques

## Obtenir de l'aide

Besoin d'assistance ? Voici vos meilleures ressources :

- **📖 [Documentation](https://stewbeet.paralya.fr/documentation)** - Guides complets et références
- **💬 [Serveur Discord](https://discord.gg/anxzu6rA9F)** - Support communautaire actif
- **🐛 [GitHub Issues](https://github.com/Stoupy51/StewBeet/issues)** - Rapports de bugs et demandes de fonctionnalités

## Conclusion

Vous avez réussi à :
- ✅ Installer uv et StewBeet
- ✅ Configurer votre premier projet
- ✅ Créer des items et blocs personnalisés
- ✅ Compiler et tester dans Minecraft
- ✅ Explorer les options de configuration clés

StewBeet est incroyablement puissant, et vous n'avez fait qu'effleurer la surface ! Le framework vous fera économiser des centaines d'heures de travail manuel tout en créant des datapacks de qualité professionnelle.

**Bon développement de datapacks !** 🚀

---

*💡 **Astuce Pro** : Commencez petit, expérimentez souvent, et n'hésitez pas à demander de l'aide dans la communauté Discord. Les développeurs et utilisateurs de StewBeet sont très amicaux et serviables !*
