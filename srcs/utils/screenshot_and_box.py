import cv2
import pyautogui
import numpy as np


def screenshot_box_and_show(x1, y1, x2, y2):
    """
    Capture a screenshot, box out the specified region, and display the modified image.

    Args:
        x1, y1, x2, y2: Coordinates of the region to box out.
    """
    # Capture a screenshot using PyAutoGUI
    screenshot = pyautogui.screenshot()

    # Convert the screenshot to a NumPy array (OpenCV format)
    screenshot_np = np.array(screenshot)

    # Create a copy of the image to avoid modifying the original
    boxed_image = screenshot_np.copy()

    # Box out the specified region by drawing a black rectangle
    cv2.rectangle(boxed_image, (x1, y1), (x2, y2), (0, 255, 0))  # -1 fills the rectangle with black color

    # Show the modified image using OpenCV
    cv2.imshow('Boxed Out Image', boxed_image)

    # Wait for a key press and then close the OpenCV window
    cv2.waitKey(0)
    cv2.destroyAllWindows()
