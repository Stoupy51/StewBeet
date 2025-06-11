
# ⚡ stewbeet.plugins.datapack.loading

📄 **Source Code**: [stewbeet/plugins/datapack/loading/__init__.py](../../python_package/stewbeet/plugins/datapack/loading/__init__.py) 🔗

## 📋 Overview
The `datapack.loading` plugin sets up the versioned loading system for Minecraft datapacks.<br>
It creates version checking functions, load management, and item storage systems following the LanternLoad convention.<br>
The plugin ensures proper datapack initialization with dependency validation and prevents duplicate loading.<br>
**(This plugin requires `stewbeet.plugins.finalyze.dependencies` later in the pipeline to complete the setup.)**

## 🎯 Purpose
- ⚡ Sets up versioned datapack loading system
- 🔍 Implements version checking and validation
- 📦 Creates item storage systems for definitions
- 🔄 Prevents duplicate datapack loading
- 🏷️ Follows LanternLoad convention standards
- 📋 Manages load status tracking with scoreboards

## 🔗 Dependencies
- **✅ Required**: None (but works best with other StewBeet plugins)
- **🔗 Requires Later**: `stewbeet.plugins.finalyze.dependencies` (to complete setup)
- **📍 Position**: Should be placed after item definitions and before finalization plugins<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
# No specific configuration required
# Uses project metadata from context:
version: "1.0.0"  # Required: semantic version (major.minor.patch)
id: "your_namespace"  # Required: project namespace
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `version` | string | **Required** | Semantic version in format "major.minor.patch" for version checking |
| `id` | string | **Required** | Project namespace used for function and storage generation |
| `name` | string | **Required** | Display name used in load confirmation messages |

## ✨ Features

### ⚡ Versioned Loading System
- 🔢 **Version Parsing** - Splits semantic version into major.minor.patch components [`#L33-L35`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L33-L35)
- 📊 **Version Checking** - Creates enumerate function for version validation [`#L37-L47`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L37-L47)
- 🎯 **Load Resolution** - Generates resolve function for proper version loading [`#L49-L53`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L49-L53)
- 🏷️ **Function Tags** - Sets up enumerate and resolve function tags [`#L55-L56`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L55-L56)

### 🔄 Load Management
- 🚫 **Duplicate Prevention** - Prevents multiple executions of load functions [`#L58-L63`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L58-L63)
- 📋 **Status Tracking** - Uses scoreboards to track loading state [`#L102-L103`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L102-L103)
- 💬 **Load Confirmation** - Displays load messages to debug-tagged players [`#L101`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L101)
- ⚙️ **Secondary Function** - Manages actual load execution flow [`#L62`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L62)

### 📦 Item Storage System
- 🗄️ **Storage Initialization** - Creates namespace:items storage system [`#L66-L67`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L66-L67)
- 🔧 **Component Processing** - Handles item components and minecraft: namespace prefixing [`#L76-L81`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L76-L81)
- 🎯 **Data Filtering** - Excludes non-component data from storage [`#L72-L75`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L72-L75)
- 📝 **JSON Serialization** - Converts definitions to storage commands [`#L90-L91`](../../python_package/stewbeet/plugins/datapack/loading/__init__.py#L90-L91) 

