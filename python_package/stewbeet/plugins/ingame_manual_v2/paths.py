"""Filesystem paths for the manual's bundled assets/templates."""

# Imports
import atexit
import shutil
import tempfile

import stouputils as stp

# Root of this plugin package, and the runtime templates folder (assets copied here at build time,
# then optionally overlaid with the project's manual_overrides). Lives in a per-process temporary
# directory so concurrent builds don't conflict with each other; removed on interpreter exit.
MANUAL_ASSETS_PATH: str = stp.get_root_path(__file__)
TEMPLATES_PATH: str = tempfile.mkdtemp(prefix="stewbeet_manual_v2_templates_").replace("\\", "/")
atexit.register(shutil.rmtree, TEMPLATES_PATH, ignore_errors=True)
