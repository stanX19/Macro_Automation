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


def main():
    global top_left, bot_right, drawing
    top_left = (0, 0)
    bot_right = (0, 0)
    drawing = False

    keyboard.wait("space")
    while keyboard.is_pressed("space"):
        pass
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
        if key_select == ord(" "):
            break

    # Return coordinates of selected region
    top_left = top_left
    bottom_right = bot_right

    print("Combined:", top_left + bottom_right)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    while True:
        main()
