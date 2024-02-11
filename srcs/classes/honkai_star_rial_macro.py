import logging
import os
import time
import traceback

import Paths
import UI
import hsr_helper
import keyboard
import macro_settings
import mouse
from logger import logger
from matcher import TemplateData, Matcher
from status_matcher import StatusMatcher
from template import Template


class Update:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["update"]
        self.assets = assets
        self.launcher_update = Template(assets["launcher_update"], (952, 589, 1196, 654))
        self.downloading_resources = Template(assets["downloading_resources"], (532, 686, 792, 723))
        self.open_launcher = Template(assets["open_launcher"], (779, 676, 1116, 746))
        self.pre_install = Template(assets["pre_install"], (1027, 784, 1094, 852))
        self.confirm = Template(assets["confirm"], (953, 582, 1201, 664))
        self.game_update = Template(assets["game_update"], (1277, 768, 1606, 875), 0.975)
        self.preinstall_pause = Template(assets["preinstall_pause"], self.pre_install.roi)
        self.accept = Template(assets["accept"], self.confirm.roi)
        self.unclickable_play = Template(assets["unclickable_play"], self.game_update.roi, 0.975)

        assets = Paths.assets_path_dict["hsr"]["templates"]["login"]
        self.launcher_play = Template(assets["launcher_play"], self.game_update.roi, self.unclickable_play.threshold)

    def update_launcher(self):
        status_matcher = StatusMatcher(self.launcher_update, self.open_launcher,
                                       self.launcher_play, self.downloading_resources)
        start_time = time.time()
        timeout = 1800
        logger.info("started")
        while start_time + timeout >= time.time():
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                if exist_time < 1:
                    continue
                if template is self.launcher_play:
                    logger.info("completed")
                    return
                elif template is self.downloading_resources:
                    start_time += exist_time
                else:
                    mouse.click_center(loc)
                    time.sleep(1)
                    mouse.move_away_from(loc)
                status_matcher.reset_template(template)

        raise TimeoutError(f"Took too long to update >{timeout}s")

    def update_game(self):
        logger.info("started")
        matcher = Matcher(self.game_update, self.launcher_play, self.unclickable_play)

        start_time = time.time()
        while start_time + 3600 < time.time():
            matched = matcher.get_matching_templates()

            update_done = True
            for data in matched:
                logger.debug(f"{data.template.file_name} matched {data.loc}")
                if data.template is self.game_update:
                    mouse.click_and_move_away(data.loc, 1)
                elif data.template is self.unclickable_play:
                    update_done = False
                elif data.template is self.launcher_play and update_done:
                    logger.info("completed")
                    return

            time.sleep(1)

    def accept_terms(self):
        logger.info("started")
        Matcher(self.accept).click_center_when_exist()
        logger.info("completed")

    def run_pre_install(self):
        logger.info("started")
        status_matcher = StatusMatcher(self.confirm, self.pre_install)
        start_time = time.time()
        timeout = 300
        while start_time + timeout >= time.time():
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                if exist_time < 1:
                    continue
                logger.debug(f"{template.file_name} matched {loc}")
                if template is self.confirm:
                    Matcher(self.confirm).click_center_when_exist()
                    logger.info("completed")
                    return
                elif template is self.pre_install:
                    mouse.click_and_move_away(loc, 1)


class LogIn:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["login"]
        self.assets = assets
        self.menu_bar = MenuBar()
        self.launcher_exe = macro_settings.hsr["launcher_exe"]
        self.launcher_play = Template(assets["launcher_play"], (1277, 768, 1606, 875))
        self.choose_server = Template(assets["choose_server"], (708, 782, 1225, 967))
        self.start_game = Template(assets["start_game"], (861, 805, 1076, 872))
        self.click_to_start = Template(assets["click_to_start"], (0, 0, 1920, 1080))
        self.checkbox = Template(assets["checkbox"], (553, 466, 607, 517), 0.975)
        self.accept = Template(assets["accept"], (963, 737, 1359, 840), 0.7)
        self.confirm = Template(assets["confirm"], (740, 603, 1194, 743), 0.9)

        self.updater = Update()

    def launch_game(self):
        os.startfile(self.launcher_exe)
        logger.info("ok")

    def log_in_to_game(self):
        status_matcher = StatusMatcher(  # self.updater.launcher_update, self.updater.pre_install,
            # self.updater.accept, self.updater.game_update,
            self.checkbox, self.accept, self.confirm,
            self.launcher_play,
            self.start_game, self.click_to_start,
            *self.menu_bar.templates)

        start_time = time.time()
        logger.info("started")
        while start_time + 1800 >= time.time():
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                if exist_time < 1:
                    continue
                logger.debug(f"{template.file_name} matched {loc}")
                if template in self.menu_bar.templates:
                    logger.info("completed")
                    return
                # if template is self.updater.launcher_update:
                #     self.updater.update_launcher()
                #     start_time = time.time()
                #     continue
                # if template is self.updater.pre_install:
                #     self.updater.run_pre_install()
                #     continue
                # if template is self.updater.game_update:
                #     self.updater.update_game()
                #     start_time = time.time()
                #     continue

                mouse.click_and_move_away(loc, 1)
                status_matcher.reset_template(template)

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
        self.survival_guide = Template(assets["survival_guide"], (543, 170, 670, 256), 0.95)
        self.teleport = Template(assets["teleport"], threshold=0.95)
        self.enter_domain = Template(assets["enter_domain"], threshold=0.95)

        self.category_templates: dict[str, Template] = {}
        self.domains: dict[str, dict[str, Template]] = {}
        self.domain_dir = macro_settings.hsr["domain_dir"]

        for key, path in assets["domain_types"].items():
            self.category_templates[key] = Template(path, (244, 271, 686, 918), 0.9)

        for category, domains in assets[self.domain_dir].items():
            if not isinstance(domains, dict):
                continue

            self.domains[category] = {}

            for key, path in domains.items():
                self.domains[category][key] = Template(path, (678, 280, 1680, 950), 0.975)

        assets = Paths.assets_path_dict["hsr"]["templates"]["domain_farm"]
        self.start_challenge = Template(assets["start_challenge"], (1343, 947, 1893, 1022), 0.9)

    def ui_choose_domain(self):
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
                elif template is self.start_challenge and exist_time > THRESHOLD_1:
                    logger.info("completed")
                    return
                elif template is target_cat and exist_time > THRESHOLD_2:
                    logger.debug("target category found")
                    mouse.click_center(loc)
                    Matcher(target_cat).wait_for_unmatch()
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

            cat_pos_relative = 0
            dom_pos_relative = 0
            cat_positive = 0
            dom_positive = 0
            cat_loc = ()
            dom_loc = ()

            clicked_menu = False
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                # logger.debug(f"{template.file_name} matched [{exist_time}, {loc}]")
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
                    cat_positive = 1
                elif template is target_domain and exist_time > THRESHOLD_2:
                    logger.debug("target domain found")
                    self.teleport.set_search_area(loc)
                    self.enter_domain.set_search_area(loc)
                    logger.debug("clicking teleport")
                    matched = Matcher(self.teleport, self.enter_domain).get_matching_templates()
                    if matched:
                        mouse.click_center(matched[0].loc)
                    dom_positive = 1
                elif template in category_templates:
                    if exist_time <= THRESHOLD_2:
                        continue
                    cat_pos_relative = target_cat_idx - category_templates.index(template)
                    cat_loc = loc
                    continue
                elif template in domain_templates:
                    if exist_time <= THRESHOLD_2:
                        continue
                    dom_pos_relative = target_dom_idx - domain_templates.index(template)
                    loc = (loc[0], loc[1], loc[0] + (loc[3] - loc[1]) * 2, loc[3])
                    dom_loc = loc
                    continue
                else:
                    continue

                status_matcher.reset_template(template)

            # print(cat_pos_relative, dom_pos_relative, cat_positive, dom_positive)
            # print()
            if dom_pos_relative != 0 and not dom_positive:
                logger.debug("Scrolling domain")
                mouse.move_to_center(dom_loc)
                if dom_pos_relative > 0:
                    mouse.scroll_down(5)
                else:
                    mouse.scroll_up(5)
            elif cat_pos_relative != 0 and not cat_positive:
                logger.debug("Scrolling category")
                mouse.move_to_center(cat_loc)
                if cat_pos_relative > 0:
                    mouse.scroll_down(5)
                else:
                    mouse.scroll_up(5)


class Dailies:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["dailies"]
        self.assets = assets
        self.navigator = Navigation()

        self.daily_logo = Template(assets["daily_logo"], (9, 9, 257, 123), 0.9)
        self.daily_tab = Template(assets["daily_tab_button"], (423, 169, 543, 258), 0.9)
        self.daily_claim = Template(assets["daily_claim"], (298, 783, 549, 873), 0.9)

        self.daily_primo1 = Template(assets["daily_primo"], (596, 272, 681, 351), 0.9)
        self.daily_primo2 = Template(assets["daily_primo"], (839, 274, 922, 352), 0.9)
        self.daily_primo3 = Template(assets["daily_primo"], (1078, 274, 1169, 351), 0.9)
        self.daily_primo4 = Template(assets["daily_primo"], (1327, 272, 1409, 353), 0.9)
        self.daily_primo5 = Template(assets["daily_primo"], (1571, 273, 1651, 353), 0.9)

        self.claimed_primo_slot = -1
        self.claimed_assignments = -1

        self.assignment_logo = Template(assets["assignment_logo"], (0, 0, 193, 95), 0.9)
        self.goto_assignment = Template(assets["goto_assignment"], (259, 397, 1666, 893), 0.99)
        self.goto_assignment_displace = (139, 422)
        self.assignment_claim = Template(assets["assignment_claim"], (1261, 863, 1670, 944), 0.7)
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
        while start_time + 120 > time.time():
            status_matcher.update()

            if last_seen + 15 < time.time():
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
                    hsr_helper.press_and_release, ["esc"], delay=1
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
                            logger.debug(f"Claim primo at {self.claimed_primo_slot}th slot")
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
        Matcher(self.daily_logo).while_exist_do(
            hsr_helper.press_and_release, ["esc"]
        )
        logger.debug("exited dailies")
        logger.info(f"completed, claimed {self.claimed_primo_slot} slots of primo")
        self.claim_monthly_pass()
        logger.debug("done")

    def do_assignments(self):
        status_matcher = StatusMatcher(self.assignment_claim, self.assignment_re, self.assignment_red_dot)

        start_time = time.time()
        last_seen = start_time + 0
        THRESHOLD = 0.5  # seconds
        MAX_ASSIGNMENT = 4
        self.claimed_assignments = 0

        logger.info(f"started")
        redeploying = False
        while start_time + 30 > time.time():
            status_matcher.update()

            if last_seen + 5 < time.time():
                logger.debug("last_seen > 10s, break")
                break
            if self.claimed_assignments >= MAX_ASSIGNMENT:
                logger.debug("claimed and redeployed MAX_ASSIGNMENTS, break")
                break
            if status_matcher[self.assignment_claim].time > THRESHOLD:
                mouse.click_center(status_matcher[self.assignment_claim].loc)
                logger.debug("clicked claim assignment")

                redeploying = True

            elif status_matcher[self.assignment_re].time > THRESHOLD:
                mouse.click_center(status_matcher[self.assignment_re].loc)
                logger.debug("clicked redeploy assignment")
                if redeploying:
                    self.claimed_assignments += 1
                    logger.debug("claimed and redeployed assignment +1")
                    redeploying = False

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
        while start_time + 15 > time.time():
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
        self.not_enough_stamina = Template(assets["not_enough_stamina"], (860, 324, 1066, 432), 0.9)
        self.stamina_cancel = Template(assets["stamina_cancel"], (559, 698, 941, 765), 0.9)
        self.start_challenge = Template(assets["start_challenge"], (1343, 947, 1893, 1022), 0.9)
        self.start_challenge_2 = Template(assets["start_challenge_2"], (1501, 948, 1853, 1021), 0.9)
        self.add_to_team = Template(assets["add_to_team"], (1526, 962, 1850, 1021), 0.95)

        # calyx specific
        self.add_count = Template(assets["calyx"]["add_count"], (1742, 882, 1888, 917), 0.8)
        self.reduce_count = Template(assets["calyx"]["reduce_count"], (1206, 881, 1279, 917), 0.9)

        # support
        self.get_support_button = Template(assets["support"]["get_support"], (1675, 704, 1833, 769), 0.9)
        self.support_end_of_list = Template(assets["support"]["end_of_list"], (520, 810, 560, 940), 0.90)
        self.support_list_title = Template(assets["support"]["list_title"], (236, 80, 364, 133), 0.85)
        self.support_priority_list: list[Template] = [
                                                         Template(path, (71, 187, 528, 957), 0.7) for path in
                                                         assets["support"]["priority"].values()
                                                     ][::-1]  # new first, old last

        self._get_support = True

    def select_prioritised_support(self, timeout=10):
        if not self.support_priority_list:
            return None
        logger.info("started")
        logger.debug("waiting for support_list_title to match")
        title_loc = Matcher(self.support_list_title).wait_and_get_location(timeout=30)
        logger.debug("found support_list_title")

        support_matcher = Matcher(*self.support_priority_list)
        start_time = time.time()

        chosen_index = float("inf")

        logger.debug("click second tab in list")
        mouse.click_relative(title_loc, (90, 300))
        if not self.support_priority_list[0] in support_matcher.get_matching_templates():
            logger.debug("first tab is not the most desired, click first tab")
            mouse.click_relative(title_loc, (90, 150))

        while start_time + timeout >= time.time():
            for data in support_matcher.get_matching_templates():
                logger.debug(f"{data.template.file_name} matched at {data.loc}")
                found_index = self.support_priority_list.index(data.template)
                if found_index < chosen_index:
                    chosen_index = found_index
                    mouse.click_center(data.loc)
                    logger.debug(f"clicked on: {data}")
                if chosen_index == 0:
                    logger.info("found most prioritized support")
                    logger.debug(f"waiting for {data} to unmatch (turn white)")
                    Matcher(data.template.as_threshold(data.threshold)).wait_for_unmatch()
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

    def start_battle_and_repeat(self, max_count):
        """
            start: in domain battle

            end: open world
        """
        self.select_auto_battle()

        i = 1
        logger.info("started")
        while i < max_count:
            # wait till battle is over
            Matcher(self.exit_challenge, self.challenge_again).wait_for_all_to_match()
            # repeat
            logger.debug("Waiting for challenge again to match")
            mouse.click_center(Matcher(self.challenge_again).wait_and_get_location())

            logger.debug("Waiting for auto_battle or not_enough_stamina to match")
            matching = Matcher(self.auto_battle_on, self.not_enough_stamina).wait_and_match()
            if matching.template is self.not_enough_stamina:
                logger.debug("not enough stamina")
                Matcher(self.stamina_cancel).click_center_when_exist()
                Matcher(self.exit_challenge).click_center_when_exist()
                break

            i += 1
        else:
            # wait till battle is over
            logger.debug("Waiting for exit challenge to match")
            Matcher(self.exit_challenge, self.challenge_again).wait_for_all_to_match()
            # exit
            logger.debug("clicking exit challenge")
            Matcher(self.exit_challenge).click_center_when_exist()
        logger.info("completed")

    def activate_open_world_boss(self):
        logger.info("started")
        keyboard.press("up")  # holds down
        Matcher(*self.navigator.menu_bar.templates).while_exist_do(
            mouse.click, delay=1
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
            *self.navigator.menu_bar.templates
        ).wait_and_match(60.00)  # 1 minutes
        if domain_type.template in self.navigator.menu_bar.templates:
            self.activate_open_world_boss()
        self.start_battle_and_repeat(max_count)
        logger.info("completed")

    def domain_farm_bulk(self, max_count):
        """
            start: team selection interface

            end: open world
        """
        logger.info(f"started, max_count={max_count}")
        logger.debug("clicking start_challenge when exist")
        Matcher(self.start_challenge).click_center_when_exist()
        logger.debug("Waiting for start_challenge or not_enough_stamina to match")
        matching = Matcher(self.start_challenge_2, self.not_enough_stamina).wait_and_match()
        if matching.template is self.not_enough_stamina:
            logger.debug("exiting (esc)")
            Matcher(self.not_enough_stamina).while_exist_do(
                hsr_helper.press_and_release, ["esc"]
            )
            Matcher(self.start_challenge).while_exist_do(
                hsr_helper.press_and_release, ["esc"]
            )
            logger.debug("exited")
            return False
        else:
            self.domain_start_farm(max_count)

    def set_settings(self, get_support=False):
        self._get_support = get_support

    def is_calyx(self):
        logger.debug("Waiting for start_challenge to match")
        Matcher(self.start_challenge).wait_and_match()
        return Matcher(self.add_count, self.reduce_count).exists()

    def calyx_farm_all(self, category, domain):
        """
            start: domain start interface

            end: open world
        """
        logger.info(f"started, category={category}, domain={domain}")
        logger.debug("Waiting for add_count to match")
        mouse.click_relative(Matcher(self.add_count).wait_and_get_location(), (9, 17))
        Matcher(self.start_challenge).click_center_when_exist()

        status_matcher = Matcher(self.start_challenge_2, self.not_enough_stamina)
        logger.debug("Waiting for start_challenge or not_enough_stamina to match")
        status = status_matcher.wait_and_match()

        if status.template is self.start_challenge_2:  # if stamina >= 60
            # farm remaining needs category and domain
            if category is None or domain is None:
                category, domain = self.navigator.ui_choose_domain()
            if category is None or domain is None:
                return

            # first bulk farm
            self.domain_start_farm(float('inf'))
            self.navigator.navigate_to_domain(category, domain)
            logger.debug("Waiting for add_count to match")
            mouse.click_relative(Matcher(self.add_count).wait_and_get_location(), (9, 17))
        else:
            logger.debug("exiting (esc)")
            Matcher(self.not_enough_stamina).while_exist_do(
                hsr_helper.press_and_release, ["esc"]
            )
            logger.debug("exited")

        reduce_button_matcher = Matcher(self.reduce_count)
        for i in range(5):
            # change count
            logger.debug("waiting for reduce_button to match")
            mouse.click_center(reduce_button_matcher.wait_and_get_location())

            # test for stamina
            logger.debug("waiting for start_challenge to match")
            Matcher(self.start_challenge).click_center_when_exist()
            status = status_matcher.wait_and_match()
            if status.template is self.not_enough_stamina:
                logger.debug("exiting not_enough_stamina (esc)")
                Matcher(self.not_enough_stamina).while_exist_do(
                    hsr_helper.press_and_release, ["esc"]
                )
                logger.debug("exited not_enough_stamina")
                continue
            else:
                break
        else:
            logger.debug("exiting farming_rewards (esc)")
            Matcher(self.start_challenge).while_exist_do(
                hsr_helper.press_and_release, ["esc"]
            )
            logger.debug("exited farming_rewards")
            return

        self.domain_start_farm(1)
        logger.info("ended")

    def general_domain_farm(self, category=None, domain=None):
        if self.is_calyx():
            self.calyx_farm_all(category, domain)
        else:
            self.domain_farm_bulk(float('inf'))


class HSRMacro:
    def __init__(self):
        self.login = LogIn()
        self.navigate = Navigation()
        self.domain_farm = DomainFarm()
        self.dailies = Dailies()
        self.options = {
            "launch game": 1,
            "log in (default server)": 1,
            "navigate to domain": 1,
            "farm domain (all stamina)": 1,
            "    get support (from first friend)": 1,
            "claim dailies": 1,
            "sleep when done": 0,
            "shut down when done": 0
        }
        self.cfg = {
            "category": None,
            "domain": None
        }

        self.sleep_command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        self.shut_down_command = "shutdown /s /t 0"

    def sleep(self):
        logger.info("execute sleep command")
        os.system(self.sleep_command)

    def shut_down(self):
        logger.info("execute shut down command")
        os.system(self.shut_down_command)

    def option_menu(self):
        self.cfg["category"] = self.cfg["domain"] = None
        while True:
            result = UI.OptionSelector(
                self.options,
                font_color=(200, 200, 200),
                outline_color=(200, 200, 200)
            ).select_option()
            if result is None:
                logger.info("Closed")
                return -1

            self.options = {text: result[idx] for idx, text in enumerate(self.options)}

            if (self.options["farm domain (all stamina)"]
                and (self.options["launch game"] or self.options["log in (default server)"])) \
                    or self.options["navigate to domain"]:
                self.cfg["category"], self.cfg["domain"] = self.navigate.ui_choose_domain()
                if self.cfg["domain"] is None or self.cfg["category"] is None:
                    continue
            break

        self.domain_farm.set_settings(
            get_support=self.options["    get support (from first friend)"]
        )
        logger.debug(f"checklist: {self.options}")
        return 0

    def execute_session(self):
        LOGIN = self.options["launch game"] or self.options["log in (default server)"]
        FARM = self.options["farm domain (all stamina)"]
        CLOSE = self.options["shut down when done"] or self.options["sleep when done"]

        if self.options["launch game"]:
            self.login.launch_game()
        if self.options["log in (default server)"]:
            self.login.log_in_to_game()
        if self.options["navigate to domain"] or (LOGIN and FARM):
            self.navigate.navigate_to_domain(self.cfg["category"], self.cfg["domain"])
        if self.options["farm domain (all stamina)"]:
            self.domain_farm.general_domain_farm(self.cfg["category"], self.cfg["domain"])
        if self.options["claim dailies"]:
            self.dailies.claim_dailies()
        if self.options["shut down when done"]:
            self.shut_down()
        elif self.options["sleep when done"]:
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

    def session_catch(self):
        try:
            return self.session()
        except TimeoutError:
            logger.error("TimeoutError")
            logger.debug_no_fmt(traceback.format_exc()[:-1])
            logger.info("Terminated")
        except KeyboardInterrupt:
            return -1
        except Exception as exc:
            logger.error(exc)
            logger.debug_no_fmt(traceback.format_exc()[:-1])
            logger.info("Terminated")

        # if error (didn't return before this)
        if self.options["shut down when done"]:
            self.shut_down()
        elif self.options["sleep when done"]:
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
    # s.dailies.claim_dailies()
    # s.dailies.claim_monthly_pass()
    # s.navigate.navigate_to_domain("relics_domain", "img_3")
    # s.domain_farm.select_prioritised_support()
    # for category in list(s.navigate.domains)[::-1]:
    #     for domain in list(s.navigate.domains[category])[::-1]:
    #         s.navigate.navigate_to_domain(category, domain)
    #         hsr_helper.press_and_release("esc")
    # for template in s.navigate.domains["open_world_boss"]:
    #     print(template)
    # s.domain_farm.domain_start_farm(100)


if __name__ == '__main__':
    main()
