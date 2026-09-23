# Configurer le build

Chaque option du fichier de configuration beet, et ce que StewBeet en fait. Le fichier est lu au début de chaque build et décide de la façon dont tout le projet est traité.

Les exemples utilisent YAML (`beet.yml`). Chaque option fonctionne de la même façon dans `beet.yaml`, `beet.json` ou `pyproject.toml`. Le fichier se trouve à la racine du projet.

Des fichiers complets à lire en parallèle de cette page :

- [extensive/beet.yml](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/beet.yml), le template qui utilise toutes les fonctionnalités
- [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml), un pack publié
- [LifeSteal/beet.yml](https://github.com/Stoupy51/LifeSteal/blob/main/beet.yml), un pack publié

## Identité du projet

### `id`

La racine du namespace des fonctions, tags et clés de storage générés. Minuscules et underscores uniquement.

```yaml
id: "_your_namespace"
```

### `name`

Le nom lisible, affiché dans `pack.mcmeta`, le lore des items et les messages en jeu.

```yaml
name: "Extensive Template"
```

### `author`

Un ou plusieurs créateurs, affichés dans `pack.mcmeta`. Séparez plusieurs noms par `", "`.

```yaml
author: "Stoupy51"
author: "Joueur1, Joueur2, Joueur3"  # Plusieurs auteurs
```

Les joueurs dont le pseudo correspond à un auteur reçoivent automatiquement le tag `convention.debug`, qui débloque les outils de développement.

### `version`

Version sémantique (`majeur.mineur.patch`), utilisée pour la vérification des dépendances et les chemins de fonctions versionnés.

```yaml
version: "3.0.0"
```

### `minecraft`

La version de jeu ciblée, qui décide des commandes et formats de ressources disponibles. Omettez-la pour cibler la dernière version.

```yaml
minecraft: "1.21.11"
```

## Dossiers

### `directory` et `output`

`directory` est la base des chemins relatifs. `output` est l'endroit où les packs compilés sont écrits.

```yaml
directory: "."
output: "build"
```

### `ignore`

Les fichiers et motifs ignorés par `beet watch`, ce qui évite les boucles de recompilation et accélère la surveillance.

```yaml
ignore: ["build", "manual_cache", "definitions_debug.json"]
```

## `require`

Les packages Python importés avant le build, ce qui rend leurs plugins disponibles dans le pipeline.

```yaml
require:
    - "stewbeet"
    - "bolt"
```

| Package | Rôle |
|---------|------|
| `stewbeet` | Le framework (obligatoire) |
| `bolt` | Une syntaxe proche de Python dans les fonctions |
| `beet.contrib.vanilla` | Générateurs de données vanilla |
| `mecha` | Compilateur de commandes (généralement chargé automatiquement) |

## Packs

### `data_pack`

Charge les fichiers `.mcfunction` et JSON de `src/data/your_namespace/` dans le datapack.

```yaml
data_pack:
    name: "datapack"
    load: ["src"]
```

### `resource_pack`

Charge les assets de `src/assets/` dans le resource pack.

```yaml
resource_pack:
    name: "resource_pack"
    load: ["src"]
```

## `pipeline`

Les plugins exécutés après le chargement des packs, dans l'ordre. Chacun travaille sur le résultat du précédent :

```yaml
pipeline:
    - "src.setup_definitions"                              # Code utilisateur de setup
    - "stewbeet.plugins.resource_pack.sounds"              # Traite les custom sounds
    - "stewbeet.plugins.resource_pack.item_models"         # Génère les item models
    - "stewbeet.plugins.resource_pack.check_power_of_2"    # Valide les dimensions des textures
    - "stewbeet.plugins.custom_recipes"                    # Génère les custom recipes
    - "stewbeet.plugins.custom_paintings"                  # Traite les custom paintings
    - "stewbeet.plugins.ingame_manual"                     # Génère le manuel en jeu
    - "stewbeet.plugins.datapack.loading"                  # Configure le chargement du datapack
    - "stewbeet.plugins.datapack.custom_blocks"            # Traite les custom blocks
    - "stewbeet.plugins.datapack.loot_tables"              # Génère les loot tables
    - "stewbeet.plugins.datapack.sorters"                  # Configure les item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"      # Compatibilité SimpleDrawer
    - "stewbeet.plugins.compatibilities.neo_enchant"       # Compatibilité NeoEnchant
    - "src.link"                                           # Code utilisateur de liaison
    - "mecha"                                              # Mecha avec Bolt
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"    # Configure le ticking des blocs
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # Crée la structure de base
    - "stewbeet.plugins.finalyze.dependencies"             # Gère les dépendances
    - "stewbeet.plugins.finalyze.check_unused_textures"    # Trouve les textures inutilisées
    - "stewbeet.plugins.finalyze.last_final"               # Nettoyage final
    - "stewbeet.plugins.auto.lang_file"                    # Génère auto les fichiers de langue
    - "stewbeet.plugins.auto.text_renders"                 # Transforme les clés "render" en glyphes
    - "stewbeet.plugins.auto.headers"                      # Ajoute les en-têtes de fichiers
    - "stewbeet.plugins.archive"                           # Crée les archives ZIP
    - "stewbeet.plugins.merge_smithed_weld.datapack"       # Fusionne les libs Smithed Weld dans le datapack
    - "stewbeet.plugins.merge_smithed_weld.resource_pack"  # Fusionne les libs Smithed Weld dans le resource pack
    - "stewbeet.plugins.copy_to_destination"               # Copie vers les dossiers de jeu
    - "stewbeet.plugins.compute_sha1"                      # Calcule les hashs de fichiers
```

L'ordre suit huit phases :

| Phase | Plugins | Ce qui se passe |
|-------|---------|-----------------|
| 1. Setup | `src.setup_definitions` | Votre code déclare items, blocks et recipes |
| 2. Resource pack | `resource_pack.sounds`, `resource_pack.item_models`, `resource_pack.check_power_of_2` | Models et sounds sont générés |
| 3. Contenu | `custom_recipes`, `custom_paintings`, `ingame_manual` | Recipes, paintings et manuel |
| 4. Cœur du datapack | `datapack.loading`, `datapack.custom_blocks`, `datapack.loot_tables` | Chargement, custom blocks, loot tables |
| 5. Code utilisateur | `src.link` | Vos fonctions, qui peuvent utiliser tout ce qui précède |
| 6. Compilation | `mecha` | Bolt et mecha compilent chaque fonction |
| 7. Finalisation | `finalyze.custom_blocks_ticking`, `finalyze.basic_datapack_structure`, `finalyze.dependencies` | Fonctions d'horloge et vérification des dépendances |
| 8. Empaquetage | `auto.lang_file`, `auto.text_renders`, `archive`, `copy_to_destination` | Fichier lang, archives, copies, hashs |

Gardez l'ordre recommandé. Votre code va dans `setup_definitions` et `link`, `mecha` vient après, et les plugins de finalisation ne sont pas optionnels : ils écrivent les fonctions d'horloge et les vérifications de dépendances dont le reste dépend.

## `meta`

### `mc_supports`

Les versions déclarées à Modrinth et Smithed à la publication. `"infinite"` déclare une compatibilité future. Définit aussi les formats supportés écrits dans `pack.mcmeta`.

```yaml
mc_supports: ["1.21.11", "26.1-snapshot-1", "infinite"]
```

### `model_resolver`

Met en cache les item models résolus dans `.beet_cache/model_resolver/`, ce qui rend les recompilations 80 à 90 % plus rapides.

```yaml
model_resolver:
    use_cache: true
```

### `mecha`

La façon dont les commandes sont analysées et formatées à la compilation.

```yaml
mecha:
    multiline: true
    formatting: preserve
```

`multiline: true` accepte les commandes réparties sur plusieurs lignes :

```mcfunction
execute
    as @a[scores={health=1..10}]
    at @s
    run function my_namespace:fn
```

`formatting: preserve` conserve votre propre mise en forme dans la sortie.

## `meta.stewbeet`

### Dossiers sources

Où StewBeet lit les textures, les sounds, les jukebox records et les bibliothèques.

```yaml
stewbeet:
    textures_folder: "assets/textures"
    sounds_folder: "assets/sounds"
    records_folder: "assets/records"
    libs_folder: "libs"
    libs_exclude_patterns: []
```

### `build_copy_destinations`

Les dossiers où les packs sont copiés après chaque build. Avec `beet watch`, le jeu a toujours le dernier build.

```yaml
build_copy_destinations:
    datapack: ["D:/latest_snapshot/world/datapacks"]
    resource_pack: ["D:/minecraft/snapshot/resourcepacks"]
```

### `source_lore` et `source_lore_color`

Une ligne ajoutée au lore de chaque custom item. `"auto"` correspond à l'icône et au nom du projet, dessinés avec la font `{id}:tooltip` générée.

```yaml
source_lore: "auto" # Format TextComponents
source_lore_color: "auto" # "auto" | une couleur | false
```

`source_lore_color` définit la couleur de cette font. `"auto"` prend la couleur dominante de votre `pack.png`, toute couleur Pillow la force (`"#55FFFF"`, `"gold"`, `[85, 255, 255]`), et `false` garde l'or fourni. Un `assets/tooltip.png` placé à côté de `pack.png` remplace entièrement l'atlas de caractères et n'est jamais recoloré.

Un source lore est un simple text component, il accepte donc aussi la clé `render` du plugin [`auto.text_renders`](../plugins/auto.text_renders.md), pour afficher l'image d'un item à côté du nom du projet :

```yaml
source_lore: [{"text":"ICON"}, " ", {"text":"Mon Pack", "color":"white", "italic":false, "font":"mon_pack:tooltip"}, " ", {"render":"steel_ingot", "height":10}]
```

### `iso_renders_path` et `text_renders`

Où vivent les PNG de chaque item, et comment la clé `render` des text components est dessinée.

```yaml
iso_renders_path: "iso_renders"
text_renders:
    default_height: 16
    font: "renders"
    # allow_oversized: true   # sans valeur, la question est posée une fois dans le terminal
```

`iso_renders_path` contient un PNG par item, sous la forme `<dossier>/<namespace>/<item>.png`. Les items du projet sont rendus depuis leur model, les items `minecraft:` sont téléchargés, et les items d'autres packs sont ceux que vous y déposez vous-même. Il est partagé par [`ingame_manual`](../7_ingame_manual/fr.md) et [`auto.text_renders`](../plugins/auto.text_renders.md), un item n'est donc rendu qu'une fois.

Une image plus grande que les 256x256 qui tiennent dans un glyphe est découpée en une grille de glyphes recollés avec un espacement négatif, au prix d'une texture par tuile. Le premier build qui en rencontre une pose la question dans le terminal et retient la réponse dans `.beet_cache`. `allow_oversized` y répond à l'avance, et `false` réduit plutôt ces rendus à un seul glyphe.

> **Obsolète** : `manual.cache_path` est remplacé par `iso_renders_path`. Les projets qui le définissent encore continuent de fonctionner (les rendus sont lus depuis `<cache_path>/items`), et tout le reste de ce que le manuel met en cache vit dans le dossier `.beet_cache` de beet.

### `load_dependencies`

Les datapacks vérifiés au chargement de votre pack. S'il en manque un, ou s'il est trop ancien, une erreur s'affiche dans le chat avec un lien de téléchargement.

```yaml
load_dependencies:
    "energy":
        version: [1, 8, 0]
        name: "DatapackEnergy"
        url: "https://github.com/ICY105/DatapackEnergy"
```

Cela ne fonctionne qu'avec les datapacks qui suivent la convention [LanternLoad](https://github.com/LanternMC/load).

### `manual`

Rendu, cache, mise en page et interaction du manuel en jeu généré.

```yaml
manual:
    debug_mode: false
    manual_overrides: "assets/manual_overrides"
    high_resolution: true
    cache_assets: true
    cache_pages: false
    name: ""
    max_items_per_row: 5
    max_rows_per_page: 5
    first_page_text: [{"text":"...", "color":"#505050"}]
    showcase_image: 3
    use_dialog: 1
```

| Option | Effet |
|--------|-------|
| `debug_mode` | `true` dessine une grille pour déboguer la mise en page |
| `manual_overrides` | Dossier de fichiers qui remplacent les assets du manuel par leur nom. Voir les [assets remplaçables](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/plugins/ingame_manual/assets) |
| `high_resolution` | Rend les images d'items en haute résolution |
| `cache_assets` | Met en cache les textures et models Minecraft (builds environ 90 % plus rapides) |
| `cache_pages` | Met en cache toutes les pages. Laissez `false` sur les petits projets |
| `name` | Titre du manuel. Vide signifie généré depuis le nom du projet |
| `max_items_per_row` | Items par ligne, de 1 à 6 |
| `max_rows_per_page` | Lignes par page, de 1 à 7. La grille par défaut est 5x5, soit 25 items par page |
| `first_page_text` | Texte d'accueil, en text components |
| `showcase_image` | `0` désactivé, `1` items du manuel seulement, `2` tous les custom items, `3` les deux (recommandé) |
| `use_dialog` | `0` livre seul (pas de redémarrage serveur), `1` livre qui ouvre un dialogue (recommandé, demande un redémarrage serveur), `2` dialogue seul (demande un redémarrage serveur) |

Les images de glyphes générées sont mises en cache dans le dossier `.beet_cache` de beet. Les rendus d'items vivent dans `iso_renders_path`, plus haut.

Exemple de texte d'accueil :

```yaml
first_page_text: [{"text":"Le manuel suivant vous guidera à travers les recipes et statistiques énergétiques des appareils.", "color": "#505050"}]
```

## Configuration minimale

Un projet beet qui n'utilise que le plugin `auto.headers` :

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

## Glossaire

| Terme | Signification |
|-------|---------------|
| **Fichier de configuration beet** | La configuration du projet (`beet.yml`, `beet.yaml`, `beet.json` ou `pyproject.toml`) chargée au début d'un build |
| **Pipeline** | La liste ordonnée des plugins qui transforment et empaquettent le projet |
| **Section meta** | Le conteneur `meta` des réglages de plugins, utilisé par StewBeet et les outils associés |

## Étapes suivantes

- [Tous les plugins](../plugins/README.md) : ce que fait chaque étape du pipeline.
- [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md) : déclarer et télécharger automatiquement les dépendances.
- [Publier automatiquement](../6_continuous_delivery/fr.md) : publier le pack que le pipeline construit.

Les questions se posent sur la [communauté Discord](https://discord.gg/anxzu6rA9F).
