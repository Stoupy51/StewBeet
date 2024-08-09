
# Project Structure
This guide will be presenting to you the structure of the template, where things must go, and more...<br>

## Basics
By default, the root folder contains several files and folders:
- [`config.py`](../config.py): The most important file for your project. It has been decided to be a python script instead of a JSON or YAML file in order to properly show the types for constants and having the ability to use previously defined constants.
- [`build.py`](../build.py): It shouldn't be modified unless you know what you are doing. Running this script will launch all the build process and install `python_datapack` module automatically if not done yet.
- [`clean.py`](../clean.py): By default, running this script will delete every auto-generated files. Some people prefers modifying this script so that the [`cmd_cache.json`](../cmd_cache.json) file doesn't get cleaned.
- [`upgrade_build.py`](../upgrade_build.py): Very simple script trying to upgrade the `python_datapack` module version to the latest.
- [`assets` folder](../assets/): This folder contains textures, sounds, jukebox records, pack icon, and some utility scripts.
  - [`original_icon.png`](../assets/): This png file will be copied to both datapack and resource pack icons, and also be used for the introduction page of the generated in-game manual.
  - [`compress_ogg.py`](../assets/compress_ogg.py): This python script is useful when you want to compress your audio files to take less space.
  - [`force_mono.py`](../assets/force_mono.py): In Minecraft, stereo sounds are not 3D positioned when played in-game. This script will convert stereo sounds to mono to change the behaviour (see [wiki](https://minecraft.wiki/w/Sounds.json#Java_Edition) sounds/name part for more information).
  - [`mp3_to_ogg.py`](../assets/mp3_to_ogg.py): Simple python script that converts mp3 files to ogg.
  - [`optimize_textures.py`](../assets/optimize_textures.py): Running this script will optimize all `.png` files without loosing quality.
  - [`records` folder](../assets/records/): Every `.ogg` file will be recognized by the build system ONLY IF you call the 'generate_custom_records()' function during [database setup](../user/setup_database.py). Then music dics will be playeable in-game.
  - [`sounds` folder](../assets/sounds/): Every `.ogg` file will be recognized by the build system by being copied to the generated resource pack and linked. Then you can use `/playsound` in-game.
  - [`textures` folder](../assets/textures/): Simple at first glance, but have lots of details to talk about. When an item is added to the database during [setup](../user/setup_database.py), the build process will be seeking for textures in this folder and try to recognize patterns. Patterns includes cake slices, front, side, top, bottom, on and off textures, .mcmeta files, etc. More details in the [_README.md file](../assets/textures/_README.md) in the folder.
- [`build` folder](../build/): Destination folder of the build process result, it will contain a datapack and resource folder, along with their zipped version. If the `MERGE_LIBS` option is enabled in [`config.py`](../config.py), zip files named with "_with_libs" will generate in the folder.
- []()
- []()
- []()
- []()
- []()



