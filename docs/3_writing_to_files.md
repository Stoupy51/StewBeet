
# 🗃️ Writing to files
Dealing with files in any programming language can be somewhat annoying. When you want to prepend something to a file, you need to read the content, add the text your want to add and rewrite the file leading sometimes to excessive disk access and unreadable code 🌀.<br>
To avoid this issue, the `python_datapack` module brings a system for writing files along with utility functions through the `python_datapack.utils.io` import.<br>
`FILES_TO_WRITE`: This global variable is a dictionnary of files paths leading to the content of the file, meaning all files are stored into RAM. You can then use python string arithmetic and functions 💾.


## 📚 Reading and writing functions
- `read_file()`: 📖 This function takes a file path and returns its content without raising any error if the file path doesn't exists
- `write_to_file()`: ✍️ Taking the file path and its content, you can indicate if you want to prepend the content, or if you want to overwrite it. If you write to a json file but there are already content in it, both content will be merged unless you put the overwrite boolean to true.
- `write_to_function()`: 📝 Write content to a function file using Minecraft function notation (e.g., "namespace:folder/function_name"). If no namespace is provided, it defaults to "minecraft".


## 🔧 Versioned functions
As you may know, a few functions such as the load and tick functions 🗂️ are located in a folder containing the version of your datapack with a path like `build/datapack/data/<namespace>/function/v1.0.0/tick.mcfunction`.<br>
Writing the entire file path again and again can be sometimes annoying, so I created 3 functions to help you out:
- `write_to_load_file()`: ⚡ Allows you to write directly to the load file.
- `write_to_tick_file()`: ⏱️ Allows you to write directly to the tick file.
- `write_to_versioned_file()`: ⏳ This function will automatically prepend the whole path to the folder and append `.mcfunction` at the end, so to write to the tick file for example you can give this relative path: `tick`.


## 🗑️ File Management
The module provides several functions for managing files:
- `delete_file()`: 🚫 Delete a single file from both the write queue and optionally from disk
- `delete_files()`: 🧹 Delete multiple files that contain a specific string in their path
- `write_all_files()`: 💾 Write all queued files to disk, optionally filtering by path (you'll probably don't need this unless you are debugging or use an external tool to read the files)


## ⚙️ JSON Dump
If you are experienced with Python, you may know how to use the `json.dumps()` function 📜.<br>
However, the `python_datapack.utils.io` import provides to you the `super_json_dump()` function where you can precise the indentation depth level.<br>
It is used pretty much everywhere during the build process because it is very convenient to make JSON files readable, such as the [`database_debug.json`](../database_debug.json) file using a max_level of 2.


## 📚 Conclusion
This guide was pretty much simple as there wasn't much to cover but I hope you understood it well!<br>
Thank you for reading 🙌.

