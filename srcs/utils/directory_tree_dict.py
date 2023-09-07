import os
from pathlib import Path

def directory_tree_dict(path):
    result = {}

    if os.path.isdir(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                result[item] = directory_tree_dict(item_path)
            else:
                name = Path(item_path).stem
                result[name] = item_path

    return result