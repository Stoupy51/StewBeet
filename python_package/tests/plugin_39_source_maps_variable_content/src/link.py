# Content built in variables, the way a pack writes a function from a loop.

# Imports
from beet import Context

from stewbeet.core import McFunction, write_function


# Classes
class Mode:
	def sub(self, name: str, body: McFunction) -> None:
		write_named(f"tns:mode_{name}", body)


# Functions
def helper_lines() -> str:
	return "say from helper\nsay helper again\n"


def write_named(path: str, body: McFunction) -> None:
	write_function(path, body)


# Main entry point
def beet_default(ctx: Context) -> None:
	# Grown in a loop that skips an item, then finished inline in the call.
	grown: str = """
say grown head
"""
	for name in ("alpha", "beta", "skipped", "gamma"):
		if name == "skipped":
			continue
		grown += f"""
say grown loop {name}
say grown loop again {name}
"""
	write_function("tns:grown", grown + """
say grown tail
""")

	# One command per literal, the line break ending it.
	ended: str = ""
	for index in range(3):
		ended += f"say ended {index}\n"
	write_function("tns:ended", ended)

	# One command per literal, the line break starting it.
	started: str = ""
	for index in range(3):
		started += f"\nsay started {index}"
	write_function("tns:started", started)

	# Reused for a second function, whose lines must not come from what the first one held.
	reused: str = """
say reused first
"""
	write_function("tns:reused_first", reused)
	reused = """
say reused second
"""
	reused += helper_lines()
	reused += """
say reused second tail
"""
	write_function("tns:reused_second", reused)

	# Assigned in one branch of two, and grown in the one taken.
	if ctx.project_id == "tns":
		branched = "say branch taken\n"
		branched += "say branch grown\n"
	else:
		branched = "say branch not taken\n"
	write_function("tns:branched", branched)

	# An interpolation holding several lines, which every line after it moves down.
	block: str = "say inner one\nsay inner two"
	write_function("tns:expanded", f"""
say expanded before
{block}
say expanded after
""")

	# Handed to a function of the project that passes it on to a write, then through a method passing it on to that function.
	write_named("tns:forwarded", """
say forwarded
""")
	Mode().sub("method", """
say through a method
""")

