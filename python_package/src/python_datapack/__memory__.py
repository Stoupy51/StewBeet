
# pyright: reportAssignmentType=false
# ruff: noqa: RUF012
from collections.abc import Iterable
from typing import Any

from beet import ProjectConfig


# Python Datapack Config class
class StewBeetCfg(ProjectConfig):
	""" Main configuration class for Python Datapack projects. """

	# Folders
	ROOT: str = None
	""" [Required] Absolute path to the project's root directory. """
	SOURCE_FOLDER: str = None
	""" [Required] Directory containing source files that will be processed by the beet build system. (Will be used to infer paths SOURCE_FOLDER/datapack and SOURCE_FOLDER/resource_pack) """
	BUILD_FOLDER: str = None
	""" [Required] Output directory where the final datapack and resource pack will be generated. """
	ASSETS_FOLDER: str = None
	""" [Required] Directory containing all project assets including textures, sounds, and other media files. """
	LIBS_FOLDER: str | None = None
	""" Directory containing libraries that will be copied to the build destination, and merged using Smithed Weld if enabled. """
	BUILD_COPY_DESTINATIONS: tuple[Iterable[str], Iterable[str]] = ([], [])
	""" Optional list of destination paths where generated files will be copied. Can be empty if no copying is needed. """

	# Dev constants
	DATABASE_DEBUG: str = "" # TODO
	""" Path where database debug information will be dumped. If empty, defaults to  """
	ENABLE_TRANSLATIONS: bool = True
	""" Will convert all the text components to translate and generate a lang file in the resource pack. Meaning you can easily translate the datapack in multiple languages! """
	MERGE_LIBS: bool = True
	""" Enables merging of libraries with the datapack and resource pack using Smithed Weld. """

	# Project information
	AUTHOR: str = None
	""" Author(s) name(s) displayed in pack.mcmeta, also used to add 'convention.debug' tag to the players of the same name(s) <-- showing additionnal displays like datapack loading """
	PROJECT_NAME: str = None
	""" Name of the project that will be used in messages, item lore, etc. """
	VERSION: str = None
	""" Project version in semantic versioning format (e.g., 1.0.0 or 2.84.615). """
	NAMESPACE: str = None
	""" Simplified project name used for function and tag namespacing. Must match merge folder namespace. """
	DESCRIPTION: str = ""	# TODO
	""" Pack description for pack.mcmeta. Defaults to "{PROJECT_NAME} [{VERSION}] by {AUTHOR}" if empty. """
	DEPENDENCIES: dict[str, dict[str, list[int] | str]] = {}
	""" Automagically, the datapack will check for the presence of dependencies and their minimum required versions at runtime.
	The url is used when the dependency is not found to suggest where to get it.
	The version dict key contains the minimum required version of the dependency in [major, minor, patch] format.
	The main key is the dependency namespace to check for.
	The name can be whatever you want, it's just used in messages

	Example:
	{
		# Example for DatapackEnergy >= 1.8.0
		"energy": {"version":[1, 8, 0], "name":"DatapackEnergy", "url":"https://github.com/ICY105/DatapackEnergy"},
	}
	"""

	# Technical constants
	SOURCE_LORE: list[Any] | str = "auto"	# TODO
	""" Custom item lore configuration. If set to "auto", uses project icon followed by PROJECT_NAME. """

	# Manual configuration
	class Manual:
		IS_ENABLED: bool = True
		""" Controls manual/guide generation. Note: Malformed database items may cause server log spam. """

		DEBUG_MODE: bool = False
		""" Enables grid display in the manual for debugging. """

		MANUAL_OVERRIDES: str | None = None
		""" Path to directory containing custom manual assets that override defaults. """

		MANUAL_HIGH_RESOLUTION: bool = True
		""" Enables high-resolution crafting displays in the manual. """

		CACHE_PATH: str = None
		""" Directory for storing cached manual assets. """

		CACHE_ASSETS: bool = True
		""" Enables caching of Minecraft assets and item renders (manual/items/*.png). """

		CACHE_PAGES: bool = False
		""" Enables caching of manual content and images (manual/pages/*.png). """

		JSON_DUMP_PATH: str = "" # TODO
		""" Path for manual debug dump. Defaults to "{Manual.CACHE_PATH}/debug_manual.json" if empty. """

		MANUAL_NAME: str = "" # TODO
		""" Manual title used in book and first page. Defaults to "{PROJECT_NAME} Manual". """

		MAX_ITEMS_PER_ROW: int = 5
		""" Maximum number of items displayed per row in manual (max: 6). """

		MAX_ROWS_PER_PAGE: int = 5
		""" Maximum number of rows displayed per page in manual (max: 6). """

		OPENGL_RESOLUTION: int = 256
		""" Resolution for OpenGL renders in manual (recommended: 256x256). """

		MANUAL_FIRST_PAGE_TEXT: list[Any] | str = [{"text":"Modify in config.py the text that will be shown in this first manual page", "color":"#505050"}]
		""" Text component used for the manual's first page. """

	Beet: ProjectConfig = ProjectConfig(
		require=[
			"bolt",
			"mecha.contrib.relative_location",
			"mecha.contrib.nested_location"
		],
		pipeline=[
			""
		]
	)
	""" Beet project configuration.
	Allows overriding individual or multiple configuration elements
	such as pipeline configuration, dependency management, etc.

	Note: Python Datapack automatically completes missing beet configuration elements (namespace, etc.) - only override if necessary.
	"""

