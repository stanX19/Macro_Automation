import traceback
import genshin_impact_macro


def main():
    genshin_macro = genshin_impact_macro.GenshinMacro()
    genshin_macro.session_catch()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        input("\n\nPress any key to continue . . . \n")
