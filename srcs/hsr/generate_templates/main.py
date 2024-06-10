import os
from PIL import Image
import utils
import Paths
from logger import logger
try:
    from . import screenshot_long
    from . import segment_domains
    from . import domain_png_to_dir
    from .traverse_categories import traverse_categories_and_screenshot
except ImportError:
    import screenshot_long
    import segment_domains
    import domain_png_to_dir
    from traverse_categories import traverse_categories_and_screenshot


def update_domain_templates(dest_dir: str, navigator, take_screenshot=True, convert_screenshot=True):
    extension = r"domain_screenshot.png"
    image_dir = os.path.join(Paths.assets_dir, "hsr", "images")

    logger.info(f"started; {take_screenshot=}; {convert_screenshot=}")
    if take_screenshot:
        traverse_categories_and_screenshot(image_dir, extension, navigator)
    if convert_screenshot:
        domain_png_to_dir.domain_png_to_dir(image_dir, dest_dir, extension)
    logger.info("completed")


def main():
    from honkai_star_rial_macro import Navigation
    cwd = os.path.dirname(__file__)
    update_domain_templates(cwd, Navigation())


if __name__ == '__main__':
    main()
