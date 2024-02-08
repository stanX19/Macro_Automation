import os
import screenshot_long
import segment_domains
import utils
from PIL import Image


def main():
    screenshot = Image.open(r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\generate_templates\all_relics.png")  # screenshot_long.screenshot_long(screenshot_long.DOMAINS_ROI)
    # screenshot.save(utils.unique_name("long_screenshot", "png"))

    domains_list = segment_domains.segment_domains(screenshot)
    dir_name = utils.unique_name(r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\generate_templates\domains", "")
    os.mkdir(dir_name)
    for domain_img in domains_list:
        domain_img.save(utils.unique_name(f"{dir_name}/img", "png"))


if __name__ == '__main__':
    main()
