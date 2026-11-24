
# Migrer un pack existant

`stewbeet migrate` transforme un datapack ou un resource pack que vous avez déjà en projet StewBeet. Vos fichiers vont dans `src/`, un template ajoute `beet.yml` et le reste d'un projet autour, et `stewbeet build` vous rend votre pack. Vos dossiers `data/` et `assets/` sont déplacés tels quels, sans une ligne modifiée.

Il est prévu pour les packs faits à la main ou avec d'autres outils. Un dossier qui a déjà une configuration beet est refusé, puisque c'est déjà un projet beet.

Nouveau avec beet ? [Comment StewBeet s'intègre à beet](../how_it_fits/fr.md) montre qui fait beet, bolt, mecha et StewBeet.

## Avant de commencer

- **Committez le dossier dans git, ou copiez-le.** La migration déplace des fichiers.
- **Ouvrez un terminal dans le dossier de votre pack, ou dans le dossier au-dessus.** Un pack est un `pack.mcmeta` à côté d'un dossier `data/`, d'un dossier `assets/`, ou des deux, et il est cherché jusqu'à deux dossiers de profondeur.
- **Un datapack et un resource pack au plus.** Un seul dossier qui contient les deux compte pour un seul pack.

## 1. Prévisualiser la migration

```bash
uvx stewbeet migrate basic --dry-run
```

`--dry-run` affiche tout ce que la migration ferait et ne change rien. Ici le pack est `My Pack/`, un datapack et un resource pack qui partagent un `pack.mcmeta` :

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
|------|---------|
| `add` | Un fichier du template, écrit parce que vous n'avez rien à ce chemin |
| `skip` | Un fichier du template laissé de côté, avec la raison |
| `write` | `beet.yml`, avec les valeurs tirées de votre pack listées dessous |
| `move` | Un de vos fichiers ou dossiers, déplacé tel quel |
| `delete` | Un `pack.mcmeta` qui ne contenait qu'une description et un pack format |
| `remove` | Un dossier laissé vide par les déplacements |

### Quel template

| Template | Ce que vous obtenez |
|----------|--------------|
| `minimal` | beet avec un seul plugin StewBeet. Le plus proche du pack que vous aviez. |
| `basic` | Chaque plugin StewBeet configuré et commenté. Le template qu'utilise le [tutoriel](../0_getting_started/fr.md). |

Sans nom, la commande demande, et appuyer sur Entrée choisit `minimal`. Avec `--yes` et sans nom, elle choisit `minimal` sans demander. `extensive` n'est pas proposé, parce que ses items d'exemple se mélangeraient aux vôtres.

## 2. Migrer

```bash
uvx stewbeet migrate basic
```

Elle affiche le même plan, puis demande `Apply this plan? (y/n)`. Ajoutez `--yes` (ou `-y`) pour sauter la question, dans un script par exemple.

## 3. Vérifier `beet.yml`, puis compiler

`name` prend le nom du dossier de votre pack. Les avertissements sous le plan listent ce qui reste à faire à la main, pour les templates dont le `beet.yml` a ces clés (`basic` les a, `minimal` non) :

- **`author`** contient encore l'auteur du template. Mettez-y votre nom.
- **`id`** est tiré de votre namespace, le dossier sous `data/` autre que `minecraft`. Avec plusieurs namespaces il n'est pas défini, donc choisissez celui sous lequel StewBeet doit générer ses functions.

Puis compilez :

```bash
uv run stewbeet build
```

`build/` contient votre datapack et votre resource pack, avec un `pack.mcmeta` écrit pour la version `minecraft` définie dans `beet.yml`. Si vous avez gardé un `pyproject.toml` à vous, celui du template a été ignoré : ajoutez `stewbeet` à ses dépendances, ou compilez avec `uvx stewbeet build`.

## Avant et après

L'exemple ci-dessus, migré sur `basic` :

```text
Before                                  After
.                                       .
└── My Pack/                            ├── beet.yml           id, name and description from your pack
    ├── pack.mcmeta                     ├── pyproject.toml
    ├── pack.png                        ├── assets/
    ├── data/                           │   └── pack.png       your icon
    │   ├── minecraft/tags/...          └── src/
    │   └── mypack/function/...             ├── data/          your datapack, unchanged
    └── assets/                             ├── assets/        your resource pack, unchanged
        └── mypack/lang/en_us.json          ├── definitions/   from the template, no items yet
                                            ├── link.py
                                            └── setup_definitions.py
```

## Ce qui arrive à chaque fichier

- **`data/` et `assets/`** vont dans `src/data/` et `src/assets/`, contenu intact.
- **`pack.mcmeta`** qui ne contient qu'une description et un pack format est supprimé : sa description va dans `beet.yml`, et StewBeet écrit un nouveau `pack.mcmeta` à chaque build. Un `pack.mcmeta` qui contient plus, comme `overlays` ou `filter`, va dans `src/pack.mcmeta`. StewBeet garde ses clés en plus mais fixe quand même `pack_format` et `description`.
- **`pack.png`** va là où le template garde son icône : `src/` pour `minimal`, `assets/` pour `basic`. Quand le datapack et le resource pack en ont chacun un, celui du datapack est utilisé et l'autre reste où il est.
- **Les fichiers que le template fournit et que vous avez déjà**, comme `.gitignore` ou `pyproject.toml`, sont conservés. La copie du template est ignorée.
- **Un resource pack migré sur `minimal`** reçoit une section `resource_pack` ajoutée à `beet.yml`, puisque ce template ne compile qu'un datapack.
- **Les dossiers dans lesquels se trouvait votre pack** sont supprimés une fois vides.

## Quand elle refuse

Chaque vérification a lieu avant le déplacement du premier fichier, donc un refus laisse le dossier comme il était.

| Message | Que faire |
|---------|------------|
| `This folder already has a beet configuration` | Le dossier est déjà un projet beet : il n'y a rien à migrer. |
| `No pack found` | Le `pack.mcmeta` manque, ou se trouve à plus de deux dossiers de profondeur. Lancez la commande plus près. |
| `Found 2 datapacks` | Un projet contient un datapack et un resource pack. Lancez la commande depuis un dossier qui ne contient que le pack à migrer. |
| `Nothing was changed, because: src/data already exists` | Quelque chose se trouve déjà là où iraient vos fichiers. Déplacez-le ailleurs et relancez. |
| `Could not download the 'basic' template` | Les templates sont téléchargés depuis GitHub pour votre version de StewBeet, donc cela demande une connexion. |

## Étapes suivantes

- [Items et blocks](../items_and_blocks/fr.md) : transformez un par un les items que vous donnez avec des loot tables écrites à la main en définitions. StewBeet écrit alors leurs loot tables, models et pages de manuel.
- [Configurer le build](../3_beet_config/fr.md) : chaque option de votre `beet.yml`.

