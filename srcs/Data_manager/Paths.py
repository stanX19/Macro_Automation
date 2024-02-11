import json
import os
import utils

settings_json = r"configs/settings.json"
exc_log_dir = r"run_logs"
assets_dir = r"assets"
_parent = os.path.dirname
cwd = _parent(_parent(_parent(os.path.realpath(__file__))))
os.chdir(cwd)

assets_path_dict = utils.directory_tree_dict(assets_dir)
# print(json.dumps(assets_path_dict, indent=2))

assets_path_dict = utils.sorted_dir_tree_by_time(assets_path_dict)

for _dir in assets_path_dict:
    if "assets_order" not in assets_path_dict[_dir]:
        continue
    with open(assets_path_dict[_dir]["assets_order"], "r") as f:
        _dir_assets_order = json.load(f)
    utils.sort_dict_by_order(assets_path_dict[_dir], _dir_assets_order)
    _new_assets_order = utils.dict_to_order(assets_path_dict[_dir])
    with open(assets_path_dict[_dir]["assets_order"], "w+") as f:
        json.dump(_new_assets_order, f, indent=2)
