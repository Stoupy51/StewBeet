
# Equations

`ScoreboardEquation` and `StorageEquation` are chainable equation builders that turn a readable Python expression into Minecraft commands. Both generate a self-documenting output: the first line is a `# comment` showing the full equation, followed by the commands that compute it.

Use equations any time you need multi-step integer arithmetic in a datapack function. Instead of writing `scoreboard players operation` commands by hand, you build the expression in Python and call `str()` to get the full mcfunction block.

- Example file: [extensive/src/link.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py)
- Source code: [stewbeet/core/utils/equation.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/core/utils/equation.py)

What they do:

- Build scoreboard arithmetic with plain Python syntax.
- Write a `# comment` header that mirrors the full equation.
- Chain methods (`.set()`, `.add()`, `.multiply()`) or use Python operators (`+`, `-`, `*`, `/`, `//`, `%`, unary `-`).
- `ScoreboardEquation` leaves its result in a scoreboard objective.
- `StorageEquation` writes its result to NBT storage, with a scale factor.
- Take another equation as an operand, whose commands are inlined.
- Handle macro arguments (`$(name)`), which get a `$` prefix on the lines that use them.

Import them with `from stewbeet import *`, and pass the output to `write_function()` to embed the commands in a datapack function. Before 26.3, the integer constants an equation uses (`#5`, `#100`) are initialised by the `stewbeet.plugins.auto.scoreboard_constants` plugin, which looks for every `#<integer> <project_id>.data` in your functions.

## From Minecraft 26.3: one `/compute` command

When the project targets 26.3 or later, an equation is rendered as a single `execute store result ... run compute default integer <provider>` command, the provider being a tree of `add`, `sub`, `mul`, `floor_div` and `floor_mod` number providers that rounds exactly like the scoreboard operations. The examples below show the scoreboard operations, which are what `.ops` holds and what is written before 26.3.

```python
equation = ScoreboardEquation("#value", f"{ns}.data").set(10).add(5).multiply(2)
```
```mcfunction
# scoreboard #value <ns>.data = 10 + 5 * 2
execute store result score #value <ns>.data run compute default integer {type:"mul",inputs:[{type:"add",inputs:[10,5]},2]}
```

- An operand a number provider cannot name, a selector other than `@s`, keeps the whole equation on scoreboard operations.
- A combined equation is computed inline: its own target score is not written.
- No `#5` constant is needed, so `auto.scoreboard_constants` has nothing to initialise for these equations.

## ScoreboardEquation

### Constructor

```python
ScoreboardEquation(player: str, scoreboard: str | None = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player` | `str` | - | Target player or fake-player (e.g. `"@s"`, `"#value"`) |
| `scoreboard` | `str \| None` | `{project_id}.data` | Target scoreboard objective |

### Basic example

From the [extensive template](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/link.py):

```python
ns: str = ctx.project_id

equation  = ScoreboardEquation("#value", f"{ns}.data").set(10).add(5).multiply(2).divide(3).modulo(100)
equation2 = (ScoreboardEquation("#value2", f"{ns}.data").set(20) - 6 + 7) * 8 // 4 % 5

write_function(f"{ns}:equation/test", str(equation) + "\n" + str(equation2))
```

Generated mcfunction before 26.3:

```mcfunction
# scoreboard #value <ns>.data = 10 + 5 * 2 / 3 % 100
scoreboard players set #value <ns>.data 10
scoreboard players operation #value <ns>.data += #5 <ns>.data
scoreboard players operation #value <ns>.data *= #2 <ns>.data
scoreboard players operation #value <ns>.data /= #3 <ns>.data
scoreboard players operation #value <ns>.data %= #100 <ns>.data
# scoreboard #value2 <ns>.data = 20 - 6 + 7 * 8 / 4 % 5
scoreboard players set #value2 <ns>.data 20
scoreboard players operation #value2 <ns>.data -= #6 <ns>.data
scoreboard players operation #value2 <ns>.data += #7 <ns>.data
scoreboard players operation #value2 <ns>.data *= #8 <ns>.data
scoreboard players operation #value2 <ns>.data /= #4 <ns>.data
scoreboard players operation #value2 <ns>.data %= #5 <ns>.data
```

When `scoreboard` is omitted it defaults to `{project_id}.data`. The integer operands are fake players such as `#5`, which the `auto.scoreboard_constants` plugin sets in the load function.

### Using a player scoreboard as operand

Pass any player name or selector as the source. Supply an explicit scoreboard as the second argument if it differs from the equation's own objective:

```python
# Copy @s's score from another objective, then divide by 100
equation = ScoreboardEquation("@s", f"{ns}.data").set("@s", f"{ns}.base").divide(100)
```

Generated mcfunction:

```mcfunction
# scoreboard @s <ns>.data = @s <ns>.base / 100
scoreboard players operation @s <ns>.data  = @s <ns>.base
scoreboard players operation @s <ns>.data /= #100 <ns>.data
```

### Combining two equations

Any equation instance can be passed directly as an operand. Its commands are inlined first, and its final player and scoreboard are used as the source value:

```python
eq_a = ScoreboardEquation("@s").set(10) * 5
eq_b = ScoreboardEquation("#toto", "some_score").set(20) * 2
write_function(f"{ns}:equation/combined", str(eq_a * eq_b))
```

Generated mcfunction before 26.3:

```mcfunction
# scoreboard @s <ns>.data = 10 * 5 * (scoreboard #toto some_score = 20 * 2)
scoreboard players set @s <ns>.data 10
scoreboard players operation @s <ns>.data *= #5 <ns>.data
scoreboard players set #toto some_score 20
scoreboard players operation #toto some_score *= #2 <ns>.data
scoreboard players operation @s <ns>.data *= #toto some_score
```

---

## StorageEquation

`StorageEquation` works like `ScoreboardEquation` for the arithmetic steps, but `str()` also stores the result in NBT storage.

### Constructor

```python
StorageEquation(storage: str, path: str, scale: float = 1.0, storage_type: str = "double")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `storage` | `str` | - | Storage resource location (e.g. `"my_ns:my_storage"`) |
| `path` | `str` | - | NBT path inside the storage (e.g. `"result"`) |
| `scale` | `float` | `1.0` | Multiplier applied when writing to storage: use small values (e.g. `0.000001`) to convert integers to floats |
| `storage_type` | `str` | `"double"` | NBT number type: `"double"`, `"float"`, `"int"`, `"long"`, `"short"`, `"byte"` |

Before 26.3 the arithmetic runs on the fake player `#temp_result` of the `{project_id}.data` objective, and an `execute store result storage ...` command is appended to write it. From 26.3 the whole equation is one `/compute` command that stores into the storage.

### Example with macro arguments

```python
equation = (
    StorageEquation("some_namespace:some_path", "result_path", 0.000005, "double")
    .set("-$(amount)")
    .multiply(1000000)
    .divide("$(max_damage)")
    .subtract("#toto")
)
write_function(f"{ns}:compute/result", str(equation))
```

Generated mcfunction before 26.3:

```mcfunction
# storage some_namespace:some_path result_path = (-$(amount) * 1000000 / $(max_damage) - #toto) * 0.000005
$scoreboard players set #temp_result <ns>.data -$(amount)
scoreboard players operation #temp_result <ns>.data *= #1000000 <ns>.data
$scoreboard players set #temp_divide <ns>.data $(max_damage)
scoreboard players operation #temp_result <ns>.data /= #temp_divide <ns>.data
scoreboard players operation #temp_result <ns>.data -= #toto <ns>.data
execute store result storage some_namespace:some_path result_path double 0.000005 run scoreboard players get #temp_result <ns>.data
```

Lines beginning with `$` are Minecraft macro commands, generated whenever a macro argument (`$(name)`) appears as an operand. From 26.3 the single `execute store` line starts with `$` as well.

---

## Operations reference

### Methods and Python operators

| Method | Python operator | Scoreboard op | Description |
|--------|----------------|---------------|-------------|
| `.set(value)` | none | `scoreboard players set` | Initial assignment, call it first |
| `.add(value)` | `+` | `+=` | Addition |
| `.subtract(value)` | `-` | `-=` | Subtraction |
| `.multiply(value)` | `*` | `*=` | Multiplication |
| `.divide(value)` | `/` or `//` | `/=` | Integer division (`//` behaves identically to `/`) |
| `.modulo(value)` | `%` | `%=` | Modulo |
| Unary negation | `-equation` | `*= #-1` | Multiplies the current value by -1 |

Every method accepts an optional `scoreboard` second argument to target a different objective for the source value.

### Accepted `value` types

| Type | Example | Behavior |
|------|---------|----------|
| `int` | `42` | Generates a `#42` fake-player constant on the `{project_id}.data` objective |
| `str`: player or selector | `"@s"`, `"#other"` | Direct scoreboard operation, on the equation's own objective unless `scoreboard` is supplied |
| `str`: macro argument | `"$(amount)"` | Prepends `$scoreboard players set #temp_... ...` to handle the macro before the operation |
| Equation | another `ScoreboardEquation` or `StorageEquation` | Inlines the source equation's commands first, then uses its final player and scoreboard as source |

Scoreboard arithmetic is integer-only. Use the `scale` parameter of `StorageEquation` to turn the integer result into a floating-point NBT value when writing to storage.

## Glossary

| Term | Meaning |
|------|---------|
| ScoreboardEquation | A chainable builder that generates the commands of an arithmetic expression and leaves the result in a scoreboard objective. |
| StorageEquation | A chainable builder that computes the expression, then stores the result in NBT storage with a configurable scale factor. |
| Method chaining | Every operation method returns `self`, so calls can be chained: `.set(10).add(5).multiply(2)`. |
| Equation header comment | The first line of every rendered equation is a `# comment` that mirrors the full expression, making generated functions self-documenting. |
| Macro argument | A Minecraft function macro parameter in the form `$(name)`. When used as an operand, the line that uses it starts with `$`. |

## Next steps

- [Writing to files](../2_writing_to_files/en.md): embed the commands an equation produces.
- [auto.scoreboard_constants](../plugins/auto.scoreboard_constants.md): how the constants equations need get initialised.

