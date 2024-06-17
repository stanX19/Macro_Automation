import cv2
import numpy as np
import pyautogui
import time
import mouse
from template import Template


class TemplateData:
    def __init__(self, template=None, location=None, time=0.0, threshold=0.0):
        self.template = template
        self.loc = location
        self.time = time
        self.threshold = threshold

    def __getitem__(self, index):
        return [self.template, self.loc, self.time, self.threshold][index]

    def __str__(self):
        if self.threshold:
            return f"{self.template}, {self.loc}, {self.threshold:.2f}"
        return f"{self.template}, {self.loc}, None"

    def __iter__(self):
        return iter((self.template, self.loc, self.time, self.threshold))


class Matcher:
    def __init__(self, *templates: Template, timeout=600):
        self.templates = templates
        self.timeout = timeout

        if not templates:
            raise AssertionError("Matcher must be tied to at least a template")

    def __str__(self):
        return "[{}]".format(", ".join(t.name for t in self.templates))

    def exists(self) -> bool:
        return bool(self.get_matching_templates_data())

    def all_exists(self) -> bool:
        return len(self.get_matching_templates_data()) == len(self.templates)

    def get_location_if_match(self) -> [tuple[int, int, int, int], None]:
        if match := self.get_matching_templates_data():
            return match[0].loc
        return None

    def get_data_if_match(self) -> [TemplateData, None]:
        if match := self.get_matching_templates_data():
            return match[0]
        return None

    def get_matching_template_list(self) -> list[Template]:
        return [i.template for i in self.get_matching_templates_data()]

    def get_matching_templates_data(self) -> list[TemplateData]:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)  # Convert to grayscale
        matching_templates = []

        for template in self.templates:
            if template.exists_in(screenshot):
                location = template.get_location_in(screenshot)
                threshold = template.get_max_matching_threshold(screenshot)
                matching_templates.append(TemplateData(template, location, threshold=threshold))

        return matching_templates

    def wait_and_get_location(self, timeout=None) -> tuple[int, int, int, int]:
        return self.wait_for_matches(timeout=timeout)[0].loc

    def wait_and_match(self, timeout=None) -> TemplateData:
        """
        Returns the FIRST matching template
        :param timeout: seconds
        """
        return self.wait_for_matches(timeout=timeout)[0]

    def wait_for_matches(self, timeout=None) -> list[TemplateData]:
        """
        Returns (any) first matching templates
        :param timeout: seconds
        :return: any matching templates in a frame
        """
        if timeout is None:
            timeout = self.timeout

        start_time = time.time()
        while time.time() - start_time < timeout:
            matching_template = self.get_matching_templates_data()
            if matching_template:
                return matching_template

        raise TimeoutError

    def wait_for_all_to_match(self, timeout=None) -> list[TemplateData]:
        if timeout is None:
            timeout = self.timeout

        start_time = time.time()
        while time.time() - start_time < timeout:
            matching_templates = self.get_matching_templates_data()

            if len(matching_templates) == len(self.templates):
                return matching_templates

        raise TimeoutError

    def wait_for_unmatch(self, delay=1.0):
        start_time = time.time()
        while self.exists() and start_time + self.timeout > time.time():
            time.sleep(delay)

    def while_exist_do(self, function, args=None, kwargs=None, interval=1.0):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []

        start_time = time.time()
        while self.exists() and start_time + self.timeout > time.time():
            function(*args, **kwargs)
            time.sleep(interval)

    def while_not_exist_do(self, function, args=None, kwargs=None, interval=1.0):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []

        start_time = time.time()
        while not self.exists() and start_time + self.timeout > time.time():
            function(*args, **kwargs)
            time.sleep(interval)

    def click_center_when_exist(self, interval=1.0):
        self.wait_and_match()
        exists = 1

        start_time = time.time()
        while exists and start_time + self.timeout > time.time():
            for button in self.get_matching_templates_data():
                mouse.click_center(button.loc)
                mouse.move_away_from(button.template.roi)
            time.sleep(interval)
            exists = self.exists()

    def click_relative_when_exist(self, displacement, interval=1.0):
        self.wait_and_match()
        exists = 1

        start_time = time.time()
        while exists and start_time + self.timeout > time.time():
            for button in self.get_matching_templates_data():
                mouse.click_relative(button.loc, displacement)
                mouse.move_away_from(button.template.roi)
            time.sleep(interval)
            exists = self.exists()


if __name__ == '__main__':
    p1 = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\test\templates\img_1.png"
    p2 = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\assets\test\templates\img_2.png"
    t1 = Template(p1)
    t2 = Template(p2)
    m = Matcher(t1, t2)
    m.wait_for_all_to_match()