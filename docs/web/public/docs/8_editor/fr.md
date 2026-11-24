
# Support de l'éditeur

L'[extension StewBeet pour VSCode](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet) apporte le support de l'éditeur à tout l'écosystème [beet](https://github.com/mcbeet/beet) : beet, bolt, mecha et StewBeet.
Les fichiers `.bolt` ont leur propre langage, et les chaînes mcfunction dans votre Python ont coloration, complétion, erreurs et liens vers le datapack compilé.

<video src="/vscode_extension.mp4" controls loop muted playsinline preload="auto">
</video>

- Installez-la en cherchant *StewBeet* dans le panneau Extensions, ou [ouvrez-la sur le marketplace](https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet).
- Elle n'a pas besoin de votre venv : elle lit vos sources et les fichiers que votre build écrit, rien d'autre.
- Sa source est dans [`extension/vscode`](https://github.com/Stoupy51/StewBeet/tree/main/extension/vscode).

| Vous écrivez | Vous obtenez |
|-----------|---------|
| Des modules `.bolt` | Le langage **Bolt** : coloration, complétion et ctrl+clic sur les commandes, et une lens par function que le module écrit |
| bolt dans un `.mcfunction` | La même chose, et Spyglass retiré d'un fichier qu'il ne sait pas analyser |
| **beet** simple, `ctx.data.functions[p] = Function(...)` | Les commandes à l'intérieur sont des commandes : colorées, complétées, vérifiées, et liées à ce que le build a écrit |
| **mecha** | Navigation de chaque ligne générée vers la ligne source dont elle vient |
| Helpers `write_*` de **StewBeet** | Tout ce qui précède, plus chaque chemin `{...}` résolu vers ce qu'il est vraiment |

## Mise en place

1. Installez [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). Il fournit la complétion, le survol et les erreurs que l'extension route dans vos blocs.
2. Pour la navigation vers le build, listez le plugin [source_maps](../plugins/source_maps.fr.md) dans le `require` de votre `beet.yml`. Le template Basic le fait déjà :

```yaml
require:
    - "stewbeet"
    - "stewbeet.plugins.source_maps"    # writes the .mcfunction.map files the editor navigates with
```

L'extension fonctionne sans l'étape 2, moins les liens entre votre Python et le pack compilé.

## Bolt

<video src="/vscode_extension_bolt.mp4" controls loop muted playsinline preload="auto">
</video>

Les fichiers `.bolt` s'ouvrent en **Bolt**, avec une grammaire générée à partir de l'arbre de commandes de mecha : `item = 3` est du Python, `item modify entity @s ...` est une commande.

- **Complétion, erreurs et ctrl+clic** sur les commandes, via Spyglass. Les expressions Python sont masquées.
- **Une lens par function** que le module écrit, menant au fichier généré.
- **Les chemins calculés restent cliquables** : `function gui.open` se résout vers ce que le dernier build a écrit.

Un `.mcfunction` qui contient du bolt reçoit aussi l'id de langage `bolt`. Spyglass l'indexe toujours, donc les functions qu'il définit sont connues des fichiers qui les appellent, et les erreurs que Spyglass signale sur ses lignes bolt sont retirées.

Voir [Approche 4 : Bolt](../2_writing_to_files/fr.md#approche-4-bolt) pour le langage lui-même.

## beet

<video src="/vscode_extension_beet.mp4" controls loop muted playsinline preload="auto">
</video>

Les plugins qui utilisent l'API propre de beet n'ont besoin de rien de plus que `stewbeet.plugins.source_maps` :

- **Les erreurs pendant la frappe**, sans build. Les erreurs de build sont relayées sur le Python qui a écrit la commande.
- **Navigation dans les deux sens** : aller à la définition mène à l'appel qui a écrit une function, trouver les références liste chaque auteur, et une lens au-dessus de chaque bloc ouvre ce qu'il a généré.

## StewBeet

```python
write_function(f"{ns}:machines/tick", f"""
execute unless score @s energy.storage >= @s {ns}.energy_rate run return fail
execute if entity @s[tag={ns}.turbine] run function {ns}:turbine/tick
""")
```

Chaque `{...}` est rempli avec ce que le dernier build a résolu, donc ctrl+clic et complétion fonctionnent sur les chemins calculés.
Un nom résolu sur une ligne est réutilisé là où le build ne couvre rien, comme les commandes collectées dans une liste.
Rien n'évalue votre Python, et ce qui reste inconnu garde un masque `_`.

### Ce qui compte comme un bloc

| Écrit comme | Exemple |
|------------|---------|
| Helpers `write_*` | `write_function`, `write_versioned_function`, `write_load_file`, ... |
| Une variable | `content = f"""..."""`, chaque `+=` jusqu'à l'appel qui la consomme, et un littéral que l'appel lui ajoute |
| Une liste | `.append`, `+= [...]`, littéraux, compréhensions, `"\n".join(lines)` |
| Votre propre function | Tout paramètre annoté `McFunction` |
| L'API propre de beet | `Function(...)` à partir d'une chaîne ou d'une `list[str]`, plus `.append`, `.prepend` et `.lines` |

Colorer une variable demande l'annotation `McFunction` (un alias de `str` fourni par `stewbeet`). Tout le reste fonctionne sans.

## Commandes

Depuis la palette : **Go to Generated Function**, **Go to Python Source**, **Reload Source Maps**, **Refresh Build Diagnostics**, **Show Diagnostics Status**, **Install Spyglass Language Server**.

## Réglages

Tous sous `StewBeet.*` :

| Réglage | Défaut | |
|---------|---------|---|
| `languageFeatures` | `true` | Complétion, survol, aide de signature et aller à la définition dans les blocs |
| `suggestSpyglass` | `true` | Proposer l'installation de Spyglass une fois, quand il manque |
| `buildOutput` | `""` | Où se trouve le pack généré, absolu ou relatif au workspace. Vide cherche dans le workspace |
| `sourceMapDiagnostics` | `true` | Relayer les erreurs de build sur le Python qui a écrit la commande |
| `resolveInterpolations` | `true` | Remplir chaque `{...}` avec ce que le dernier build a résolu |
| `diagnosticRuleDenylist` | `["undeclaredSymbol"]` | Règles jamais relayées sur le Python |
| `codeLens` | `true` | Le lien au-dessus d'un bloc qui a produit une function |
| `headerLinks` | `true` | Les resource locations dans l'en-tête `#>` d'un fichier généré |
| `boltInMcfunction` | `true` | Donner l'id de langage `bolt` à un `.mcfunction` qui contient du bolt |
| `enableBlockDecorations` | `true` | La boîte colorée autour d'un bloc |
| `backgroundColor` | `rgba(80,40,0,0.15)` | Toute couleur CSS |
| `borderColor` | `rgba(200,120,30,0.30)` | Toute couleur CSS |
| `borderWidth` | `"2px"` | |

## Si vous venez d'Aegis

Comparée à [Aegis](https://marketplace.visualstudio.com/items?itemName=thenuclearnexus.mecha-language-server), StewBeet n'a besoin ni de `ms-python.python` ni d'un environnement, mais ne fournit pas encore les symboles Python dans la complétion.

| | Aegis | StewBeet |
|---|-------|----------|
| Coloration `.bolt` | Aucune, lu comme `mcfunction` | Grammaire Bolt |
| Commandes dans les chaînes Python | Non | Oui |
| Navigation source vers build | Non | Dans les deux sens |
| Nécessite | `ms-python.python` et votre environnement | Rien |
| Complétion `.bolt` | Compilateur complet, symboles Python compris | Commandes seulement, via Spyglass |

Gardez Aegis si vous avez besoin de cette dernière ligne.

## Étapes suivantes

- [Functions et fichiers](../2_writing_to_files/fr.md) : les quatre façons d'écrire les commandes que l'extension lit, Bolt compris.
- [stewbeet.plugins.source_maps](../plugins/source_maps.fr.md) : les source maps derrière la navigation.

