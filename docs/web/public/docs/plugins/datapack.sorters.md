
# List sorting

Generates the functions that sort a list stored in a storage, from a small JSON file.

It runs in the `basic` and `extensive` templates as `stewbeet.plugins.datapack.sorters`, with no configuration. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/sorters/__init__.py)

## Declare a sorter

Write `data/<namespace>/sorter/<name>.json`:

```json
{
  "algorithm": "selection_sort",
  "functions_location": "switch:stats/sort",
  "to_sort": {
    "storage": "switch:stats",
    "target": "all.played"
  },
  "key": "count",
  "scale": 100,
  "limit": 10
}
```

Then call `/function switch:stats/sort/sort`. The list at `target` is replaced by its sorted copy, from the lowest `key` to the highest. A negative `scale` gives the highest first.

The sorter file is removed from the pack once its functions are written.

## What this plugin writes

Under `functions_location`:

- `sort` is the entry point.
- `selection_sort_loop`, `find_min`, `move_min_element`, and `append_remaining` when `limit` is set, for `selection_sort`.
- `quick_sort`, `partition_main`, `partition_loop`, `partition_swap` and `partition_loop_swap`, for `quick_sort`.

The sorting scores are on the `sorter.val` objective and the temporary data in `sorter:temp`.

## Options

| Option | Default | What it does |
|---|---|---|
| `algorithm` | `"selection_sort"` | `"selection_sort"` or `"quick_sort"` |
| `functions_location` | required | The function path under which the functions are written |
| `to_sort.storage` | required | The storage holding the list |
| `to_sort.target` | required | The NBT path of the list in that storage |
| `key` | required | The number inside each element that is compared |
| `scale` | `1` | Integer by which the key is multiplied before it is rounded to a score |
| `limit` | none | Sort only the first elements, and keep the rest after them. `selection_sort` only |

`selection_sort` is the one to pick. `quick_sort` calls itself through macros, and in a datapack that costs more than the quadratic loop.

## Limits

- A key is compared as an integer score. Use `scale` to keep decimals: `1000` keeps 3.
- `limit` is ignored by `quick_sort`.
- A sorter with a missing `functions_location`, `key` or `to_sort` fails the build.

## Editor support

Spyglass completes and checks sorter files when `sorter` is a custom resource. In the Spyglass config, under `env`:

```json
"customResources": {
  "sorter": { "category": "sorter" }
}
```

Then add [`mod.mcdoc`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/sorters/mod.mcdoc) anywhere in the workspace and restart VS Code.

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md): calling the generated functions from your own.

The quick sort implementation is by [Darukshock](https://github.com/Darukshock).

