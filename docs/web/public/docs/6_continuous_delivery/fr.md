# Publier automatiquement

StewBeet fournit un patron de script `upload.py` unique qui gère la publication d'une nouvelle release sur toutes les grandes plateformes de distribution en une seule commande.<br>
Vous appelez les fonctions d'upload de chaque plateforme en séquence — GitHub en premier (il génère le changelog), puis Modrinth, Smithed et PlanetMinecraft avec ce changelog.<br>
Les identifiants sont stockés **en dehors** du projet dans `~/stewbeet/credentials.yml` pour ne jamais être accidentellement commités.

**Exemple réel** : [SimplEnergy/upload.py](https://github.com/Stoupy51/SimplEnergy/blob/main/upload.py) <br>  
**Code source** : [stewbeet/continuous_delivery/](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/continuous_delivery/) <br>

- Centraliser toutes les clés API dans un seul fichier hors du dépôt
- Créer une release GitHub taguée et y uploader les artefacts de build automatiquement
- Publier sur Modrinth avec synchronisation de description et empaquetage mod optionnel
- Enregistrer une nouvelle version sur Smithed en liant les artefacts GitHub
- Ouvrir la page d'édition PlanetMinecraft et copier le changelog BBCode dans le presse-papier

## Configuration des Identifiants

Créez le fichier `~/stewbeet/credentials.yml` (soit `C:\Users\VotreNom\stewbeet\credentials.yml` sous Windows) :

```yaml
github:
  api_key: "ghp_..."         # Personal Access Token — https://github.com/settings/tokens
  username: "VotreNom"       # Nom d'utilisateur GitHub

modrinth_api_key: "mrp_..."  # PAT avec le scope "Create versions" — https://modrinth.com/settings/pats

smithed_api_key: "..."       # Token avec le scope WRITE_PACKS — https://smithed.net/settings?tab=account

# Optionnel : destinations SFTP utilisées par le plugin copy_to_destination
sftp:
  user@host:
    password: "votre_mot_de_passe"
```

> ⚠️ Ne committez jamais `credentials.yml` dans votre dépôt. Ajoutez-le à votre `.gitignore` si vous le gardez dans un dossier de projet.

---

## GitHub

`upload_to_github` crée une release taguée sur GitHub, y upload tous les artefacts de build correspondants et retourne une **chaîne de changelog** générée depuis les commits depuis le tag précédent.

### Identifiants requis
| Clé | Description |
|-----|-------------|
| `github.api_key` | Personal Access Token GitHub |
| `github.username` | Nom d'utilisateur GitHub |

### Configuration

| Clé | Requis | Description |
|-----|--------|-------------|
| `project_name` | ✅ | Nom du dépôt (utilisé pour construire l'URL de la release) |
| `version` | ✅ | Chaîne de version, ex. `"1.2.3"` — devient le tag `v1.2.3` |
| `build_folder` | ✅ | Chemin vers le dossier contenant les zips buildés |
| `endswith` | ❌ | Liste de suffixes pour filtrer les fichiers uploadés (ex. `[".zip"]`) |

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
- Si le tag `v{version}` existe déjà, la release et le tag existants sont **supprimés** avant recréation.
- Upload chaque fichier de `build_folder` dont le nom se termine par un des suffixes `endswith`.
- Retourne le changelog généré sous forme de chaîne Markdown (utilisée en entrée des autres fonctions d'upload).

---

## Modrinth

`upload_to_modrinth` synchronise la description et le résumé du projet sur Modrinth, puis upload une nouvelle version avec les zips buildés.

### Identifiants requis
| Clé | Description |
|-----|-------------|
| `modrinth_api_key` | PAT Modrinth avec le scope "Create versions" |

### Configuration

| Clé | Requis | Description |
|-----|--------|-------------|
| `slug` | ✅ | Namespace du projet sur Modrinth (ex. `"simplenergy"`) |
| `project_name` | ✅ | Nom d'affichage du projet |
| `version` | ✅ | Chaîne de version |
| `summary` | ✅ | Description courte affichée sur la carte du projet |
| `description_markdown` | ✅ | Description complète en Markdown (généralement `README.md`) |
| `version_type` | ✅ | `"release"`, `"beta"`, ou `"alpha"` |
| `build_folder` | ✅ | Chemin vers le dossier contenant les zips buildés |
| `dependencies` | ❌ | Liste d'objets de dépendances Modrinth (défaut : `[]`) |
| `package_as_mod` | ❌ | `"all"` ou `"separate"` — upload aussi des jars mod pour les plateformes de loaders |
| `mod_platforms` | ❌ | Liste de plateformes pour l'empaquetage mod (défaut : `["fabric", "forge", "neoforge", "quilt"]`) |

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
- Met toujours à jour la description et le résumé du projet **avant** d'uploader la version.
- Si la version existe déjà, propose `y/N` — répondre `y` la supprime et la recrée.
- Avec `package_as_mod = "all"`, upload une version datapack et une version mod couvrant toutes les plateformes.
- Avec `package_as_mod = "separate"`, upload une version datapack et une version mod distincte par plateforme.

---

## Smithed

`upload_to_smithed` enregistre une nouvelle version sur Smithed. Il résout automatiquement les liens de téléchargement depuis la release GitHub créée à l'étape précédente.

### Identifiants requis
| Clé | Description |
|-----|-------------|
| `smithed_api_key` | Token Smithed avec le scope `WRITE_PACKS` |
| `github.api_key` | PAT GitHub (utilisé pour résoudre les URLs des artefacts) |
| `github.username` | Nom d'utilisateur GitHub |

### Configuration

| Clé | Requis | Description |
|-----|--------|-------------|
| `project_id` | ✅ | ID / namespace du projet Smithed |
| `project_name` | ✅ | Nom du dépôt GitHub (utilisé pour construire les URLs de téléchargement) |
| `version` | ✅ | Chaîne de version |

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
- Résout les URLs de téléchargement du datapack et du resource pack depuis la release GitHub (`_with_libs.zip` en priorité, repli sur le zip simple).
- Les versions Minecraft supportées sont déterminées automatiquement depuis la configuration du projet (champ `mc_supports` ou `minecraft` dans `beet.yml`).
- Les chaînes de version snapshot et release-candidate sont exclues de la liste `supports`.

---

## PlanetMinecraft

`upload_to_pmc` n'a pas d'API — il ouvre la page d'édition du projet dans votre navigateur et copie le changelog converti en **BBCode** dans le presse-papier, prêt à coller.

### Configuration

| Clé           | Requis | Description                                             |
| ------------- | ------ | ------------------------------------------------------- |
| `project_url` | ✅      | URL de la page de gestion du projet sur PlanetMinecraft |
| `version`     | ✅      | Chaîne de version (incluse pour validation)             |

### Exemple
```python
pmc_config: JsonDict = {
    "project_url": "https://www.planetminecraft.com/account/manage/data-packs/VOTRE_ID/",
    "version": cfg.version,
}
upload_to_pmc(pmc_config, changelog)
```

### Comportement
- Ouvre `project_url` dans le navigateur par défaut.
- Convertit le changelog Markdown en BBCode et le copie dans le presse-papier.
- Affiche un message de confirmation — collez le contenu dans la description de version sur la page.

---

## Script Complet d'Exemple

Un `upload.py` complet pour un projet typique (exemple de [SimplEnergy](https://github.com/Stoupy51/SimplEnergy/blob/main/upload.py)):

```python
# pyright: reportUnknownVariableType=false
# Imports
from beet import ProjectConfig
from stewbeet import JsonDict
from stewbeet.continuous_delivery import load_credentials, upload_to_github, upload_to_modrinth, upload_to_pmc, upload_to_smithed
from stewbeet.utils import get_project_config
from stouputils.io import read_file

# Récupère les identifiants et tente de trouver la configuration beet
credentials: dict[str, str] = load_credentials("~/stewbeet/credentials.yml")
cfg: ProjectConfig = get_project_config()

# Constantes
SUMMARY: str = """
Description courte de votre projet affichée sur la carte Modrinth.
"""

# Upload sur GitHub (génère également le changelog)
github_config: JsonDict = {
    "project_name": cfg.name,
    "version": cfg.version,
    "build_folder": cfg.output,
    "endswith": [".zip"],
}
changelog: str = upload_to_github(credentials, github_config)

# Upload sur Modrinth
modrinth_config: JsonDict = {
    "slug": cfg.id,
    "project_name": cfg.name,
    "version": cfg.version,
    "summary": SUMMARY,
    "description_markdown": read_file(f"{cfg.directory}/README.md"),
    "dependencies": [],
    "version_type": "beta",
    "build_folder": cfg.output,
}
upload_to_modrinth(credentials, modrinth_config, changelog)

# Upload sur Smithed
smithed_config: JsonDict = {
    "project_id": cfg.id,
    "project_name": cfg.name,
    "version": cfg.version,
}
upload_to_smithed(credentials, smithed_config, changelog)

# Upload sur PlanetMinecraft
pmc_config: JsonDict = {
    "project_url": "https://www.planetminecraft.com/account/manage/data-packs/VOTRE_ID/",
    "version": cfg.version,
}
upload_to_pmc(pmc_config, changelog)
```

## Glossaire

| Terme | Signification |
|-------|---------------|
| **`load_credentials`** | : Lit `~/stewbeet/credentials.yml` (ou un chemin personnalisé) et retourne un dictionnaire de clés API et secrets utilisés par les fonctions d'upload. |
| **`get_project_config`** | : Lit le `beet.yml` du répertoire courant et retourne un objet `ProjectConfig` avec les champs `name`, `version`, `id`, `output` et `directory`. |
| **Changelog** | : Une chaîne Markdown générée automatiquement à partir des commits Git depuis le dernier tag. Retournée par `upload_to_github` et transmise aux autres fonctions d'upload. |
| **`version_type`** | : La maturité de la release pour Modrinth — `"release"`, `"beta"`, ou `"alpha"`. |
| **`package_as_mod`** | : Mode d'empaquetage Modrinth optionnel qui encapsule votre datapack en jar de mod Fabric/Forge/NeoForge/Quilt en plus de l'upload normal. |

## Prochaines étapes

- [compute_sha1](../plugins/compute_sha1.md) — les hashes publiés avec les releases.
- [Configurer le build](../3_beet_config/fr.md) — le build que la publication exécute.
- [Bibliothèques de datapack](../5_dependencies/fr.md) — les vérifications de version au runtime.
