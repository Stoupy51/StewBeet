
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point (runs after all definition plugins)
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Basic arithmetic equation: set, add, multiply, divide, modulo (method chaining)
    equation = (
        ScoreboardEquation("#value", f"{ns}.data")
        .set(10)
        .add(5)
        .multiply(2)
        .divide(3)
        .modulo(100)
    )
    write_function(f"{ns}:equations/basic", str(equation))

    # Operator overloads: -, +, *, //, %
    equation2 = (ScoreboardEquation("#value2", f"{ns}.data").set(20) - 6 + 7) * 8 // 4 % 5
    write_function(f"{ns}:equations/operators", str(equation2))

    # Combine two equations into one function
    combined = (
        ScoreboardEquation("#health", f"{ns}.data").set(100).add(20)
    )
    write_function(f"{ns}:equations/combined", str(equation) + "\n" + str(combined))
