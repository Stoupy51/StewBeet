
# Imports
import os

import stouputils as stp

# Constants
ROOT: str = stp.relative_path(stp.get_root_path(__file__, go_up=1))
TEMPLATES_FOLDER: str = f"{ROOT}/templates"
TEMPLATES: list[str] = [
    f"{TEMPLATES_FOLDER}/minimal",
    f"{TEMPLATES_FOLDER}/basic",
    f"{TEMPLATES_FOLDER}/extensive",
]

# Main function
def main() -> None:
    """
    Main function to create zip archives of templates.
    """
    for template in TEMPLATES:
        stp.make_archive(
            source=template,
            destinations=f"{TEMPLATES_FOLDER}/{os.path.basename(template)}_template.zip",
            create_dir=True,
            ignore_patterns="__pycache__, .beet_cache, build, .venv, uv.lock",
        )
        stp.info(f"Created archive for '{template}' template.")

if __name__ == "__main__":
    main()

