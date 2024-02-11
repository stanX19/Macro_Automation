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
            Paths.assets_path_dict["hsr"]["templates"]["navigation"]["teleport"],
            Paths.assets_path_dict["hsr"]["templates"]["navigation"]["enter_domain"]
        ]
    if rel_block_displace is None:
        rel_block_displace = [
            (-10000, -108, 10000, 82),
            (-10000, -106, 10000, 84)
        ]
    # preprocess
    domains_arr = np.array(domains_img)

    all_seps = []  # list[ (x, y) ]
    domains = []
    for idx, teleport_path in enumerate(teleport_paths):
        cur_locs = locate_teleport(domains_img, Image.open(teleport_path), 0.9)
        pt = rel_block_displace[idx]

        for loc in cur_locs:
            all_seps.append(min(domains_arr.shape[0] - 1, loc[1] + pt[3]))

    all_seps.sort()
    all_seps.insert(0, max(0, all_seps[0] - 200))
    all_seps[-1] = min(all_seps[-1], domains_arr.shape[0])
    for idx in range(len(all_seps) - 1):
        top_y = all_seps[idx] + 1
        bot_y = all_seps[idx + 1]
        img = Image.fromarray(domains_arr[top_y:bot_y])
        domains.append(img)

    return domains

