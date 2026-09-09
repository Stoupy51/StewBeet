# A StewBeet helper writing a function in the same build as the bolt file beside it.

# Imports
from beet import Context

from stewbeet.core import write_function


# Main entry point
def beet_default(ctx: Context) -> None:
    write_function("tns:written", "say written by the helper\n")
