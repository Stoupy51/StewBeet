# Migrer un pack existant

`stewbeet migrate` transforme un datapack ou un resource pack que vous avez déjà en projet StewBeet. Vos fichiers vont dans `src/`, un template ajoute `beet.yml` et le reste d'un projet autour, et `stewbeet build` vous rend votre pack. Rien de ce que vous avez écrit n'est modifié, seulement déplacé.

C'est prévu pour les packs faits à la main ou avec d'autres outils. Un dossier qui a déjà une configuration beet est refusé, puisque c'est déjà un projet beet.

Vous découvrez beet ? Le schéma en haut de la [page de configuration beet](../3_beet_config/fr.md) montre qui fait beet, bolt, mecha et StewBeet.

## Avant de commencer

- **Commitez le dossier dans git, ou copiez-le.** La migration déplace des fichiers.
- **Ouvrez un terminal dans le dossier de votre pack, ou dans le dossier au-dessus.** Un pack, c'est un `pack.mcmeta` à côté d'un dossier `data/`, d'un dossier `assets/`, ou des deux, et il est cherché jusqu'à deux dossiers de profondeur.
- **Un datapack et un resource pack au maximum.** Un même dossier qui contient les deux compte pour un seul pack.

## 1. Prévisualiser la migration

```bash
uvx stewbeet migrate basic --dry-run
```

`--dry-run` affiche tout ce que la migration ferait, sans rien changer. Ici le pack est `My Pack/`, un datapack et un resource pack qui partagent un seul `pack.mcmeta` :

```text
Found datapack and resource pack in My Pack
Migration plan:
  add     .gitignore
  add     definitions_debug.json
  add     pyproject.toml
  skip    assets/pack.png (replaced by your pack.png)
  add     assets/textures/README.md
  add     src/link.py
  add     src/setup_definitions.py
  skip    src/data/basic_template/function/enjoy.mcfunction (replaced by your datapack)
  add     src/definitions/additions.py
  add     src/definitions/ores.py
  write   beet.yml
            name: My Pack
            id: mypack
            description: from pack.mcmeta
  move    My Pack/data -> src/data
  move    My Pack/assets -> src/assets
  move    My Pack/pack.png -> assets/pack.png
  delete  My Pack/pack.mcmeta (beet.yml and StewBeet write it at build time)
  remove  My Pack/ (empty once moved)
WARNING Set author in beet.yml: it still names the template's author
Dry run: nothing was changed. Run the same command without --dry-run to apply this plan.
```

| Ligne | Signification |
|-------|---------------|
| `add` | Un fichier du template, écrit parce que vous n'avez rien à cet emplacement |
| `skip` | Un fichier du template laissé de côté, avec la raison |
| `write` | `beet.yml`, avec en dessous les valeurs reprises de votre pack |
| `move` | Un de vos fichiers ou dossiers, déplacé tel quel |
| `delete` | Un `pack.mcmeta` qui ne contenait qu'une description et un pack format |
| `remove` | Un dossier vidé par les déplacements |

### Quel template

| Template | Ce que vous obtenez |
|----------|---------------------|
| `minimal` | beet avec un seul plugin StewBeet. Le plus proche du pack que vous aviez. |
| `basic` | Tous les plugins StewBeet configurés et commentés. Le template qu'utilise le [tutoriel](../0_getting_started/fr.md). |

Sans nom, la commande vous le demande, et Entrée choisit `minimal`. `extensive` n'est pas proposé, car ses items d'exemple se mélangeraient aux vôtres.

## 2. Migrer

```bash
uvx stewbeet migrate basic
```

La commande affiche le même plan, puis demande `Apply this plan? (y/n)`. Ajoutez `--yes` pour sauter la question, dans un script par exemple.

## 3. Vérifier `beet.yml`, puis compiler

Les avertissements sous le plan listent ce qui reste à faire à la main :

- **`author`** contient encore l'auteur du template. Mettez votre nom.
- **`id`** est repris de votre namespace, le dossier sous `data/` autre que `minecraft`. S'il y a plusieurs namespaces, il n'est pas rempli : choisissez celui sous lequel StewBeet doit générer ses fonctions.

Puis compilez :

```bash
uv run stewbeet build
```

`build/` contient maintenant votre datapack et votre resource pack, avec un `pack.mcmeta` écrit pour la version `minecraft` indiquée dans `beet.yml`. Si vous aviez votre propre `pyproject.toml`, celui du template a été ignoré : ajoutez `stewbeet` à ses dépendances, ou compilez avec `uvx stewbeet build`.

## Avant et après

L'exemple ci-dessus, migré vers `basic` :

```text
Avant                                   Après
.                                       .
└── My Pack/                            ├── beet.yml           id, nom et description repris du pack
    ├── pack.mcmeta                     ├── pyproject.toml
    ├── pack.png                        ├── assets/
    ├── data/                           │   └── pack.png       votre icône
    │   ├── minecraft/tags/...          └── src/
    │   └── mypack/function/...             ├── data/          votre datapack, inchangé
    └── assets/                             ├── assets/        votre resource pack, inchangé
        └── mypack/lang/en_us.json          ├── definitions/   du template, sans item pour l'instant
                                            ├── link.py
                                            └── setup_definitions.py
```

## Ce que devient chaque fichier

- **`data/` et `assets/`** vont dans `src/data/` et `src/assets/`, contenu intact.
- **Un `pack.mcmeta`** qui ne contient qu'une description et un pack format est supprimé : sa description passe dans `beet.yml`, et StewBeet écrit un nouveau `pack.mcmeta` à chaque build. S'il contient plus, comme `overlays` ou `filter`, il va dans `src/pack.mcmeta`. StewBeet garde ses clés en plus mais fixe toujours `pack_format` et `description` : vérifiez que les formats qu'il liste correspondent aux versions que vous visez.
- **`pack.png`** va là où le template range son icône : `src/` pour `minimal`, `assets/` pour `basic`. Si le datapack et le resource pack en ont chacun une, celle du datapack est utilisée et l'autre reste à sa place.
- **Les fichiers du template que vous avez déjà**, comme `.gitignore` ou `pyproject.toml`, sont conservés. La copie du template est ignorée.
- **Un resource pack migré vers `minimal`** reçoit une section `resource_pack` dans `beet.yml`, car ce template ne compile qu'un datapack.
- **Les dossiers où se trouvait votre pack** sont supprimés une fois vides.

## Quand la commande refuse

Toutes les vérifications ont lieu avant le premier déplacement : un refus laisse le dossier tel quel.

| Message | Que faire |
|---------|-----------|
| `This folder already has a beet configuration` | Le dossier est déjà un projet beet : il n'y a rien à migrer. |
| `No pack found` | Le `pack.mcmeta` manque, ou il est à plus de deux dossiers de profondeur. Lancez la commande plus près. |
| `Found 2 datapacks` | Un projet contient un datapack et un resource pack. Lancez la commande depuis un dossier qui ne contient que le pack à migrer. |
| `Nothing was changed, because: src/data already exists` | Quelque chose occupe déjà la place de vos fichiers. Déplacez-le et relancez. |
| `Could not download the 'basic' template` | Les templates sont téléchargés depuis GitHub pour votre version de StewBeet : il faut une connexion. |

## Et ensuite

- [Définitions](../1_definitions_setup/fr.md) : transformez un à un les items que vous donnez avec des loot tables écrites à la main en définitions. StewBeet écrit alors leurs loot tables, leurs modèles et leurs pages de manuel.
- [Configuration beet](../3_beet_config/fr.md) : chaque option du `beet.yml` que vous venez d'obtenir.
