
# Lang file

Déplace le texte de vos commandes et loot tables dans `lang/en_us.json`, pour qu'un resource pack puisse le traduire.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.auto.lang_file`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/lang_file/__init__.py)

## Ce qu'il fait de votre texte

Vous écrivez des text components simples. Le plugin trouve chaque valeur `"text"` dans tous les fichiers du datapack et la réécrit en component `translate`. Le texte d'origine reste en `fallback`, donc le pack se lit toujours bien sans resource pack.

```mcfunction
# You write
tellraw @s {"text":"Not enough energy"}

# The build writes
tellraw @s {"translate":"simplenergy.not_enough_energy",
  "fallback":"Not enough energy"}
```

La clé est l'id du projet, un point, puis le texte en minuscules sans les autres signes de ponctuation, avec les espaces, `.`, `/` et `:` changés en `_`. La partie texte est coupée à 64 caractères.

Une valeur est laissée telle quelle quand elle :

- compte moins de 3 lettres ou chiffres une fois simplifiée,
- contient un `$`, pour que les lignes de macro continuent de fonctionner,
- contient un échappement `\u`.

Les symboles et la ponctuation autour des mots restent en texte brut à côté de la partie traduite. Le texte `" attacks | "` devient un espace, la clé de `attacks`, puis `" | "`. Deux textes qui ne diffèrent que par là partagent une même clé.

Deux textes différents qui donnent la même clé reçoivent `_2`, `_3` et ainsi de suite.

## Ce que ce plugin écrit

- `lang/en_us.json` dans le namespace `minecraft` du resource pack : toutes les clés, triées, fusionnées avec le fichier que vous y avez déjà.
- Le texte de chaque fichier du datapack qui a une clé `text` : functions, loot tables, advancements et le reste.

## Limites

- Seul `en_us` est écrit. Les autres langues, c'est à vous de les ajouter.
- Un texte réparti sur plusieurs valeurs `"text"` est traduit morceau par morceau.

