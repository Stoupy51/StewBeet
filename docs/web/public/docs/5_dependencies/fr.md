# Utiliser des bibliothèques de datapack

Le système de dépendances de StewBeet a deux couches : les **bibliothèques officielles** auto-détectées depuis les fonctions (sans config), et les **`load_dependencies` personnalisées** déclarées dans `beet.yml`. Les deux sont téléchargées au build et génèrent des vérifications de version au runtime avec des messages d'erreur cliquables.

**Référence de configuration** : [extensive/beet.yml](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/beet.yml) <br>  
**Exemple réel** : [SimplEnergy/beet.yml](https://github.com/Stoupy51/SimplEnergy/blob/main/beet.yml) <br>  
**Code source** : [stewbeet/plugins/finalyze/dependencies/__init__.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/finalyze/dependencies/__init__.py) <br>  
**Requis** : `stewbeet.plugins.finalyze.dependencies` dans le pipeline  
**Requis** : `stewbeet.plugins.datapack.loading` doit s'exécuter avant  
**Position** : Doit être placé **après** que toutes les fonctions utilisateur aient été écrites (les scanne pour détecter les bibliothèques)

- Détecter et télécharger automatiquement les bibliothèques officielles: aucune configuration requise
- Déclarer des dépendances personnalisées dans `beet.yml` avec `load_dependencies`
- Générer des vérifications de version au runtime et de compatibilité Minecraft
- Fournir des messages d'erreur en jeu cliquables quand des dépendances sont manquantes

## Déclarer une Dépendance: Partir d'un Exemple Réel

[SimplEnergy](https://github.com/Stoupy51/SimplEnergy) déclare une bibliothèque externe dans son `beet.yml` :

```yaml
meta:
  stewbeet:
    load_dependencies:
      energy:                                           # namespace de la dépendance (utilisé pour les vérifications de scoreboard au runtime)
        name: "DatapackEnergy"                         # nom affiché dans les messages d'erreur
        url: "https://github.com/ICY105/DatapackEnergy" # lien cliquable si la bibliothèque est manquante
        source: "smithed"                              # méthode de téléchargement
        smithed_id: "energy"                           # ID du pack Smithed
```

Au build, StewBeet interroge l'API Smithed pour la dernière version d'`energy` compatible avec la version Minecraft configurée, télécharge le zip et le fusionne dans la sortie. Au runtime, il vérifie que les scores `#energy.major/minor/patch load.status` respectent la version requise.

### Référence des Champs

| Champ | Requis | Description |
|-------|--------|-------------|
| `name` | ✅ | Nom affiché dans les messages d'erreur au runtime |
| `url` | ✅ | Lien cliquable affiché quand la dépendance est manquante |
| `source` | ✅ | Méthode de téléchargement : `"smithed"`, `"modrinth"`, ou `"static"` |
| `smithed_id` | Smithed only | ID du pack Smithed utilisé pour interroger l'API |
| `has_resource_pack` | Smithed only | Télécharger également le resource pack (défaut : `false`) |
| `modrinth_slug` | Modrinth only | Slug du projet Modrinth |
| `static_urls` | Static only | Associe des clés `"((mc_ver), (dep_ver))"` à des URLs de téléchargement |
| `version` | Static only | Résolu automatiquement depuis `static_urls` au moment du build |

### Autres Source Types

En dehors de `"smithed"`, deux autres source types sont disponibles :

```yaml
load_dependencies:
  # Modrinth: dernière release pour la version MC courante auto-récupérée
  "itemio":
    name: "ItemIO"
    url: "https://github.com/edayot/ItemIO"
    source: "modrinth"
    modrinth_slug: "itemio"

  # Static: URL zip figée, meilleure clé de version MC sélectionnée
  "common_signals":
    version: [0, 2, 0]
    name: "Common Signals"
    url: "https://github.com/Stoupy51/CommonSignals"
    source: "static"
    static_urls:
      "((1, 21, 7), (0, 2, 0))": "https://github.com/Stoupy51/CommonSignals/releases/download/v0.2.0/CommonSignals_datapack.zip"
```

---

## Bibliothèques Officielles (Auto-détectées)

Pour les bibliothèques bien connues, **aucune entrée `load_dependencies` n'est nécessaire**: StewBeet les détecte en scannant les fonctions et les télécharge automatiquement.

- **Modules Bookshelf** (`bs.*`) : détectés quand un appel de tag `#bs.X:...` apparaît dans n'importe quelle fonction.
- **Autres bibliothèques** : détectées quand leur namespace apparaît dans n'importe quelle fonction.

**Smithed**: `smithed.custom_block`, `smithed.crafter`, `smithed.actionbar`, `realistic_explosion`<br>
**Modrinth**: `itemio`, `common_signals`, `furnace_nbt_recipes`, `smart_ore_generation`<br>
**Bookshelf** (tous les modules `bs.*` (`bs.math`, `bs.block`, `bs.raycast`, ...))voir [Bookshelf releases](https://github.com/mcbookshelf/bookshelf/releases)

> `smart_ore_generation` câble aussi automatiquement vos fonctions `calls/smart_ore_generation/generate_ores`, `denied_dimensions` et `post_generation` vers les tags `smart_ore_generation:v1/signals/` correspondants.

---

## Comportement au Runtime

Au chargement du monde, les fonctions générées s'exécutent dans cet ordre :

1. Lantern Load déclenche le tag `#dep:load` de chaque dépendance afin que les bibliothèques publient leurs scores de version dans `load.status`.
2. **`check_dependencies`**: positionne le flag `#dependency_error ns.data` si un score de version est trop ancien.
3. **`valid_dependencies`**: attend une entité joueur, lit `DataVersion` pour vérifier la version Minecraft (par rapport au minimum de `mc_supports`), puis envoie des `tellraw @a` avec des liens d'erreur cliquables en cas d'échec. N'appelle `confirm_load` que quand toutes les vérifications passent.

**Messages d'erreur en jeu quand des dépendances sont manquantes :**<br>
<img src="../plugins/img/finalyze.dependencies.ingame_errors.jpg">

**Fonction `check_dependencies` générée :**<br>
<img src="../plugins/img/finalyze.dependencies.check_function.jpg">

---

## Fichiers Générés

| Fichier | Type | Description |
|---------|------|-------------|
| Tag `minecraft:load` | Tag | Point d'entrée: déclenche `#load:_private/load` |
| Tag `load:load` | Tag | Pointe vers `#ns:load` |
| Tag `ns:load` | Tag | Appelle `[#ns:enumerate, #ns:resolve]` |
| Tag `ns:enumerate` | Tag | Préfixé avec `#ns:dependencies` |
| Tag `ns:dependencies` | Tag | Liste `#dep:load` pour chaque dépendance |
| `load:_private/init` | Function | Réinitialise le scoreboard `load.status` |
| `ns:vX.Y.Z/load/secondary` | Function | Enregistre le scoreboard `ns.data`, appelle check/valid |
| `ns:vX.Y.Z/load/check_dependencies` | Function | Positionne `#dependency_error` via des vérifications de version |
| `ns:vX.Y.Z/load/valid_dependencies` | Function | Attend un joueur, vérifie `DataVersion`, affiche les erreurs |
| `ns:vX.Y.Z/load/confirm_load` | Function | Appelée uniquement quand toutes les vérifications passent |
| `ns:vX.Y.Z/load/tick_verification` | Function | Route la fonction tick uniquement quand la bonne version est chargée |

## Glossaire

| Terme | Signification |
|-------|---------------|
| **`load_dependencies`** | Un dictionnaire dans `beet.yml` où déclarer les bibliothèques externes à télécharger automatiquement et vérifier en version au runtime. |
| **Source type** | La méthode de résolution et téléchargement d'une bibliothèque: `"smithed"` (API Smithed), `"modrinth"` (API Modrinth), ou `"static"` (URL zip figée par version MC). |
| **Bibliothèque officielle** | Une bibliothèque pré-enregistrée dans le registre `OFFICIAL_LIBS` de StewBeet, détectée automatiquement depuis les fonctions: aucune configuration requise. |
| **Lantern Load** | Un standard communautaire pour l'ordre de chargement des datapacks ; StewBeet le configure automatiquement. |
| **`DataVersion`** | Un champ NBT d'entité utilisé pour détecter la version Minecraft au runtime ; comparé au minimum issu de `mc_supports`. |

## Prochaines étapes

- [finalyze.dependencies](../plugins/finalyze.dependencies.md): le plugin qui effectue les vérifications.
- [Configurer le build](../3_beet_config/fr.md): où load_dependencies se déclare.
- [Publier automatiquement](../6_continuous_delivery/fr.md): publier un pack qui dépend de bibliothèques.
