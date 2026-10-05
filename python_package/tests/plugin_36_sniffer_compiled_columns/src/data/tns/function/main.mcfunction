
major = 2
data modify storage tns:main version set value {"major": int(major), "minor": 4}
execute as @a run function ~/child:
    say inside
schedule function ~/ 1t replace
say loudly hello
