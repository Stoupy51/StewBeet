
# Lang file

Moves the text of your commands and loot tables into `lang/en_us.json`, so a resource pack can translate it.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.auto.lang_file`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/lang_file/__init__.py)

## What it does to your text

You write plain text components. The plugin finds each `"text"` value in every file of the datapack and rewrites it as a `translate` component. The original text stays as the `fallback`, so the pack still reads right without a resource pack.

```mcfunction
# You write
tellraw @s {"text":"Not enough energy"}

# The build writes
tellraw @s {"translate":"simplenergy.not_enough_energy",
  "fallback":"Not enough energy"}
```

The key is the project id, a dot, then the text lowercased with other punctuation removed, and spaces, `.`, `/` and `:` turned into `_`. The text part is cut at 64 characters.

A value is left alone when it:

- has fewer than 3 letters or digits once simplified,
- holds a `$`, so macro lines keep working,
- holds a `\u` escape.

Symbols and punctuation around the words stay as plain text next to the translated part. The text `" attacks | "` becomes a space, the key for `attacks`, then `" | "`. Two texts that differ only there share one key.

Two different texts that give the same key get `_2`, `_3` and so on.

## What this plugin writes

- `lang/en_us.json` in the `minecraft` namespace of the resource pack: every key, sorted, merged with the file you already have there.
- The text of every datapack file with a `text` key: functions, loot tables, advancements and the rest.

## Limits

- Only `en_us` is written. Other languages are yours to add.
- A text split over several `"text"` values is translated piece by piece.

