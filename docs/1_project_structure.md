
# 🗃️ Project Structure
This guide will be presenting to you the structure of the template, where things must go, and more...<br>

## 📂 Content and description
By default, the root folder contains several files and folders:
- [`config.py`](../config.py) ⚙️: The most important file for your project. It has been decided to be a python script instead of a JSON or YAML file in order to properly show the types for constants and having the ability to use previously defined constants.
- [`build.py`](../build.py) 🛠️: It shouldn't be modified unless you know what you are doing. Running this script will launch all the build process and install `python_datapack` module automatically if not done yet.
- [`watcher.py`](../watcher.py) 🔍: This script is used to watch for changes and automatically launch the build process each time a file is modified (Not very eco-friendly 🌍).
- [`clean.py`](../clean.py) 🧹: By default, running this script will delete every auto-generated files. Some people prefers modifying this script so that the [`cmd_cache.json`](../cmd_cache.json) file doesn't get cleaned.
- [`upgrade_build.py`](../upgrade_build.py) ⬆️: Very simple script trying to upgrade the `python_datapack` module version to the latest.
- 🎨 [`assets` folder](../assets/): This folder contains textures, sounds, jukebox records, pack icon, and some utility scripts.
  - [`original_icon.png`](../assets/) 🖼️: This png file will be copied to both datapack and resource pack icons, and also be used for the introduction page of the generated in-game manual.
  - [`compress_ogg.py`](../assets/compress_ogg.py) 🎶: This python script is useful when you want to compress your audio files to take less space.
  - [`force_mono.py`](../assets/force_mono.py) 🔊: In Minecraft, stereo sounds are not 3D positioned when played in-game. This script will convert stereo sounds to mono to change the behaviour (see [wiki](https://minecraft.wiki/w/Sounds.json#Java_Edition) sounds/name part for more information).
  - [`mp3_to_ogg.py`](../assets/mp3_to_ogg.py) 🔄: Simple python script that converts mp3 files to ogg.
  - [`optimize_textures.py`](../assets/optimize_textures.py) 🖌️: Running this script will optimize all `.png` files without loosing quality.
  - [`records` subfolder](../assets/records/) 🎵: Every `.ogg` file will be recognized by the build system ONLY IF you call the 'generate_custom_records()' function during [definitions setup](../user/setup_definitions.py). Then music dics will be playeable in-game.
  - [`sounds` subfolder](../assets/sounds/) 🔊: Every `.ogg` file will be recognized by the build system by being copied to the generated resource pack and linked. Then you can use `/playsound` in-game.
  - [`textures` subfolder](../assets/textures/) 🎨: Simple at first glance, but have lots of details to talk about. When an item is added to the definitions during [setup](../user/setup_definitions.py), the build process will be seeking for textures in this folder and try to recognize patterns. Patterns includes cake slices, front, side, top, bottom, on and off textures, .mcmeta files, etc. More details in the [_README.md file](../assets/textures/_README.md) in the folder.
  - [`manual_overrides` subfolder](../assets/manual_overrides/) 📖: This folder is used to override the assets used for generating the manual. Every file in this folder will replace the [original ones](https://github.com/Stoupy51/python_datapack/tree/main/src/python_datapack/manual/assets) as long as the file name is the same. For instance, if you want to replace the `shaped_3x3.png` file, you need to create a `shaped_3x3.png` file in this folder.
- 🗃️ [`build` folder](../build/): Destination folder of the build process result, it will contain a datapack and resource folder, along with their zipped version. If the `MERGE_LIBS` option is enabled in [`config.py`](../config.py), zip files named with "_with_libs" will generate in the folder.
- 📚 [`libs` folder](../libs/): This folder contains a datapack and a resource_pack subfolder where you place non-official zipped datapacks you want to include in your project, their content are copied to the build copy destination if properly configured in [`config.py`](../config.py). Usually, when you put a datapack in this folder, you may add it as a dependency in the configuration script.
- 📖 [`manual` folder](../manual/): This folder is a cache folder used for the generated manual. The [`items` subfolder](../manual/items/) contains isometric renders of every blocks in the definitions along with normal items, for each namespace you are using in the recipes. The [`font` subfolder](../manual/font/) contains every single generated asset used in the manual.
- 🔗 [`merge` folder](../merge/): This folder is very optionnal, it contains a datapack and a resource_pack subfolder. At the end of the build process, the folder will be read and merged to the adjacent [`build` folder](../build/). If a file in the merge folder is already in the build folder without the same content, they will be merged. If you want to overwrite a file in the build folder, prefer using `write_file()` method during link phase ([see tutorial here](3_writing_to_files.md))
- 👤 [`user` folder](../user/): Finally, the user folder is where you will add you python code to affect you project in many ways starting by the definition of your custom items.
  - [`setup_definitions.py`](../user/setup_definitions.py) 🛠️: In this file, you will fill up a dictionnary with your custom items. To make things easy, you have multiple functions provided by the `definitions_helper` import such as `generate_everything_about_these_materials()` that will look up at the [`assets/textures` folder](../assets/textures/) and automatically detect armor, tool, ingot, ore, deepslate ore, stick, rod, and many more. Check the [next tutorial](2_setup_definitions.md) for more detailled information.
  - [`setup_external_definitions.py`](../user/setup_external_definitions.py) 🌐: This should be used only if you are using items from other datapacks in your recipes. This may be a little scuffed so make sure to check the tutorial when it will be available.
  - [`link.py`](../user/link.py) 🔗: This script is called at the end of the build process just before making zip files. You can use it to run any code, write to any file you want, and write dynamically your datapack. This is also the place where you define your custom ore generation. For instance, the datapack [`SimplEnergy`](https://github.com/Stoupy51/SimplEnergy/blob/main/user/link.py) wrote all its features inside this file (with proper scripts management) without the use of the merge folder, making it very easy to update for future Minecraft versions.


## 📚 Conclusion
If you understood properly everything above, congratulations!<br>
You passed the hardest (in my opinion), if you are feeling confident you can now properly start your project.<br>
If at any point you need more information about a part, read the next documentation files about the topic you want!<br>
Thank you for reading 🙌.

