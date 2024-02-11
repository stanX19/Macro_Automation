import Paths
import utils
import json

def traverse(path_dict: dict):
    for key in path_dict:
        if isinstance(path_dict[key], str):
            path_dict[key] = [path_dict[key], [], 0.7]
        else:
            traverse(path_dict[key])

path_dict = Paths.assets_path_dict
traverse(path_dict)
print(json.dumps(path_dict, indent=2))