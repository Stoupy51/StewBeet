
# ⏰ stewbeet.plugins.finalyze.custom_blocks_ticking

📄 **Source Code**: [stewbeet/plugins/finalyze/custom_blocks_ticking/__init__.py](../../python_package/stewbeet/plugins/finalyze/custom_blocks_ticking/__init__.py) 🔗

## 🔗 Dependencies
- **✅ Required**: Custom block functions in the `custom_blocks/` folder
- **🔧 Optional**: Custom blocks with `block_name/tick.mcfunction` or `block_name/second.mcfunction` files
- **📋 Related**: Works with `datapack.custom_blocks` plugin for block infrastructure

## 📋 Overview
The `finalyze.custom_blocks_ticking` plugin automatically sets up ticking functionality<br>
for custom blocks by detecting tick and second functions in the custom_blocks folder.<br>
It generates the necessary infrastructure to call these functions efficiently, including<br>
entity tagging, scoreboard optimization, and proper integration with versioned functions.

### <u>Some Features Showcase</u>

**Automatically links custom blocks tick and second functions efficiently:**<br>
<img src="img/finalyze.custom_blocks_ticking.timers.jpg" style="width: min(960px, 100%)">

## 🎯 Purpose
- ⏰ Automatically detects custom block tick and second functions
- 🏷️ Sets up entity tagging system for ticking custom blocks
- 📊 Implements scoreboard-based performance optimization
- 🔄 Integrates with versioned function system for proper timing
- ⚡ Provides efficient execution only when ticking entities exist
- 📈 Adds statistics tracking for ticking entities

## ⚙️ Configuration

### 🎯 Basic Example Configuration
```yaml
pipeline:
  - ...
  - stewbeet.plugins.datapack.custom_blocks  # Optional if you are adding custom blocks functions yourself
  - ...
  - stewbeet.plugins.finalyze.custom_blocks_ticking
  - ...
# No specific configuration required - automatically detects ticking functions
# Create tick/second functions in custom_blocks folder:
# custom_blocks/{block_name}/tick.mcfunction
# custom_blocks/{block_name}/second.mcfunction
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `tick.mcfunction` | file | Auto-detected | Custom block function that runs every tick (20 times/second) |
| `second.mcfunction` | file | Auto-detected | Custom block function that runs every second |
| Function Detection | automatic | N/A | Scans `custom_blocks/` folder for ticking functions |
| Entity Optimization | automatic | Enabled | Uses scoreboards to optimize execution when no entities exist |

## ✨ Features

### 🔍 Automatic Function Detection
Scans the custom_blocks folder for tick and second functions:
- 📁 Searches for functions in `{namespace}:custom_blocks/{block}/tick`
- ⏱️ Detects `second.mcfunction` for once-per-second execution
- ⚡ Identifies `tick.mcfunction` for every-tick execution
- 🎯 Validates proper folder structure and naming

### 🏷️ Entity Tagging System
Sets up proper entity tags for ticking custom blocks:
- 🔖 Adds tags during block placement (`place_secondary`)
- ⏰ Creates `{namespace}.second` tags for second-based ticking
- ⚡ Creates `{namespace}.tick` tags for tick-based execution
- 🧹 Removes tags during block destruction to prevent memory leaks

### 📊 Performance Optimization
Implements scoreboard-based optimization for efficient execution:
- 🔢 Tracks `#second_entities` count for second functions
- ⚡ Tracks `#tick_entities` count for tick functions
- 🎯 Only executes when entities with tags exist
- ⚙️ Prevents unnecessary function calls when no ticking blocks are present

### 🔄 Versioned Function Integration
Integrates with the versioned function system for proper timing:
- ⏰ Adds to versioned `second` function for once-per-second execution
- ⚡ Adds to versioned `tick` function for every-tick execution
- 🎯 Uses scoreboard checks to optimize performance
- 📋 Proper integration with existing timing infrastructure

### 🌐 Custom Block Function Distribution
Creates centralized distribution functions for multiple custom blocks:
- 📦 Generates `{namespace}:custom_blocks/second` distribution function
- ⚡ Creates `{namespace}:custom_blocks/tick` distribution function
- 🏷️ Uses entity tags to route to specific block functions
- 🔄 Allows multiple custom blocks to have ticking functionality

### 📈 Statistics Integration
Adds ticking entity statistics to the stats system:
- 📊 Initializes scoreboard values for statistics
- 📈 Reports count of entities with second tags
- ⚡ Reports count of entities with tick tags
- 🎯 Integrates with existing `_stats_custom_blocks` system 

