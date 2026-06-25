"""Filesystem paths for the manual's bundled assets/templates."""

# Imports
import stouputils as stp

# Root of this plugin package, and the runtime templates folder (assets copied here at build time,
# then optionally overlaid with the project's manual_overrides). Kept gitignored like v1.
MANUAL_ASSETS_PATH: str = stp.get_root_path(__file__)
TEMPLATES_PATH: str = MANUAL_ASSETS_PATH + "/templates"
