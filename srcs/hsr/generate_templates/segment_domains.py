import logging
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

def img_preprocess(img: np.ndarray):
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img

def locate_template_no_overlap(base_img: PngImageFile, template: PngImageFile, threshold: float) -> list[tuple[int, int]]:
    base_img_gray = img_preprocess(cv2.cvtColor(np.array(base_img), cv2.COLOR_BGR2GRAY))
    template_img_gray = img_preprocess(cv2.cvtColor(np.array(template), cv2.COLOR_BGR2GRAY))

    result = cv2.matchTemplate(base_img_gray, template_img_gray, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    filtered_locations: list[tuple[int, int]] = []
    for loc in zip(*locations[::-1]):
        if not in_list(loc, filtered_locations, template.size):
            filtered_locations.append(loc)

    return filtered_locations


def average_height(seps: list[int], reject=10):
    """

    :param seps: sorted list of y-value of seps
    :param reject: height is ignored if lower than reject
    :return: average height
    """
    all_height = [seps[i + 1] - seps[i] for i in range(len(seps) - 1)]
    if not all_height:
        return 0
    # now seps is confirmed to have at least len 2
    all_height = [i for i in all_height if i > reject]
    average = sorted(all_height)[len(all_height) // 2]
    return average


def segment_domains(domains_img: PngImageFile) -> list[Image]:
    template_dir = os.path.join(Paths.assets_dir, "hsr", "templates", "navigation", "update_template")

    # y displacement from top of sep_image
    sep_paths: list[tuple[str, int]] = [(os.path.join(template_dir, f), d )for f, d in {
        r"domain_sep.png": 3,
        r"domain_sep_1.png": 2,
        r"domain_sep_2.png": 2,
        r"domain_sep_3.png": 3,
    }.items()]
    # preprocess
    domains_arr = np.array(domains_img)

    all_seps: list[int] = []  # y-coordinates
    domains: list[Image] = []
    for idx, (teleport_path, displace) in enumerate(sep_paths):
        cur_locs = locate_template_no_overlap(domains_img, Image.open(teleport_path), 0.9)
        # print(idx, [i[1] + displace for i in cur_locs])
        for loc in cur_locs:
            all_seps.append(loc[1] + displace)

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

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    print(len(segment_domains(Image.open(r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr"
                                         r"\images\calyx_crimson.domain_screenshot.png"))))