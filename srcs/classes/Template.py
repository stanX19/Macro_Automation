import cv2
import win32api
import utils


class Template:
    def __init__(self, template_path, roi=None, threshold=0.6):
        image = cv2.imread(template_path)
        if image is None:
            raise ValueError(f"Failed to load template image from '{template_path}'")

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

    def set_search_area(self, roi: [tuple[4], list[4]]):
        self.roi = roi

    def set_threshold(self, threshold):
        self.threshold = threshold

    def _match_with_img(self, img_grey):
        img_grey = img_grey[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]
        
        # if there's an error here check if img img_grey is really in greyscale
        result = cv2.matchTemplate(img_grey, self.array, cv2.TM_CCOEFF_NORMED)
        return cv2.minMaxLoc(result)

    def exists_in(self, img_grey) -> bool:
        _, max_val, _, _ = self._match_with_img(img_grey)

        if max_val < self.threshold:
            return False
        return True

    def get_location_in(self, img_grey) -> [tuple, None]:
        _, max_val, _, max_loc = self._match_with_img(img_grey)
        
        if max_val < self.threshold:
            return None
        top_left = max_loc

        # Convert top-left coordinates to screen coordinates
        top_left_screen = (self.roi[0] + top_left[0], self.roi[1] + top_left[1])
        bot_right_screen = (top_left_screen[0] + self.template_w, top_left_screen[1] + self.template_h)

        return top_left_screen + bot_right_screen

    def __str__(self):
        return f"({self.file_name}, {self.roi}, {self.threshold})"
