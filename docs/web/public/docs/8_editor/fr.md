# Support éditeur

L'[extension StewBeet pour VSCode](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) est le support éditeur de tout l'écosystème [beet](https://github.com/mcbeet/beet) : **beet**, **bolt**, **mecha** et **StewBeet**.
Les fichiers `.bolt` obtiennent leur propre langage, et les chaînes mcfunction dans votre Python obtiennent coloration, complétion, erreurs et liens vers le datapack construit.

<video src="/vscode_extension.mp4" controls loop muted playsinline preload="auto">
</video>

**Installation** : cherchez *StewBeet* dans le panneau Extensions, ou [ouvrez-la sur le marketplace](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet).<br>
**Besoin de votre venv** : non. Elle lit vos sources et les fichiers que votre build écrit, rien d'autre.<br>
**Code source** : [`extension/vscode`](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode) <br>

| Vous écrivez | Vous obtenez |
|--------------|--------------|
| Des modules `.bolt` | Le langage **Bolt** : coloration, complétion et ctrl+clic sur les commandes, et un lens par fonction que le module écrit |
| Du bolt dans un `.mcfunction` | La même chose, et Spyglass retiré d'un fichier qu'il ne sait pas lire |
| Du **beet** simple, `ctx.data.functions[p] = Function(...)` | Les commandes dedans sont des commandes : colorées, complétées, vérifiées, et liées à ce que le build a écrit |
| **mecha** | La navigation de chaque ligne générée vers la ligne source dont elle vient |
| Les helpers `write_*` de **StewBeet** | Tout ce qui précède, plus chaque chemin `{...}` résolu vers ce qu'il est vraiment |

## Mise en place

1. Installez [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). Il fournit la complétion, le survol et les erreurs que l'extension redirige dans vos blocs.
2. Pour la navigation vers le build, ajoutez le plugin [sniffer](../plugins/sniffer.md) à votre `beet.yml` :

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.sniffer"    # écrit les fichiers .mcfunction.map avec lesquels l'éditeur navigue
```

C'est toute la configuration. L'extension fonctionne sans l'étape 2, moins les liens entre votre Python et le pack construit.

## Bolt

<video src="/vscode_extension_bolt.mp4" controls loop muted playsinline preload="auto">
</video>

Les fichiers `.bolt` s'ouvrent en **Bolt**, avec une grammaire générée depuis l'arbre de commandes de mecha : `item = 3` est du Python, `item modify entity @s ...` est une commande.

- **Complétion, erreurs et ctrl+clic** sur les commandes, via Spyglass. Les expressions Python sont masquées.
- **Un lens par fonction** que le module écrit, menant au fichier généré.
- **Les chemins calculés restent cliquables** : `function gui.open` résout vers ce que le dernier build a écrit.

Un `.mcfunction` contenant du bolt reçoit aussi l'id de langage `bolt`. Spyglass les lit toujours depuis le disque, donc **StewBeet: Exclude Bolt Files From Spyglass** les ajoute à `.spyglassrc.json`, ou votre build tient cette liste à jour avec le plugin [spyglass](../plugins/spyglass.md).

Voir [Approche 4 : Bolt](../2_writing_to_files/fr.md#approche-4-bolt) pour le langage lui-même.

## beet

<video src="/vscode_extension_beet.mp4" controls loop muted playsinline preload="auto">
</video>

Les plugins qui utilisent l'API de beet n'ont besoin de rien d'autre que `stewbeet.plugins.sniffer` :

- **Les erreurs à la frappe**, sans build. Les erreurs de build sont reportées sur le Python qui a écrit la commande.
- **La navigation dans les deux sens** : aller à la définition atterrit sur l'appel qui a écrit une fonction, chercher les références liste chaque écrivain, et un lens au-dessus de chaque bloc ouvre ce qu'il a généré.

## StewBeet

```python
write_function(f"{ns}:machines/tick", f"""
execute unless score @s energy.storage >= @s {ns}.energy_rate run return fail
execute if entity @s[tag={ns}.turbine] run function {ns}:turbine/tick
""")
```

Chaque `{...}` est rempli avec ce que le dernier build y a résolu, donc ctrl+clic et complétion fonctionnent sur les chemins calculés.
Un nom résolu sur une ligne est réutilisé là où le build ne couvre rien, par exemple des commandes assemblées dans une variable.
Rien n'évalue votre Python, et ce qui reste inconnu garde un masque `_`.

### Ce qui compte comme un bloc

| Écrit comme | Exemple |
|-------------|---------|
| Les helpers `write_*` | `write_function`, `write_versioned_function`, `write_load_file`, ... |
| Une variable | Une f-string triple assignée à un nom, et chaque `+=` jusqu'à l'appel qui la consomme |
| Une liste | `.append`, `+= [...]`, littéraux, compréhensions, `"\n".join(lines)` |
| Votre propre fonction | Tout paramètre annoté `McFunction` |
| L'API de beet | `Function(...)` depuis une chaîne ou une `list[str]`, plus `.append`, `.prepend` et `.lines` |

Colorer une variable demande l'annotation `McFunction` (un simple alias de `str` fourni par `stewbeet`). Tout le reste fonctionne sans.

## Commandes

Depuis la palette : **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Exclude Bolt Files From Spyglass**, **Install Spyglass Language Server**.

## Paramètres

Tous sous `StewBeet.*` :

| Paramètre | Défaut | |
|-----------|--------|---|
| `languageFeatures` | `true` | Complétion, survol, aide à la signature et aller à la définition dans les blocs |
| `suggestSpyglass` | `true` | Propose l'installation de Spyglass une fois, s'il manque |
| `buildOutput` | `""` | Où se trouve le pack généré, en absolu ou relatif au workspace. Vide cherche dans le workspace |
| `sourceMapDiagnostics` | `true` | Reporte les erreurs de build sur le Python qui a écrit la commande |
| `resolveInterpolations` | `true` | Remplit chaque `{...}` avec ce que le dernier build y a résolu |
| `diagnosticRuleDenylist` | `["undeclaredSymbol"]` | Règles jamais reportées sur le Python |
| `codeLens` | `true` | Le lien au-dessus d'un bloc ayant produit une fonction |
| `headerLinks` | `true` | Les resource locations dans l'en-tête `#>` d'un fichier généré |
| `boltInMcfunction` | `true` | Donne l'id de langage `bolt` à un `.mcfunction` contenant du bolt |
| `enableBlockDecorations` | `true` | Le cadre coloré autour d'un bloc |
| `backgroundColor` | `rgba(80,40,0,0.15)` | N'importe quelle couleur CSS |
| `borderColor` | `rgba(200,120,30,0.30)` | N'importe quelle couleur CSS |
| `borderWidth` | `"2px"` | |

## En venant d'Aegis

Comparée à [Aegis](https://marketplace.visualstudio.com/items?itemName=thenuclearnexus.mecha-language-server), StewBeet est plus légère et plus simple à installer, mais elle ne fournit pas encore les symboles Python dans la complétion.

| | Aegis | StewBeet |
|---|-------|----------|
| Coloration `.bolt` | Aucune, lu comme du `mcfunction` | **Grammaire Bolt** |
| Commandes dans les chaînes Python | Non | **Oui** |
| Navigation source vers build | Non | **Dans les deux sens** |
| Requiert | `ms-python.python` et votre environnement | **Rien** |
| Complétion `.bolt` | **Compilateur complet, symboles Python inclus** | Commandes seulement, via Spyglass |

Gardez Aegis si vous avez besoin de cette dernière ligne.

## Prochaines étapes

- [Écrire fonctions et fichiers](../2_writing_to_files/fr.md) : tout ce que l'extension lit, Bolt compris.
- [stewbeet.plugins.sniffer](../plugins/sniffer.md) : les source maps derrière la navigation.
- [stewbeet.plugins.spyglass](../plugins/spyglass.md) : garder Spyglass loin des fichiers qu'il ne sait pas lire.
