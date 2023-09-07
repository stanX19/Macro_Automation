import time
import os
import keyboard
import HonkaiStarRialMacro

def main():
    hsr_macro = HonkaiStarRialMacro.HSRMacro()
    while True:
        if hsr_macro.session():
            break


if __name__ == '__main__':
    main()
