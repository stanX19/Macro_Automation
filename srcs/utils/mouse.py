import keyboard
import pyautogui
import time
from pyautogui import moveTo as move_to


def click():
    pyautogui.mouseDown(button="left")
    time.sleep(0.1)
    pyautogui.mouseUp(button="left")
    time.sleep(0.4)


def delayed_click_center(cords: tuple[int, int, int, int], delay=0.5):
    time.sleep(delay)
    click_center(cords)


def delayed_relative_click(top_left: tuple, displacement, delay=0.5):
    time.sleep(delay)
    click_relative(top_left, displacement)


def click_center(cords: tuple[int, int, int, int]):
    x = (cords[0] + cords[2]) / 2
    y = (cords[1] + cords[3]) / 2
    pyautogui.moveTo(x, y)
    click()


def click_relative(top_left: tuple, displacement):
    x = top_left[0] + displacement[0]
    y = top_left[1] + displacement[1]
    pyautogui.moveTo(x, y)
    click()


def move_relative(top_left: tuple, displacement):
    x = top_left[0] + displacement[0]
    y = top_left[1] + displacement[1]
    pyautogui.moveTo(x, y)


def move_to_center(cords: tuple[int, int, int, int]):
    x = (cords[0] + cords[2]) / 2
    y = (cords[1] + cords[3]) / 2
    pyautogui.moveTo(x, y)


def move_away_from(cords):
    x = cords[2] + 10
    y = cords[3] + 10
    screen_width, screen_height = pyautogui.size()
    if x > screen_width:
        x = screen_width - 1
    if y > screen_height:
        y = screen_height - 1
    pyautogui.moveTo(x, y)


def scroll_up(y: int):
    for i in range(y):
        pyautogui.vscroll(1)


def scroll_down(y: int):
    for i in range(y):
        pyautogui.scroll(-1)


def scroll_down_general(y: int):
    if y > 0:
        scroll_down(y)
    else:
        scroll_up(-y)


def alt_and_click(loc: tuple, displacement: tuple):
    pyautogui.keyDown("alt")
    time.sleep(0.1)
    click_relative(loc, displacement)
    pyautogui.keyUp("alt")


def click_and_move_away(loc: tuple, interval=1):
    click_center(loc)
    time.sleep(interval)
    move_away_from(loc)


pyautogui.FAILSAFE = False


if __name__ == '__main__':
    import time

    while True:
        scroll_down(18)
        time.sleep(3)
