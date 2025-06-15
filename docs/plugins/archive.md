
# 📦 stewbeet.plugins.archive

📄 **Source Code**: [stewbeet/plugins/archive/__init__.py](../../python_package/stewbeet/plugins/archive/__init__.py) 🔗

## 📋 Overview
The `archive` plugin creates zip archives of generated datapacks and resource packs.<br>
It replaces the legacy archive system with beet-native functionality, providing<br>
deterministic compression, consistent timestamps, and parallel processing while<br>
preserving original pack directories and integrating seamlessly with beet's output system.

## 🎯 Purpose
- 📦 Creates zip archives of generated datapacks and resource packs
- 🕐 Provides consistent timestamps for reproducible builds
- ⚡ Uses parallel processing for efficient archive creation
- 🔧 Integrates with beet's native pack management system
- 📁 Preserves original pack directory structure
- 🎯 Replaces legacy archive systems with modern beet-compatible approach

## 🔗 Dependencies
- **✅ Required**: Beet context with generated packs (datapacks/resource packs)
- **✅ Required**: Configured output directory in project settings
- **📍 Position**: Should run after all pack generation is complete
- **🔧 Optional**: Beet cache directory for timestamp consistency
- **📋 Related**: Works with any plugins that generate pack content

## ⚙️ Configuration

### 🎯 Basic Example Configuration
```yaml
# No direct configuration required - uses project settings
# Requires output_directory to be configured in beet.yml:
output_directory: "build"
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_directory` | string | **Required** | Directory where zip archives will be saved |
| Archive Naming | automatic | `{project_name}_{pack_type}.zip` | Naming convention for generated archives |
| Compression Level | constant | `6` | ZIP_DEFLATED compression level for optimal size/speed balance |
| Timestamp Source | automatic | Beet cache | Uses beet cache modification time for consistency |

## ✨ Features

### 🕐 Consistent Timestamp System
Ensures reproducible builds with deterministic timestamps: [`#L37-L50`](../../python_package/stewbeet/plugins/archive/__init__.py#L37-L50)
- 📅 Uses beet cache directory modification time as timestamp source
- 🔄 Applies consistent timestamps to all zip entries
- 📦 Enables reproducible archive builds across environments
- ⏰ Falls back to default time (2025-01-01) if cache unavailable

### 📦 Pack Detection and Processing
Automatically detects and processes all generated packs: [`#L61-L66`](../../python_package/stewbeet/plugins/archive/__init__.py#L61-L66)
- 🔍 Identifies both datapacks and resource packs from context
- 🏷️ Determines pack types automatically using isinstance checks
- 📝 Generates descriptive archive names based on project and pack type
- ✅ Validates pack availability before processing

### 🗜️ Advanced Compression System
Implements two-pass compression for optimal results: [`#L75-L86, #L88-L96`](../../python_package/stewbeet/plugins/archive/__init__.py#L75-L96)
- 🔧 Uses ZIP_DEFLATED compression with level 6 for size/speed balance
- 🔄 Two-pass system: first creates archive, then recreates with timestamps
- 📊 Handles beet's dump() system that bypasses standard writestr()
- ✅ Ensures all entries have consistent compression and timestamps

### ⚡ Parallel Archive Creation
Processes multiple packs simultaneously for efficiency: [`#L115`](../../python_package/stewbeet/plugins/archive/__init__.py#L115)
- 🚀 Uses multithreading for simultaneous pack processing
- 📊 Optimizes worker count based on number of packs
- 🛡️ Includes error handling for robust archive creation
- ⚡ Significantly improves build times for multiple packs

### 🔧 Beet Integration System
Seamlessly integrates with beet's pack management: [`#L75-L86`](../../python_package/stewbeet/plugins/archive/__init__.py#L75-L86)
- 📦 Uses pack.dump() to avoid interfering with existing directories
- 🎯 Leverages beet's native Context and pack system
- 📁 Preserves original pack structure and organization
- 🔗 Integrates with beet's output directory management

### 🛡️ Error Handling and Validation
Provides robust error handling and validation: [`#L58-L65, #L69`](../../python_package/stewbeet/plugins/archive/__init__.py#L58-L69)
- ✅ Validates output directory configuration before processing
- 📦 Ensures packs are available in context before archiving
- 📁 Creates output directory if it doesn't exist
- 🛡️ Uses @handle_error decorator for graceful error management 

