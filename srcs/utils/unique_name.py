from pathlib import Path

def unique_name(path: str) -> str:
    """
    Finds a unique name for the given file path.
    :param path: name of file
    :return: str representing unique path
    """
    path = Path(path)
    n = 1
    new_path = path
    while new_path.exists():
        new_path = path.with_stem(f"{path.stem}_{n}")
        n += 1
    return str(new_path)

if __name__ == '__main__':
    print(unique_name(__file__))
