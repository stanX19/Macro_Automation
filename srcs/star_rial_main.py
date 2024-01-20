import traceback
import honkai_star_rial_macro

def main():
    hsr_macro = honkai_star_rial_macro.HSRMacro()
    while True:
        if hsr_macro.session_catch():
            break


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        input("\n\nPress any key to continue . . . \n")
