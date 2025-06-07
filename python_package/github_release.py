
# Imports
from src.stewbeet.continuous_delivery import load_credentials, upload_to_github

# Get credentials
credentials: dict = load_credentials("~/stewbeet/credentials.yml")

# Upload to GitHub
from upgrade import current_version

github_config: dict = {
	"project_name": "stewbeet",
	"version": current_version,
	"build_folder": "",
}
changelog: str = upload_to_github(credentials, github_config)

