import ctypes

def get_startup_folder():
    CSIDL_STARTUP = 0x0007
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value

    buf = ctypes.create_unicode_buffer(260)  # Maximum path length
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_STARTUP, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value

if __name__ == '__main__':
    print(f"Startup Folder: {get_startup_folder()}")
