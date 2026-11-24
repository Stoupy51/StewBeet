
# Unused textures

Signale les fichiers `.png` de votre dossier de textures que rien n'utilise dans le resource pack.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.check_unused_textures`. Il a besoin de `textures_folder` dans la section `stewbeet` de `beet.yml`, et tourne tard dans le pipeline, une fois les textures en place. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/check_unused_textures/__init__.py)

## Ce que ce plugin écrit

Rien. Il affiche un seul avertissement qui liste les fichiers, et le build continue :

```text
Some textures are not used in the resource pack:
- 'assets/textures/old_ruby.png'
```

Une texture compte comme utilisée quand un générateur l'a consommée, ou quand une texture du resource pack a son nom de fichier dans son chemin source.

## Limites

- La correspondance est large. Un fichier nommé `ore.png` n'est pas signalé tant que `ruby_ore.png` est dans le pack, puisque son nom apparaît dans ce chemin.
- Sans `textures_folder`, le build s'arrête avec `meta.stewbeet.textures_folder is not set`.

