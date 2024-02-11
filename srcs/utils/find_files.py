import os
import fnmatch

def find_files(directory: str, pattern: str) -> list[str]:
    matching_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                matching_files.append(os.path.join(root, filename))
    return matching_files