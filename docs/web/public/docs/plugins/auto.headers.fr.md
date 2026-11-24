
# Function headers

Écrit un commentaire d'en-tête en haut de chaque function, qui dit ce qui l'appelle, dans quel contexte, et quels arguments de macro elle prend.

Il tourne en dernier des plugins `auto` dans les templates `basic` et `extensive`, sous le nom `stewbeet.plugins.auto.headers`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/headers/__init__.py)

## À quoi ressemble un en-tête

```mcfunction
#> stardust:dimensions/teleport_to
#
# @executed	as the player & at current position
#
# @within	stardust:dimensions/teleport_home
#
# @args		dimension (string)
#			x (int)
#			y (int)
#			z (int)
#
$execute in $(dimension) run tp @s $(x) $(y) $(z)
```

- `@within` liste les appelants : une function, `#namespace:tag`, `advancement <id>`, `dialog <id>` ou `enchantment <id>`. Un id de function écrit dans une chaîne, comme dans un `suggest_command`, est listé en `string in <function>`.
- `@executed` est le contexte d'exécution que lui donnent les appelants, par exemple `as the player & at current position` pour la récompense d'une advancement.
- `@args` n'est écrit que pour les functions à macro. Les types viennent du NBT de chaque appel (`10` est un `int`, `20.5f` un `float`, `"a"` un `string`), des lignes `data modify storage` avant un appel `with storage`, et des `@args` de l'appelant quand il transmet `$(name)`.
- Une function jamais appelée affiche `@within ???`. Quand le projet a un dossier `<namespace>:v<version>/`, une function jamais appelée du namespace et située hors de ce dossier affiche `(public)` à la place, puisque vous la lancez à la main ou qu'un autre pack le fait.

## Garder votre propre texte

Le plugin relit un en-tête qu'il trouve, donc le build est répétable :

- Les lignes sous `@args` que vous avez écrites, descriptions comprises, sont conservées. Seuls les arguments manquants sont ajoutés, et le build avertit `had incomplete @args` pour chaque function qui en manquait.
- Toute autre ligne de commentaire de l'en-tête (une description, un exemple) est conservée sous `@args`.

```mcfunction
# @args		count (int): How many to give
#			- at least 1
```

## Ce que ce plugin écrit

- L'en-tête `#>` de chaque function du datapack, réécrit à chaque build.

## Limites

- L'analyse est mise en cache dans `.beet_cache` et recalculée en entier dès qu'une function, un tag, une advancement, un dialog ou un enchantment change.
- Les appelants sont trouvés dans le texte des fichiers. Un id de function construit à l'exécution n'est pas vu.

## Pour continuer

- [Écrire des functions et des fichiers](../2_writing_to_files/fr.md) : d'où viennent vos functions.

