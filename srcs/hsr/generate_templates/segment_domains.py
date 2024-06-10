import os.path
import cv2
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
import Paths
from logger import logger


def in_list(val: tuple, container: list[tuple], uncertainty: tuple):
    for data in container:
        if abs(val[0] - data[0]) <= uncertainty[0] and abs(val[1] - data[1]) <= uncertainty[1]:
            return True
    return False


def locate_template_no_overlap(base_img: PngImageFile, template: PngImageFile, threshold: float) -> list[tuple[int, int]]:
    base_img_gray = cv2.cvtColor(np.array(base_img), cv2.COLOR_BGR2GRAY)
    template_img_gray = cv2.cvtColor(np.array(template), cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(base_img_gray, template_img_gray, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    filtered_locations: list[tuple] = []
    for loc in zip(*locations[::-1]):
        if not in_list(loc, filtered_locations, template.size):
            filtered_locations.append(loc)

    return filtered_locations


def average_height(seps: list[int]):
    """

    :param seps: sorted list of y-value of seps
    :return:
    """
    all_height = [seps[i + 1] - seps[i] for i in range(len(seps) - 1)]
    if not all_height:
        return 0
    # now seps is confirmed to have at least len 2
    new_seps = []
    average = all_height[len(all_height) // 2]
    return average


def segment_domains(domains_img: PngImageFile, sep_paths=None, rel_sep_displace=None):
    template_dir = os.path.join(Paths.assets_dir, "hsr", "templates", "navigation", "update_template")

    if sep_paths is None:
        sep_paths = [os.path.join(template_dir, f) for f in [
            r"domain_sep.png"
        ]]
    if rel_sep_displace is None:
        rel_sep_displace = [
            3,
        ]
    # preprocess
    domains_arr = np.array(domains_img)

    all_seps = []  # list[ (x, y) ]
    domains = []
    for idx, teleport_path in enumerate(sep_paths):
        cur_locs = locate_template_no_overlap(domains_img, Image.open(teleport_path), 0.9)

        for loc in cur_locs:
            all_seps.append(loc[1] + rel_sep_displace[idx])

    all_seps.append(0)
    all_seps.append(domains_arr.shape[0])
    all_seps = [max(0, min(domains_arr.shape[0], x)) for x in all_seps]
    all_seps = list(set(all_seps))
    all_seps.sort()

    average = average_height(all_seps)

    logger.debug(f"{all_seps=}, {domains_arr.shape[0]=}")
    for idx in range(len(all_seps) - 1):
        top_y = all_seps[idx] + 1
        bot_y = all_seps[idx + 1]
        if bot_y - top_y < average / 2:
            logger.debug(f"y=[{top_y}, {bot_y}] filtered")
            continue
        img = Image.fromarray(domains_arr[top_y:bot_y])
        domains.append(img)

    return domains

