from datetime import datetime
import os
import utils
import keyboard
import time
import traceback
import logging
from typing import Union, Optional
import Paths
import UI
import hsr_helper
import macro_settings
import mouse
from logger import logger
from matcher import TemplateData, Matcher
from status_matcher import StatusMatcher
from template import Template
from exceptions import GameConnectionError, BattleLostError, DomainNotSpecifiedError, ScreenCaptureFailedError
from generate_templates import update_domain_templates


class LogIn:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["login"]
        self.assets = assets
        self.menu_bar = MenuBar()
        self.launcher_exe = macro_settings.hsr["launcher_exe"]
        self.launcher_play_old = Template(assets["launcher_play_old"], (1277, 768, 1606, 875))
        self.launcher_play = Template(assets["launcher_play"], threshold=0.9)
        self.launcher_update = Template(assets["launcher_update"], threshold=0.9)
        self.launcher_checkbox = Template(assets["launcher_checkbox"], threshold=0.9)
        self.launcher_accept = Template(assets["launcher_accept"], threshold=0.9)
        self.update_game = Template(assets["update_game"], threshold=0.9)
        self.hsr_logo = Template(assets["hsr_logo"], threshold=0.7, binary=True, variable_size=True)
        self.hsr_icon = Template(assets["hsr_icon"], threshold=0.9)
        self.choose_server = Template(assets["choose_server"], (708, 782, 1225, 967))
        self.start_game = Template(assets["start_game"], (861, 805, 1076, 872))
        self.click_to_start = Template(assets["click_to_start"])
        self.checkbox = Template(assets["checkbox"], (553, 466, 607, 517), 0.975)
        self.accept = Template(assets["accept"], (963, 737, 1359, 840), 0.7)
        self.confirm = Template(assets["confirm"], (740, 603, 1194, 743), 0.9)
        self.my_popup_close = Template(assets["my_popup_close"], (1411, 105, 1459, 154), 0.9)

    def launch_game(self):
        os.startfile(self.launcher_exe)
        logger.info("ok")

    def log_in_to_game(self):
        status_matcher = StatusMatcher(
            self.checkbox, self.accept, self.confirm,
            self.launcher_play, self.update_game, self.launcher_checkbox,
            self.launcher_accept, self.launcher_update,
            self.hsr_icon, self.hsr_logo,
            self.start_game, self.click_to_start,
            self.my_popup_close,
            *self.menu_bar.templates
        )

        start_time = time.time()
        logger.info("started")
        TIMEOUT = 1800
        is_update = False
        while start_time + TIMEOUT >= time.time():
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                if exist_time < 1:
                    continue
                logger.debug(f"{template.file_name} matched {loc} {exist_time}")
                if template in self.menu_bar.templates:
                    logger.info("completed")
                    return
                if template is self.launcher_play and status_matcher[self.hsr_logo].time < 2.0:
                    continue
                if template is self.hsr_logo:
                    continue
                if template is self.update_game and not is_update:
                    is_update = True
                    TIMEOUT += 3600
                mouse.click_and_move_away(loc)

        raise TimeoutError("failed to log in")

    def start_and_log_in(self):
        self.launch_game()
        self.log_in_to_game()


class MenuBar:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]

        self.templates = [
            # Template(assets["menu_bar_0"], (1275, 0, 1961, 114), 0.8),
            # Template(assets["menu_bar_2"], (1386, 5, 1904, 91), 0.8),
            Template(assets["menu_bar_3_0"], (1557, 4, 1891, 91), 0.7),
            Template(assets["menu_bar_3_1"], (1557, 4, 1891, 91), 0.7),
            # Template(assets["menu_bar_3_2"], (1557, 4, 1891, 91), 0.7),
        ]
        self.nav_btn_displacement = {self.templates[i]: cord for i, cord in enumerate([
            # (285, 33),
            # (196, 29),
            (30, 30),
            (30, 30),
            # (30, 30),
        ])}
        self.monthly_pass_displacement = {template: (x - 178, y) for template, (x, y) in
                                          self.nav_btn_displacement.items()}

    def exists(self):
        return Matcher(*self.templates).exists()

    def click_nav(self, data: TemplateData):
        mouse.alt_and_click(data.loc, self.nav_btn_displacement[data.template])
        logger.info(f"clicked {data}")

    def click_monthly_pass(self, data: TemplateData):
        mouse.alt_and_click(data.loc, self.monthly_pass_displacement[data.template])
        logger.info(f"clicked {data}")

    def wait_and_click_nav(self):
        logger.info("started")
        exists = True
        while exists:
            logger.debug("Waiting for any menu bar to match")
            matched = Matcher(*self.templates).wait_and_match()
            logger.debug(f"found menu bar: location={matched.loc}")
            displacement = self.nav_btn_displacement[matched.template]
            logger.debug(f"Alt clicking menu bar, location={matched.loc}; displacement={displacement}")
            mouse.alt_and_click(matched.loc, displacement)
            mouse.move_away_from(matched.loc)
            time.sleep(1.5)
            exists = Matcher(*self.templates).exists()
        logger.info("completed")


class Navigation:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]
        self.assets = assets
        self.menu_bar = MenuBar()
        self.survival_guide = Template(assets["survival_guide"], (284, 161, 1039, 268), 0.95)
        self.teleport = Template(assets["teleport"], threshold=0.85)
        self.enter_domain = Template(assets["enter_domain"], threshold=0.85)
        self.track_domain = Template(assets["track_domain"], threshold=0.85)

        self.CATEGORY_ROI = (244, 271, 686, 918)
        self.DOMAIN_ROI = (678, 280, 1680, 950)
        self.category_templates: dict[str, Template] = {}
        self.domains: dict[str, dict[str, Template]] = {}
        self.domain_dir = macro_settings.hsr["domain_dir"]

        for key, path in assets["domain_types"].items():
            self.category_templates[key] = Template(path, self.CATEGORY_ROI, 0.95, crop=(20, 60, 200, 90),
                                                    binary=True)

        for category, domains in assets[self.domain_dir].items():
            if not isinstance(domains, dict):
                continue

            self.domains[category] = {}

            for key, path in domains.items():
                self.domains[category][key] = Template(path, self.DOMAIN_ROI, 0.975)

        assets = Paths.assets_path_dict["hsr"]["templates"]["domain_farm"]
        self.start_challenge = Template(assets["start_challenge"], (1343, 947, 1893, 1022), 0.9)

    def update_domain_templates(self, skip_screenshot):
        """
        Overwrites existing domain templates, program needs to be rerun when this method is called
        :return: None
        """
        dst_dir = os.path.join(Paths.assets_dir, r"hsr\templates\navigation\domains")
        update_domain_templates(dst_dir, self, take_screenshot=not skip_screenshot, convert_screenshot=True)

    def ui_choose_domain(self) -> tuple[Optional[str], Optional[str]]:
        """

        :return: category, domain
        """
        logger.info("selecting domain and category")
        category_selector = UI.ImageSelector(
            hsr_helper.to_path_dict(self.category_templates),
            "Select domain category",
            max_height=600
        )

        category = "calyx_crimson"
        domain = None
        while category is not None:
            if domain is None:
                category = category_selector.select_image_key()
            else:
                break
            if category not in self.domains:
                continue
            domain_selector = UI.ImageSelector(
                hsr_helper.to_path_dict(self.domains[category]),
                "Select domain",
                max_height=800
            )
            domain = domain_selector.select_image_key()

        logger.info(f"category={category}, domain={domain}")
        return category, domain

    def navigate_to_category(self, category_key: str):
        category_templates = list(self.category_templates.values())
        target_cat = self.category_templates[category_key]
        target_cat_idx = category_templates.index(target_cat)

        status_matcher = StatusMatcher(*self.menu_bar.templates, self.survival_guide,
                                       *self.category_templates.values())

        start_time = time.time()
        THRESHOLD_1 = 1  # seconds
        THRESHOLD_2 = 0

        logger.info("started")
        while start_time + 1800 > time.time():

            cat_pos_relative = 0
            cat_loc = ()

            clicked_menu = False
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                # logger.debug(f"{template.file_name} matched [{exist_time}, {loc}]")
                if template in self.menu_bar.templates and exist_time > THRESHOLD_1 and not clicked_menu:
                    self.menu_bar.click_nav(TemplateData(template, loc))
                    clicked_menu = True
                elif template is self.survival_guide and exist_time > THRESHOLD_2:
                    mouse.click_center(loc)
                elif template is target_cat and exist_time > THRESHOLD_2:
                    logger.debug("target category found")
                    for _ in range(3):
                        mouse.click_and_move_away(loc)
                        time.sleep(0.5)
                    return
                elif template in category_templates:
                    if exist_time <= THRESHOLD_2:
                        continue
                    cat_pos_relative = target_cat_idx - category_templates.index(template)
                    cat_loc = loc
                    continue
                else:
                    continue

                status_matcher.reset_template(template)

            # print(cat_pos_relative, dom_pos_relative, cat_positive, dom_positive)
            # print()
            if cat_pos_relative == 0:
                continue
            logger.debug("Scrolling category")
            mouse.move_to_center(cat_loc)
            if cat_pos_relative > 0:
                mouse.scroll_down(5)
            else:
                mouse.scroll_up(5)

    def navigate_to_domain(self, category_key: str, domain_key: str):
        if not category_key or not domain_key:
            raise DomainNotSpecifiedError()
        category_templates = list(self.category_templates.values())
        target_cat = self.category_templates[category_key]
        target_cat_idx = category_templates.index(target_cat)
        domain_templates = list(self.domains[category_key].values())
        target_domain = self.domains[category_key][domain_key]
        target_dom_idx = domain_templates.index(target_domain)

        status_matcher = StatusMatcher(*self.menu_bar.templates, self.survival_guide,
                                       *self.category_templates.values(),
                                       *self.domains[category_key].values(),
                                       self.start_challenge)

        start_time = time.time()
        THRESHOLD_1 = 1  # seconds
        THRESHOLD_2 = 0

        logger.info("started")
        while start_time + 1800 > time.time():

            cat_relative_positive_idx = 0
            cat_relative_negative_idx = 0
            dom_relative_positive_idx = 0
            dom_relative_negative_idx = 0
            cat_positive_idx_loc = ()
            cat_negative_idx_loc = ()
            dom_positive_idx_loc = ()
            dom_negative_idx_loc = ()

            cat_found = False
            dom_found = False

            clicked_menu = False
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                if exist_time:
                    logger.debug(f"{template.file_name} matched [{exist_time}, {loc}]")
                if template in self.menu_bar.templates and exist_time > THRESHOLD_1 and not clicked_menu:
                    self.menu_bar.click_nav(TemplateData(template, loc))
                    clicked_menu = True
                elif template is self.survival_guide and exist_time > THRESHOLD_2:
                    mouse.click_center(loc)
                elif template is self.start_challenge and exist_time > THRESHOLD_1:
                    logger.info("completed")
                    return
                elif template is target_cat and exist_time > THRESHOLD_2:
                    logger.debug("target category found")
                    mouse.click_center(loc)
                    cat_found = True
                    continue
                elif template is target_domain and exist_time > THRESHOLD_2:
                    dom_found = True
                    logger.debug("target domain found")
                    self.teleport.set_search_area(loc)
                    self.enter_domain.set_search_area(loc)
                    self.track_domain.set_search_area(loc)
                    logger.debug("clicking teleport")
                    time.sleep(0.5)
                    matched = Matcher(self.teleport, self.enter_domain, self.track_domain).get_data_if_match()
                    if matched is not None:
                        if matched.template is self.track_domain:
                            raise RuntimeError("Domain not unlocked")
                        mouse.click_center(matched.loc)

                elif template in category_templates:
                    if exist_time <= THRESHOLD_2:
                        continue
                    rel_idx = target_cat_idx - category_templates.index(template)
                    if rel_idx > 0 and (cat_relative_positive_idx == 0 or rel_idx < cat_relative_positive_idx):
                        cat_relative_positive_idx = rel_idx
                        cat_positive_idx_loc = loc
                    elif cat_relative_negative_idx == 0 or rel_idx > cat_relative_negative_idx:
                        cat_relative_negative_idx = rel_idx
                        cat_negative_idx_loc = loc
                    continue
                elif template in domain_templates:
                    if exist_time <= THRESHOLD_2:
                        continue
                    rel_idx = target_dom_idx - domain_templates.index(template)
                    loc = (loc[0], loc[1], loc[0] + (loc[3] - loc[1]) * 2, loc[3])
                    if rel_idx > 0 and (dom_relative_positive_idx == 0 or rel_idx < dom_relative_positive_idx):
                        dom_relative_positive_idx = rel_idx
                        dom_positive_idx_loc = loc
                    elif dom_relative_negative_idx == 0 or rel_idx > dom_relative_negative_idx:
                        dom_relative_negative_idx = rel_idx
                        dom_negative_idx_loc = loc
                    continue
                else:
                    continue

                status_matcher.reset_template(template)

            # print(cat_pos_relative, dom_pos_relative, cat_positive, dom_positive)
            # print()

            SCROLL_MAGNITUDE = 5
            scroll_vector = 0
            scroll_loc = (0, 0, 0, 0)
            if bool(dom_relative_negative_idx) != bool(dom_relative_positive_idx) and not dom_found:
                if dom_relative_positive_idx:
                    scroll_loc = dom_positive_idx_loc
                    scroll_vector = dom_relative_positive_idx * SCROLL_MAGNITUDE
                else:
                    scroll_loc = dom_negative_idx_loc
                    scroll_vector = dom_relative_negative_idx * SCROLL_MAGNITUDE

            elif bool(cat_relative_negative_idx) != bool(cat_relative_positive_idx) and not cat_found and not dom_found:
                if cat_relative_positive_idx:
                    scroll_loc = cat_positive_idx_loc
                    scroll_vector = cat_relative_positive_idx * SCROLL_MAGNITUDE
                else:
                    scroll_loc = cat_negative_idx_loc
                    scroll_vector = cat_relative_negative_idx * SCROLL_MAGNITUDE

            elif cat_found and not dom_found and status_matcher[target_cat].time > 5:
                scroll_loc = self.DOMAIN_ROI
                scroll_vector = SCROLL_MAGNITUDE

            if scroll_vector:
                mouse.move_to_center(scroll_loc)
                mouse.scroll_down_general(scroll_vector)
                mouse.move_away_from(scroll_loc)


class Dailies:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["dailies"]
        self.assets = assets
        self.navigator = Navigation()

        self.daily_logo = Template(assets["daily_logo"], (9, 9, 257, 123), 0.9, binary=True)
        self.daily_tab = Template(assets["daily_tab_button"], (284, 161, 1039, 268), 0.9)
        self.daily_claim = Template(assets["daily_claim"], (298, 783, 549, 873), 0.9)

        self.daily_primo1 = Template(assets["daily_primo"], (596, 272, 681, 351), 0.9)
        self.daily_primo2 = Template(assets["daily_primo"], (839, 274, 922, 352), 0.9)
        self.daily_primo3 = Template(assets["daily_primo"], (1078, 274, 1169, 351), 0.9)
        self.daily_primo4 = Template(assets["daily_primo"], (1327, 272, 1409, 353), 0.9)
        self.daily_primo5 = Template(assets["daily_primo"], (1571, 273, 1651, 353), 0.9)

        self.claimed_primo_slot = -1
        self.claimed_assignments = -1

        self.assignment_logo = Template(assets["assignment_logo"], (0, 0, 193, 95), 0.9, binary=True)
        self.goto_assignment = Template(assets["goto_assignment"], (259, 397, 1666, 893), 0.95)
        self.goto_assignment_displace = (139, 422)
        self.assignment_claim = Template(assets["assignment_claim"], (1261, 863, 1670, 944), 0.9)
        self.assignment_claim_all = Template(assets["assignment_claim_all"], (328, 872, 621, 950), 0.9)
        self.assignment_re = Template(assets["assignment_re"], (1006, 905, 1403, 987), 0.7)
        self.assignment_red_dot = Template(assets["red_dot"], (307, 175, 1208, 298), 0.9)

        self.monthly_pass_claim_all = Template(assets["monthly_pass_claim_all"], (1487, 878, 1842, 959), 0.9)
        self.monthly_pass_red_dot = Template(assets["red_dot"], (806, 16, 1099, 67), 0.7)
        self.monthly_pass_claim_all_2 = Template(assets["monthly_pass_claim_all_2"], (1315, 875, 1543, 948), 0.9)

    def claim_dailies(self):
        all_daily_primo = [self.daily_primo5, self.daily_primo4, self.daily_primo3,
                           self.daily_primo2, self.daily_primo1]
        status_matcher = StatusMatcher(self.daily_claim, *all_daily_primo, self.goto_assignment,
                                       *self.navigator.menu_bar.templates,
                                       self.daily_tab)

        start_time = time.time()
        last_seen = start_time + 0
        THRESHOLD = 1  # seconds
        self.claimed_primo_slot = 0

        logger.info("started")
        while start_time + 300 > time.time():
            status_matcher.update()

            if last_seen + 120 < time.time():
                logger.debug("last_seen > 15s, break")
                break

            if status_matcher[self.daily_tab].time > THRESHOLD:
                mouse.click_center(status_matcher[self.daily_tab].loc)

            elif status_matcher[self.goto_assignment].time > THRESHOLD and self.claimed_assignments < 0:
                logger.debug("found assignment, entering")
                mouse.click_relative(status_matcher[self.goto_assignment].loc, self.goto_assignment_displace)
                self.do_assignments()
                logger.debug("exiting assignment (esc)")
                Matcher(self.daily_logo).while_not_exist_do(
                    hsr_helper.press_and_release, ["esc"], interval=1
                )
                logger.debug("exited assignment")
            elif status_matcher[self.daily_claim].time > THRESHOLD:
                mouse.click_and_move_away(status_matcher[self.daily_claim].loc)
                logger.debug("Claim daily task +1")
            else:
                for menu_bar in self.navigator.menu_bar.templates:
                    if status_matcher[menu_bar].time > THRESHOLD:
                        self.navigator.menu_bar.click_nav(status_matcher[menu_bar])
                        logger.debug("click menu bar")
                        break
                else:
                    for idx, claim_t in enumerate(all_daily_primo):
                        if status_matcher[claim_t].time > THRESHOLD:
                            self.claimed_primo_slot = len(all_daily_primo) - idx
                            logger.debug(f"Claimed primo at {self.claimed_primo_slot}th slot")
                            mouse.click_and_move_away(status_matcher[claim_t].loc)
                            for i in range(2):  # cancel/exit claim animation
                                time.sleep(0.5)
                                mouse.click()
                            break
                    else:
                        continue
            if self.claimed_primo_slot == len(all_daily_primo):
                break
            last_seen = time.time()
            status_matcher.reset_all_template()
        logger.debug("exiting dailies (esc)")
        Matcher(*self.navigator.menu_bar.templates).while_not_exist_do(
            hsr_helper.press_and_release, ["esc"]
        )
        logger.debug("exited dailies")
        logger.info(f"completed, claimed {self.claimed_primo_slot} slots of primo")
        self.claim_monthly_pass()
        logger.debug("done")

    def do_assignments(self):
        status_matcher = StatusMatcher(self.assignment_claim, self.assignment_claim_all,
                                       self.assignment_re, self.assignment_red_dot)

        start_time = time.time()
        last_seen = start_time + 5
        THRESHOLD = 0.5  # seconds
        MAX_ASSIGNMENT = 4
        self.claimed_assignments = 0

        logger.info(f"started")
        redeploying = 0  # number of claimed assignments waiting to be redeployed
        while start_time + 30 > time.time():
            status_matcher.update()

            if last_seen + 5 < time.time():
                logger.debug("last_seen > 10s, break")
                break
            if self.claimed_assignments >= MAX_ASSIGNMENT:
                logger.debug("claimed and redeployed MAX_ASSIGNMENTS, break")
                break
            if status_matcher[self.assignment_claim_all].time > THRESHOLD:
                mouse.click_center(status_matcher[self.assignment_claim_all].loc)
                logger.debug("clicked claim all assignment")

                redeploying = MAX_ASSIGNMENT

            elif status_matcher[self.assignment_claim].time > THRESHOLD:
                mouse.click_center(status_matcher[self.assignment_claim].loc)
                logger.debug("clicked claim assignment")

                redeploying = 1

            elif status_matcher[self.assignment_re].time > THRESHOLD:
                mouse.click_center(status_matcher[self.assignment_re].loc)
                logger.debug("clicked redeploy assignment")
                if redeploying:
                    self.claimed_assignments += redeploying
                    logger.debug(f"claimed and redeployed assignment +{redeploying}")
                    redeploying = 0

            elif status_matcher[self.assignment_red_dot].time > THRESHOLD:  # and not redeploying:
                mouse.click_center(status_matcher[self.assignment_red_dot].loc)
                logger.debug("clicked on red dot")
                status_matcher.reset_template(self.assignment_red_dot)
            else:
                continue
            last_seen = time.time()
        logger.info(f"claimed and redeployed {self.claimed_assignments} assignments")
        logger.info("ended")

    def claim_monthly_pass(self):
        status_matcher = StatusMatcher(*self.navigator.menu_bar.templates,
                                       self.monthly_pass_claim_all,
                                       self.monthly_pass_claim_all_2,
                                       self.monthly_pass_red_dot)
        threshold = 0.5

        logger.debug("started")
        start_time = time.time()
        last_seen = start_time + 5
        while start_time + 45 > time.time():
            if last_seen + 5 < time.time():
                logger.debug("last seen > 5s, break")
                break
            for data in status_matcher.get_all_template_data():
                if not data.time > threshold:
                    continue
                if data.template in self.navigator.menu_bar.templates:
                    self.navigator.menu_bar.click_monthly_pass(data)
                    break
                logger.debug(f"Template matched: {data}; click and move away")
                mouse.click_and_move_away(data.loc)
                last_seen = time.time()

        logger.debug("exiting monthly pass interface")
        Matcher(*self.navigator.menu_bar.templates).while_not_exist_do(
            hsr_helper.press_and_release, ["esc"]
        )
        logger.debug("completed")


class DomainFarm:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["domain_farm"]
        self.assets = assets
        self.navigator = Navigation()

        self.auto_battle_off = Template(assets["auto_battle_off"], (1570, 15, 1930, 82), 0.775)
        self.auto_battle_on = Template(assets["auto_battle_on"], (1570, 15, 1930, 82), 0.775)
        self.challenge_again = Template(assets["challenge_again"], (1007, 912, 1407, 983), 0.9)
        self.exit_challenge = Template(assets["exit_challenge"], (517, 914, 915, 982), 0.9)
        # self.not_enough_stamina = Template(assets["not_enough_stamina"], (860, 324, 1066, 432), 0.9)
        self.battle_lost = Template(assets["battle_lost"], (701, 129, 1205, 417), 0.9)
        self.cancel = Template(assets["cancel"], (540, 620, 960, 770), 0.9)
        self.start_challenge = Template(assets["start_challenge"], (1343, 947, 1893, 1022), 0.9)
        self.start_challenge_2 = Template(assets["start_challenge_2"], (1501, 948, 1853, 1021), 0.9)
        self.confirm = Template(assets["confirm"], (955, 607, 1384, 739), 0.9)
        self.add_to_team = Template(assets["add_to_team"], (1526, 962, 1850, 1021), 0.95)

        # calyx specific
        self.reduce_count = Template(assets["calyx"]["reduce_count"], (1206, 881, 1279, 917), 0.9)
        self.add_count = Template(assets["calyx"]["add_count"], (1742, 882, 1888, 917), 0.8)

        self.add_count_loc = (9, 17)

        # support
        self.get_support_button = Template(assets["support"]["get_support"], (1675, 704, 1833, 769), 0.90)
        self.support_end_of_list = Template(assets["support"]["end_of_list"], (520, 810, 560, 940), 0.90)
        self.support_list_title = Template(assets["support"]["list_title"], (172, 42, 423, 136), 0.85)
        self.support_priority_list: list[Template] = [
                                                         Template(path, (0, 100, 600, 1000), 0.85) for path in
                                                         assets["support"]["priority"].values()
                                                     ][::-1]  # new first, old last
        self._domain = None
        self._category = None
        self._get_support = True
        self.farm_count = 0

    def select_prioritised_support(self, timeout=20):
        if not self.support_priority_list:
            return None
        logger.info("started")
        logger.debug("waiting for support_list_title to match")
        title_loc = Matcher(self.support_list_title).wait_and_get_location(timeout=30)
        logger.debug("found support_list_title")

        support_matcher = Matcher(*self.support_priority_list)
        start_time = time.time()

        logger.debug("click second tab in list")
        BLOCK_HEIGHT = 150
        TITLE_TO_BLOCK = 200
        mouse.click_relative(title_loc, (90, TITLE_TO_BLOCK + BLOCK_HEIGHT))

        # since we are going to search for the most prioritized support anyway so any other matches is not important
        if not self.support_priority_list[0] in support_matcher.get_matching_template_list():
            logger.debug("first tab is not the most desired, click first tab")
            mouse.click_relative(title_loc, (90, TITLE_TO_BLOCK))

        chosen_index = float("inf")

        while start_time + timeout >= time.time():
            for data in support_matcher.get_matching_templates_data():
                logger.debug(f"{data.template.file_name} matched at {data.loc}")
                found_index = self.support_priority_list.index(data.template)
                if found_index < chosen_index:
                    chosen_index = found_index
                    mouse.click_and_move_away(data.loc)
                    logger.debug(f"clicked on: {data}")
                if chosen_index == 0:
                    logger.info("found most prioritized support")
                    logger.debug(f"waiting for {data.template.file_name} to unmatch (turn white)")
                    Matcher(data.template.as_threshold(data.threshold * 0.975)).while_exist_do(
                        mouse.click_and_move_away, (data.loc, )
                    )
                    break
            if chosen_index == 0:
                break
            mouse.move_relative(title_loc, (90, 150))
            logger.debug("scrolling down [5]")
            mouse.scroll_down(5)

        if chosen_index < len(self.support_priority_list):
            name = self.support_priority_list[chosen_index].file_name
            logger.info(f"completed, selected support: {name} ({chosen_index})")
        else:
            logger.info(f"completed, selected default support")

    def get_support(self):
        """
            start: team selection interface

            end: team selection interface
        """
        if not self._get_support:
            return

        logger.info("started")
        logger.debug("clicking get_support")
        Matcher(self.get_support_button).click_center_when_exist()
        # if self.support_priority_list:
        self.select_prioritised_support()
        logger.debug("clicking add_to_team")
        Matcher(self.add_to_team).click_center_when_exist()
        logger.info("completed")

    def select_auto_battle(self):
        logger.info("started")
        logger.debug("waiting for auto_battle to match")
        auto_battle = Matcher(self.auto_battle_off).wait_and_get_location()
        mouse.click_relative(auto_battle, (179, 24))
        logger.info("completed")

    def exit_challenge_reward(self):
        logger.debug("started")
        exit_btn = Matcher(self.exit_challenge)

        exit_btn.while_not_exist_do(
            hsr_helper.press_and_release, ["esc"]
        )
        exit_btn.click_center_when_exist()
        Matcher(*self.navigator.menu_bar.templates).while_not_exist_do(
            hsr_helper.press_and_release, ["esc"]
        )
        logger.debug("ended")

    def start_battle_and_repeat_safe(self, max_count=float('inf')):
        """
            start: in domain battle

            end: open world
        """
        try:
            self._start_battle_and_repeat(max_count)
        except (GameConnectionError, BattleLostError) as exc:
            logger.debug(f"Error: {exc}")

    def _start_battle_and_repeat(self, max_count):
        """
            start: in domain battle

            end: open world
        """
        logger.info("started")

        self.select_auto_battle()
        i = 1
        while i < max_count:
            # wait till battle is over
            logger.debug("Waiting for battle to end")
            matching = Matcher(self.challenge_again,
                               *self.navigator.menu_bar.templates, self.battle_lost).wait_and_match()

            if matching.template in self.navigator.menu_bar.templates:
                raise GameConnectionError("start_battle_and_repeat")
            if matching.template is self.battle_lost:
                mouse.click_center(matching.loc)
                raise BattleLostError()

            # repeat, matching must be self.challenge_again
            logger.debug("Waiting for challenge again to match")
            Matcher(self.challenge_again).click_center_when_exist()

            logger.debug("Waiting for auto_battle or not_enough_stamina to match")
            matching = Matcher(
                self.auto_battle_on, self.cancel, *self.navigator.menu_bar.templates
            ).wait_and_match()

            if matching.template in self.navigator.menu_bar.templates:
                raise GameConnectionError()
            if matching.template is self.cancel:
                logger.debug("not enough stamina / all chances used")
                self.exit_challenge_reward()
                break

            i += 1
        else:
            # wait till battle is over
            logger.debug("Waiting for exit challenge to match")
            matched = Matcher(self.exit_challenge, *self.navigator.menu_bar.templates).wait_and_match()
            # exit
            logger.debug("clicking exit challenge")
            if matched.template is self.exit_challenge:
                self.exit_challenge_reward()
        self.farm_count += i
        logger.info(f"completed, farmed {i} times")

    def activate_open_world_boss(self):
        logger.info("started")
        keyboard.press("up")  # holds down
        Matcher(*self.navigator.menu_bar.templates).while_exist_do(
            mouse.click, interval=1
        )
        keyboard.release("up")
        logger.info("completed")

    def domain_start_farm(self, max_count):
        """
            start: team selection interface

            end: open world
        """
        self.get_support()
        logger.info(f"started, max_count={max_count}")
        Matcher(self.start_challenge_2).click_center_when_exist()

        logger.debug("Waiting for auto_battle or menu_bar to match")
        domain_type = Matcher(
            self.auto_battle_off,
            self.confirm,
            *self.navigator.menu_bar.templates
        ).wait_and_match(60.00)  # 1 minutes
        if domain_type.template is self.confirm:
            logger.debug("Clicking confirm")
            Matcher(self.confirm).click_center_when_exist()
            Matcher(self.auto_battle_off).wait_and_match(60.00)
        if domain_type.template in self.navigator.menu_bar.templates:
            self.activate_open_world_boss()
        self._start_battle_and_repeat(max_count)
        logger.info("completed")

    def domain_farm_bulk(self, max_count):
        """
            start: domain start interface

            end: open world
        """
        logger.info(f"started, max_count={max_count}")
        logger.debug("clicking start_challenge when exist")
        Matcher(self.start_challenge).click_center_when_exist()
        logger.debug("Waiting for start_challenge or not_enough_stamina to match")
        matching = Matcher(self.start_challenge_2, self.cancel).wait_and_match()

        if matching.template is self.cancel:  # not enough stamina
            logger.debug("clicking cancel")
            Matcher(self.cancel).click_center_when_exist(interval=0.5)
            logger.debug("exiting (esc)")
            Matcher(*self.navigator.menu_bar.templates).while_not_exist_do(
                hsr_helper.press_and_release, ["esc"]
            )
            logger.debug("exited")
            return 0
        else:
            return self.domain_start_farm(max_count)

    def set_settings(self, get_support=False):
        self._get_support = get_support

    def is_calyx(self):
        logger.debug("Waiting for start_challenge to match")
        Matcher(self.start_challenge).wait_and_match()
        return Matcher(self.add_count, self.reduce_count).exists()

    def calyx_farm_all(self):
        """
            start: domain start interface

            end: open world
        """
        logger.info(f"started, category={self._category}, domain={self._domain}")
        logger.debug("Waiting for add_count to match")
        mouse.click_relative(Matcher(self.add_count).wait_and_get_location(), self.add_count_loc)
        Matcher(self.start_challenge).click_center_when_exist()

        status_matcher = Matcher(self.start_challenge_2, self.cancel)
        logger.debug("Waiting for start_challenge or cancel to match")
        status = status_matcher.wait_and_match()

        if status.template is self.start_challenge_2:  # if stamina >= 60
            # first bulk farm
            self.domain_start_farm(float('inf'))
            self.navigator.navigate_to_domain(self._category, self._domain)
            logger.debug("Waiting for add_count to match")
            mouse.click_relative(Matcher(self.add_count).wait_and_get_location(), (9, 17))
        else:
            logger.debug("exiting (click cancel)")
            Matcher(self.cancel).click_center_when_exist(interval=0.5)
            logger.debug("exited")

        button_matcher = Matcher(self.reduce_count, self.add_count, *self.navigator.menu_bar.templates)

        # increase count
        data = button_matcher.wait_and_match()
        if data.template is self.add_count:
            logger.debug(f"add button matched, clicking; {data}")
            mouse.click_relative(data.loc, self.add_count_loc)

        # reduce count
        for i in range(5):
            logger.debug("waiting for reduce_button to match")
            data = button_matcher.wait_and_match()
            if data.template in self.navigator.menu_bar.templates:
                raise GameConnectionError()
            mouse.click_center(data.loc)

            # test for stamina
            logger.debug("waiting for start_challenge to match")
            Matcher(self.start_challenge).click_center_when_exist()
            status = status_matcher.wait_and_match()
            if status.template is self.cancel:
                logger.debug("exiting not_enough_stamina (click cancel)")
                Matcher(self.cancel).click_center_when_exist()
                logger.debug("exited not_enough_stamina")
                continue
            else:
                break
        else:
            logger.debug("exiting farming_rewards (esc)")
            Matcher(*self.navigator.menu_bar.templates).while_not_exist_do(
                hsr_helper.press_and_release, ["esc"]
            )
            logger.debug("exited farming_rewards")
            return

        self.domain_start_farm(1)
        logger.info("ended")

    def general_domain_farm(self, category: str, domain: str):
        self._category = category
        self._domain = domain
        if self.is_calyx():
            self.calyx_farm_all()
        else:
            self.domain_farm_bulk(float('inf'))

    def retrying_domain_farm(self, category: str, domain: str):
        # if category is None or domain is None:
        #     category, domain = self.navigator.ui_choose_domain()

        MAX_RETRIES = 3
        for _ in range(MAX_RETRIES):
            try:
                self.general_domain_farm(category, domain)
                return
            except GameConnectionError as exc:
                logger.debug(f"Connection Error: {exc}")
            except BattleLostError as exc:
                logger.debug(f"Battle Lost Error: {exc}")
            except DomainNotSpecifiedError:
                logger.debug(f"Domain not specified; ended")
            logger.info(f"Re-navigating to {domain}")
            try:
                self.navigator.navigate_to_domain(category, domain)
            except DomainNotSpecifiedError as exc:
                logger.debug(f"Failed: {exc}")
        else:
            logger.debug(f"Encountered errors for {MAX_RETRIES} times")
            logger.error("Failed to farm domain")


class RunOptions:
    def ui_select_options(self) -> int:
        ui_options = self.get_option_dict()

        result = UI.OptionSelector(
            ui_options,
            font_color=(200, 200, 200),
            outline_color=(200, 200, 200)
        ).select_option()

        if result is None:
            return -1

        for key in ui_options:
            if key in result:
                setattr(self, self.get_varname_from_desc(key), result[key])

        return 0

    def get_option_dict(self) -> dict[str, bool]:
        option_dict = {}

        for varname, description in self._descriptions.items():
            if hasattr(self, varname):
                option_dict[description] = getattr(self, varname)
            else:
                logger.warning(f"Description '{description}' references a missing variable '{varname}'")

        for varname in self.get_all_bool_varnames():
            if varname not in self._descriptions:
                option_dict[varname] = getattr(self, varname)
                logger.warning(f"Description for variable '{varname}' not found; Using variable name as description")

        return option_dict

    def get_varname_from_desc(self, description: str) -> str:
        for varname, desc in self._descriptions.items():
            if desc == description:
                return varname
        raise ValueError(f"No such variable that matches description \"{description}\"")

    def get_all_bool_varnames(self) -> list[str]:
        return [attr for attr in dir(self) if isinstance(getattr(self, attr), bool) and not attr.startswith('_')]

    def __str__(self):
        ret = "<RunOptions, dict={\n"
        desc_len = max(len(self._descriptions.get(attr, attr)) + 2 for attr in self.get_all_bool_varnames())
        for key, val in self.get_option_dict().items():
            ret += f"  \"{key}\"{' ' * (desc_len - len(key))}: {val},\n"
        ret += "}>"
        return ret

    def __repr__(self):
        return self.__str__()

    def __init__(self):
        self._descriptions = {
            "LAUNCH_GAME": "launch game",
            "LOG_IN": "log in (default server)",
            "UPDATE_DOMAIN_TEMPLATES": "update domain templates",
            "USE_PREVIOUS_SCREENSHOT": "    use previous screenshot",
            "NAVIGATE_TO_DOMAIN": "navigate to domain",
            "BATTLE_REPEAT_EXPLICIT": "start battle and repeat (explicit)",
            "START_DOMAIN_FARM": "start domain farm (all stamina)",
            "GET_SUPPORT": "    get support (from first friend)",
            "CLAIM_DAILIES": "claim dailies",
            "SLEEP_WHEN_DONE": "sleep when done",
            "SHUT_DOWN_WHEN_DONE": "shut down when done",
        }

        # Boolean options
        self.LAUNCH_GAME = True
        self.LOG_IN = True
        self.UPDATE_DOMAIN_TEMPLATES = False
        self.USE_PREVIOUS_SCREENSHOT = False
        self.NAVIGATE_TO_DOMAIN = True
        self.START_DOMAIN_FARM = True
        self.GET_SUPPORT = True
        self.BATTLE_REPEAT_EXPLICIT = False
        self.CLAIM_DAILIES = True
        self.SLEEP_WHEN_DONE = False
        self.SHUT_DOWN_WHEN_DONE = False

class HSRMacro:
    def __init__(self):
        self.login = LogIn()
        self.navigate = Navigation()
        self.domain_farm = DomainFarm()
        self.dailies = Dailies()
        self.options = RunOptions()
        self.cfg: dict[str, Union[str, None]] = {
            "category": None,
            "domain": None
        }

        self.sleep_command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        self.shut_down_command = "shutdown /s /hybrid /t 60"

        self.run_summary = []

    def get_summary_message(self):
        return '\n'.join(self.run_summary)

    def leave_summary_notif(self):
        utils.leave_notif_on_login(self.get_summary_message(), title=f"HSR Automation")  #  {datetime.now().strftime('%d-%m-%y')}
        logger.debug(f"Created message: {self.get_summary_message()}")

    def sleep(self):
        logger.info("Execute sleep command")
        os.system(self.sleep_command)

    def shut_down(self):
        logger.info("Execute shut down command")
        os.system(self.shut_down_command)
        self.leave_summary_notif()

    def preprocess_options(self):
        LOGIN = self.options.LOG_IN
        UPDATE = self.options.UPDATE_DOMAIN_TEMPLATES

        if UPDATE:
            self.options.START_DOMAIN_FARM = False
            self.options.BATTLE_REPEAT_EXPLICIT = False
            logger.debug("detected UPDATE; FARM disabled")

        FARM = self.options.START_DOMAIN_FARM

        if LOGIN and FARM and not self.options.NAVIGATE_TO_DOMAIN:
            self.options.NAVIGATE_TO_DOMAIN = True
            logger.debug("detected LOGIN and FARM; NAVIGATE enabled")
        if FARM:
            self.options.BATTLE_REPEAT_EXPLICIT = False
            logger.debug("detected FARM; BATTLE_REPEAT_EXPLICIT=False")

    def option_menu(self):
        logger.debug("Started")
        self.cfg["category"] = self.cfg["domain"] = None
        while True:
            if self.options.ui_select_options() != 0:
                logger.info("Closed")
                return -1
            self.preprocess_options()
            if self.options.NAVIGATE_TO_DOMAIN:
                self.cfg["category"], self.cfg["domain"] = self.navigate.ui_choose_domain()
                if not self.cfg["category"] or not self.cfg["domain"]:
                    continue
            break

        logger.debug(f"options: {self.options}")
        return 0

    def execute_session(self):
        self.domain_farm.set_settings(
            get_support=self.options.GET_SUPPORT
        )
        CLOSE = self.options.SHUT_DOWN_WHEN_DONE or self.options.SLEEP_WHEN_DONE

        if self.options.LAUNCH_GAME:
            self.login.launch_game()
        if self.options.LOG_IN:
            self.login.log_in_to_game()
        if self.options.UPDATE_DOMAIN_TEMPLATES:
            self.navigate.update_domain_templates(skip_screenshot=self.options.USE_PREVIOUS_SCREENSHOT)
            self.run_summary.append("Updated domain templates")
        if self.options.NAVIGATE_TO_DOMAIN:
            self.navigate.navigate_to_domain(self.cfg["category"], self.cfg["domain"])
        if self.options.START_DOMAIN_FARM:
            self.domain_farm.retrying_domain_farm(self.cfg["category"], self.cfg["domain"])
            self.run_summary.append(f"Farmed {self.domain_farm.farm_count} times")
        if self.options.BATTLE_REPEAT_EXPLICIT:
            self.domain_farm.start_battle_and_repeat_safe()
            self.run_summary.append(f"Farmed {self.domain_farm.farm_count} times")
        if self.options.CLAIM_DAILIES:
            self.dailies.claim_dailies()
            self.run_summary.append(f"Claimed {self.dailies.claimed_primo_slot} slots")
        if self.options.SHUT_DOWN_WHEN_DONE:
            self.shut_down()
        elif self.options.SLEEP_WHEN_DONE:
            self.sleep()
        if CLOSE:
            return -1
        return 0

    def session(self):
        logger.set_name_and_path("HSR_Macro", macro_settings.hsr["log"])
        # logger.edit_stream_logger(log_level=logging.DEBUG)
        logger.program_start()
        if self.option_menu() != 0:
            return -1
        return self.execute_session()

    def handle_terminating_error(self, exc):
        self.run_summary.append(f"Terminated [{exc.__class__.__name__}]")
        logger.error(exc)
        logger.debug_no_fmt(traceback.format_exc()[:-1])
        logger.info("Terminated")

    def session_catch(self):
        try:
            return self.session()
        except KeyboardInterrupt:
            return 0
        except ScreenCaptureFailedError as exc:
            if not self.options.SLEEP_WHEN_DONE and not self.options.SHUT_DOWN_WHEN_DONE:
                return self.handle_terminating_error(exc)
            try:
                print("\nProgram will end in 120 seconds, press ctrl+c to cancel shutdown/sleep")
                time.sleep(120)
            except KeyboardInterrupt:
                return 0
            self.handle_terminating_error(exc)
        except BaseException as exc:
            self.handle_terminating_error(exc)

        # if error (didn't return before this)
        if self.options.SHUT_DOWN_WHEN_DONE:
            self.shut_down()
        elif self.options.SLEEP_WHEN_DONE:
            self.sleep()
        return -1


def main():
    # d = Dailies()
    # d.claim_dailies()
    s = HSRMacro()
    logger.edit_stream_logger(log_level=logging.DEBUG)
    # while not Matcher(s.navigate.survival_guide).exists():
    #     print("no")
    # print("yes")
    s.session_catch()
    # s.domain_farm.get_support()
    # s.login.log_in_to_game()
    # s.dailies.claim_dailies()
    # s.dailies.claim_monthly_pass()
    # s.navigate.navigate_to_domain("relics_domain", "relics_domain_3")
    # s.domain_farm.select_prioritised_support()
    # for category in list(s.navigate.domains)[::-1]:
    #     for domain in list(s.navigate.domains[category])[::-1]:
    #         s.navigate.navigate_to_domain(category, domain)
    #         hsr_helper.press_and_release("esc")
    # for domain in s.navigate.domains["calyx_crimson"]:
    #     s.navigate.navigate_to_domain("calyx_crimson", domain)
    #     hsr_helper.press_and_release("esc")
    # s.domain_farm.domain_start_farm(100)


if __name__ == '__main__':
    main()
