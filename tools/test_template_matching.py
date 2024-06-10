import cv2
import numpy as np
from template import Template

# Load the image and the template
image = cv2.imread(r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\test\screenshot\img_29.png')
path = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr\templates\navigation\update_template\double_drop.png"
path2 = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr\templates\navigation\domain_types\calyx_crimson.png"

template = Template(path2, (244, 271, 686, 918), 0.7, crop=(20, 10, 200, 90))
print(template.array.shape)
# Extract the ROI from the image
x1, y1, x2, y2 = template.roi
roi = image[y1:y2, x1:x2]

# Get the height and width of the image
image_height, image_width, _ = roi.shape

# Get the height and width of the template
template_height, template_width = template.array.shape

# Convert both the ROI and template to grayscale
roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
template_gray = template.array

locations = ([],)

result = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)

template.threshold += 0.001
while not len(locations[0]) > 0 and template.threshold >= 0:
    # Set a threshold to identify good matches
    template.threshold -= 0.001
    locations = np.where(result >= template.threshold)



# Draw rectangles around the matched areas in the ROI
for pt in zip(*locations[::-1]):
    print(pt)
    cv2.rectangle(roi, pt, (pt[0] + template.array.shape[1], pt[1] + template.array.shape[0]), (0, 255, 0), 2)

print(template.threshold)

# Display the result image with rectangles in the ROI
cv2.imshow('Matching Result', cv2.resize(image, (960, 540)))
cv2.waitKey(0)
cv2.destroyAllWindows()
