
# User folder
## setup_database.py
This script is used to setup the database for the datapack.
If your datapack needs to create custom items or blocks with recipes (or not), you must setup the dictionnary in this function.
See the example in the file for more information.

## setup_external_database.py
This script is used to setup the external database for the datapack.
When you are using items or blocks from another datapack in recipes, you must setup the dictionnary in this function.
The format is the same as the setup_database.py file.

## link.py
This script is used to run your own python code before the build process finalize.
You can use this script to dynamically write files in the build folder.
If so, you must use the efficient `write_file` function in `python_datapack.utils.io` module.

