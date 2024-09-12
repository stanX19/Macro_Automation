import time
import timeit
from typing import Sequence, Union

import cv2
import numpy as np
import utils
from template_utils import cvt_to_binary, use_cached_result_for_same_array


class _MatchHelper:
    def __init__(self, img_array, roi: tuple[int, int, int, int], method: int = cv2.TM_CCOEFF_NORMED,
                 binary_preprocess: bool = False, varying_size: bool = False):
        self.template_array: np.ndarray = img_array
        if binary_preprocess:
            self.template_array = cvt_to_binary(self.template_array)
        self.method: int = method
        self.binary_preprocess: bool = binary_preprocess
        self.varying_size: bool = varying_size
        self.scales: list[float] = [1.0] if not varying_size else [1.0, 0.8, 0.9, 1.1, 1.2]
        self.roi: tuple[int, int, int, int] = roi

    def preprocess_image_gray(self, img_gray: np.ndarray) -> np.ndarray:
        shape = img_gray.shape[:2]
        roi = self.roi
        roi = [roi[0], roi[1], min(roi[2], shape[1]), min(roi[3], shape[0])]  # Clamping the ROI

        img_gray = img_gray[roi[1]:roi[3], roi[0]:roi[2]]

        if self.binary_preprocess:
            img_gray = cvt_to_binary(img_gray)

        return img_gray

    @use_cached_result_for_same_array
    def match_with(self, img_gray: np.ndarray) -> tuple[float, Sequence[int]]:
        img_gray = self.preprocess_image_gray(img_gray)
        best_val = -1.0
        best_loc = None

        for scale in self.scales:
            val, loc = self._match_with_scale(img_gray, scale)
            if val > best_val:
                best_loc = loc
                best_val = val

        return best_val, best_loc

    def _match_with_scale(self, cropped_img_gray: np.ndarray, scale: float):
        resized_template = cv2.resize(self.template_array, (0, 0), fx=scale, fy=scale)
        result = cv2.matchTemplate(cropped_img_gray, resized_template, self.method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if self.method == cv2.TM_SQDIFF_NORMED:
            match_val = 1 - min_val
            match_loc = min_loc
        else:
            match_val = max_val
            match_loc = max_loc

        return match_val, self._matched_loc_to_rect(match_loc, scale)

    def _matched_loc_to_rect(self, max_loc: Union[None, tuple[int, int], Sequence[int]], scale: float = 1.0):
        if max_loc is None:
            return None
        template_h, template_w = self.template_array.shape[:2]
        template_h, template_w = int(template_h * scale), int(template_w * scale)

        top_left_screen = (self.roi[0] + max_loc[0], self.roi[1] + max_loc[1])
        bot_right_screen = (top_left_screen[0] + template_w, top_left_screen[1] + template_h)

        return top_left_screen + bot_right_screen


class Template:
    def __init__(self, template_path, roi=None, threshold=0.6, crop=None, method=cv2.TM_CCOEFF_NORMED, binary=False,
                 variable_size=False):
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
        self.threshold = threshold
        if roi is not None:
            self.roi = roi
        else:
            self.roi = (0, 0, 10000000, 10000000)
        self._matcher = _MatchHelper(self.array, self.roi, method=method, binary_preprocess=binary,
                                     varying_size=variable_size)

    def set_search_area(self, roi: [tuple[int, int, int, int], list[int]]):
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
        return max_loc

    def get_max_matching_threshold(self, img_gray: np.ndarray) -> float:
        max_val, max_loc = self._match_with_img(img_gray)
        return max_val

    def as_threshold(self, threshold: float):
        return Template(self.path, self.roi, threshold)

    def __str__(self):
        return f"({self.file_name}, {self.roi}, {self.threshold})"


def test():
    path = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\genshin\templates\login\genshin_logo.png"
    t = Template(path, threshold=0.9, binary=True)
    import pyautogui

    input("Press enter to start: ")
    start_time = time.time()
    N = 25
    for i in range(N):
        print(f"{i} ok")
        raw_screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_BGR2RGB)
        screenshot = cv2.cvtColor(raw_screenshot, cv2.COLOR_RGB2GRAY)  # Convert to grayscale
        print(t.exists_in(screenshot))
        # print(t.exists_in(screenshot))
        # print(t.exists_in(screenshot))
        # print(t.exists_in(screenshot))
        # print(t.exists_in(screenshot))
        # if t.exists_in(screenshot) or 1:
        #     # print("exists")
        #     loc = t.get_location_in(screenshot)
        #     threshold = t.get_max_matching_threshold(screenshot)
            # print(loc, threshold)
            # pt = (loc[0], loc[1], loc[2] - loc[0], loc[3] - loc[1])
            # cv2.rectangle(raw_screenshot, pt, (0, 255, 0))
            # cv2.putText(raw_screenshot, f"{threshold:.2f}", (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
    print((time.time() - start_time) / N)
    # cv2.imshow("test", raw_screenshot)
    # cv2.waitKey(0)


if __name__ == '__main__':
    test()