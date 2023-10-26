import mouse
import time
from matcher import Matcher
from template import Template


def scroll_and_find(matcher: Matcher, scroll_location: tuple, scroll_tick: int, timeout=1800)\
        -> tuple[int, int, int, int]:
    target_loc = matcher.get_location_if_match()

    start_time = time.time()
    while target_loc is None and time.time() - start_time <= timeout:
        mouse.move_to_center(scroll_location)
        mouse.scroll_down(scroll_tick)
        target_loc = matcher.get_location_if_match()

    if not time.time() - start_time <= timeout and target_loc is None:
        raise TimeoutError("Target not matched within time limit")
    return target_loc


def to_path_dict(template_dict: dict[str, Template]):
    return {key: temp.path for key, temp in template_dict.items()}

