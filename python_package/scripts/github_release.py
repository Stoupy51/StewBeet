
# Imports
import stouputils.continuous_delivery as cd
from beet.core.utils import JsonDict
from stouputils.io import get_root_path

# Constants
ROOT: str = get_root_path(__file__, go_up=1)
CURRENT_VERSION: str = cd.get_version_from_pyproject(f"{ROOT}/pyproject.toml")
CREDENTIALS_PATH: str = "~/stewbeet/credentials.yml"
GITHUB_CONFIG: JsonDict = {
	"project_name": "stewbeet",
	"version": CURRENT_VERSION,
	"build_folder": f"{ROOT}/dist",
	"endswith": [
		f"{CURRENT_VERSION}.tar.gz",
		f"{CURRENT_VERSION}-py3-none-any.whl",
	],
}

# Main
if __name__ == "__main__":

	# Get credentials
	credentials: JsonDict = cd.load_credentials(CREDENTIALS_PATH)

	# Upload to GitHub
	changelog: str = cd.upload_to_github(credentials, GITHUB_CONFIG)

