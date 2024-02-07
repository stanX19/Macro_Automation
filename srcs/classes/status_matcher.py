import time
from typing import Union
import mouse
import pyautogui
from matcher import Matcher, TemplateData
from template import Template


class StatusMatcher:
    def __init__(self, *templates: Template):
        self._delta_time = 0
        self._templates = list(templates)
        self._matcher = Matcher(*templates)
        self._previous_time = float("inf")
        self._counter: dict[Template: float] = {t: 0 for t in self._templates}
        self._locations: dict[Template: tuple[int, int, int, int]] = {}

    def add_template(self, *templates: Template, raise_error=True):
        for template in templates:
            if template not in self._templates:
                self._templates.append(template)
                self._counter[template] = 0
            elif raise_error:
                raise ValueError("template already exists")

        self._matcher.templates = self._templates

    def remove_template(self, *templates: Template, raise_error=True):
        for template in templates:
            if template in self._templates:
                self._templates.remove(template)
                del self._counter[template]
                del self._locations[template]
            elif raise_error:
                raise ValueError("template not found")

        self._matcher.templates = self._templates

    def reset_start_time(self):
        self._delta_time = 0
        self._previous_time = float('inf')

    def refresh_delta_time(self) -> float:
        current_time = time.time()
        self._delta_time = max(0.0, current_time - self._previous_time)
        self._previous_time = current_time
        return self._delta_time

    def update(self):
        template_datas = self._matcher.get_matching_templates()
        self.refresh_delta_time()

        matching_templates = [t.template for t in template_datas]

        for template_data in template_datas:
            template, loc = template_data.pair()
            self._locations[template] = loc

        for template in self._counter:
            if template in matching_templates:
                self._counter[template] += self._delta_time
            else:
                self._counter[template] = 0
                self._locations[template] = None

    def templates_filtered(self, threshold_secs=1):
        return [t for t in self._counter if self._counter[t] > threshold_secs]

    def reset_template(self, template):
        self._counter[template] = 0
        self._locations[template] = None

    def reset_all_template(self):
        for template in self._templates:
            self.reset_template(template)

    def ignore_template_for(self, template: Template, secs: float):
        self._counter[template] = -secs

    def get_all_template_status_list(self) -> list[tuple[Template, Union[tuple[int, int, int, int], None], float]]:
        self.update()
        return list(self.__iter__())

    def get_all_template_status_dict(self) -> dict[Template, tuple[float, Union[tuple[int, int, int, int], None]]]:
        self.update()
        return {t: TemplateData(t, l, s) for t, s, l in self}  # {t: template, s: second, l: location}

    def counter(self, template: Template) -> float:
        return self._counter[template]

    def location(self, template: Template) -> Union[tuple[int, int, int, int], None]:
        return self._locations.get(template, None)

    def __getitem__(self, template: Template) -> TemplateData:
        return TemplateData(template, self._locations.get(template, None), max(0, self._counter[template]))

    def __iter__(self) -> list[tuple[Template, Union[tuple[int, int, int, int], None], float]]:
        return [(template, self._locations.get(template, None), max(0, self._counter[template])) for template in
                self._counter]
