
# Imports
import json
from typing import Any

from ..utils.io import FILES_TO_WRITE


def main(config: dict):

	# Get all mcfunctions paths
	mcfunctions: dict[str, dict[str, Any]] = {}
	functions_folder = "/function/"
	for file_path in FILES_TO_WRITE:
		if functions_folder in file_path and file_path.endswith(".mcfunction"):

			# Get namespace of the file
			splitted = file_path.split(functions_folder, 1)
			namespace = splitted[0].split("/")[-1]

			# Get string that is used for calling the function (ex: "namespace:my_function")
			to_be_called = f"{config['namespace']}:" + splitted[1].replace(".mcfunction","")

			# Add to mcfunctions dictionary
			mcfunctions[to_be_called] = {"path": file_path, "within": []}

	# For each json file, get the functions that it calls
	functions_tags_folder = "/tags/function/"
	advancements_folder = "/advancement/"
	for file_path in FILES_TO_WRITE:
		if file_path.endswith(".json"):
			if functions_tags_folder in file_path:

				# Get namespace of the file
				splitted = file_path.split(functions_tags_folder, 1)
				namespace = splitted[0].split("/")[-1]

				# Get string that is used for calling the function (ex: "#namespace:my_function")
				to_be_called = f"#{namespace}:" + splitted[1].replace(".json","")

				# Read the json file and loop its values
				data = json.loads(FILES_TO_WRITE[file_path])
				if data.get("values"):
					for value in data["values"]:

						# Get the function that is called, either "function" or {"id": "function", ...}
						calling = value if isinstance(value, str) else value["id"]

						# If the called function is registered, append the name of this file
						if calling in mcfunctions.keys() and to_be_called not in mcfunctions[calling]["within"]:
							mcfunctions[calling]["within"].append(to_be_called)

			elif advancements_folder in file_path:

				# Get namespace of the file
				splitted = file_path.split(advancements_folder, 1)
				namespace = splitted[0].split("/")[-1]

				# Get string that is used for calling the function (ex: "advancement namespace:my_function")
				to_be_called = f"advancement {namespace}:" + splitted[1].replace(".json","")

				# Read the json file and loop its values
				data: dict = json.loads(FILES_TO_WRITE[file_path])
				if data.get("rewards", {}) and data["rewards"].get("function"):
					calling = data["rewards"]["function"]
					if calling in mcfunctions.keys() and to_be_called not in mcfunctions[calling]["within"]:
						mcfunctions[calling]["within"].append(to_be_called)


	# For each mcfunction file, look at each lines
	for file, data in mcfunctions.items():
		for line in FILES_TO_WRITE[data["path"]].split("\n"):

			# If the line call a function,
			if "function " in line:

				# Get the called function
				splitted = line.split("function ", 1)[1].replace("\n","").split(" ")
				calling = splitted[0].replace('"', '').replace("'", "")

				# Get additional text like macros, ex: function iyc:function {id:"51"}
				more = ""
				if len(splitted) > 0:
					more = " " + " ".join(splitted[1:]) # Add Macros or schedule time

				# If the called function is registered, append the name of this file as well as the additional text
				if calling in mcfunctions.keys() and (file + more) not in mcfunctions[calling]["within"]:
					mcfunctions[calling]["within"].append(file + more)


	# For each mcfunction file, add the header
	for file, data in mcfunctions.items():

		# Get file content
		content = FILES_TO_WRITE[data["path"]]
		if not content.startswith("\n"):
			content = "\n" + content

		# Prepare header
		header: str = f"""
#> {file}
#
# @within\t"""

		# Get all the calling function and join them with new lines
		withins = "\n#\t\t\t".join(w.strip() for w in data["within"])
		if data["within"]:
			header += withins + "\n#\n"
		else:
			header += "???\n#\n"

		# Re-write the file
		FILES_TO_WRITE[data["path"]] = header + content

