# A StewBeet helper writing into the implementation path a versioning plugin later moves.

# Imports
from beet import Context

from stewbeet.core import write_function


# Main entry point
def beet_default(ctx: Context) -> None:
    write_function("tns:impl/written", "say written by the helper\n")

