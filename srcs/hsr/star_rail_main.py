import traceback
import honkai_star_rail_macro


def main():
    while True:
        hsr_macro = honkai_star_rail_macro.HSRMacro()
        if hsr_macro.session_catch():
            break

def safe_main():
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        input("\n\nPress any key to continue . . . \n")

if __name__ == '__main__':
    safe_main()
