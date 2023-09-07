import pyautogui
import time

def delayed_click_center(cords: tuple[4], delay=0.5):
    time.sleep(delay)
    click_center(cords)

def delayed_relative_click(top_left: tuple, displacement, delay=0.5):
    time.sleep(delay)
    relative_click(top_left, displacement)

def click_center(cords: tuple[4]):
    x = (cords[0] + cords[2]) / 2
    y = (cords[1] + cords[3]) / 2
    pyautogui.moveTo(x, y)
    pyautogui.click()

def relative_click(top_left: tuple, displacement):
    x = top_left[0] + displacement[0]
    y = top_left[1] + displacement[1]
    pyautogui.moveTo(x, y)
    pyautogui.click()

def move_to_center(cords: tuple[4]):
    x = (cords[0] + cords[2]) / 2
    y = (cords[1] + cords[3]) / 2
    pyautogui.moveTo(x, y)

def move_away_from(cords):
    x = cords[2] + 1
    y = cords[3] + 1
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

pyautogui.FAILSAFE = False
if __name__ == '__main__':
    import time
    while True:
        scroll_down(18)
        time.sleep(3)