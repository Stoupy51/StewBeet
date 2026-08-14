""" Pooled SFTP connections shared by every plugin that writes to an ``sftp://`` destination.

Opening an SSH connection costs roughly half a second: importing paramiko, the key exchange, the
authentication and the first channel. That dwarfs the transfers themselves when a single zip changed.
One authenticated transport is therefore kept per server for the whole process, and each thread opens a
cheap channel on top of it instead of shaking hands again. ``SftpPool.warmup_from_context`` starts all of
that in the background at the very beginning of the build, so the connection is already waiting by the
time the copy plugin runs at the end.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
import posixpath
import threading
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import stouputils as stp
from beet import Context

if TYPE_CHECKING:
	from paramiko import SFTPClient, SSHClient

# Constants
CREDENTIALS_PATH: str = "~/stewbeet/credentials.yml"
""" YAML file holding the `sftp: {"user@host": {password: ...}}` entries used by destinations without an inline password. """
DESTINATION_KEYS: tuple[str, ...] = ("datapack", "resource_pack")
""" Keys of `meta.stewbeet.build_copy_destinations` that can hold remote destinations. """


# Functions
def is_sftp_path(path: str) -> bool:
	""" Return whether the given destination is a remote SFTP URL rather than a local path.

	Args:
		path (str): The destination to test.
	Returns:
		bool: True when the destination is an ``sftp://`` URL.

	Examples:
		>>> is_sftp_path("sftp://bob@example.com/datapacks")
		True
		>>> is_sftp_path("D:/minecraft/latest/resourcepacks")
		False
	"""
	return str(path).startswith("sftp://")


def remote_path_of(url: str) -> str:
	""" Return the server-side path of a destination URL.

	Args:
		url (str): An ``sftp://user[:pass]@host[:port]/path`` URL.
	Returns:
		str: The path part of the URL, always POSIX style.

	Examples:
		>>> remote_path_of("sftp://bob@example.com/sftp/Switch/datapacks/x.zip")
		'/sftp/Switch/datapacks/x.zip'
	"""
	return urllib.parse.urlparse(url).path


# Classes
@dataclass(frozen=True)
class SftpEndpoint:
	""" The SSH server behind one or more ``sftp://`` destination URLs. """
	host: str
	""" Hostname of the server. """
	port: int
	""" SSH port, 22 unless the URL says otherwise. """
	username: str
	""" User to authenticate as. """
	password: str | None
	""" Password to authenticate with, or None to let paramiko try the local keys and agent. """

	@staticmethod
	@stp.simple_cache
	def resolve_password(netloc: str) -> str | None:
		""" Read the password of a `user@host` pair from the stewbeet credentials file.

		Cached for the whole build: every destination resolves its endpoint, and re-parsing the credentials
		file each time costs more than the upload it is preparing.

		Args:
			netloc (str): The ``user@host`` part of the destination URL, used as credentials key.
		Returns:
			str | None: The configured password, or None when there is none to be found.
		"""
		creds_path: str = stp.clean_path(CREDENTIALS_PATH)
		if not os.path.exists(creds_path):
			return None
		import yaml
		with open(creds_path) as f:
			creds = yaml.safe_load(f)
		return creds.get("sftp", {}).get(netloc, {}).get("password")

	@staticmethod
	def from_url(url: str) -> SftpEndpoint:
		""" Parse a destination URL into the server it points at.

		Args:
			url (str): An ``sftp://user[:pass]@host[:port]/path`` URL.
		Returns:
			SftpEndpoint: The server behind that URL, password taken from the credentials file when the URL has none.

		Examples:
			>>> SftpEndpoint.from_url("sftp://bob:hunter2@example.com/datapacks/x.zip")
			SftpEndpoint(host='example.com', port=22, username='bob', password='hunter2')
		"""
		parsed: urllib.parse.ParseResult = urllib.parse.urlparse(url)
		return SftpEndpoint(
			host     = parsed.hostname or "",
			port     = parsed.port or 22,
			username = parsed.username or "",
			password = parsed.password or SftpEndpoint.resolve_password(parsed.netloc),
		)


class SftpChannels(threading.local):
	""" Per-thread SFTP channel holder: a channel is cheap to open but not safe to share between threads. """
	channel: SFTPClient | None = None
	""" This thread's channel on the shared transport, opened on first use. """


@dataclass
class SftpConnection:
	""" One authenticated SSH transport, plus one SFTP channel per thread that asks for it. """
	endpoint: SftpEndpoint
	""" The server this connection talks to. """
	ready: threading.Event = field(default_factory=threading.Event)
	""" Set once the connection attempt finished, successfully or not. """
	client: SSHClient | None = None
	""" The authenticated client, or None while connecting and after a failure. """
	error: BaseException | None = None
	""" The failure raised while connecting, kept to be re-raised in the threads asking for a channel. """
	channels: SftpChannels = field(default_factory=SftpChannels)
	""" The per-thread channels opened on this connection. """

	def connect(self) -> None:
		""" Open and authenticate the transport, storing any failure instead of raising it.

		This usually runs in the warm-up thread, where nothing would catch an exception. The error is kept
		and re-raised by `channel`, so a broken connection is reported where the copy actually happens.
		"""
		try:
			import paramiko  # Local import: pulls in cryptography, useless for local-only destinations

			# With a password in hand, skip paramiko's key hunt: it decrypts every ~/.ssh key and burns a
			# failed publickey round trip before falling back to the password anyway.
			try_keys: bool = self.endpoint.password is None
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.connect(
				self.endpoint.host,
				port=self.endpoint.port,
				username=self.endpoint.username,
				password=self.endpoint.password,
				look_for_keys=try_keys,
				allow_agent=try_keys,
			)
			self.client = client
		except BaseException as e:
			self.error = e
		finally:
			self.ready.set()

	def is_usable(self) -> bool:
		""" Return whether this connection is still worth reusing, either still connecting or holding a live transport.

		Returns:
			bool: False once the handshake failed or the server dropped the transport between two builds.
		"""
		if not self.ready.is_set():
			return True
		if self.client is None:
			return False
		transport = self.client.get_transport()
		return transport is not None and transport.is_active()

	def channel(self) -> SFTPClient:
		""" Return this thread's SFTP channel, opening one on the shared transport when needed.

		Waits for the background warm-up to be done. Opening a channel is a single round trip, unlike the
		full handshake `connect` already paid once for the whole build.

		Returns:
			SFTPClient: A channel this thread can use on its own.
		"""
		self.ready.wait()
		if self.client is None:
			raise self.error or ConnectionError(f"Could not connect to '{self.endpoint.username}@{self.endpoint.host}'")
		if self.channels.channel is None:
			self.channels.channel = self.client.open_sftp()
		return self.channels.channel


class SftpPool:
	""" Process-wide registry of SFTP connections, one per server. """

	CONNECTIONS: ClassVar[dict[SftpEndpoint, SftpConnection]] = {}
	""" Live connections, keyed by server so several destinations on the same host share one transport. """
	LOCK: ClassVar[threading.Lock] = threading.Lock()
	""" Guards CONNECTIONS so the warm-up and the copy workers cannot open two transports for one server. """

	@staticmethod
	def get(endpoint: SftpEndpoint) -> SftpConnection:
		""" Return the connection to a server, opening it now when nothing opened it yet.

		Args:
			endpoint (SftpEndpoint): The server to reach.
		Returns:
			SftpConnection: The shared connection, possibly still being opened by another thread.
		"""
		with SftpPool.LOCK:
			if (existing := SftpPool.CONNECTIONS.get(endpoint)) is not None:
				return existing
			connection: SftpConnection = SftpConnection(endpoint=endpoint)
			SftpPool.CONNECTIONS[endpoint] = connection

		# Connect outside the lock: threads asking for the same server meanwhile get this very object and
		# wait on its `ready` event, instead of queueing behind the lock for the whole handshake.
		connection.connect()
		return connection

	@staticmethod
	def channel_for(url: str) -> tuple[SFTPClient, str]:
		""" Return the channel serving a destination URL, along with the path to write to on the server.

		Args:
			url (str): An ``sftp://user[:pass]@host[:port]/path`` URL.
		Returns:
			tuple[SFTPClient, str]: This thread's channel, and the remote path parsed out of the URL.
		"""
		return SftpPool.get(SftpEndpoint.from_url(url)).channel(), remote_path_of(url)

	@staticmethod
	def warmup(urls: Iterable[str]) -> None:
		""" Start connecting to every server behind the given destinations, in the background.

		Called at the beginning of the build so the handshake overlaps the rest of the pipeline: by the time
		the copy plugin runs at the end, `get` finds a connection that is already open. Connections left dead
		by a previous build are dropped first, which is what makes `stewbeet watch` reconnect on its own.

		Args:
			urls (Iterable[str]): Destinations to warm up, local paths are ignored.
		"""
		endpoints: list[SftpEndpoint] = list(dict.fromkeys(SftpEndpoint.from_url(url) for url in urls if is_sftp_path(url)))
		if not endpoints:
			return
		with SftpPool.LOCK:
			for endpoint, connection in list(SftpPool.CONNECTIONS.items()):
				if not connection.is_usable():
					del SftpPool.CONNECTIONS[endpoint]
		for endpoint in endpoints:
			threading.Thread(target=SftpPool.get, args=(endpoint,), daemon=True).start()

	@staticmethod
	def warmup_from_context(ctx: Context) -> None:
		""" Start warming up every remote destination listed in `meta.stewbeet.build_copy_destinations`.

		Args:
			ctx (Context): The beet context.
		"""
		destinations = ctx.meta.get("stewbeet", {}).get("build_copy_destinations", {})
		SftpPool.warmup([str(dest) for key in DESTINATION_KEYS for dest in destinations.get(key, [])])

	@staticmethod
	def list_sizes(url: str) -> dict[str, int] | None:
		""" List the directory holding a destination, as a mapping of remote path to file size.

		Listing costs one round trip and keeps the upload cache honest: a file deleted or truncated
		server-side gets uploaded again instead of being wrongly considered up to date. A missing directory
		is detected from the listing itself, which saves the extra round trip an existence check would cost.

		Args:
			url (str): An ``sftp://user[:pass]@host[:port]/path`` URL pointing at a file.
		Returns:
			dict[str, int] | None: Sizes of every entry of the parent directory, or None if it does not exist.
		"""
		channel, remote_path = SftpPool.channel_for(url)
		remote_dir: str = posixpath.dirname(remote_path)
		try:
			entries = channel.listdir_attr(remote_dir)
		except OSError:
			return None
		return {posixpath.join(remote_dir, entry.filename): (entry.st_size or 0) for entry in entries}

	@staticmethod
	def put(url: str, src: str) -> None:
		""" Upload a local file to a destination URL.

		Args:
			url (str): The ``sftp://`` destination to write to.
			src (str): Path of the local file to send.
		"""
		channel, remote_path = SftpPool.channel_for(url)
		channel.put(src, remote_path)

	@staticmethod
	def remove(url: str) -> None:
		""" Delete the file a destination URL points at, doing nothing when it is already gone.

		Args:
			url (str): The ``sftp://`` destination to delete.
		"""
		channel, remote_path = SftpPool.channel_for(url)
		try:
			channel.remove(remote_path)
		except OSError:
			pass

