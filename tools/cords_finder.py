import time
import pyperclip
import cv2
import numpy as np
import pyautogui
import keyboard

# Global variables to track mouse events
drawing = False
top_left = (0, 0)
bot_right = (0, 0)


def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    return screenshot


def read_mouse(event, x, y, flags, param):
    global drawing, top_left, bot_right

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        top_left = (x, y)
        bot_right = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            bot_right = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        bot_right = (x, y)

def wait_for_key_release(key):
    while keyboard.is_pressed(key):
        pass

def main():
    global top_left, bot_right, drawing
    top_left = (0, 0)
    bot_right = (0, 0)
    drawing = False

    while True:
        if keyboard.is_pressed("space"):
            wait_for_key_release("space")
            break
        elif keyboard.is_pressed("tab"):
            wait_for_key_release("tab")
            print("paused")
            keyboard.wait("tab")
            wait_for_key_release("tab")
            print("running")
    # Space key pressed, capture screenshot
    screenshot = capture_screenshot()
    cv2.namedWindow("Screenshot")
    cv2.setMouseCallback("Screenshot", read_mouse)
    cv2.setWindowProperty("Screenshot", cv2.WND_PROP_TOPMOST, 1)

    while cv2.getWindowProperty('Screenshot', cv2.WND_PROP_VISIBLE) > 0:
        displayed = screenshot.copy()
        cv2.rectangle(displayed, top_left, bot_right, (255, 255, 0))
        cv2.imshow("Screenshot", displayed)
        key_select = cv2.waitKey(1) & 0xFF
        if keyboard.is_pressed("space"):
            wait_for_key_release("space")
            break

    top_left = list(top_left)
    bot_right = list(bot_right)
    if top_left[0] > bot_right[0]:
        top_left[0], bot_right[0] = bot_right[0], top_left[0]
    if top_left[1] > bot_right[1]:
        top_left[1], bot_right[1] = bot_right[1], top_left[1]
    top_left = tuple(top_left)
    bot_right = tuple(bot_right)
    pyperclip.copy(str(top_left + bot_right))
    width = bot_right[0] - top_left[0]
    height = bot_right[1] - top_left[1]
    print("Combined:", top_left + bot_right, "Width:", width, "Height:", height)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("press space to capture screenshot")
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
