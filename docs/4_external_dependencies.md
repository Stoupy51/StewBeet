
# 🗃️ Using External Libraries 📚
When creating datapacks, you might want to use items from other datapacks in your recipes or interact with their functionality.<br>
Or maybe, you want to use a library for your project.<br>
This documentation will explain how to do both! ✨


## 🔗 Adding Dependencies
In order to automatically check for the dependencies, you'll need to add them in your [`config.py`](../config.py) file.

```python
DEPENDENCIES: dict[str, dict] = {
	# Automagically, the datapack will check for the presence of dependencies and their minimum required versions at runtime
	# The url is used when the dependency is not found to suggest where to get it
	# The version dict key contains the minimum required version of the dependency in [major, minor, patch] format
	# The main key is the dependency namespace to check for
	# The name can be whatever you want, it's just used in messages
	
	# Example for DatapackEnergy >= 1.8.0
	"energy": {"version":[1, 8, 0], "name":"DatapackEnergy", "url":"https://github.com/ICY105/DatapackEnergy"},
}
```
🔍 By default, an example dependency is already added to the template as you can see above.<br>
The only purpose of this constant is to automatically check for the presence of the dependency and suggest where to get it if not found on load.<br>
⚠️ DISCLAIMER: The dependency must use [LanternLoad](https://github.com/LanternMC/load) with [proper versioning](https://github.com/Gunivers/Bookshelf/issues/272) (e.g. `#your_namespace.major load.status` scoreboard, and same for `minor` and `patch`).

Now, you can add the datapack/library to your `libs` folder and configure whether it should be merged with your pack using the `MERGE_LIBS` option.<br>
When building, the `libs/datapack` folder will be copied to the `BUILD_COPY_DESTINATIONS` folders (only datapacks, not resourcepacks).


## 📦 External Database Setup
The 📝 [`setup_external_definitions.py`](../user/setup_external_definitions.py) script is used to define items from other datapacks that you want to use in your recipes 🛠️.<br>
This currently is the only use-case for the external definitions 📦.<br>
⚠️ DISCLAIMER: This script is currently very scuffed, I'm still figuring out how to properly handle external items.


## 📚 Conclusion
Now you know how to:
- Add dependencies to your project and check for their presence at runtime
- Configure whether libraries should be merged with your pack
- Set up an external definitions to use items from other datapacks in your recipes
This will help you create more complex datapacks that interact with other datapacks and libraries!
Thank you for reading 🙌.

