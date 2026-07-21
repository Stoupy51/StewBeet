
# ⚙️ Guide de Configuration Beet & StewBeet

## 📖 Définitions
- **Fichier de configuration Beet** : Fichier principal du projet (`beet.yml`, `beet.yaml`, `beet.json` ou `pyproject.toml`) lu au démarrage du build.
- **Pipeline** : Liste ordonnée de plugins exécutés par beet pour transformer et générer le contenu du projet.
- **Section meta** : Conteneur de paramètres personnalisés (`meta`) utilisé par StewBeet et les autres outils.

## 🧪 Exemples
📄 **Fichier d'exemple**: [extensive/beet.yml](../../templates/extensive/beet.yml) 🔗<br>
📄 **Exemple réel**: [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml) 🔗<br>
📄 **Exemple réel**: [LifeSteal/beet.yml](https://github.com/Stoupy51/LifeSteal/blob/main/beet.yml) 🔗<br>

## 🔗 Formats de Fichier de Configuration
- **Formats supportés**: `beet.yml`, `beet.yaml`, `beet.json`, ou `pyproject.toml`
- **📍 Emplacement**: Racine du projet
- **🔄 Intégration**: Contrôle l'ensemble du processus de build et du pipeline de plugins

## 📋 Aperçu
Le fichier de configuration est le cœur de votre projet StewBeet. Il définit tout, des métadonnées de base du projet aux pipelines de plugins complexes et aux paramètres personnalisés. Ce guide utilise le format YAML (`beet.yml`) pour les exemples, mais toutes les options fonctionnent également avec JSON ou pyproject.toml.

**Le fichier de configuration est lu au début de chaque build et détermine comment l'ensemble de votre projet est traité.**

## 🎯 Objectifs
- 🏷️ Définir l'identité du projet (nom, version, auteur)
- 📂 Configurer la structure des dossiers et la sortie du build
- 🔌 Gérer les dépendances et les plugins requis
- 📦 Configurer le chargement du datapack et du resource pack
- ⚙️ Contrôler le pipeline d'exécution des plugins
- 🎨 Personnaliser les fonctionnalités spécifiques à StewBeet
- 📚 Configurer la génération du manuel en jeu
- 🔄 Configurer la copie automatique des fichiers pour les tests

## 📚 Table des Matières

- [🎨 Configuration de Base du Projet](#-configuration-de-base-du-projet)
- [📂 Paramètres des Répertoires](#-paramètres-des-répertoires)
- [🔌 Dépendances](#-dépendances)
- [📦 Configuration des Packs](#-configuration-des-packs)
- [⚡ Pipeline](#-pipeline)
- [🎛️ Méta Configuration](#-méta-configuration)
  - [🎮 Support Minecraft](#-support-minecraft)
  - [🗄️ Model Resolver](#-model-resolver)
  - [🔧 Mecha](#-mecha)
  - [⚙️ Paramètres StewBeet](#-paramètres-stewbeet)
---

## 🎨 Configuration de Base du Projet

### 🆔 Identifiant du Projet
Définit la racine de namespace utilisée dans les fonctions, tags et clés de stockage générés.

```yaml
id: "_votre_namespace"
```
Utilisé pour les espaces de noms des fonctions, tags et stockage. Doit être en minuscules avec uniquement des underscores.

### 📛 Nom du Projet
Définit le nom lisible par les joueurs, affiché dans les métadonnées et les textes générés.

```yaml
name: "Extensive Template"
```
Affiché dans pack.mcmeta, lore des items et messages en jeu.

### 👤 Auteur
Définit un ou plusieurs auteurs pour l'attribution et les conventions liées au projet.

```yaml
author: "Stoupy51"
author: "Joueur1, Joueur2, Joueur3"  # Plusieurs auteurs
```
Affiché dans pack.mcmeta. Supporte plusieurs noms séparés par `", "`.<br>
**🎁 Fonctionnalité spéciale**: Les joueurs avec des noms en jeu correspondants reçoivent automatiquement le tag `convention.debug` pour les outils de développement.

### 🔢 Version
Définit la version de release utilisée pour le suivi et les vérifications de compatibilité.

```yaml
version: "3.0.0"
```
Versionnement sémantique (`majeur.mineur.correctif`) utilisé pour la validation des dépendances et les chemins de fonctions versionnés.

### 🎮 Version Minecraft
Définit la version principale ciblée pour la compatibilité des commandes et formats de données.

```yaml
minecraft: "1.21.11"
```
Détermine les commandes et ressources disponibles. Omettre pour utiliser la dernière version.

---

## 📂 Paramètres des Répertoires

### 📁 Répertoire de Base & Sortie
Définit la résolution des chemins relatifs et l'emplacement d'écriture des packs générés.

```yaml
directory: "."
output: "build"
```
Répertoire de base pour les chemins relatifs. Output définit où les packs générés sont sauvegardés.

### 🚫 Patterns Ignorés
Définit les fichiers/dossiers ignorés par la surveillance pour éviter les boucles de rebuild.

```yaml
ignore: ["build", "manual_cache", "definitions_debug.json"]
```
Fichiers/patterns ignorés par `beet watch` pour éviter les boucles de rebuild infinies et accélérer la surveillance.

---

## 🔌 Dépendances

```yaml
require:
    - "stewbeet"
    - "bolt"
```
Packages/modules Python requis pour votre projet. Les packages listés sont importés avant le traitement, rendant leurs plugins disponibles dans le pipeline.

Dépendances courantes:
- `stewbeet` - Framework StewBeet (requis)
- `bolt` - Syntaxe de fonction type Python
- `beet.contrib.vanilla` - Générateurs de données vanilla
- `mecha` - Préprocesseur de commandes (généralement auto-chargé)

---

## 📦 Configuration des Packs

### 📊 Data Pack
Définit les règles de chargement des sources de datapack sous `src/data/...`.

```yaml
data_pack:
    name: "datapack"
    load: ["src"]
```
Charge les fichiers `.mcfunction` et JSON depuis `src/data/votre_namespace/` dans le datapack.

### 🎨 Resource Pack
Définit les règles de chargement des assets client sous `src/assets/...`.

```yaml
resource_pack:
    name: "resource_pack"
    load: ["src"]
```
Charge les assets depuis `src/assets/` dans le resource pack.

---

## ⚡ Pipeline

Le pipeline définit l'ordre des plugins exécutés après le chargement des packs. Chaque plugin traite votre projet en séquence:

```yaml
pipeline:
    - "src.setup_definitions"                              # 🎨 Code utilisateur de setup
    - "stewbeet.plugins.resource_pack.sounds"              # 🔊 Traite les sons personnalisés
    - "stewbeet.plugins.resource_pack.item_models"         # 🎁 Génère les modèles d'items
    - "stewbeet.plugins.resource_pack.check_power_of_2"    # ✅ Valide les dimensions des textures
    - "stewbeet.plugins.custom_recipes"                    # 🍳 Génère les recettes personnalisées
    - "stewbeet.plugins.custom_paintings"                  # 🖼️ Traite les peintures personnalisées
    - "stewbeet.plugins.ingame_manual"                     # 📚 Génère le manuel en jeu
    - "stewbeet.plugins.datapack.loading"                  # 🚀 Configure le chargement du datapack
    - "stewbeet.plugins.datapack.custom_blocks"            # 🧱 Traite les blocs personnalisés
    - "stewbeet.plugins.datapack.loot_tables"              # 🎁 Génère les loot tables
    - "stewbeet.plugins.datapack.sorters"                  # 📋 Configure les trieurs d'items
    - "stewbeet.plugins.compatibilities.simpledrawer"      # 🗄️ Compatibilité SimpleDrawer
    - "stewbeet.plugins.compatibilities.neo_enchant"       # ✨ Compatibilité NeoEnchant
    - "src.link"                                           # 🔗 Code utilisateur de liaison
    - "mecha"                                              # 🔧 Mecha avec Bolt
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"    # ⏰ Configure le ticking des blocs
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # 🏗️ Crée la structure de base
    - "stewbeet.plugins.finalyze.dependencies"             # 📦 Gère les dépendances
    - "stewbeet.plugins.finalyze.check_unused_textures"    # 🔍 Trouve les textures inutilisées
    - "stewbeet.plugins.finalyze.last_final"               # 🎯 Nettoyage final
    - "stewbeet.plugins.auto.lang_file"                    # 🌐 Génère auto les fichiers de langue
    - "stewbeet.plugins.auto.headers"                      # 📄 Ajoute les en-têtes de fichiers
    - "stewbeet.plugins.archive"                           # 🗜️ Crée les archives ZIP
    - "stewbeet.plugins.merge_smithed_weld"                # 🔀 Fusionne les libs Smithed Weld
    - "stewbeet.plugins.copy_to_destination"               # 📁 Copie vers les dossiers de jeu
    - "stewbeet.plugins.compute_sha1"                      # #️⃣ Calcule les hashs de fichiers
```

### 📋 Étapes du Pipeline Expliquées

**🎨 Phase 1: Setup** - Définir les items, blocs, recettes pour les plugins StewBeet
```yaml
- "src.setup_definitions"
```

**🎨 Phase 2: Resource Pack** - Générer les modèles et sons
```yaml
- "stewbeet.plugins.resource_pack.sounds"
- "stewbeet.plugins.resource_pack.item_models"
- "stewbeet.plugins.resource_pack.check_power_of_2"
```

**🍳 Phase 3: Contenu** - Recettes, peintures, manuel
```yaml
- "stewbeet.plugins.custom_recipes"
- "stewbeet.plugins.custom_paintings"
- "stewbeet.plugins.ingame_manual"
```

**⚙️ Phase 4: Cœur du Datapack** - Chargement, blocs, loot tables
```yaml
- "stewbeet.plugins.datapack.loading"
- "stewbeet.plugins.datapack.custom_blocks"
- "stewbeet.plugins.datapack.loot_tables"
```

**🔗 Phase 5: Code Utilisateur** - Vos fonctions personnalisées
```yaml
- "src.link"
```

**🔧 Phase 6: Compilation** - Traitement Mecha/Bolt
```yaml
- "mecha"
```

**🎯 Phase 7: Finalisation** - Fonctions clock, dépendances
```yaml
- "stewbeet.plugins.finalyze.custom_blocks_ticking"
- "stewbeet.plugins.finalyze.basic_datapack_structure"
- "stewbeet.plugins.finalyze.dependencies"
```

**📦 Phase 8: Empaquetage** - ZIPs, copie, hashing
```yaml
- "stewbeet.plugins.auto.lang_file"
- "stewbeet.plugins.archive"
- "stewbeet.plugins.copy_to_destination"
```

### 💡 Conseils Pipeline

**✅ À FAIRE:**
- Garder l'ordre recommandé
- Placer le code utilisateur aux points stratégiques

**❌ À NE PAS FAIRE:**
- Mettre `mecha` avant votre code
- Sauter les plugins de finalisation

---

## 🎛️ Méta Configuration

### 🎮 Support Minecraft
Déclare les versions supportées pour les métadonnées de distribution et le signalement de compatibilité.

```yaml
mc_supports: ["1.21.11", "26.1-snapshot-1", "infinite"]
```
Déclare la compatibilité de version pour les uploads de plateformes (Modrinth, Smithed). Utiliser `"infinite"` pour la compatibilité future.<br>
(Influence les formats supportés dans `pack.mcmeta`)

### 🗄️ Model Resolver
Configure le cache des modèles afin d'accélérer les rebuilds.

```yaml
model_resolver:
    use_cache: true
```
Met en cache les modèles d'items résolus (80-90% plus rapide). Stocké dans `.beet_cache/model_resolver/`.

### 🔧 Mecha
Configure l'analyse et le formatage des commandes pendant la compilation.

```yaml
mecha:
    multiline: true
    formatting: preserve
```
**`multiline: true`** - Active la syntaxe de commande multi-lignes:
```mcfunction
execute
    as @a[scores={health=1..10}]
    at @s
    run function my_namespace:fn
```

**`formatting: preserve`** - Garde votre style de formatage original.

---

### ⚙️ Paramètres StewBeet

#### 📁 Chemins des Répertoires
Définit les dossiers sources StewBeet pour les textures, sons, disques et bibliothèques.

```yaml
stewbeet:
    textures_folder: "assets/textures"
    sounds_folder: "assets/sounds"
    records_folder: "assets/records"
    libs_folder: "libs"
```

#### 🚀 Destinations de Copie du Build
Définit les cibles de synchronisation post-build pour les sorties datapack et resource pack.

```yaml
build_copy_destinations:
    datapack: ["D:/latest_snapshot/world/datapacks"]
    resource_pack: ["D:/minecraft/snapshot/resourcepacks"]
```
Copie automatiquement les packs après le build. Parfait avec `beet watch` pour les tests en direct.

#### 🏷️ Lore d'Item Personnalisé
Définit le marquage de lore par défaut appliqué aux items personnalisés générés.

```yaml
source_lore: "auto" # Format TextComponents
```
Ajouté au lore des items personnalisés, `"auto"` utilise par défaut l'icône du projet + le nom.

#### 📦 Dépendances de Chargement
Définit les contrôles de dépendances à l'exécution pour signaler les datapacks manquants ou obsolètes.

```yaml
load_dependencies:
    "energy":
        version: [1, 8, 0]
        name: "DatapackEnergy"
        url: "https://github.com/ICY105/DatapackEnergy"
```
**Vérification des dépendances à l'exécution** - Valide les dépendances au chargement du datapack, affiche des messages d'erreur avec liens de téléchargement si manquant/obsolète.

**⚠️ Prérequis:** Fonctionne uniquement avec les datapacks suivant la convention [LanternLoad](https://github.com/LanternMC/load).

---

#### 📚 Configuration du Manuel en Jeu

Définit le rendu, le cache, la mise en page et le mode d'interaction du manuel généré.

```yaml
manual:
    debug_mode: false
    manual_overrides: "assets/manual_overrides"
    high_resolution: true
    cache_path: "manual_cache"
    cache_assets: true
    cache_pages: false
    name: ""
    max_items_per_row: 5
    max_rows_per_page: 5
    first_page_text: [{"text":"...", "color":"#505050"}]
    showcase_image: 3
    use_dialog: 1
```

**Documentation interactive auto-générée** montrant les items personnalisés, recettes et navigation.

**🐛 Debug & Développement:**
- `debug_mode: true` - Affiche une grille overlay pour le debug de layout

**🎨 Personnalisation:**
- `manual_overrides: "assets/manual_overrides"` - Remplace les assets par défaut du manuel en plaçant des fichiers avec les mêmes noms. Voir les [assets disponibles](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/plugins/ingame_manual/assets) pour la liste complète des fichiers remplaçables
- `name: ""` - Titre du manuel (vide = auto-généré depuis le nom du projet)
- `first_page_text: [...]` - Message de bienvenue utilisant les components de texte

**💾 Cache:**
- `cache_path: "manual_cache"` - Où stocker les fichiers de cache
- `cache_assets: true` - Met en cache les textures/modèles MC (90% plus rapide)
- `cache_pages: false` - Met en cache toutes les pages (recommandé à false pour les petits projets)

**📐 Layout:**
- `max_items_per_row: 5` - Items par ligne (1-6)
- `max_rows_per_page: 5` - Lignes par page (1-7)
- Grille par défaut: 5×5 = 25 items/page

**📸 Images Vitrine:**
- `0` - Désactivé
- `1` - Items du manuel uniquement
- `2` - Tous les items personnalisés
- `3` - Les deux (recommandé)

**💬 Mode d'Affichage:**
- `0` - Livre uniquement (legacy, pas de redémarrage serveur nécessaire)
- `1` - Livre ouvrant un dialog (recommandé, nécessite redémarrage serveur)
- `2` - Dialog uniquement (nécessite redémarrage serveur)

**Exemple de texte de bienvenue:**
```yaml
first_page_text: [{"text":"Le manuel suivant vous guidera à travers les recettes et statistiques énergétiques des appareils.", "color": "#505050"}]
```

---

## 💡 Conseils et Bonnes Pratiques

1. 🆔 **Namespace unique** - Utilisez un `id` unique pour éviter les conflits
2. 🔢 **Versionnement sémantique** - Suivez le format `majeur.mineur.correctif`
3. 🔀 **Ordre du pipeline** - Placez le code utilisateur à `setup_definitions` et `link`
4. ⚡ **Activer le cache** - `cache_assets` et `use_cache` pour des builds plus rapides
5. 🧪 **Tests automatiques** - Configurez `build_copy_destinations`
6. 📦 **Documenter les dépendances** - Toujours spécifier dans `load_dependencies`

---

## 📝 Exemple: Configuration Minimale

```yaml
# Chemin du dossier de sortie de beet
output: "build"

# Liste des chaînes de plugins importables
require:
    - "bolt"

# Configuration du pack
data_pack:
    name: "datapack"
    load: ["src"]

pipeline:
    - "mecha"
    - "stewbeet.plugins.auto.headers"
```

---

**Besoin d'aide?** Rejoignez la [communauté Discord](https://discord.gg/anxzu6rA9F)!

