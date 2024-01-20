import os
import traceback
import keyboard
import time
import Paths
import logging
import macro_settings
import mouse
import utils
import UI
import hsr_helper
from template import Template
from matcher import TemplateData, Matcher
from status_matcher import StatusMatcher
from logger import logger


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
            for template, exist_time, loc in status_matcher.get_all_template_status_list():
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
                logger.debug(f"{data.template.file_name} matched {data.location}")
                if data.template is self.game_update:
                    mouse.click_and_move_away(data.location, 1)
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
            for template, exist_time, loc in status_matcher.get_all_template_status_list():
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
        self.launcher_exe = macro_settings.hsr["launcher_exe"]
        self.launcher_play = Template(assets["launcher_play"], (1277, 768, 1606, 875))
        self.choose_server = Template(assets["choose_server"], (708, 782, 1225, 967))
        self.start_game = Template(assets["start_game"], (861, 805, 1076, 872))
        self.click_to_start = Template(assets["click_to_start"], (0, 0, 1920, 1080))
        self.checkbox = Template(assets["checkbox"], (553, 466, 607, 517), 0.975)
        self.accept = Template(assets["accept"], (963, 737, 1359, 840), 0.7)
        self.confirm = Template(assets["confirm"], (740, 603, 1194, 743), 0.9)

        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]
        self.menu_bar = Template(assets["menu_bar"], (1304, 1, 1895, 95), 0.8)

        self.updater = Update()

    def launch_game(self):
        os.startfile(self.launcher_exe)
        logger.info("ok")

    def log_in_to_game(self):
        status_matcher = StatusMatcher(self.updater.launcher_update, self.updater.pre_install,
                                       self.updater.accept, self.updater.game_update,
                                       self.checkbox, self.accept, self.confirm,
                                       self.launcher_play,
                                       self.start_game, self.click_to_start, self.menu_bar)

        start_time = time.time()
        logger.info("started")
        while start_time + 1800 >= time.time():
            for template, exist_time, loc in status_matcher.get_all_template_status_list():
                if exist_time < 1:
                    continue
                logger.debug(f"{template.file_name} matched {loc}")
                if template is self.menu_bar:
                    logger.info("completed")
                    return
                if template is self.updater.launcher_update:
                    self.updater.update_launcher()
                    start_time = time.time()
                    continue
                if template is self.updater.pre_install:
                    self.updater.run_pre_install()
                    continue
                if template is self.updater.game_update:
                    self.updater.update_game()
                    start_time = time.time()
                    continue

                mouse.click_and_move_away(loc, 1)
                status_matcher.reset_template(template)

        raise TimeoutError("failed to log in")

    def start_and_log_in(self):
        self.launch_game()
        self.log_in_to_game()


class Navigation:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]
        self.assets = assets
        self.menu_bar = Template(assets["menu_bar"], (1275, 0, 1961, 114), 0.7)
        self.menu_bar_2 = Template(assets["menu_bar_2"], (1275, 0, 1961, 114), 0.7)
        self.survival_guide = Template(assets["survival_guide"], (543, 170, 670, 256), 0.95)
        self.teleport = Template(assets["teleport"], threshold=0.95)

        self.category_templates = {}
        self.domains = {}
        self.domain_dir = macro_settings.hsr["domain_dir"]

        for key, path in assets["domain_types"].items():
            self.category_templates[key] = Template(path, (244, 271, 686, 918), 0.9)

        for category, domains in assets[self.domain_dir].items():
            if not isinstance(domains, dict):
                continue

            self.domains[category] = {}

            for key, path in domains.items():
                self.domains[category][key] = Template(path, (678, 280, 1680, 950), 0.975)

        self.nav_btn_displacement = (285, 33)
        self.nav_btn_2_displacement = (196, 29)

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

    def wait_and_click_menu_bar(self, displacement):
        logger.info("started")
        logger.debug("Waiting for menu bar to match")
        menu_bar_loc = Matcher(self.menu_bar).wait_and_get_location()
        exists = True
        time.sleep(1.5)
        while exists:
            logger.debug("Alt clicking menu bar")
            mouse.alt_and_click(menu_bar_loc, displacement)
            mouse.move_away_from(menu_bar_loc)
            time.sleep(1.5)
            exists = Matcher(self.menu_bar).exists()
        logger.info("completed")

    def navigate_to_domain(self, category_key, domain_key):
        category_templates = list(self.category_templates.values())
        target_cat = self.category_templates[category_key]
        target_cat_idx = category_templates.index(target_cat)
        domain_templates = list(self.domains[category_key].values())
        target_domain = self.domains[category_key][domain_key]
        target_dom_idx = domain_templates.index(target_domain)

        status_matcher = StatusMatcher(self.menu_bar, self.menu_bar_2, self.survival_guide,
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

            for template, exist_time, loc in status_matcher.get_all_template_status_list():
                # logger.debug(f"{template.file_name} matched [{exist_time}, {loc}]")
                if template is self.menu_bar and exist_time > THRESHOLD_1:
                    mouse.alt_and_click(loc, self.nav_btn_displacement)
                    mouse.move_away_from(loc)
                elif template is self.menu_bar_2 and exist_time > THRESHOLD_1:
                    mouse.alt_and_click(loc, self.nav_btn_2_displacement)
                    mouse.move_away_from(loc)
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
                    logger.debug("clicking teleport")
                    Matcher(self.teleport).click_center_when_exist()
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
        self.assignment_red_dot = Template(assets["assignment_red_dot"], (307, 175, 1208, 298), 0.9)

    def claim_dailies(self):
        all_daily_primo = [self.daily_primo5, self.daily_primo4, self.daily_primo3,
                           self.daily_primo2, self.daily_primo1]
        status_matcher = StatusMatcher(self.daily_claim, *all_daily_primo, self.goto_assignment,
                                       self.navigator.menu_bar, self.navigator.menu_bar_2,
                                       self.daily_tab)

        start_time = time.time()
        last_seen = start_time + 0
        THRESHOLD = 1  # seconds
        self.claimed_primo_slot = 0

        logger.info("started")
        while start_time + 180 > time.time():
            status_matcher.update()

            if last_seen + 15 < time.time():
                logger.debug("last_seen > 15s, break")
                break
            if status_matcher[self.navigator.menu_bar].time > THRESHOLD:
                mouse.alt_and_click(status_matcher[self.navigator.menu_bar].loc,
                                    self.navigator.nav_btn_displacement)
                logger.debug("click menu bar")

            elif status_matcher[self.navigator.menu_bar_2].time > THRESHOLD:
                mouse.alt_and_click(status_matcher[self.navigator.menu_bar_2].loc,
                                    self.navigator.nav_btn_2_displacement)
                logger.debug("click menu bar 2")

            elif status_matcher[self.daily_tab].time > THRESHOLD:
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

    def do_assignments(self):
        status_matcher = StatusMatcher(self.assignment_claim, self.assignment_re, self.assignment_red_dot)

        start_time = time.time()
        last_seen = start_time + 0
        THRESHOLD = 0.5  # seconds
        MAX_ASSIGNMENT = 4
        self.claimed_assignments = 0

        logger.info(f"started")
        redeploying = False
        while start_time + 60 > time.time():
            status_matcher.update()

            if last_seen + 10 < time.time():
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
        self.support_priority_list = [
            Template(path, (43, 57, 554, 1024), 0.95) for path in assets["support"]["priority"].values()
        ][::-1]  # new first, old last

        self._get_support = True

    def select_prioritised_support(self, timeout=30):
        if not self.support_priority_list:
            return None
        logger.info("started")
        logger.debug("waiting for support_list_title to match")
        title_loc = Matcher(self.support_list_title).wait_and_get_location(timeout=30)

        support_matcher = Matcher(*self.support_priority_list)
        start_time = time.time()

        chosen_index = float("inf")
        logger.debug("scrolling down")

        while start_time + timeout >= time.time():
            for data in support_matcher.get_matching_templates():
                logger.debug(f"{data.template.file_name} matched at {data.location}")
                found_index = self.support_priority_list.index(data.template)
                if found_index < chosen_index:
                    chosen_index = found_index
                    mouse.click_center(data.location)
                    logger.debug(f"clicked on: {data.template.file_name}")
                if chosen_index == 0:
                    logger.info("found most prioritized support")
                    logger.debug(f"waiting for {data.template.file_name} to unmatch (turn white)")
                    Matcher(data.template).wait_for_unmatch()
                    break
            if chosen_index == 0:
                break
            mouse.move_relative(title_loc, (90, 150))
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
        Matcher(self.navigator.menu_bar).while_exist_do(
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
        domain_type = Matcher(self.auto_battle_off,
                              self.navigator.menu_bar,
                              self.navigator.menu_bar_2).wait_and_match(60.00)  # 1 minutes
        if domain_type.template is self.navigator.menu_bar or domain_type.template is self.navigator.menu_bar_2:
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
                    and (self.options["launch game"] or self.options["log in (default server)"]))\
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
            os.system(self.shut_down_command)
        elif self.options["sleep when done"]:
            os.system(self.sleep_command)
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
            os.system(self.shut_down_command)
        elif self.options["sleep when done"]:
            os.system(self.sleep_command)
        return -1


def main():
    # d = Dailies()
    # d.claim_dailies()
    s = HSRMacro()
    # while not Matcher(s.navigate.survival_guide).exists():
    #     print("no")
    # print("yes")
    s.session_catch()
    # s.navigate.navigate_to_domain("relics_domain", "img_3")
    # s.domain_farm.select_prioritised_support()
    # for category in list(s.navigate.domains)[::-1]:
    #     for domain in list(s.navigate.domains[category])[::-1]:
    #         s.navigate.navigate_to_domain(category, domain)
    #         hsr_helper.press_and_release("esc")
    # for template in s.navigate.domains["open_world_boss"]:
    #     print(template)
    # Matcher(s.domain_farm.support_end_of_list).click_center_when_exist()


if __name__ == '__main__':
    main()
