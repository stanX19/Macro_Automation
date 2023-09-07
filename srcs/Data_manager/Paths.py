import json
import os
import utils

settings_json = r"assets\settings.json"
parent = os.path.dirname
cwd = parent(parent(os.path.realpath(__file__)))
os.chdir(cwd)

assets_path_dict = utils.directory_tree_dict("assets")
# print(json.dumps(assets_path_dict, indent=2))


# +--------------------------------+
# | Some sorting for astestics     |
# +--------------------------------+

with open(assets_path_dict["hsr"]["assets_order"], "r") as f:
   hsr_assets_order = json.load(f)

utils.sort_dict_by_order(assets_path_dict["hsr"], hsr_assets_order)
