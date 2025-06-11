
# 🔗 stewbeet.plugins.merge_smithed_weld

📄 **Source Code**: [stewbeet/plugins/merge_smithed_weld/__init__.py](../../python_package/src/stewbeet/plugins/merge_smithed_weld/__init__.py) 🔗

## 📋 Overview
The `merge_smithed_weld` plugin merges generated datapacks and resource packs with their dependencies.<br>
It uses Smithed Weld to combine project archives with library dependencies, official libraries,<br>
and custom libraries into unified distribution packages with proper metadata handling,<br>
consistent timestamps, and optimized compression for production deployment.

## 🎯 Purpose
- 🔗 Merges project packs with library dependencies using Smithed Weld
- 📦 Combines custom libraries from configured libs folder
- 🏛️ Integrates used official libraries automatically
- 🛠️ Handles proper pack.mcmeta and pack.png preservation
- 🕐 Maintains consistent timestamps for reproducible builds
- 📋 Creates distribution-ready merged archives

## 🔗 Dependencies
- **✅ Required**: Generated base archives from archive plugin
- **✅ Required**: Configured output directory and project name
- **🔧 Optional**: Custom libraries in configured libs folder
- **🔧 Optional**: Official libraries (automatically detected from usage)
- **📍 Position**: Must run after archive plugin creates base zip files

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
# Requires output_directory and project name configuration
output_directory: "build"
name: "My Project"

meta:
  stewbeet:
    libs_folder: "libs"  # Optional: custom libraries folder
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_directory` | string | **Required** | Directory containing base archives and destination for merged archives |
| `name` | string | **Required** | Project name used for archive naming |
| `libs_folder` | string | `"libs"` | Folder containing custom library archives (datapack/*.zip, resource_pack/*.zip) |
| Archive Naming | automatic | `{project}_with_libs.zip` | Naming pattern for merged archive outputs |

## ✨ Features

### 🔍 Archive Detection System
Automatically detects and validates base archives for merging: [`__init__.py#L29-L37`](../../python_package/src/stewbeet/plugins/merge_smithed_weld/__init__.py#L29-L37)
- 📦 Looks for project datapack and resource pack archives
- ✅ Only processes packs when base archives exist
- 🏷️ Uses sanitized project names for consistent file naming
- 📁 Ensures output directory structure is properly created

### 🔗 Smithed Weld Integration
Uses Smithed Weld CLI for professional pack merging: [`weld.py#L31-L35, #L117-L121`](../../python_package/src/stewbeet/plugins/merge_smithed_weld/weld.py#L31-L35)
- ⚡ Leverages Smithed's battle-tested merging algorithms
- 🛡️ Handles conflict resolution and dependency management
- 🔧 Configures error-only logging for clean output
- 📊 Creates temporary files for safe processing

### 🏛️ Official Library Integration
Automatically includes used official libraries in merged packs: [`weld.py#L37-L43, #L123-L129`](../../python_package/src/stewbeet/plugins/merge_smithed_weld/weld.py#L37-L43)
- 📚 Reads from OFFICIAL_LIBS registry for available libraries
- ✅ Only includes libraries marked as used in the project
- 📁 Supports separate datapack and resource pack library paths
- 🔍 Validates library existence before inclusion

### 📦 Custom Library Support
Integrates custom libraries from configured folders: [`weld.py#L29-L30, #L115-L116`](../../python_package/src/stewbeet/plugins/merge_smithed_weld/weld.py#L29-L30)
- 📁 Scans configured libs_folder for datapack and resource pack archives
- 🔍 Uses glob patterns to find all zip files in respective folders
- 🎯 Supports organized library structure with separate pack types
- ✅ Gracefully handles missing or empty library folders

### 🛠️ Metadata Preservation System
Ensures proper pack.mcmeta and pack.png handling: [`weld.py#L52-L72, #L138-L158`](../../python_package/src/stewbeet/plugins/merge_smithed_weld/weld.py#L52-L72)
- 🔄 Excludes conflicting metadata from merged libraries
- 📝 Uses project's original pack.mcmeta for final archive
- 🖼️ Preserves project's pack.png if available
- ✅ Ensures proper metadata precedence and consistency

### 🕐 Timestamp and Compression Management
Maintains consistent timestamps and optimal compression: [`weld.py#L47-L51, #L74-L76`](../../python_package/src/stewbeet/plugins/merge_smithed_weld/weld.py#L47-L51)
- ⏰ Uses get_consistent_timestamp for reproducible builds
- 🗜️ Applies ZIP_DEFLATED compression with level 6
- 📊 Creates proper ZipInfo objects for all entries
- 🧹 Cleans up temporary files after processing 

