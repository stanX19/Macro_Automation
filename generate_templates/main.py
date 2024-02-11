import os
import screenshot_long
import segment_domains
import utils
import domain_png_to_dir
from PIL import Image
from traverse_categories import traverse_categories_and_screenshot


def main():
    target_dir = r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\generate_templates\images"
    extension = r"domain_screenshot.png"
    traverse_categories_and_screenshot(target_dir, extension)
    domain_png_to_dir.domain_png_to_dir(target_dir, extension)


if __name__ == '__main__':
    main()
