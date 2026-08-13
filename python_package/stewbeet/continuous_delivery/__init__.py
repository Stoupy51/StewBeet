
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from .cd_utils import (
	get_supported_versions as get_supported_versions,
	load_credentials as load_credentials,
	replace_tilde as replace_tilde,
)
from .github import (
	GITHUB_API_URL as GITHUB_API_URL,
	build_github_config as build_github_config,
	create_github_release as create_github_release,
	create_github_tag as create_github_tag,
	delete_github_release as delete_github_release,
	delete_github_tag as delete_github_tag,
	extract_github_commit_data as extract_github_commit_data,
	get_github_commit_date as get_github_commit_date,
	get_github_sha as get_github_sha,
	upload_github_assets as upload_github_assets,
	upload_to_github as upload_to_github,
	validate_github_config as validate_github_config,
	validate_github_credentials as validate_github_credentials,
)
from .modrinth import (
	MODRINTH_API_URL as MODRINTH_API_URL,
	PROJECT_ENDPOINT as PROJECT_ENDPOINT,
	VERSION_ENDPOINT as VERSION_ENDPOINT,
	convert_datapack_to_mod as convert_datapack_to_mod,
	generate_fabric_metadata as generate_fabric_metadata,
	generate_forge_metadata as generate_forge_metadata,
	generate_quilt_metadata as generate_quilt_metadata,
	get_file_parts as get_file_parts,
	get_project as get_project,
	handle_existing_version as handle_existing_version,
	set_resource_pack_required as set_resource_pack_required,
	update_project_description as update_project_description,
	upload_to_modrinth as upload_to_modrinth,
)
from .pmc import (
	convert_list_block as convert_list_block,
	convert_markdown_to_bbcode as convert_markdown_to_bbcode,
	table_to_bbcode as table_to_bbcode,
	upload_to_pmc as upload_to_pmc,
)
from .smithed import (
	SMITHED_API_URL as SMITHED_API_URL,
	upload_to_smithed as upload_to_smithed,
	upload_version as upload_version,
	validate_config as validate_config,
	validate_credentials as validate_credentials,
)

