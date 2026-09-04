from stewbeet import write_function

write_function("probe:demo", """
execute as @a run say hi
function probe:alpha
""")

x = 1

ns = "probe"

write_function(f"{ns}:gamma", f"""
function {ns}:alpha
""")
