import cv2
import numpy as np

import honkai_star_rail_macro
from template import Template
from honkai_star_rail_macro import *

# Load the image and the template
image = cv2.imread(r'D:\Users\user\PycharmProjects\Macro_Automation\assets\test\screenshot\img_43.png')
# path = r"D:\Users\user\PycharmProjects\Macro_Automation\assets\hsr\templates\navigation\domains\calyx_crimson\calyx_crimson.png"

image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
template = honkai_star_rail_macro.DomainFarm().reduce_count
# template = Dailies().daily_logo

threshold_change = 0.001
while template.threshold >= threshold_change and not template.exists_in(image_gray):
    template.threshold -= threshold_change

loc = template.get_location_in(image_gray)
print(f"{loc}\n{template.threshold}")
cv2.rectangle(image, loc[:2], loc[2:], (0, 255, 0), 2)
cv2.imshow('Matching Result', cv2.resize(image, (960, 540)))
cv2.waitKey(0)
cv2.destroyAllWindows()
