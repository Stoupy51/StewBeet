
# Texture size check

Signale les textures d'items et de blocks dont la largeur ou la hauteur n'est pas une puissance de 2.

Il tourne dans les templates `basic` et `extensive` sous le nom `stewbeet.plugins.resource_pack.check_power_of_2`, sans configuration. Il tourne après les plugins qui écrivent des textures. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/resource_pack/check_power_of_2/__init__.py)

## Ce que ce plugin écrit

Rien. Il affiche un seul avertissement qui liste chaque mauvaise texture et sa taille, et le build continue :

```text
The following textures are not in power of 2
resolution (2x2, 4x4, 8x8, 16x16, ...):
- simplenergy:item/ruby	(15x16)
```

## Limites

- Il lit les textures sous `item/` et `block/`, dans chaque namespace du resource pack. Les autres dossiers ne sont pas vérifiés.
- Une texture plus haute que large, dont la hauteur est un multiple de la largeur, est ignorée comme bande d'animation. Une texture de 48x144 passe, une de 48x48 est signalée.

