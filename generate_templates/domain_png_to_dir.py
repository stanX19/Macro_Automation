import os
from PIL import Image
from segment_domains import segment_domains
import utils
import time


def domain_png_to_dir(target_dir: str, extension="domain_screenshot.png"):
    long_screenshots = utils.find_files(target_dir, "*." + extension)

    for png_path in long_screenshots:
        dir_path = "".join(png_path.rsplit("." + extension, 1))
        dir_name = os.path.basename(dir_path)

        domain_png = Image.open(png_path)
        all_segmented_png = segment_domains(domain_png)

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
