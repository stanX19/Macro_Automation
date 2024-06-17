import cv2
import win32api
import utils
import numpy as np
from typing import Sequence
from template_utils import cvt_to_binary


class _Matcher:
    def __init__(self, img_array, roi, method=cv2.TM_CCOEFF_NORMED, binary_preprocess=False):
        self.img_array = img_array
        if binary_preprocess:
            self.img_array = cvt_to_binary(self.img_array)
        self.method = method
        self.binary_preprocess = binary_preprocess
        self.roi = roi

    def match_with(self, img_gray) -> tuple[float, Sequence[int]]:
        roi = self.roi
        img_gray = img_gray[roi[1]:roi[3], roi[0]:roi[2]]
        if self.binary_preprocess:
            img_gray = cvt_to_binary(img_gray)
        result = cv2.matchTemplate(img_gray, self.img_array, self.method)

        # cv2.imshow("template", self.img_array)
        # cv2.waitKey(0)
        # cv2.imshow("screenshot", img_gray)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if self.method is cv2.TM_SQDIFF_NORMED:
            return 1 - min_val, min_loc
        else:
            return max_val, max_loc

    def set_method(self, method):
        self.method = method

    def set_binary_preprocess(self, binary_preprocess):
        self.binary_preprocess = binary_preprocess


class Template:
    def __init__(self, template_path, roi=None, threshold=0.6, crop=None, method=cv2.TM_CCOEFF_NORMED,
                 binary=False):
        image = cv2.imread(template_path)
        if image is None:
            raise ValueError(f"Failed to load template image from '{template_path}'")
        if crop is not None:
            x1, y1, x2, y2 = crop
            image = image[y1: y2, x1: x2]
        self.path = template_path
        self.file_name = utils.get_file_name(template_path)
        self.image = image
        self.array = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.template_h, self.template_w = self.array.shape
        self.threshold = threshold
        if roi is not None:
            self.roi = roi
        else:
            self.roi = (0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
        self._matcher = _Matcher(self.array, self.roi, method=method,
                                 binary_preprocess=binary)

    def set_search_area(self, roi: [tuple[4], list[4]]):
        self.roi = roi
        self._matcher.roi = roi

    def set_threshold(self, threshold):
        self.threshold = threshold

    def _match_with_img(self, img_gray) -> tuple[float, Sequence[int]]:
        return self._matcher.match_with(img_gray)

    def exists_in(self, img_gray) -> bool:
        max_val, max_loc = self._match_with_img(img_gray)

        if max_val < self.threshold:
            return False
        return True

    def get_location_in(self, img_gray) -> [tuple[int, int, int, int], None]:
        max_val, max_loc = self._match_with_img(img_gray)

        if max_val < self.threshold:
            return None
        top_left = max_loc

        # Convert top-left coordinates to screen coordinates
        top_left_screen = (self.roi[0] + top_left[0], self.roi[1] + top_left[1])
        bot_right_screen = (top_left_screen[0] + self.template_w, top_left_screen[1] + self.template_h)

        return top_left_screen + bot_right_screen

    def get_max_matching_threshold(self, img_gray: np.ndarray) -> float:
        max_val, max_loc = self._match_with_img(img_gray)
        return max_val

    def as_threshold(self, threshold: float):
        return Template(self.path, self.roi, threshold)

    def __str__(self):
        return f"({self.file_name}, {self.roi}, {self.threshold})"


if __name__ == '__main__':
    path = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr\templates\navigation\domain_types\calyx_gold.png"
    t = Template(path, crop=(20, 10, 300, 90))
    cv2.imshow("test", t.image)
    cv2.waitKey(0)
