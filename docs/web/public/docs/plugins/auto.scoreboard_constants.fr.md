
# Scoreboard constants

Écrit dans la load function chaque nombre que vous utilisez comme score holder dans vos functions, pour que vous ne déclariez jamais de constantes à la main.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.auto.scoreboard_constants`, sans configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/scoreboard_constants/__init__.py)

## Utiliser une constante

Écrivez le nombre sous la forme `#<nombre> <id>.data` dans n'importe quelle function :

```mcfunction
scoreboard players operation @s simplenergy.data *= #100 simplenergy.data
```

Au build, le plugin trouve `#100` et écrit sa valeur dans la load function.

## Ce que ce plugin écrit

Pour chaque nombre distinct, triés, à la fin de la load function :

```mcfunction
# Set scoreboard constants for simplenergy.data
scoreboard players set #-1 simplenergy.data -1
scoreboard players set #100 simplenergy.data 100
```

Rien n'est écrit quand aucune function n'utilise de constante.

## Limites

- Le motif est `#` suivi d'un entier, éventuellement négatif, puis d'un espace et de `<id>.data`. Une constante sur un autre objective est laissée telle quelle.
- Il lit les functions du pack telles que construites. Une function écrite par un plugin qui tourne après celui-ci n'est pas analysée.
- L'analyse porte sur le texte. Une constante dans un commentaire ou dans une chaîne compte aussi.

## Pour continuer

- [Écrire des functions et des fichiers](../2_writing_to_files/fr.md) : les functions que ce plugin lit.

