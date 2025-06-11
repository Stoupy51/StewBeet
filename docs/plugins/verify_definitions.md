
# ✅ stewbeet.plugins.verify_definitions

📄 **Source Code**: [stewbeet/plugins/verify_definitions.py](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py) 🔗

## 📋 Overview
The `verify_definitions` plugin performs comprehensive validation of item definitions to ensure data integrity and consistency across the StewBeet framework.<br>
It validates item configurations, recipe structures, and performs consistency checks before further processing.

## 🎯 Purpose
- ✅ Validates all item definitions in `Mem.definitions`
- 🔍 Performs consistency checks on recipe data
- 🚫 Prevents invalid configurations from proceeding
- 📝 Validates text component formats
- 🔧 Ensures custom data integrity
- 🧹 Cleans up empty recipe lists
- 🐛 Exports debug information for troubleshooting

## 🔗 Dependencies
- **✅ Required**: `None`
- **📍 Position**: Should be run immediately after user definitions are loaded<br>
(see [`extensive/beet.yml`](../../templates/extensive/beet.yml) for an example)
- **🔄 Follows**: User definition scripts (e.g., `src.setup_definitions`)

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
meta:
  stewbeet:
    definitions_debug: "definitions_debug.json"  # Optional debug export path
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `definitions_debug` | string | `""` | Path where cleaned definitions will be exported for debugging |

## ✨ Features

### 🔍 Core Validation Checks
The plugin performs extensive validation on every item definition:

#### 🆔 Item Structure Validation
- **ID Requirements**: Ensures proper namespaced IDs (e.g., `minecraft:stone`) [`#L66-L70`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L66-L70)
- **Reserved Names**: Prevents use of reserved item names like `heavy_workbench` [`#L63-L64`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L63-L64)
- **Reserved IDs**: Blocks usage of reserved ID `minecraft:polished_deepslate` [`#L72-L73`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L72-L73)
- **Item Name Validation**: Validates text component format for `item_name` [`#L109-L113`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L109-L113)
- **Lore Format**: Checks lore text component structure and recommends [Misode's Text Component Generator](https://misode.github.io/text-component/) [`#L115-L129`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L115-L129)
- **Category Validation**: Ensures category strings are properly formatted [`#L92-L94`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L92-L94)

#### 🧱 Custom Block Validation
- **VANILLA_BLOCK Requirements**: Validates vanilla block configuration for custom blocks [`#L76-L86`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L76-L86)
- **Apply Facing Configuration**: Ensures proper `apply_facing` boolean settings [`#L84-L85`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L84-L85)
- **Container Restrictions**: Prevents invalid container usage with custom blocks [`#L88-L89`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L88-L89)
- **Ore Drop Validation**: Validates `NO_SILK_TOUCH_DROP` configuration for ore blocks [`#L103-L108`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L103-L108)

#### 🔒 Custom Data Validation
- **Project Namespace**: Ensures custom data follows project namespace structure [`#L96-L102`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L96-L102)
- **Required Format**: Validates `custom_data: {project_id: {item_name: true}}` pattern
- **Data Types**: Ensures proper dictionary structure and boolean values

#### 🍳 Recipe Validation System
Comprehensive recipe validation for all supported types:

##### 🔨 Crafting Recipes
- **`crafting_shaped`**: Validates shape patterns (max 3x3), ingredient mapping, and symbol usage [`#L155-L173`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L155-L173)
- **`crafting_shapeless`**: Validates ingredient lists and proper ingredient representation [`#L175-L184`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L175-L184)

##### 🔥 Furnace Recipes
- **`smelting`**: Standard furnace recipe validation [`#L186-L195`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L186-L195)
- **`blasting`**: Blast furnace recipe validation  
- **`smoking`**: Smoker recipe validation
- **`campfire_cooking`**: Campfire recipe validation
- **Experience & Cooking Time**: Validates numeric values for XP and cooking duration [`#L201-L204`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L201-L204)

##### ⚡ Special Recipes
- **`simplenergy_pulverizing`**: SimplEnergy pulverizer compatibility validation [`#L186`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L186)

### 🧹 Data Cleanup Operations
- **Empty Recipe Removal**: Automatically removes empty `RESULT_OF_CRAFTING` and `USED_FOR_CRAFTING` lists [`#L37-L41`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L37-L41)
- **Override Model Cleanup**: Removes `override_model` keys from debug exports [`#L43-L49`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L43-L49)
- **Debug Export**: Optionally exports cleaned definitions to specified path for debugging [`#L51-L55`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L51-L55)

### 📝 Error Reporting System
- **Comprehensive Error Collection**: Gathers all validation errors before reporting [`#L57-L58`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L57-L58)
- **Detailed Error Messages**: Provides specific guidance for fixing each issue [`#L212-L217`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L212-L217)
- **Ingredient Validation**: Ensures proper use of `ingr_repr` function for recipe ingredients [`#L168-L172`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L168-L172)
- **Format Recommendations**: Suggests proper text component formats and tools [`#L127-L129`](../../python_package/src/stewbeet/plugins/verify_definitions/__init__.py#L127-L129)

