import os
import Paths
import cv2
import macro_settings
import mouse
import keyboard
import time
import pyautogui
import utils
from template import Template
from matcher import TemplateData, Matcher
from status_matcher import StatusMatcher
import UI
import hsr_helper


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
        while start_time + timeout >= time.time():
            for template, exist_time, loc in status_matcher.get_all_template_status():
                if exist_time < 1:
                    continue
                if template is self.launcher_play:
                    return
                elif template is self.downloading_resources:
                    start_time += exist_time
                else:
                    mouse.click_center(loc)
                    time.sleep(1)
                    mouse.move_away_from(loc)
                status_matcher.reset_template(template)

        raise TimeoutError("Took too long to update")

    def update_game(self):
        matcher = Matcher(self.game_update, self.launcher_play, self.unclickable_play)

        start_time = time.time()
        while start_time + 3600 < time.time():
            matched = matcher.get_matching_templates()

            update_done = True
            for data in matched:
                if data.template is self.game_update:
                    mouse.click_center(data.location)
                    time.sleep(1)
                    mouse.move_away_from(data.location)
                elif data.template is self.unclickable_play:
                    update_done = False
                elif data.template is self.launcher_play and update_done:
                    return

            time.sleep(1)

    def accept_terms(self):
        Matcher(self.accept).click_center_when_exist()

    def run_pre_install(self):
        Matcher(self.pre_install).click_center_when_exist()
        Matcher(self.confirm).click_center_when_exist()


class LogIn:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["login"]
        self.assets = assets
        self.launcher_exe = macro_settings.hsr_launcher_exe
        self.launcher_play = Template(assets["launcher_play"], (1277, 768, 1606, 875))
        self.choose_server = Template(assets["choose_server"], (708, 782, 1225, 967))
        self.start_game = Template(assets["start_game"], (861, 805, 1076, 872))
        self.click_to_start = Template(assets["click_to_start"], (0, 0, 1920, 1080))
        self.checkbox = Template(assets["checkbox"], (553, 466, 607, 517), 0.975)
        self.accept = Template(assets["accept"], (963, 737, 1359, 840), 0.7)

        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]
        self.menu_bar = Template(assets["menu_bar"], (1304, 1, 1895, 95), 0.8)

        self.updater = Update()

    def launch_game(self):
        os.startfile(self.launcher_exe)

    # def log_in_to_game(self):
    #     Matcher(self.launcher_play).click_center_when_exist()
    #     Matcher(self.start_game).click_center_when_exist()
    #     Matcher(self.click_to_start).click_center_when_exist()

    def log_in_to_game(self):
        status_matcher = StatusMatcher(self.updater.launcher_update, self.updater.pre_install,
                                       self.updater.accept, self.updater.game_update,
                                       self.checkbox, self.accept,
                                       self.launcher_play,
                                       self.start_game, self.click_to_start, self.menu_bar)

        start_time = time.time()
        while start_time + 1800 >= time.time():
            for template, exist_time, loc in status_matcher.get_all_template_status():
                if exist_time < 1:
                    continue
                if template is self.menu_bar:
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

                mouse.click_center(loc)  # loc is not none
                time.sleep(1)
                mouse.move_away_from(loc)
                status_matcher.reset_template(template)

        raise TimeoutError("failed to log in")

    def start_and_log_in(self):
        self.launch_game()
        self.log_in_to_game()


class Navigation:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]
        self.assets = assets
        self.menu_bar = Template(assets["menu_bar"], (1304, 1, 1895, 95), 0.7)
        self.menu_bar_2 = Template(assets["menu_bar_2"], (1304, 1, 1895, 95), 0.7)
        self.survival_guide = Template(assets["survival_guide"], (526, 176, 640, 247), 0.95)
        self.teleport = Template(assets["teleport"], threshold=0.95)

        self.category_templates = {}
        self.domains = {}

        for key, path in assets["domain_types"].items():
            self.category_templates[key] = Template(path, (262, 292, 682, 909), 0.9)

        for category, domains in assets["domains"].items():
            if not isinstance(domains, dict):
                continue

            self.domains[category] = {}

            for key, path in domains.items():
                self.domains[category][key] = Template(path, (688, 291, 1660, 935), 0.975)

        self.nav_btn_displacement = (285, 33)
        self.nav_btn_displacement_2 = (196, 29)

        assets = Paths.assets_path_dict["hsr"]["templates"]["domain_farm"]
        self.start_challenge = Template(assets["start_challenge"], (1343, 947, 1893, 1022), 0.9)

    def ui_choose_domain(self):
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

        return category, domain

    def wait_and_click_menu_bar(self, displacement):
        menu_bar_loc = Matcher(self.menu_bar).wait_and_get_location()
        exists = True
        time.sleep(1)
        while exists:
            mouse.alt_and_click(menu_bar_loc, displacement)
            mouse.move_away_from(menu_bar_loc)
            time.sleep(1)
            exists = Matcher(self.menu_bar).exists()

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

        while start_time + 1800 > time.time():

            cat_pos_relative = 0
            dom_pos_relative = 0
            cat_positive = 0
            dom_positive = 0
            cat_loc = ()
            dom_loc = ()

            for template, exist_time, loc in status_matcher.get_all_template_status():
                if template is self.menu_bar and exist_time > THRESHOLD_1:
                    mouse.alt_and_click(loc, self.nav_btn_displacement)
                    mouse.move_away_from(loc)
                elif template is self.menu_bar_2 and exist_time > THRESHOLD_1:
                    mouse.alt_and_click(loc, self.nav_btn_displacement_2)
                    mouse.move_away_from(loc)
                elif template is self.survival_guide and exist_time > THRESHOLD_2:
                    mouse.click_center(loc)
                elif template is self.start_challenge and exist_time > THRESHOLD_1:
                    return
                elif template is target_cat and exist_time > THRESHOLD_2:
                    mouse.click_center(loc)
                    cat_positive = 1
                elif template is target_domain and exist_time > THRESHOLD_2:
                    self.teleport.set_search_area(loc)
                    Matcher(self.teleport).click_center_when_exist()
                    dom_positive = 1
                elif template in category_templates and exist_time > THRESHOLD_2:
                    cat_pos_relative = target_cat_idx - category_templates.index(template)
                    cat_loc = loc
                    continue
                elif template in domain_templates and exist_time > THRESHOLD_2:
                    dom_pos_relative = target_dom_idx - domain_templates.index(template)
                    loc = (loc[0], loc[1], loc[0] + (loc[3] - loc[1]) * 2, loc[3])
                    dom_loc = loc
                    continue
                else:
                    continue
                status_matcher.reset_template(template)

            if dom_pos_relative != 0 and not dom_positive:
                mouse.move_to_center(dom_loc)
                if dom_pos_relative > 0:
                    mouse.scroll_down(5)
                else:
                    mouse.scroll_up(5)
            elif cat_pos_relative != 0 and not cat_positive:
                mouse.move_to_center(cat_loc)
                if cat_pos_relative > 0:
                    mouse.scroll_down(5)
                else:
                    mouse.scroll_up(5)

    # def navigate_to_domain0(self, category_key, domain_key):
    #     first_cat = list(self.category_templates.values())[0]
    #     target_cat = self.category_templates[category_key]
    #     first_domain = list(self.domains[category_key].values())[0]
    #     target_domain = self.domains[category_key][domain_key]
    #
    #     matcher = Matcher(self.menu_bar,
    #                       self.survival_guide,
    #                       first_domain,
    #                       first_cat,
    #                       self.start_challenge)
    #
    #     # 1 sec = 15 loop
    #     THRESHOLD = 10
    #
    #     start_time = time.time()
    #     while start_time + 1800 > time.time():
    #
    #         exist_menu_bar = 0
    #         exist_survival_guide = 0
    #         exist_first_domain = 0
    #         exist_first_cat = 0
    #         exist_start_challenge = 0
    #
    #         while start_time + 1800 > time.time():
    #             template_data_list = matcher.get_matching_templates()
    #
    #             templates = [t.template for t in template_data_list]
    #
    #             exist_menu_bar = (exist_menu_bar + 1) * (self.menu_bar in templates)
    #             exist_survival_guide = (exist_survival_guide + 1) * (self.survival_guide in templates)
    #             exist_first_domain = (exist_first_domain + 1) * (first_domain in templates)
    #             exist_first_cat = (exist_first_cat + 1) * (first_cat in templates)
    #             exist_start_challenge = (exist_start_challenge + 1) * (self.start_challenge in templates)
    #
    #             if exist_menu_bar > THRESHOLD:
    #                 loc = [t.location for t in template_data_list if t.template is self.menu_bar][0]
    #                 mouse.alt_and_click(loc, self.nav_btn_displacement)
    #                 mouse.move_away_from(loc)
    #             elif exist_survival_guide > THRESHOLD:
    #                 loc = [t.location for t in template_data_list if t.template is self.survival_guide][0]
    #                 mouse.click_center(loc)
    #             elif exist_first_domain:
    #                 loc = [t.location for t in template_data_list if t.template is first_domain][0]
    #                 loc = (loc[0], loc[1], loc[0] + int(loc[1] + loc[3]) // 2, loc[3])
    #
    #                 try:
    #                     target_domain_loc = hsr_helper.scroll_and_find(
    #                         Matcher(target_domain), loc, 5, timeout=60
    #                     )
    #                     self.teleport.set_search_area(target_domain_loc)
    #                 except TimeoutError:
    #                     continue
    #                 Matcher(self.teleport).click_center_when_exist()
    #
    #             elif exist_first_cat > THRESHOLD:
    #                 loc = [t.location for t in template_data_list if t.template is first_cat][0]
    #                 try:
    #                     target_cat_loc = hsr_helper.scroll_and_find(
    #                         Matcher(target_cat), loc, 5, timeout=60
    #                     )
    #                     mouse.click_center(target_cat_loc)
    #                 except TimeoutError:
    #                     continue
    #             elif exist_start_challenge > THRESHOLD:
    #                 return  # the only correct exit
    #             else:
    #                 continue
    #
    #             # reset everything if something is done
    #             break
    #
    #     raise TimeoutError


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

    def select_prioritised_support(self, timeout=60):
        if not self.support_priority_list:
            return None
        title_loc = Matcher(self.support_list_title).wait_and_get_location()

        support_matcher = Matcher(*self.support_priority_list)
        eol_matcher = Matcher(self.support_end_of_list)
        start_time = time.time()

        target = None
        target_index = float("inf")
        while not eol_matcher.exists() and start_time + timeout >= time.time():

            for template_data in support_matcher.get_matching_templates():
                found_index = self.support_priority_list.index(template_data.template)
                if found_index < target_index:
                    target = template_data.template
                    target_index = found_index
                if target_index == 0:
                    break
            if target_index == 0:
                break
            mouse.move_relative(title_loc, (90, 150))
            mouse.scroll_down(5)

        if target is None:
            return None

        target_matcher = Matcher(target)

        start_time = time.time()
        while start_time + 60 > time.time():
            loc = target_matcher.get_location_if_match()
            if loc is not None:
                mouse.click_center(loc)
                time.sleep(2)
                break
            mouse.move_relative(title_loc, (90, 150))
            mouse.scroll_up(5)

    def get_support(self):
        """
            start: team selection interface

            end: team selection interface
        """
        if not self._get_support:
            return

        Matcher(self.get_support_button).click_center_when_exist()
        # if self.support_priority_list:
        self.select_prioritised_support()
        Matcher(self.add_to_team).click_center_when_exist()

    def select_auto_battle(self):
        auto_battle = Matcher(self.auto_battle_off).wait_and_get_location()
        mouse.relative_click(auto_battle, (179, 24))

    def start_battle_and_repeat(self, max_count):
        """
            start: in domain battle

            end: open world
        """
        self.select_auto_battle()

        i = 1
        while i < max_count:
            # wait till battle is over
            Matcher(self.exit_challenge, self.challenge_again).wait_for_all_to_match()
            # repeat
            mouse.click_center(Matcher(self.challenge_again).wait_and_get_location())

            matching = Matcher(self.auto_battle_on, self.not_enough_stamina).wait_and_match()
            if matching.template is self.not_enough_stamina:
                Matcher(self.stamina_cancel).click_center_when_exist()
                Matcher(self.exit_challenge).click_center_when_exist()
                break

            i += 1
        else:
            # wait till battle is over
            Matcher(self.exit_challenge, self.challenge_again).wait_for_all_to_match()
            # exit
            Matcher(self.exit_challenge).click_center_when_exist()

    def activate_open_world_boss(self):
        keyboard.press("up")
        Matcher(self.navigator.menu_bar).while_exist_do(
            mouse.click, delay=1
        )
        keyboard.release("up")

    def domain_start_farm(self, max_count):
        """
            start: team selection interface

            end: open world
        """
        self.get_support()
        Matcher(self.start_challenge_2).click_center_when_exist()

        domain_type = Matcher(self.auto_battle_off,
                              self.navigator.menu_bar,
                              self.navigator.menu_bar_2).wait_and_match(300.00)  # 5 minutes
        if domain_type.template is self.navigator.menu_bar or domain_type.template is self.navigator.menu_bar_2:
            self.activate_open_world_boss()
        self.start_battle_and_repeat(max_count)

    def domain_farm_bulk(self, max_count):
        """
            start: team selection interface

            end: open world
        """
        Matcher(self.start_challenge).click_center_when_exist()

        matching = Matcher(self.start_challenge_2, self.not_enough_stamina).wait_and_match()
        if matching.template is self.not_enough_stamina:
            Matcher(self.not_enough_stamina).while_exist_do(
                keyboard.press_and_release, ["esc"]
            )
            Matcher(self.start_challenge).while_exist_do(
                keyboard.press_and_release, ["esc"]
            )
            return False
        else:
            self.domain_start_farm(max_count)

    def set_settings(self, get_support=False):
        self._get_support = get_support

    def is_calyx(self):
        Matcher(self.start_challenge).wait_and_match()
        return Matcher(self.add_count, self.reduce_count).exists()

    def calyx_farm_all(self, category, domain):
        """
            start: domain start interface

            end: open world
        """
        mouse.relative_click(Matcher(self.add_count).wait_and_get_location(), (9, 17))
        Matcher(self.start_challenge).click_center_when_exist()

        status_matcher = Matcher(self.start_challenge_2, self.not_enough_stamina)
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
            mouse.relative_click(Matcher(self.add_count).wait_and_get_location(), (9, 17))
        else:
            Matcher(self.not_enough_stamina).while_exist_do(
                keyboard.press_and_release, ["esc"]
            )

        reduce_button_matcher = Matcher(self.reduce_count)
        for i in range(5):
            # change count
            mouse.click_center(reduce_button_matcher.wait_and_get_location())

            # test for stamina
            Matcher(self.start_challenge).click_center_when_exist()
            status = status_matcher.wait_and_match()
            if status.template is self.not_enough_stamina:
                Matcher(self.not_enough_stamina).while_exist_do(
                    keyboard.press_and_release, ["esc"]
                )
                continue
            else:
                break
        else:
            Matcher(self.start_challenge).while_exist_do(
                keyboard.press_and_release, ["esc"]
            )
            return

        self.domain_start_farm(1)

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
        self.options = {
            "launch game": 1,
            "log in (default server)": 1,
            "navigate to domain": 1,
            "farm domain (all stamina)": 1,
            "    get support (from first friend)": 1,
            "sleep when done": 0,
            "shut down when done": 0
        }

        self.sleep_command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        self.shut_down_command = "shutdown /s /t 0"

    def session(self):
        category, domain = None, None
        while True:
            result = UI.OptionSelector(
                self.options,
                font_color=(200, 200, 200),
                outline_color=(200, 200, 200)
            ).select_option()
            if result is None:
                return -1

            self.options = {text: result[idx] for idx, text in enumerate(self.options)}

            if (self.options["farm domain (all stamina)"]
                    and (self.options["launch game"] or self.options["log in (default server)"]))\
                    or self.options["navigate to domain"]:
                category, domain = self.navigate.ui_choose_domain()
                if domain is None or category is None:
                    continue
            break

        self.domain_farm.set_settings(
            get_support=self.options["    get support (from first friend)"]
        )

        LOGIN = self.options["launch game"] or self.options["log in (default server)"]
        FARM = self.options["farm domain (all stamina)"]
        CLOSE = self.options["shut down when done"] or self.options["sleep when done"]

        if self.options["launch game"]:
            self.login.launch_game()
        if self.options["log in (default server)"]:
            self.login.log_in_to_game()
        if self.options["navigate to domain"] or (LOGIN and FARM):
            self.navigate.navigate_to_domain(category, domain)
        if self.options["farm domain (all stamina)"]:
            self.domain_farm.general_domain_farm(category, domain)
        if self.options["shut down when done"]:
            os.system(self.shut_down_command)
        elif self.options["sleep when done"]:
            os.system(self.sleep_command)

        return 0

    def session_catch_timeout(self):
        try:
            return self.session()
        except TimeoutError:
            utils.write_exc_log_to_file(Paths.exc_log_dir, "hsr")

            if self.options["sleep when done"]:
                os.system(self.sleep_command)
            if self.options["shut down when done"]:
                os.system(self.shut_down_command)
            return 1


def main():
    s = HSRMacro()
    s.session_catch_timeout()
    # s.login.log_in_to_game()
    # s.domain_farm.select_prioritised_support()
    # for category in list(s.navigate.domains)[::-1]:
    #     for domain in list(s.navigate.domains[category])[::-1]:
    #         s.navigate.navigate_to_domain(category, domain)
    #         keyboard.press_and_release("esc")
    # for template in s.navigate.domains["open_world_boss"]:
    #     print(template)
    # Matcher(s.domain_farm.support_end_of_list).click_center_when_exist()


if __name__ == '__main__':
    main()
