
for i in range(1, 6):
    say f"Hello, world! {i}"

execute function ./goodbye:
    say Goodbye, world!
    for suffix in ["", "_again"]:
        execute function f"extensive:farewell{suffix}":
            say f"Farewell, world! with {suffix}"

