import cv2
import numpy as np
import pyautogui
import win32gui
import win32ui
import win32api
import time
import mouse


class Template:
    def __init__(self, template_path, roi=None, threshold=0.6):
        image = cv2.imread(template_path)
        if image is None:
            raise ValueError(f"Failed to load template image from '{template_path}'")

        self.path = template_path
        self.image = image
        self.template = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.template_h, self.template_w = self.template.shape
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
        
        # if there's a bug here check if img img_grey is really in greyscale
        result = cv2.matchTemplate(img_grey, self.template, cv2.TM_CCOEFF_NORMED)
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


class TemplateData:
    def __init__(self, template, location):
        self.template = template
        self.location = location


class Matcher:
    def __init__(self, *templates: Template, timeout=3600):
        self.templates = templates
        self.timeout = timeout

        if not templates:
            raise AssertionError("Matcher must be tied to at least a template")

    def exists(self) -> bool:
        return bool(self.get_matching_templates())

    def all_exists(self) -> bool:
        return len(self.get_matching_templates()) == len(self.templates)

    def get_location_if_match(self) -> [tuple[4], None]:
        match = self.get_matching_templates()
        if match:
            return match[0].location
        return None

    def get_matching_templates(self) -> list[TemplateData]:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)  # Convert to grayscale
        matching_templates = []

        for template in self.templates:
            if template.exists_in(screenshot):
                location = template.get_location_in(screenshot)
                matching_templates.append(TemplateData(template, location))

        return matching_templates

    def wait_and_get_location(self, timeout=None) -> tuple[4]:
        return self.wait_for_matches(timeout=timeout)[0].location

    def wait_and_match(self, timeout=None) -> TemplateData:
        return self.wait_for_matches(timeout=timeout)[0]

    def wait_for_matches(self, timeout=None) -> list[TemplateData]:
        if timeout is None:
            timeout = self.timeout

        start_time = time.time()
        while time.time() - start_time < timeout:
            matching_template = self.get_matching_templates()
            if matching_template:
                return matching_template

        raise TimeoutError

    def wait_for_all_to_match(self, timeout=None) -> list[TemplateData]:
        if timeout is None:
            timeout = self.timeout

        start_time = time.time()
        while time.time() - start_time < timeout:
            matching_templates = self.get_matching_templates()
            
            if len(matching_templates) == len(self.templates):
                return matching_templates

        raise TimeoutError

    def while_exist_do(self, function, args=None, kwargs=None, exist=True, delay=1):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        while self.exists() == exist:
            function(*args, **kwargs)
            time.sleep(delay)

    def click_center_when_exist(self, delay=1):
        button = self.wait_and_match()
        exists = 1
        while exists:
            mouse.click_center(button.location)
            mouse.move_away_from(button.template.roi)
            time.sleep(delay)
            exists = self.exists()

    def click_relative_when_exist(self, displacement, delay=1):
        button = self.wait_and_match()
        exists = 1
        while exists:
            mouse.relative_click(button.location, displacement)
            mouse.move_away_from(button.template.roi)
            time.sleep(delay)
            exists = self.exists()


if __name__ == '__main__':
    p1 = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\test\templates\img_1.png"
    p2 = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\test\templates\img_2.png"
    t1 = Template(p1)
    t2 = Template(p2)
    m = Matcher(t1, t2)
    m.wait_for_all_to_match()
