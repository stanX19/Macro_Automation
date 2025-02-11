import time
from typing import Union
from matcher import Matcher, TemplateData
from template import Template


class StatusMatcher:
    """
    Extension for Matcher
    Automatically stores existing time for each template data upon update()
    """
    def __init__(self, *templates: Template):
        """

        :param templates: Template objects, returned matching list will follow the input order
        """
        self._delta_time = 0
        self._templates = list(templates)
        self._matcher = Matcher(*templates)
        self._previous_time = float("inf")
        self._data: dict[Template, TemplateData] = {t: TemplateData(t) for t in self._templates}

    def add_template(self, *templates: Template, raise_error=True):
        for template in templates:
            if template not in self._templates:
                self._templates.append(template)
                self._data[template] = TemplateData()
            elif raise_error:
                raise ValueError("template already exists")

        self._matcher.templates = self._templates

    def remove_template(self, *templates: Template, raise_error=True):
        for template in templates:
            if template in self._templates:
                self._templates.remove(template)
                del self._data[template]
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
        template_datas = self._matcher.get_matching_templates_data()
        self.refresh_delta_time()

        matching_templates = [t.template for t in template_datas]

        for template, loc, _, threshold in template_datas:
            self._data[template].loc = loc
            self._data[template].threshold = threshold

        for template, data in self._data.items():
            if template in matching_templates:
                if data.time == 0.0:
                    data.time += min(0.001, self._delta_time)
                else:
                    data.time += self._delta_time
            else:
                data.time = 0.0
                data.location = None

    def templates_filtered(self, threshold_secs=1):
        return [t for t in self._data if self._data[t].time > threshold_secs]

    def reset_template(self, template):
        self._data[template].time = 0
        self._data[template].loc = None

    def reset_all_template(self):
        for template in self._templates:
            self.reset_template(template)

    def ignore_template_for(self, template: Template, secs: float):
        self._data[template].time = -secs

    def get_all_template_status_list(self) -> list[tuple[Template, Union[tuple[int, int, int, int], None], float]]:
        self.update()
        return [(t, l, m) for t, l, m, h in self._data.values()]

    def get_all_template_status_dict(self) -> dict[Template, TemplateData]:
        self.update()
        return self._data.copy()

    def get_all_template_data(self) -> list[TemplateData]:
        self.update()
        return list(self._data.copy().values())

    def counter(self, template: Template) -> float:
        return self._data[template].time

    def location(self, template: Template) -> Union[tuple[int, int, int, int], None]:
        try:
            return self._data[template].loc
        except KeyError:
            return None

    def __getitem__(self, template: Template) -> TemplateData:
        try:
            return self._data[template]
        except KeyError:
            return TemplateData(template)

    def __iter__(self) -> list[TemplateData]:
        return list(self._data.values())