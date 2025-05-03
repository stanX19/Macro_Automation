import os
import pathlib
import shutil

from PIL import Image
import utils
import time
from logger import logger
try:
    from .segment_domains import segment_domains
except ImportError:
    from segment_domains import segment_domains


def domain_png_to_dir(target_dir: str, dst_dir: str, extension="domain_screenshot.png"):
    """

    :param target_dir: directory where screenshots are stored
    :param dst_dir: parent directory for domain types, structure:
        - dst_dir/
            - calyx_crimson/
                - img.png
                - img_1.png
                ...
    :param extension: file extension of screenshot for searching
    :return: None
    """
    long_screenshots = utils.find_files(target_dir, "*." + extension)
    logger.debug(f"{long_screenshots=}")

    for png_path in long_screenshots:
        png_path_no_ext = png_path.replace(f".{extension}", "")
        dir_name = os.path.basename(png_path_no_ext)
        dir_path = os.path.join(dst_dir, dir_name)

        domain_png = Image.open(png_path)
        all_segmented_png = segment_domains(domain_png)
        logger.debug(f"Segment domain completed: {dir_name}")

        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path, exist_ok=True)
        name = os.path.join(dir_path, dir_name)

        for idx, png in enumerate(all_segmented_png):
            if idx:
                img_path = f"{name}_{idx}.png"
            else:
                img_path = f"{name}.png"
            png.save(img_path)
            cur_time = time.time() + idx
            os.utime(img_path, (cur_time, cur_time))
        logger.debug(f"saving completed: {dir_name}")
