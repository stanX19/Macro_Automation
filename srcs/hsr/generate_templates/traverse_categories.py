import os
import time

try:
    from .screenshot_long import screenshot_long, DOMAINS_ROI
except ImportError:
    from screenshot_long import screenshot_long, DOMAINS_ROI


# extension no dot
def traverse_categories_and_screenshot(dst_dir: str, extension: str, navigator):
    for name in navigator.category_templates:
        navigator.navigate_to_category(name)
        time.sleep(3)

        ROI_DICT = {
            # "calyx_gold":(693, 371, 1655, 926),
            "weekly_boss_domain": (692, 450, 1656, 884),
            "ornament_domain": (692, 450, 1656, 884)
        }
        roi = ROI_DICT.get(name, DOMAINS_ROI)

        screenshot = screenshot_long(roi, scroll_magnitude=5, scroll_loc_rel=(100, 300))
        save_loc = f"{os.path.join(dst_dir, name)}.{extension}"
        screenshot.save(save_loc)
