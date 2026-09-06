
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from .download_manager import (
	BUILD_CACHE as BUILD_CACHE,
	MODRINTH_API_BASE as MODRINTH_API_BASE,
	SMITHED_API_BASE as SMITHED_API_BASE,
	DownloadedLib as DownloadedLib,
	get_lib_paths as get_lib_paths,
	lookup_static as lookup_static,
	mc_compatible as mc_compatible,
	mc_str as mc_str,
	mc_tuple as mc_tuple,
	parse_version as parse_version,
	resolve_modrinth_lib as resolve_modrinth_lib,
	resolve_smithed_lib as resolve_smithed_lib,
	resolve_static_lib as resolve_static_lib,
	version_str as version_str,
)
from .network import (
	CONNECTIVITY as CONNECTIVITY,
	CONNECTIVITY_LOCK as CONNECTIVITY_LOCK,
	DOWNLOAD_ATTEMPTS as DOWNLOAD_ATTEMPTS,
	DOWNLOAD_DELAY as DOWNLOAD_DELAY,
	DOWNLOAD_LOCKS as DOWNLOAD_LOCKS,
	DOWNLOAD_LOCKS_GUARD as DOWNLOAD_LOCKS_GUARD,
	HEADERS as HEADERS,
	HTTP_HINTS as HTTP_HINTS,
	PROBE_TIMEOUT as PROBE_TIMEOUT,
	PROBE_URLS as PROBE_URLS,
	SOCKET_HINTS as SOCKET_HINTS,
	TRANSIENT_STATUS as TRANSIENT_STATUS,
	TransientDownloadError as TransientDownloadError,
	attempt_download as attempt_download,
	cached_json as cached_json,
	cached_zip as cached_zip,
	connectivity_verdict as connectivity_verdict,
	describe_body as describe_body,
	describe_network_error as describe_network_error,
	download_lock as download_lock,
	download_to_cache as download_to_cache,
	host_answers as host_answers,
	internet_reachable as internet_reachable,
	is_transient as is_transient,
	socket_hint as socket_hint,
)
from .official_libs import (
	OFFICIAL_LIBS as OFFICIAL_LIBS,
	detection_markers as detection_markers,
	official_lib_used as official_lib_used,
)

