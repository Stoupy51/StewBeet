""" Turning an exception into the one line a reader can act on, shared by both runners. """
# Imports


# Functions
def root_cause(error: BaseException) -> BaseException:
	""" Walk to the exception that actually went wrong.

	beet wraps a plugin failure in PluginError, and stouputils turns any error into a prompt on stdin
	that fails with EOFError and then exits. Reporting either of those tells the reader nothing. The
	chain is walked to the deepest link, skipping the two that are only plumbing.

	Args:
		error (BaseException): The exception that reached the top.
	Returns:
		BaseException: The most specific cause worth naming.
	"""
	chain: list[BaseException] = []
	seen: set[int] = set()
	current: BaseException | None = error
	while current is not None and id(current) not in seen:
		seen.add(id(current))
		chain.append(current)
		current = current.__cause__ or current.__context__

	for candidate in reversed(chain):
		if not isinstance(candidate, SystemExit | EOFError):
			return candidate
	return chain[-1]

