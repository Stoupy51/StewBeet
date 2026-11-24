
# Comment StewBeet s'intègre à beet

StewBeet est un ensemble de plugins pour beet, l'outil de build de l'équipe mcbeet. beet exécute le build, mecha et bolt lisent vos commandes, et StewBeet écrit les fichiers dont vos définitions ont besoin.

![beet runs the build and bolt and mecha plug into it, all three made by the beet team. StewBeet is a separate project that runs inside beet as plugins.](../../img/stack/stewbeet-stack.en.dark.png)

## beet exécute le build

beet lit `beet.yml`, charge en mémoire le datapack et le resource pack de votre projet, puis les passe à chaque plugin du fichier tour à tour : d'abord ceux de `require`, ensuite le `pipeline`. Un plugin est une fonction Python qui ajoute, modifie ou supprime des fichiers dans ces packs. Quand le dernier a tourné, beet écrit les deux packs dans le dossier de sortie.

`stewbeet build` lance beet sur votre projet, et `stewbeet watch` le relance à chaque sauvegarde. Tout plugin beet fonctionne dans un projet StewBeet, et toute option lue par beet garde son sens.

## mecha et bolt lisent vos commandes

mecha analyse chaque function du datapack, vérifie chaque commande par rapport à la version de Minecraft visée, et fait échouer le build sur une faute de frappe que le jeu ne signalerait qu'au `/reload`. bolt, construit sur mecha, permet à une function de contenir du Python : boucles, variables et imports, compilés en commandes classiques.

Les deux sont faits par l'équipe beet et installés avec StewBeet.

## StewBeet est le reste du pipeline

L'entrée `stewbeet` de `require` charge vos définitions. Chaque étape du `pipeline` du template est un plugin StewBeet, avec sa propre page sous [Plugins](../plugins/README.fr.md) : models, recipes, loot tables, le manuel, les zips. Un plugin dont vous n'avez pas besoin sort de la liste, et un plugin beet de votre cru se place n'importe où dedans.

Vos appels Python, comme `write_function`, écrivent dans les mêmes packs que ceux de beet, donc les plugins qui suivent voient aussi vos fichiers.

## Ce sur quoi il s'appuie aussi

- Les bibliothèques de datapack que vos functions appellent, comme Smithed Custom Block ou un module Bookshelf, téléchargées et vérifiées en jeu. [Bibliothèques de datapack](../5_dependencies/fr.md) les liste.
- model_resolver rend chaque item en image pour le [manuel en jeu](../7_ingame_manual/fr.md).
- Spyglass, via l'[extension VS Code](../8_editor/fr.md), vérifie les commandes dans vos chaînes Python pendant la frappe.

Les [crédits](/credits) remercient les personnes derrière chacun.

## Étapes suivantes

- [beet.yml](../3_beet_config/fr.md) : chaque option du fichier, `require` et `pipeline` compris.
- [Plugins](../plugins/README.fr.md) : ce qu'écrit chaque étape du pipeline.

