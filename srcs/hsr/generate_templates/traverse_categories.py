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

        if name == "calyx_gold":
            roi = (693, 371, 1655, 926)
        elif name == "weekly_boss_domain":
            roi = (692, 451, 1658, 926)
        else:
            roi = DOMAINS_ROI

        screenshot = screenshot_long(roi, scroll_magnitude=5, scroll_loc_rel=(100, 300))
        save_loc = f"{os.path.join(dst_dir, name)}.{extension}"
        screenshot.save(save_loc)
