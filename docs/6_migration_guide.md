
# 🔄 Migration Guide
This guide will help you migrate your project to use Python Datapack in a few simple steps.

## 🔧 Prerequisites
Before migrating your project, make sure you have:
- Python 3.10 or higher installed.
- A working datapack that you want to migrate.
- Understood the [project structure](./1_project_structure.md) with the guide.


## 📦 Fast Migration Steps
1. Clone or download this template repository.
2. Move your datapack and resource pack files into the [`merge` folder](../merge).
3. Configure your [`config.py`](../config.py) with your project details.
4. Run `build.py` and check the generated files in `build/`.


## 🚨 Important Notes
Be aware that the [tick and load](../build/datapack/data/your_namespace/function/v1.21.615/tick.mcfunction) functions will probably not match your existing ones,<br>
so you will have to either:
- Remove them and write your own logic in `user/link.py`
- Change their paths in the merge folder to match the generated ones


## 🎯 Next Steps
After migrating:
1. Test in Minecraft to ensure everything works
2. Start using Python Datapack's features to enhance your datapack!


## 📚 Conclusion
You now know how to:
- Migrate an existing project to use Python Datapack
- Handle potential conflicts with tick/load functions
- Start enhancing your project with Python Datapack features

Migration can seem daunting at first, but Python Datapack makes it as simple as possible! 🎉<br>
The benefits of using Python Datapack will quickly become apparent as you explore its features.

Thank you for reading 🙌



