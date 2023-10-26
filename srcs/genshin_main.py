import traceback
from genshin_impact_macro import LogIn


def main():
    login = LogIn()
    login.start_and_log_in()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        input("\n\nPress any key to continue . . . \n")