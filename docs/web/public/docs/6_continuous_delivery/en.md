# Shipping releases automatically

StewBeet provides a single `upload.py` script pattern that handles publishing a new release to all major distribution platforms in one command.<br>
You call each platform's upload function in sequence: GitHub first (it generates the changelog), then Modrinth, Smithed, and PlanetMinecraft with that changelog.<br>
Credentials are stored **outside** the project in `~/stewbeet/credentials.yml` so they are never accidentally committed.

**Real-world Example**: [SimplEnergy/upload.py](https://github.com/Stoupy51/SimplEnergy/blob/main/upload.py) <br>  
**Source Code**: [stewbeet/continuous_delivery/](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/continuous_delivery/) <br>

- Centralise all API credentials in a single file outside the repository
- Create a tagged GitHub release and upload build artifacts automatically
- Publish to Modrinth with description sync and optional mod packaging
- Register a new version on Smithed linking to the GitHub release assets
- Open the PlanetMinecraft edit page and copy the BBCode changelog to the clipboard

## Credentials Setup

Create the file `~/stewbeet/credentials.yml` (i.e. `C:\Users\YourName\stewbeet\credentials.yml` on Windows):

```yaml
github:
  api_key: "ghp_..."         # Personal Access Token: https://github.com/settings/tokens
  username: "YourUsername"   # GitHub account username

modrinth_api_key: "mrp_..."  # PAT with "Create versions" scope: https://modrinth.com/settings/pats

smithed_api_key: "..."       # Token with WRITE_PACKS scope: https://smithed.net/settings?tab=account

# Optional: SFTP destinations used by copy_to_destination plugin
sftp:
  user@host:
    password: "your_password"
```

> ⚠️ Never commit `credentials.yml` to version control. Add it to your `.gitignore` if you keep it inside a project folder.

---

## GitHub

`upload_to_github` creates a tagged release on GitHub, uploads all matching build artifacts, and returns a **changelog string** generated from commits since the previous tag.

### Required credentials
| Key | Description |
|-----|-------------|
| `github.api_key` | GitHub Personal Access Token |
| `github.username` | GitHub account username |

### Configuration

| Key | Required | Description |
|-----|----------|-------------|
| `project_name` | ✅ | Repository name (used to construct the release URL) |
| `version` | ✅ | Version string, e.g. `"1.2.3"`: becomes tag `v1.2.3` |
| `build_folder` | ✅ | Path to the folder containing the built zip files |
| `endswith` | ❌ | List of suffixes to filter uploaded files (e.g. `[".zip"]`) |

### Example
```python
github_config: JsonDict = {
    "project_name": cfg.name,
    "version": cfg.version,
    "build_folder": cfg.output,
    "endswith": [".zip"],
}
changelog: str = upload_to_github(credentials, github_config)
```

### Behaviour
- If the tag `v{version}` already exists, the existing release and tag are **deleted** before recreating.
- Uploads every file in `build_folder` whose name ends with one of the `endswith` suffixes.
- Returns the generated changelog as a Markdown string (used as input to the other upload functions).

---

## Modrinth

`upload_to_modrinth` syncs the project description and summary on Modrinth, then uploads a new version with the built zip files attached.

### Required credentials
| Key | Description |
|-----|-------------|
| `modrinth_api_key` | Modrinth PAT with "Create versions" scope |

### Configuration

| Key | Required | Description |
|-----|----------|-------------|
| `slug` | ✅ | Project namespace on Modrinth (e.g. `"simplenergy"`) |
| `project_name` | ✅ | Display name of the project |
| `version` | ✅ | Version string |
| `summary` | ✅ | Short description shown on the project card |
| `description_markdown` | ✅ | Full project description in Markdown (usually `README.md`) |
| `version_type` | ✅ | `"release"`, `"beta"`, or `"alpha"` |
| `build_folder` | ✅ | Path to the folder containing the built zip files |
| `dependencies` | ❌ | List of Modrinth dependency objects (default: `[]`) |
| `package_as_mod` | ❌ | `"all"` or `"separate"`: also uploads mod jars for loader platforms |
| `mod_platforms` | ❌ | List of platforms for mod packaging (default: `["fabric", "forge", "neoforge", "quilt"]`) |

### Example
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

### Behaviour
- Always updates the project description and summary **before** uploading the version.
- If the version already exists, prompts `y/N`: answering `y` deletes and recreates it.
- With `package_as_mod = "all"`, uploads one datapack version and one mod version covering all platforms.
- With `package_as_mod = "separate"`, uploads one datapack version and a separate mod version per platform.

---

## Smithed

`upload_to_smithed` registers a new version on Smithed. It resolves download links automatically from the GitHub release created in the previous step.

### Required credentials
| Key | Description |
|-----|-------------|
| `smithed_api_key` | Smithed token with `WRITE_PACKS` scope |
| `github.api_key` | GitHub PAT (used to resolve the release asset URLs) |
| `github.username` | GitHub account username |

### Configuration

| Key | Required | Description |
|-----|----------|-------------|
| `project_id` | ✅ | Smithed project ID / namespace |
| `project_name` | ✅ | Repository name on GitHub (used to build download URLs) |
| `version` | ✅ | Version string |

### Example
```python
smithed_config: JsonDict = {
    "project_id": cfg.id,
    "project_name": cfg.name,
    "version": cfg.version,
}
upload_to_smithed(credentials, smithed_config, changelog)
```

### Behaviour
- Resolves datapack and resource pack download URLs from the GitHub release (`_with_libs.zip` first, falls back to the plain zip).
- Supported Minecraft versions are determined automatically from the project configuration (`mc_supports` or `minecraft` field in `beet.yml`).
- Snapshot and release-candidate version strings are excluded from the `supports` list.

---

## PlanetMinecraft

`upload_to_pmc` has no API. It opens the project's edit page in your browser and copies the changelog converted to **BBCode** to the clipboard, ready to paste.

### Configuration

| Key           | Required | Description                                           |
| ------------- | -------- | ----------------------------------------------------- |
| `project_url` | ✅        | URL to the project management page on PlanetMinecraft |
| `version`     | ✅        | Version string (included for validation)              |

### Example
```python
pmc_config: JsonDict = {
    "project_url": "https://www.planetminecraft.com/account/manage/data-packs/5305840/",
    "version": cfg.version,
}
upload_to_pmc(pmc_config, changelog)
```

### Behaviour
- Opens `project_url` in the default browser.
- Converts the Markdown changelog to BBCode and copies it to the clipboard.
- Prints a confirmation message: paste the clipboard content into the version description on the page.

---

## Full Example Script

A complete `upload.py` for a typical project (example from [SimplEnergy](https://github.com/Stoupy51/SimplEnergy/blob/main/upload.py)):

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
SimplEnergy is a simple Technology data pack created to add simple energy mechanics in your survival world.
Also, it has been made to help the development of energy data packs by using an energy library as simple as possible.
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

## Glossary

| Term | Meaning |
|------|---------|
| **`load_credentials`** | Reads `~/stewbeet/credentials.yml` (or a custom path) and returns a dictionary of API keys and secrets used by the upload functions. |
| **`get_project_config`** | Reads the `beet.yml` in the current directory and returns a `ProjectConfig` object with `name`, `version`, `id`, `output`, and `directory` fields. |
| **Changelog** | A Markdown string generated automatically from Git commits since the last tag. Returned by `upload_to_github` and forwarded to the other upload functions. |
| **`version_type`** | The release maturity for Modrinth: `"release"`, `"beta"`, or `"alpha"`. |
| **`package_as_mod`** | Optional Modrinth packaging mode that wraps your datapack as a Fabric/Forge/NeoForge/Quilt mod jar alongside the normal datapack upload. |

## Next steps

- [compute_sha1](../plugins/compute_sha1.md): the hashes releases are published with.
- [Configuring the build](../3_beet_config/en.md): the build the release pipeline runs.
- [Using datapack libraries](../5_dependencies/en.md): version checks your released pack performs.
