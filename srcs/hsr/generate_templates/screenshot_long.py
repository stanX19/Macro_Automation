import time

import numpy as np
import pyautogui
import numpy
import mouse
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from logger import logger
import utils
try:
    from . import image_catv
except ImportError:
    import image_catv

@utils.retry_on_exception(RuntimeError, max_retries=3)
def capture_and_compare(roi, prev_img: np.ndarray, full_img: np.ndarray):
    current_img = pyautogui.screenshot()
    current_img = np.array(current_img)[roi[1]:roi[3], roi[0]:roi[2]]

    match_rate = 1 - np.sum(np.abs(current_img.astype(int) - prev_img.astype(int))) / current_img.size / 255
    logger.debug(f"{match_rate=}")

    if match_rate > 0.98:
        return current_img, full_img, False

    full_img = image_catv.array_catv(full_img, current_img, 150, 0.975)

    return current_img, full_img, True


def screenshot_long(roi: tuple[int, int, int, int], scroll_magnitude=5, scroll_loc_rel=None) -> PngImageFile:
    # Capture the initial screenshot
    prev_img = pyautogui.screenshot()
    prev_img = numpy.array(prev_img)[roi[1]:roi[3], roi[0]:roi[2]]
    full_img = prev_img

    running = True
    while running:
        if scroll_loc_rel is not None:
            mouse.move_relative(roi, scroll_loc_rel)
        else:
            mouse.move_to_center(roi)
        mouse.scroll_down(scroll_magnitude)
        mouse.move_away_from(roi)

        prev_img, full_img, running = capture_and_compare(roi, prev_img, full_img)

    return Image.fromarray(full_img)


DOMAINS_ROI = (693, 290, 1656, 884)


def main():
    import keyboard
    keyboard.wait(" ")
    long_screenshot = screenshot_long((692, 450, 1656, 884), scroll_loc_rel=(100, 300))
    long_screenshot.save("long_screnshot.png")  # Save the long screenshot
    long_screenshot.show()

    # print(np.array_equal(np.array(pyautogui.screenshot())[1:101, 2:102],
    #   np.array(pyautogui.screenshot(region=(2, 1, 100, 100)))))


if __name__ == '__main__':
    main()
