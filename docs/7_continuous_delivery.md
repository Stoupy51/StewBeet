
# 🚀 Continuous Delivery
This guide will explain how to set up automatic deployment of your datapack to various platforms like GitHub, Modrinth, Smithed, and PlanetMinecraft.

## 📋 What is Continuous Delivery?
Continuous Delivery is the process of automatically publishing your datapack to distribution platforms whenever a new version is ready. The StewBeet Template provides tooling to make this process simple and consistent across multiple platforms.

## 🛠️ Setup Process
To set up continuous delivery for your datapack, follow these steps:

1. 📁 Create a `continuous_delivery` folder in your project root
2. ⚙️ Create configuration files for each platform you want to deploy to
3. 📝 Create an `upload.py` script that uses these configurations
4. 🚀 Run the upload script when you want to publish a new version


## 🔑 Credentials
For security, platform credentials are stored separately from your configuration. The `load_credentials` function reads these from a YAML file:

```python
credentials: dict[str, str] = load_credentials("~/python_datapack/credentials.yml")
```

The credentials file should have this structure:

```yaml
github:
  username: "your_github_username"
  api_key: "your_github_api_key"
modrinth_api_key: "your_modrinth_api_key"
smithed_api_key: "your_smithed_api_key"
```

⚠️ **IMPORTANT**: Never commit your credentials file to version control!


## 🔧 Platform Configurations

### 🐙 GitHub Configuration
GitHub configuration is simple with just a few required fields:

```python
github_config: dict = {
    "project_name": PROJECT_NAME,
    "version": VERSION,
    "build_folder": BUILD_FOLDER,
}
```

The configuration uses constants from your main `config.py` file to maintain consistency.<br>
See [github_config.py](https://github.com/Stoupy51/SimplEnergy/blob/main/continuous_delivery/github_config.py) for an example.

### 🔵 Modrinth Configuration
Modrinth requires more detailed information:

```python
modrinth_config: dict = {
    "slug": NAMESPACE,
    "project_name": PROJECT_NAME,
    "version": VERSION,
    "summary": SUMMARY,
    "description_markdown": DESCRIPTION_MARKDOWN,
    "dependencies": DEPENDENCIES,
    "version_type": VERSION_TYPE,
    "build_folder": BUILD_FOLDER,
}
```

- 📌 `slug`: Your project's unique identifier on Modrinth
- 📄 `summary`: A short description of your datapack
- 📝 `description_markdown`: Detailed description in Markdown format
- 🔗 `dependencies`: List of other projects your datapack depends on
- 🏷️ `version_type`: Release type ("release", "beta", or "alpha")

See [modrinth_config.py](https://github.com/Stoupy51/SimplEnergy/blob/main/continuous_delivery/modrinth_config.py) for an example.

### ⚒️ Smithed Configuration
Smithed has a simpler configuration:

```python
smithed_config: dict = {
    "project_id": NAMESPACE,
    "project_name": PROJECT_NAME,
    "version": VERSION,
}
```

See [smithed_config.py](https://github.com/Stoupy51/SimplEnergy/blob/main/continuous_delivery/smithed_config.py) for an example.

### 🌍 PlanetMinecraft Configuration
PlanetMinecraft configuration is the simplest:

```python
pmc_config: dict = {
    "project_url": PMC_URL,
    "version": VERSION,
}
```

- 🔗 `project_url`: The URL to your project's management page on PlanetMinecraft

See [pmc_config.py](https://github.com/Stoupy51/SimplEnergy/blob/main/continuous_delivery/pmc_config.py) for an example.


## 📤 Upload Script
Your main upload script will import these configurations and use them to publish your datapack:

```python
# Imports
from python_datapack.continuous_delivery import load_credentials, upload_to_github, upload_to_modrinth, upload_to_smithed, upload_to_pmc

# Get credentials
credentials: dict[str, str] = load_credentials("~/python_datapack/credentials.yml")

# Upload to GitHub (and get changelog)
from continuous_delivery.github_config import github_config
changelog: str = upload_to_github(credentials, github_config)

# Upload to Modrinth
from continuous_delivery.modrinth_config import modrinth_config
upload_to_modrinth(credentials, modrinth_config, changelog)

# Upload to Smithed
from continuous_delivery.smithed_config import smithed_config
upload_to_smithed(credentials, smithed_config, changelog)

# Upload to PlanetMinecraft
from continuous_delivery.pmc_config import pmc_config
upload_to_pmc(pmc_config, changelog)
```

Note that the GitHub upload returns a changelog string that is then used for the other platforms to ensure consistency.<br>
You can change this behavior as you want in the script.


## 🔄 Workflow Integration
You can, if you want, integrate your upload script with your development workflow in several ways:

1. 👨‍💻 **Manual upload**: Run `python upload.py` after building your datapack
2. 🪝 **Git hooks**: Set up a post-tag hook to run the upload script when you create a new version tag
3. ⚙️ **CI/CD pipelines**: Configure GitHub Actions or other CI systems to run your upload script

But I won't go into details here, as it's not the purpose of this template.


## 📚 Conclusion
You now know how to:
- 🛠️ Configure deployment for multiple platforms
- 🤖 Automate the release process for your datapack

This continuous delivery setup will save you time and ensure consistency when publishing new versions of your datapack!

Thank you for reading 🙌

