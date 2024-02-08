import os

def unique_name(basename: str, extension: str)->str:
    """
    finds unique name
    :param basename: name of file
    :param extension: dot not included
    :return: str representing unique path
    """
    n = 1
    if extension:
        extension = "." + extension

    new_name = f"{basename}{extension}"
    while os.path.exists(new_name):
        new_name = f"{basename}_{n}{extension}"
        n += 1
    return new_name