
# Configurer le build

Les options du fichier de configuration beet que StewBeet lit, et ce qu'il fait de chacune. Le fichier est lu au début de chaque build.

Si beet, bolt et mecha sont de nouveaux noms pour vous, [Comment StewBeet s'articule avec beet](../how_it_fits/fr.md) explique qui fait quoi.

Les exemples utilisent YAML (`beet.yml`). Chaque option fonctionne de la même façon dans `beet.yaml`, `beet.json` ou `pyproject.toml`. Le fichier se trouve à la racine du projet.

Des fichiers complets à lire en parallèle de cette page :

- [extensive/beet.yml](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/beet.yml), le template qui utilise toutes les fonctionnalités
- [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml), un pack publié
- [LifeSteal/beet.yml](https://github.com/Stoupy51/LifeSteal/blob/main/beet.yml), un pack publié

## Identité du projet

### `id`

La racine de namespace des functions, tags et clés de storage générés. Minuscules et underscores uniquement.

```yaml
id: "_your_namespace"
```

### `name`

Le nom lisible, affiché dans `pack.mcmeta`, le lore des items et les messages en jeu.

```yaml
name: "Extensive Template"
```

### `author`

Un ou plusieurs créateurs, affichés dans `pack.mcmeta`. Séparez plusieurs noms avec `", "`.

```yaml
author: "Stoupy51"
author: "Player1, Player2, Player3"  # Multiple authors
```

Les joueurs dont le nom en jeu correspond à un auteur reçoivent automatiquement le tag `convention.debug`, qui débloque les outils de développement.

### `version`

Version sémantique (`major.minor.patch`), utilisée pour les vérifications de dépendances et les chemins de functions versionnés.

```yaml
version: "3.0.0"
```

### `minecraft`

La version cible du jeu, qui décide des commandes et des formats de resource pack disponibles. Omettez-la pour cibler la dernière version.

```yaml
minecraft: "26.3"
```

## Dossiers

### `directory` et `output`

`directory` est la base des chemins relatifs. `output` est l'endroit où les packs compilés sont écrits.

```yaml
directory: "."
output: "build"
```

### `ignore`

Les fichiers et patterns que le watcher ignore, ce qui évite les boucles de rebuild et accélère `stewbeet watch`.

```yaml
ignore: ["build", "iso_renders", "manual_content.json", "definitions_debug.json", "external_definitions.json"]
```

## `require`

Les packages Python importés avant le build, ce qui rend leurs plugins disponibles pour le pipeline.

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.livereload"
    - "stewbeet.plugins.source_maps"
    - "bolt"
```

| Package | Rôle |
|---------|------|
| `stewbeet` | Le framework (requis) |
| `stewbeet.plugins.livereload` | Recharge le jeu après chaque build, voir [livereload](../plugins/livereload.fr.md) |
| `stewbeet.plugins.source_maps` | Enregistre quelle ligne de votre code a écrit chaque function, voir [source_maps](../plugins/source_maps.fr.md) |
| `bolt` | Syntaxe proche de Python dans les functions |

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

Les plugins qui s'exécutent une fois les packs chargés, dans l'ordre. Chacun travaille sur le résultat du précédent :

```yaml
pipeline:
    - "src.setup_definitions"                              # User setup code
    - "stewbeet.plugins.resource_pack.sounds"              # Process custom sounds
    - "stewbeet.plugins.resource_pack.item_models"         # Generate item models
    - "stewbeet.plugins.resource_pack.check_power_of_2"    # Validate texture dimensions
    - "stewbeet.plugins.custom_recipes"                    # Generate custom recipes
    - "stewbeet.plugins.custom_paintings"                  # Process custom paintings
    - "stewbeet.plugins.ingame_manual"                     # Generate in-game manual
    - "stewbeet.plugins.datapack.loading"                  # Setup datapack loading
    - "stewbeet.plugins.datapack.custom_blocks"            # Process custom blocks
    - "stewbeet.plugins.datapack.loot_tables"              # Generate loot tables
    - "stewbeet.plugins.datapack.sorters"                  # Setup item sorters
    - "stewbeet.plugins.compatibilities.simpledrawer"      # SimpleDrawer compatibility
    - "stewbeet.plugins.compatibilities.neo_enchant"       # NeoEnchant compatibility
    - "src.link"                                           # User linking code
    - "mecha"                                              # Mecha paired with Bolt
    - "stewbeet.plugins.finalyze.custom_blocks_ticking"    # Setup block ticking
    - "stewbeet.plugins.finalyze.basic_datapack_structure" # Create basic structure
    - "stewbeet.plugins.finalyze.dependencies"             # Handle dependencies
    - "stewbeet.plugins.finalyze.unload"                   # Write the unload functions
    - "stewbeet.plugins.finalyze.last_final"               # Final cleanup
    - "stewbeet.plugins.auto.scoreboard_constants"         # Initialize the #<number> constants
    - "stewbeet.plugins.auto.lang_file"                    # Auto-generate lang files
    - "stewbeet.plugins.auto.text_renders"                 # Turn "render" keys into item glyphs
    - "stewbeet.plugins.auto.headers"                      # Add file headers
    - "stewbeet.plugins.source_maps.emit"                  # Write the source maps
    - "stewbeet.plugins.check_unused_textures"             # Find unused textures
    - "stewbeet.plugins.archive"                           # Create ZIP archives
    - "stewbeet.plugins.merge_smithed_weld.datapack"       # Merge Smithed Weld libs into the datapack
    - "stewbeet.plugins.merge_smithed_weld.resource_pack"  # Merge Smithed Weld libs into the resource pack
    - "stewbeet.plugins.copy_to_destination"               # Copy to game folders
    - "stewbeet.plugins.compute_sha1"                      # Compute file hashes
```

Ajouter `.silent` au nom d'un plugin StewBeet, comme dans `stewbeet.plugins.datapack.loading.silent`, masque sa sortie console. Les templates le font pour les plugins qui affichent le plus.

L'ordre suit huit phases :

| Phase | Plugins | Ce qui se passe |
|-------|---------|-----------------|
| 1. Setup | `src.setup_definitions` | Votre code déclare les items, blocks et recipes |
| 2. Resource pack | `resource_pack.sounds`, `resource_pack.item_models`, `resource_pack.check_power_of_2` | Les models et les sons sont générés |
| 3. Contenu | `custom_recipes`, `custom_paintings`, `ingame_manual` | Les recipes, les paintings et le manual |
| 4. Cœur du datapack | `datapack.loading`, `datapack.custom_blocks`, `datapack.loot_tables`, `datapack.sorters`, `compatibilities.simpledrawer`, `compatibilities.neo_enchant` | Le chargement, les blocks, les loot tables, les sorters et les compatibilités |
| 5. Code utilisateur | `src.link` | Vos functions, qui peuvent utiliser tout ce qui précède |
| 6. Compilation | `mecha` | Bolt et mecha compilent chaque function |
| 7. Finalisation | `finalyze.custom_blocks_ticking`, `finalyze.basic_datapack_structure`, `finalyze.dependencies`, `finalyze.unload`, `finalyze.last_final` | Les functions tick, les vérifications de dépendances, les functions unload |
| 8. Packaging | `auto.scoreboard_constants`, `auto.lang_file`, `auto.text_renders`, `auto.headers`, `source_maps.emit`, `check_unused_textures`, `archive`, `merge_smithed_weld`, `copy_to_destination`, `compute_sha1` | Les constantes, le fichier lang, les archives, les bibliothèques, les copies, les hashes |

Gardez l'ordre des templates. Votre code va dans `setup_definitions` et `link`, `mecha` vient après `link`, et les plugins de finalisation lisent les functions qu'il a compilées, donc ils restent après lui.

## `meta`

### `mc_supports`

Les versions déclarées à Modrinth et Smithed à l'upload. `"infinite"` déclare la compatibilité future. Il fixe aussi les formats supportés écrits dans `pack.mcmeta`, et sa plus basse release est la version de Minecraft que demande la vérification au chargement.

```yaml
mc_supports: ["26.3", "infinite"]
```

### `model_resolver`

Configure le moteur de rendu qui dessine les images d'items. `use_cache` réutilise les textures dynamiques qu'il extrait, au lieu de les extraire de nouveau à chaque build.

```yaml
model_resolver:
    use_cache: true
```

### `mecha`

Comment les commandes sont analysées et formatées pendant la compilation.

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

`formatting: preserve` garde votre propre mise en forme dans la sortie.

Laissez `version` non défini. Mecha analyse alors avec l'arbre de commandes de votre version `minecraft`, et le build avertit quand `meta.mecha.version` est plus ancienne.

## `meta.stewbeet`

### Dossiers sources

Où StewBeet lit les textures, sons, records de jukebox et bibliothèques.

```yaml
stewbeet:
    textures_folder: "assets/textures"
    sounds:
        folder: "assets/sounds"
        exclude_patterns: ["some_sub_folder/*"]
    records_folder: "assets/records"
    libs_folder: "libs"
    libs_exclude_patterns: []
```

`sounds.exclude_patterns` et `libs_exclude_patterns` sont des patterns glob de fichiers à laisser de côté. Ceux de `libs_exclude_patterns` sont relatifs à `libs_folder`.

### `build_copy_destinations`

Les dossiers où les packs sont copiés après chaque build. Combiné à `stewbeet watch`, le jeu a toujours le dernier build.

```yaml
build_copy_destinations:
    datapack: ["D:/latest_snapshot/world/datapacks"]
    resource_pack: ["D:/minecraft/snapshot/resourcepacks"]
```

Une destination peut aussi être une URL `sftp://user@host/path`. Le mot de passe vient de l'URL ou de l'entrée `sftp` de `~/stewbeet/credentials.yml`.

### `source_lore` et `source_lore_color`

Une ligne ajoutée au lore de chaque item custom. `"auto"` est le nom du projet, dessiné avec la font générée `{id}:tooltip` et précédé de l'icône du projet quand un `pack.png` existe.

```yaml
source_lore: "auto" # TextComponents format
source_lore_color: "auto" # "auto" | any color | false
```

`source_lore_color` fixe la couleur de cette font. `"auto"` prend la couleur dominante de votre `pack.png`, n'importe quelle couleur Pillow la force (`"#55FFFF"`, `"gold"`, `[85, 255, 255]`), et `false` garde l'or fourni. Un `assets/tooltip.png` placé à côté de `pack.png` remplace entièrement l'atlas de caractères et n'est jamais recoloré.

Un source lore est un text component simple, donc il accepte aussi la clé `render` du plugin [`auto.text_renders`](../plugins/auto.text_renders.fr.md), pour afficher une image d'item à côté du nom du projet :

```yaml
source_lore: [{"text":"ICON"}, " ", {"text":"Extensive Template", "color":"white", "italic":false, "font":"_your_namespace:tooltip"}, " ", {"render":"steel_ingot", "height":10}]
```

### `iso_renders_path` et `text_renders`

Où vivent les PNG par item, et comment la clé `render` des text components est dessinée.

```yaml
iso_renders_path: "iso_renders"
text_renders:
    default_height: 16
    default_resolution: 0
    font: "renders"
    # allow_oversized: true   # unset asks once in the terminal, and remembers the answer
```

`iso_renders_path` contient un PNG par item, sous la forme `<folder>/<namespace>/<item>.png`. Les items du projet sont rendus depuis leur model, les items `minecraft:` sont téléchargés, et les items d'autres packs sont ceux que vous y placez vous-même. Il est partagé par [`ingame_manual`](../7_ingame_manual/fr.md) et [`auto.text_renders`](../plugins/auto.text_renders.fr.md), donc un item n'est rendu qu'une fois.

`default_height` est la hauteur à l'écran d'un glyphe en pixels, et `default_resolution` la hauteur à laquelle sa texture est stockée (`0` laisse chaque image intacte). Une image plus grande que les 256x256 qui tiennent dans un glyphe est découpée en grille de glyphes reliés par un espacement négatif, au prix d'une texture par tuile. Le premier build qui en rencontre une pose la question dans le terminal et retient la réponse dans `.beet_cache`. `allow_oversized` répond d'avance, et `false` réduit ces rendus à un seul glyphe.

### `load_dependencies`

Les datapacks vérifiés quand votre pack se charge. Un datapack absent ou obsolète affiche une erreur dans le chat avec un lien de téléchargement.

```yaml
load_dependencies:
    "energy":
        version: [1, 8, 0]
        name: "DatapackEnergy"
        url: "https://github.com/ICY105/DatapackEnergy"
```

Cela ne marche qu'avec les datapacks qui suivent la convention [LanternLoad](https://github.com/LanternMC/load). Ajouter `source` et un id télécharge aussi la bibliothèque, voir [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md#load_dependencies-personnalises).

### `items_storage`

Activé par défaut : la function load remplit le storage `<namespace>:items` avec chaque item du projet. Mettez `items_storage: false` pour l'ignorer.

### `manual`

Rendu, mise en page et interaction du manual en jeu généré.

```yaml
manual:
    debug_mode: false
    manual_overrides: "assets/manual_overrides"
    high_resolution: true
    cache_assets: true
    json_dump_path: "manual_content.json"
    name: ""
    max_items_per_row: 5
    max_rows_per_page: 5
    first_page_text: [{"text":"...", "color":"#505050"}]
    showcase_image: 3
    item_layout: "craft"
    item_box_gap: 4
    use_dialog: 1
```

| Option | Effet |
|--------|-------|
| `debug_mode` | `true` dessine une grille en surimpression pour déboguer la mise en page |
| `manual_overrides` | Dossier de fichiers qui remplacent par leur nom les assets par défaut du manual. Voir les [assets remplaçables](https://github.com/Stoupy51/StewBeet/tree/main/python_package/stewbeet/plugins/ingame_manual/assets) |
| `high_resolution` | Rend les images d'items en haute résolution |
| `cache_assets` | Garde les textures Minecraft et les rendus d'items qui existent déjà au lieu de les refaire |
| `json_dump_path` | Écrit les pages rendues dans ce fichier, pour le débogage |
| `name` | Titre du manual, moins de 32 caractères. Vide veut dire généré depuis le nom du projet |
| `max_items_per_row` | Items par ligne, jusqu'à 6 |
| `max_rows_per_page` | Lignes par page, jusqu'à 7. La grille par défaut est 5x5, donc 25 items par page |
| `first_page_text` | Texte d'accueil, sous forme de text components |
| `showcase_image` | `0` désactivé, `1` items du manual seulement, `2` tous les items custom, `3` les deux (recommandé) |
| `item_layout` | Ce que montre une page d'item : `"craft"`, `"item"` (l'item dans sa boîte) ou `"item+craft"` (la boîte à gauche de la recipe) |
| `item_box_gap` | Pixels entre la boîte et la recipe de `"item+craft"`, négatif pour dessiner la recipe sur la boîte |
| `use_dialog` | `1` dialog plus un item `manual` qui l'ouvre (recommandé), `2` dialog seul |

Les images de glyphes générées sont mises en cache dans le dossier `.beet_cache` de beet. Les rendus d'items vivent dans `iso_renders_path`, plus haut.

Exemple de texte d'accueil :

```yaml
first_page_text: [{"text":"The following manual will guide you through recipes and energy statistics about devices.", "color": "#505050"}]
```

## Configuration minimale

Un projet beet qui n'utilise que le plugin `auto.headers` :

```yaml
# Path to a folder for beet to output
output: "build"

# A list of importable plugin strings
require:
    - "bolt"

# Takes a nested pack config
data_pack:
    name: "datapack"
    load: ["src"]

pipeline:
    - "mecha"
    - "stewbeet.plugins.auto.headers"
```

## Pour continuer

- [Tous les plugins](../plugins/README.fr.md) : ce que fait chaque étape du pipeline.
- [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md) : déclarez des dépendances et téléchargez-les automatiquement.
- [Manual en jeu](../7_ingame_manual/fr.md) : les pages et hooks derrière les options `manual`.

Les questions vont sur la [communauté Discord](https://discord.gg/anxzu6rA9F).

