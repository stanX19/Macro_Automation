from pathlib import Path

def get_file_name(path):
    return Path(path).stem

if __name__ == '__main__':
    print(get_file_name(r"srcs\utils\get_file_name.py"))