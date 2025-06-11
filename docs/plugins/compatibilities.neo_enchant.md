
# ⚔️ stewbeet.plugins.compatibilities.neo_enchant

📄 **Source Code**: [stewbeet/plugins/compatibilities/neo_enchant/__init__.py](../../python_package/stewbeet/plugins/compatibilities/neo_enchant/__init__.py) 🔗

## 📋 Overview
The `compatibilities.neo_enchant` plugin provides integration with the NeoEnchant datapack's<br>
veinminer functionality. It automatically detects when custom ore blocks use the<br>
`VANILLA_BLOCK_FOR_ORES` configuration and adds the corresponding vanilla block<br>
to NeoEnchant's veinminer block tag for proper mining compatibility.

## 🎯 Purpose
- ⛏️ Enables veinminer functionality for custom ore blocks
- 🔗 Integrates custom ores with NeoEnchant's mining system
- 🎯 Automatically detects ore block configurations
- 📋 Adds vanilla ore blocks to veinminer tags
- ⚡ Provides seamless mod compatibility
- 🧱 Supports the optimized ore system using polished deepslate

## 🔗 Dependencies
- **✅ Required**: Item definitions with ore blocks using `VANILLA_BLOCK_FOR_ORES` in memory
- **✅ Required**: Project context initialization
- **🔧 Optional**: NeoEnchant datapack (external dependency)
- **📋 Related**: Works with `datapack.custom_blocks` plugin ore functionality

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
# No specific configuration required - automatically detects ore usage
# Works when items use VANILLA_BLOCK_FOR_ORES constant
# Example ore block definition:
# steel_ore:
#   vanilla_block: VANILLA_BLOCK_FOR_ORES  # Uses minecraft:polished_deepslate
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `VANILLA_BLOCK_FOR_ORES` | constant | `{"id": "minecraft:polished_deepslate", "apply_facing": false}` | The vanilla block used for ore optimization |
| `vanilla_block` | object | Auto-detected | Vanilla block configuration in item definitions |
| Ore Detection | automatic | N/A | Automatically scans definitions for ore blocks |

## ✨ Features

### 🔍 Automatic Ore Detection
Scans item definitions to identify ore blocks using the optimized ore system: [`#L24-L25`](../../python_package/stewbeet/plugins/compatibilities/neo_enchant/__init__.py#L24-L25)
- 🎯 Detects items with `VANILLA_BLOCK_FOR_ORES` configuration
- ⛏️ Identifies custom ore blocks automatically
- 🧱 Focuses on polished deepslate-based ores
- ⚡ Leverages the optimized ore system design

### 📋 Veinminer Tag Generation
Creates the necessary block tag for NeoEnchant veinminer compatibility: [`#L27-L29`](../../python_package/stewbeet/plugins/compatibilities/neo_enchant/__init__.py#L27-L29)
- 🏷️ Generates `enchantplus:veinminer` block tag
- 🧱 Adds `minecraft:polished_deepslate` to veinminer blocks
- 📦 Uses proper JSON encoding and formatting
- 🔗 Integrates with NeoEnchant's tag system

### ⚡ Optimization Integration
Works seamlessly with the StewBeet ore optimization system: [`#L13-L15`](../../python_package/stewbeet/plugins/compatibilities/neo_enchant/__init__.py#L13-L15)
- 🎯 Leverages `VANILLA_BLOCK_FOR_ORES` constant
- 🔧 Supports the polished deepslate optimization
- ⛏️ Enables efficient veinmining of custom ores
- 🛡️ Maintains compatibility with ore break detection

### 🔄 Conditional Activation
Only activates when relevant ore configurations are detected: [`#L24`](../../python_package/stewbeet/plugins/compatibilities/neo_enchant/__init__.py#L24)
- ✅ Checks for ore blocks in definitions before proceeding
- ⚡ Minimal performance impact when no ores are present
- 🎯 Smart detection based on vanilla block configuration
- 🔧 Automatic compatibility setup only when needed 

