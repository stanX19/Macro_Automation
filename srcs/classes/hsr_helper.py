import Template
import mouse


def scroll_and_find(matcher: Template.Matcher, scroll_location: tuple, scroll_tick: int) -> tuple[4]:
    target_cat = matcher.get_location_if_match()
    while target_cat is None:
        mouse.move_to_center(scroll_location)
        mouse.scroll_down(scroll_tick)
        target_cat = matcher.get_location_if_match()

    return target_cat


def to_path_dict(template_dict: dict[str, Template]):
    return {key: temp.path for key, temp in template_dict.items()}
