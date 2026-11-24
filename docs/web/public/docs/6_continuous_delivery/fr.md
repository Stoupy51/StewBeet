
# Publier des releases automatiquement

Un seul script `upload.py` publie une release sur GitHub, Modrinth, Smithed et PlanetMinecraft. Il appelle chaque plateforme à tour de rôle : GitHub en premier, car il écrit le changelog, puis les autres avec ce changelog.

Les identifiants vivent hors du projet, dans `~/stewbeet/credentials.yml`, pour qu'un commit ne les embarque pas.

- Un script publié : [SimplEnergy/upload.py](https://github.com/Stoupy51/SimplEnergy/blob/main/upload.py)
- Le source : [stewbeet/continuous_delivery/](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/continuous_delivery/)

| Plateforme | Ce que fait le script |
|------------|-----------------------|
| GitHub | Crée une release taguée sur le HEAD poussé et envoie les artefacts du build |
| Modrinth | Publie la version, synchronise la description, empaquette éventuellement des jars de mod |
| Smithed | Enregistre la version, avec un lien vers les assets de la release GitHub |
| PlanetMinecraft | Ouvre la page d'édition et copie le changelog en BBCode dans le presse-papiers |

## Configuration des identifiants

Créez le fichier `~/stewbeet/credentials.yml` (soit `C:\Users\YourName\stewbeet\credentials.yml` sous Windows) :

```yaml
github:
  api_key: "ghp_..."         # Personal Access Token: https://github.com/settings/tokens
  username: "YourUsername"   # GitHub account username

modrinth_api_key: "mrp_..."  # PAT with "Create versions" scope: https://modrinth.com/settings/pats

smithed_api_key: "..."       # Token with WRITE_PACKS scope: https://smithed.net/settings?tab=account

# Optional: SFTP destinations used by the copy_to_destination plugin
sftp:
  user@host:
    password: "your_password"
```

Ne commitez jamais `credentials.yml`. Ajoutez-le à votre `.gitignore` si vous le gardez dans un dossier de projet.

---

## GitHub

`upload_to_github` crée une release taguée sur GitHub, envoie les artefacts du build correspondants, et renvoie une chaîne de changelog générée depuis les commits depuis le tag précédent.

### Identifiants requis

| Clé | Description |
|-----|-------------|
| `github.api_key` | Personal Access Token GitHub |
| `github.username` | Nom d'utilisateur du compte GitHub |

### Configuration

| Clé | Requis | Description |
|-----|--------|-------------|
| `project_name` | Oui | Nom du dépôt, sans espaces (sert à construire l'URL de la release) |
| `version` | Oui | Chaîne de version, ex. `"1.2.3"` : devient le tag `v1.2.3` |
| `build_folder` | Oui | Chemin du dossier contenant les zips construits |
| `endswith` | Non | Liste de suffixes pour filtrer les fichiers envoyés (ex. `[".zip"]`) |
| `files` | Non | Chemins explicites à envoyer au lieu de parcourir `build_folder` |

### Exemple

```python
github_config: JsonDict = {
    "project_name": cfg.name,
    "version": cfg.version,
    "build_folder": cfg.output,
    "endswith": [".zip"],
}
changelog: str = upload_to_github(credentials, github_config)
```

### Comportement

- Le tag est créé sur votre HEAD local. Le script s'arrête avec une erreur quand ce commit n'est pas encore sur GitHub : poussez avant d'envoyer.
- Si le tag `v{version}` existe déjà, le script demande `y/N`. Répondre `y` supprime la release et le tag existants, puis les recrée. Toute autre réponse saute la release GitHub.
- La release est créée en brouillon, reçoit ses assets, puis est publiée. Un envoi d'asset qui échoue avec une réponse 5xx est retenté jusqu'à 4 fois.
- Envoie chaque fichier de `build_folder` dont le nom se termine par l'un des suffixes de `endswith`.
- Renvoie le changelog généré sous forme de chaîne Markdown, utilisée comme entrée des autres fonctions d'envoi.

---

## Modrinth

`upload_to_modrinth` synchronise la description et le résumé du projet sur Modrinth, puis envoie une nouvelle version avec les zips construits en pièces jointes.

### Identifiants requis

| Clé | Description |
|-----|-------------|
| `modrinth_api_key` | PAT Modrinth avec le scope "Create versions" |

### Configuration

| Clé | Requis | Description |
|-----|--------|-------------|
| `slug` | Oui | Namespace du projet sur Modrinth (ex. `"simplenergy"`) |
| `project_name` | Oui | Nom d'affichage du projet |
| `version` | Oui | Chaîne de version |
| `summary` | Oui | Courte description affichée sur la carte du projet |
| `description_markdown` | Oui | Description complète du projet en Markdown (en général `README.md`) |
| `version_type` | Oui | `"release"`, `"beta"` ou `"alpha"` |
| `build_folder` | Oui | Chemin du dossier contenant les zips construits |
| `dependencies` | Non | Liste d'objets de dépendance Modrinth (défaut : `[]`) |
| `package_as_mod` | Non | `"all"` ou `"separate"` : envoie aussi des jars de mod pour les plateformes de loader |
| `mod_platforms` | Non | Liste des plateformes pour l'empaquetage en mod (défaut : `["fabric", "forge", "neoforge", "quilt"]`) |
| `files` | Non | Chemins de zips à envoyer à la place des packs de `build_folder`, datapack en premier. Les noms doivent contenir `datapack` et `resource_pack` |

Sans `files`, le script envoie les `_datapack_with_libs.zip` et `_resource_pack_with_libs.zip` de `build_folder`, ou les `_datapack.zip` et `_resource_pack.zip` simples quand le build n'a pas produit de paire `_with_libs`. Le resource pack est marqué comme requis sur la version.

### Exemple

```python
modrinth_config: JsonDict = {
    "slug": cfg.id,
    "project_name": cfg.name,
    "version": cfg.version,
    "summary": SUMMARY,
    "description_markdown": read_file(f"{cfg.directory}/README.md"),
    "dependencies": [
        # {"project_id": "QQRRSSTT", "version_id": "IIJJKKLL", "dependency_type": "required"},
    ],
    "version_type": "beta",
    "build_folder": cfg.output,
}
upload_to_modrinth(credentials, modrinth_config, changelog)
```

### Comportement

- Met toujours à jour la description et le résumé du projet avant d'envoyer la version.
- Si la version existe déjà, demande `y/N` : répondre `y` la supprime et la recrée, toute autre réponse arrête l'envoi.
- Avec `package_as_mod = "all"`, envoie une version datapack et une version mod (`<version>+mod`) couvrant toutes les plateformes.
- Avec `package_as_mod = "separate"`, envoie une version datapack et une version mod distincte par plateforme (`<version>+<platform>`).

---

## Smithed

`upload_to_smithed` enregistre une nouvelle version sur Smithed. Il trouve les liens de téléchargement dans la release GitHub créée à l'étape précédente.

### Identifiants requis

| Clé | Description |
|-----|-------------|
| `smithed_api_key` | Token Smithed avec le scope `WRITE_PACKS` |
| `github.api_key` | PAT GitHub, qui doit être présent dans le fichier |
| `github.username` | Nom d'utilisateur du compte GitHub, utilisé pour construire les URLs de release |

### Configuration

| Clé | Requis | Description |
|-----|--------|-------------|
| `project_id` | Oui | ID du projet Smithed / namespace |
| `project_name` | Oui | Nom du pack, utilisé pour construire les noms de fichiers de téléchargement par défaut |
| `version` | Oui | Chaîne de version |
| `github_project_name` | Non | Nom du dépôt GitHub, s'il diffère de `project_name` |
| `files` | Non | `{"datapack": ..., "resourcepack": ...}` zips locaux déjà joints à la release GitHub (`resourcepack` est optionnel). Les noms n'utilisent que des lettres, des chiffres, `.`, `_` et `-` |

### Exemple

```python
smithed_config: JsonDict = {
    "project_id": cfg.id,
    "project_name": cfg.name,
    "version": cfg.version,
}
upload_to_smithed(credentials, smithed_config, changelog)
```

### Comportement

- Cherche le datapack et le resource pack dans la release GitHub (`_with_libs.zip` d'abord, puis le zip simple), et garde la première URL qui répond.
- Les versions de Minecraft prises en charge viennent de `mc_supports`, sinon de `minecraft`, dans `beet.yml`, sans `"infinite"`. Les versions qui ne sont pas faites de chiffres et de points (snapshots, release candidates) sont écartées.
- L'argument changelog est accepté mais pas envoyé : Smithed ne reçoit que la version et ses téléchargements.

---

## PlanetMinecraft

`upload_to_pmc` n'a pas d'API. Il ouvre la page d'édition du projet dans votre navigateur et copie dans le presse-papiers le changelog converti en BBCode, prêt à coller. Il ouvre la page avec la commande Windows `start`.

### Configuration

| Clé           | Requis | Description                                           |
| ------------- | ------ | ----------------------------------------------------- |
| `project_url` | Oui | URL de la page de gestion du projet sur PlanetMinecraft |
| `version`     | Oui | Chaîne de version, que le script exige sans l'utiliser davantage |

### Exemple

```python
pmc_config: JsonDict = {
    "project_url": "https://www.planetminecraft.com/account/manage/data-packs/5305840/",
    "version": cfg.version,
}
upload_to_pmc(pmc_config, changelog)
```

### Comportement

- Ouvre `project_url` dans le navigateur par défaut.
- Convertit le changelog Markdown en BBCode et le copie dans le presse-papiers.
- Affiche un message de confirmation : collez le contenu du presse-papiers dans la description de la version sur la page.

---

## Script d'exemple complet

Un `upload.py` complet pour un projet type (exemple tiré de [SimplEnergy](https://github.com/Stoupy51/SimplEnergy/blob/main/upload.py)) :

```python
# pyright: reportUnknownVariableType=false
# Imports
from beet import ProjectConfig
from stewbeet import JsonDict
from stewbeet.continuous_delivery import load_credentials, upload_to_github, upload_to_modrinth, upload_to_pmc, upload_to_smithed
from stewbeet.utils import get_project_config
from stouputils.io import read_file

# Get credentials and try to find the beet configuration
credentials: dict[str, str] = load_credentials("~/stewbeet/credentials.yml")
cfg: ProjectConfig = get_project_config()

# Constants
SUMMARY: str = """
SimplEnergy is a simple Technology datapack created to add simple energy mechanics in your survival world.
Also, it has been made to help the development of energy datapacks by using an energy library as simple as possible.
"""

## Uploads
# Upload to GitHub
github_config: JsonDict = {
    "project_name": cfg.name,
    "version": cfg.version,
    "build_folder": cfg.output,
    "endswith": [".zip"]
}
changelog: str = upload_to_github(credentials, github_config)

# Upload to Modrinth
modrinth_config: JsonDict = {
    "slug": cfg.id,
    "project_name": cfg.name,
    "version": cfg.version,
    "summary": SUMMARY,
    "description_markdown": read_file(f"{cfg.directory}/README.md"),
    "dependencies": [
        #{"project_id": "QQRRSSTT", "version_id": "IIJJKKLL", "dependency_type": "required"},
    ],
    "version_type": "beta",
    "build_folder": cfg.output,
}
upload_to_modrinth(credentials, modrinth_config, changelog)

# Upload to Smithed
smithed_config: JsonDict = {
	"project_id": cfg.id,
	"project_name": cfg.name,
	"version": cfg.version,
}
upload_to_smithed(credentials, smithed_config, changelog)

# Upload to PlanetMinecraft
pmc_config: JsonDict = {
	"project_url": "https://www.planetminecraft.com/account/manage/data-packs/5305840/",
	"version": cfg.version,
}
upload_to_pmc(pmc_config, changelog)
```

## Étapes suivantes

- [Configurer le build](../3_beet_config/fr.md#mc_supports) : `mc_supports` fixe les versions de Minecraft envoyées à Modrinth et Smithed.
- [Utiliser des bibliothèques de datapack](../5_dependencies/fr.md) : comment les bibliothèques arrivent dans les zips `_with_libs` et les vérifications que votre pack publié exécute.
- [merge_smithed_weld](../plugins/merge_smithed_weld.fr.md) : le plugin qui écrit ces zips `_with_libs`.

