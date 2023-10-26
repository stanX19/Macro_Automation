import os


def sorted_dir_tree_by_time(tree_dict):
    unsorted_files = {}
    ret = {}

    for key, value in tree_dict.items():
        if isinstance(value, dict):
            # Recursively sort files in subdirectories
            ret[key] = sorted_dir_tree_by_time(value)
        elif os.path.isfile(value):
            unsorted_files[key] = value

    sorted_files = sorted(unsorted_files.items(), key=lambda item: os.path.getmtime(item[1]))

    for key, path in sorted_files:
        ret[key] = path
    return ret


if __name__ == '__main__':
    import json
    from directory_tree_dict import directory_tree_dict

    path_to_directory = r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\hsr\templates\navigation'
    directory_tree = directory_tree_dict(path_to_directory)
    x = sorted_dir_tree_by_time(directory_tree)
    print(json.dumps(x, indent=2))
