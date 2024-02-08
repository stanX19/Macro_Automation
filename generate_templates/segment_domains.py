import cv2
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
import Paths


def locate_teleport(domains_img: PngImageFile, teleport_img: PngImageFile, threshold: float)->list[tuple[int, int]]:
    domains_img_gray = cv2.cvtColor(np.array(domains_img), cv2.COLOR_BGR2GRAY)
    teleport_img_gray = cv2.cvtColor(np.array(teleport_img), cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(domains_img_gray, teleport_img_gray, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    return [(int(x), int(y)) for x, y in zip(*locations[::-1])]


def segment_domains(domains_img: PngImageFile, teleport_paths=None, rel_block_displace=None):
    if teleport_paths is None:
        teleport_paths = [
            Paths.assets_path_dict["hsr"]["templates"]["navigation"]["teleport"]
        ]
    if rel_block_displace is None:
        rel_block_displace = [
            (-10000, -110, 10000, 80)
        ]
    # preprocess
    domains_arr = np.array(domains_img)

    locations = []  # list[ (x, y) ]
    domains = []
    for idx, teleport_path in enumerate(teleport_paths):
        cur_locs = locate_teleport(domains_img, Image.open(teleport_path), 0.9)
        cur_locs.sort(key=lambda pair: pair[1])  # sort by y cord

        pt = rel_block_displace[idx]
        for loc in cur_locs:
            top_x = max(0, loc[0] + pt[0])
            top_y = max(0, loc[1] + pt[1])
            bot_x = min(domains_arr.shape[1] - 1, loc[0] + pt[2])
            bot_y = min(domains_arr.shape[0] - 1, loc[1] + pt[3])
            img = Image.fromarray(domains_arr[top_y:bot_y, top_x:bot_x])
            domains.append(img)

    return domains

