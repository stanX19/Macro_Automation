import cv2
import numpy as np
import os
from easygui import fileopenbox

# Load the image
# path = r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\hsr\templates\dailies\goto_assignment.png'
path = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr\images\calyx_gold.domain_screenshot.png"
#fileopenbox("select image file", default=os.path.join(os.path.dirname(__file__), "..", "assets\\"))

image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
# Create a copy of the image for visualization
image_with_displacement = image.copy()
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Draw a circle at the selected point on the image copy
        cv2.circle(image_with_displacement, (x, y), 2, (0, 0, 255), -1)
        # Display the image with the selected displacement point
        cv2.imshow('Image with Displacement', image_with_displacement)
        # Print the coordinates of the selected point
        print(f"Displacement Point: ({x}, {y})")

# Create a window to display the image with displacement
cv2.namedWindow('Image with Displacement')
cv2.setMouseCallback('Image with Displacement', mouse_callback)
cv2.imshow('Image with Displacement', image_with_displacement)



# Wait for a key press to exit
cv2.waitKey(0)
cv2.destroyAllWindows()

