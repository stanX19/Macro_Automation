import numpy as np
import pyautogui
import numpy
import mouse
import image_catv
from PIL import Image
from PIL.PngImagePlugin import PngImageFile


def screenshot_long(roi: tuple[int, int, int, int], scroll_magnitude=5) -> PngImageFile:
    # Capture the initial screenshot
    prev_img = pyautogui.screenshot()
    prev_img = numpy.array(prev_img)[roi[1]:roi[3], roi[0]:roi[2]]
    full_img = prev_img

    # Scroll and capture until the last captured image matches the previous one
    while True:
        # Scroll down
        mouse.move_to_center(roi)
        # print("scroll down pls")
        # keyboard.wait(" ")
        mouse.scroll_down(scroll_magnitude)
        mouse.move_away_from(roi)

        # Capture the current screenshot
        current_img = pyautogui.screenshot()
        current_img = numpy.array(current_img)[roi[1]:roi[3], roi[0]:roi[2]]

        # If the current screenshot matches the previous one, break the loop
        print(" ", np.sum(current_img == prev_img) / current_img.size)
        if np.sum(current_img == prev_img) / current_img.size > 0.75:
            break

        # Concatenate the current image to the full image
        full_img = image_catv.array_catv(full_img, current_img, 300, 0.7)
        # Update the previous image for comparison in the next iteration
        prev_img = current_img

    # Return the full captured long screenshot
    return Image.fromarray(full_img)


DOMAINS_ROI = (694, 293, 1656, 925)


def main():
    import keyboard
    keyboard.wait(" ")
    long_screenshot = screenshot_long(DOMAINS_ROI)
    long_screenshot.save("long_screnshot.png")  # Save the long screenshot
    long_screenshot.show()

    # print(np.array_equal(np.array(pyautogui.screenshot())[1:101, 2:102],
    #   np.array(pyautogui.screenshot(region=(2, 1, 100, 100)))))


if __name__ == '__main__':
    main()
