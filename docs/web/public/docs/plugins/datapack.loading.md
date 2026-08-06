# stewbeet.plugins.datapack.loading

The `datapack.loading` plugin sets up the versioned loading system for Minecraft datapacks.<br>
It creates version checking functions, load management, and item storage systems following the LanternLoad convention.<br>
The plugin ensures proper datapack initialization with dependency validation and prevents duplicate loading.<br>
**(This plugin requires `stewbeet.plugins.finalyze.dependencies` later in the pipeline to complete the setup.)**

### <u>Some Features Showcase</u>

**Lantern Load Setup (#load, #enumerate, #resolve, etc.):**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loading.lantern_load.jpg">

**All item definitions stored into a storage:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loading.items_storage.jpg">

**Confirm datapack load for players with `convention.debug` tag:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loading.load_messages.jpg">

**Source Code**: [`stewbeet/plugins/datapack/loading/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/datapack/loading/__init__.py)


## What it does

- Sets up versioned datapack loading system
- Implements version checking and validation
- Creates item storage systems for definitions
- Prevents duplicate datapack loading
- Follows LanternLoad convention standards
- Manages load status tracking with scoreboards

## Dependencies
- **✅ Required**: None (but works best with other StewBeet plugins)
- **🔗 Requires Later**: `stewbeet.plugins.finalyze.dependencies` (to complete setup)
- **📍 Position**: Should be placed after item definitions and before finalization plugins<br>
(see [`basic/beet.yml`](https://github.com/Stoupy51/StewBeet/blob/main/templates/basic/beet.yml) for an example)

## Configuration

### Basic Example Configuration
```yaml
version: "1.0.0"  # Required: semantic version (major.minor.patch)
id: "your_namespace"  # Required: project namespace
name: "Your Project Name"  # Required: display name for load messages

pipeline:
  - ...
  - stewbeet.plugins.datapack.loading  # Place this plugin in the pipeline
  - ...  # Other plugins follow
  - stewbeet.plugins.finalyze.dependencies  # Required later for completion
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `version` | string | **Required** | Semantic version in format "major.minor.patch" for version checking |
| `id` | string | **Required** | Project namespace used for function and storage generation |
| `name` | string | **Required** | Display name used in load confirmation messages |

## Features

### Versioned Loading System
- 🔢 **Version Parsing** - Splits semantic version into major.minor.patch components
- 📊 **Version Checking** - Creates enumerate function for version validation
- 🎯 **Load Resolution** - Generates resolve function for proper version loading
- 🏷️ **Function Tags** - Sets up enumerate and resolve function tags

### Load Management
- 🚫 **Duplicate Prevention** - Prevents multiple executions of load functions
- 📋 **Status Tracking** - Uses scoreboards to track loading state
- 💬 **Load Confirmation** - Displays load messages to players with `convention.debug` tag
- ⚙️ **Secondary Function** - Manages actual load execution flow

### Item Storage System
- 🗄️ **Storage Initialization** - Creates namespace:items storage system
- 🔧 **Component Processing** - Handles item components and minecraft: namespace prefixing
- 🎯 **Data Filtering** - Excludes non-component data from storage
- 📝 **JSON Serialization** - Converts definitions to storage commands

## Next steps

- [Defining items and blocks](../1_definitions_setup/en.md): where the items this plugin reads are declared.
- [All plugins](README.md): the rest of the pipeline, in the order it runs.
- [Configuring the build](../3_beet_config/en.md): enabling, ordering and configuring plugins.
