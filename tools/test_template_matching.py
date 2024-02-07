import cv2
import numpy as np
from template import Template

# Load the image and the template
image = cv2.imread(r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\test\screenshot\img_15.png')
path = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\hsr\templates\domain_farm\support\priority\BangWoSu69 JingLiu.png"
path2 = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\hsr\templates\navigation\domain_types\img.png"

template = Template(path, (71, 187, 528, 957), 0.9)

# Extract the ROI from the image
x1, y1, x2, y2 = template.roi
roi = image[y1:y2, x1:x2]

# Get the height and width of the image
image_height, image_width, _ = roi.shape

# Get the height and width of the template
template_height, template_width = template.template.shape

# Convert both the ROI and template to grayscale
roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
template_gray = template.template

locations = ([],)

result = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)

template.threshold += 0.001
while not len(locations[0]) > 0 and template.threshold >= 0:
    # Set a threshold to identify good matches
    template.threshold -= 0.001
    locations = np.where(result >= template.threshold)


print(template.threshold)
# Draw rectangles around the matched areas in the ROI
for pt in zip(*locations[::-1]):
    cv2.rectangle(roi, pt, (pt[0] + template.template.shape[1], pt[1] + template.template.shape[0]), (0, 255, 0), 2)

# Display the result image with rectangles in the ROI
cv2.imshow('Matching Result', cv2.resize(image, (960, 540)))
cv2.waitKey(0)
cv2.destroyAllWindows()
