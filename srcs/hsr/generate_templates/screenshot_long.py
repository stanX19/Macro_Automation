import numpy as np
import pyautogui
import numpy
import mouse
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from logger import logger
try:
    from . import image_catv
except ImportError:
    import image_catv


def screenshot_long(roi: tuple[int, int, int, int], scroll_magnitude=5, scroll_loc_rel=None) -> PngImageFile:
    # Capture the initial screenshot
    prev_img = pyautogui.screenshot()
    prev_img = numpy.array(prev_img)[roi[1]:roi[3], roi[0]:roi[2]]
    full_img = prev_img

    # Scroll and capture until the last captured image matches the previous one
    while True:
        # Scroll down
        if scroll_loc_rel is not None:
            mouse.move_relative(roi, scroll_loc_rel)
        else:
            mouse.move_to_center(roi)
        mouse.scroll_down(scroll_magnitude)
        mouse.move_away_from(roi)

        # Capture the current screenshot
        current_img = pyautogui.screenshot()
        current_img = numpy.array(current_img)[roi[1]:roi[3], roi[0]:roi[2]]

        # If the current screenshot matches the previous one, break the loop
        match_rate = 1 - np.sum(np.abs(current_img.astype(int) - prev_img.astype(int))) / current_img.size / 255
        logger.debug(f"{match_rate=}")
        if match_rate > 0.95:
            break

        # Concatenate the current image to the full image
        full_img = image_catv.array_catv(full_img, current_img, 300, 0.975)
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
