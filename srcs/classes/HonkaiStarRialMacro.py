import os
import Paths
import macro_settings
import mouse
import keyboard
import time
import pyautogui
from Template import Template, Matcher
import UI
import hsr_helper


class LogIn:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["login"]
        self.templates = assets
        self.launcher_exe = macro_settings.hsr_launcher_exe
        self.launcher_play = Template(assets["launcher_play"], (1277, 768, 1606, 875))
        self.choose_server = Template(assets["choose_server"], (708, 782, 1225, 967))
        self.click_to_start = Template(assets["click_to_start"], (0, 0, 1920, 1080))

    def launch_game(self):
        os.startfile(self.launcher_exe)

    def log_in_to_game(self):
        Matcher(self.launcher_play).click_center_when_exist()
        Matcher(self.choose_server).click_relative_when_exist((0, 0))
        Matcher(self.click_to_start).click_center_when_exist()

    def start_and_log_in(self):
        self.launch_game()
        self.log_in_to_game()


class Navigation:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["navigation"]
        self.templates = assets
        self.menu_bar = Template(assets["menu_bar"], (1304, 1, 1895, 95), 0.8)
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

    def click_menu_bar(self, displacement):
        menu_bar = Matcher(self.menu_bar).wait_and_get_location()
        exists = True
        time.sleep(1)
        while exists:
            pyautogui.keyDown("alt")
            mouse.relative_click(menu_bar, displacement)
            pyautogui.keyUp("alt")
            time.sleep(1)
            exists = Matcher(self.menu_bar).exists()

    def navigate_to_domain(self, category_key, domain_key):
        self.click_menu_bar((285, 33))

        first_cat = list(self.category_templates.values())[0]

        # wait till any of these appear
        matching = Matcher(self.survival_guide, first_cat).wait_and_match()

        if matching.template is self.survival_guide:
            mouse.click_center(matching.location)
            first_cat_location = Matcher(first_cat).wait_and_get_location()
        else:
            first_cat_location = matching.location

        # choose category, need to scroll up and down
        target_cat = hsr_helper.scroll_and_find(
            Matcher(self.category_templates[category_key]), first_cat_location, 5
        )

        mouse.click_center(target_cat)
        first_domain = list(self.domains[category_key].values())[0]
        first_domain_loc = Matcher(first_domain).wait_and_get_location()

        first_domain_loc = (first_domain_loc[0],
                            first_domain_loc[1],
                            first_domain_loc[0] + (first_domain_loc[3] - first_domain_loc[1]),
                            first_domain_loc[3])
        target_domain = hsr_helper.scroll_and_find(
            Matcher(self.domains[category_key][domain_key]), first_domain_loc, 18
        )

        # print(f"domain found, ROI: {target_domain}")
        self.teleport.set_search_area(target_domain)
        Matcher(self.teleport).click_center_when_exist()


class DomainFarm:
    def __init__(self):
        assets = Paths.assets_path_dict["hsr"]["templates"]["domain_farm"]
        self.templates = assets
        self.navigator = Navigation()

        self.auto_battle_off = Template(assets["auto_battle_off"], (1570, 15, 1930, 82), 0.775)
        self.auto_battle_on = Template(assets["auto_battle_on"], (1570, 15, 1930, 82), 0.775)
        self.challenge_again = Template(assets["challenge_again"], (1007, 912, 1407, 983), 0.9)
        self.exit_challenge = Template(assets["exit_challenge"], (517, 914, 915, 982), 0.9)
        self.not_enough_stamina = Template(assets["not_enough_stamina"], (860, 324, 1066, 432), 0.9)
        self.stamina_cancel = Template(assets["stamina_cancel"], (559, 698, 941, 765), 0.9)
        self.start_challenge = Template(assets["start_challenge"], (1343, 947, 1893, 1022), 0.9)
        self.start_challenge_2 = Template(assets["start_challenge_2"], (1501, 948, 1853, 1021), 0.9)
        self.get_support_button = Template(assets["get_support"], (1675, 704, 1833, 769), 0.9)
        self.add_to_team = Template(assets["add_to_team"], (1526, 962, 1850, 1021), 0.95)

        # calyx specific
        self.add_count = Template(assets["calyx"]["add_count"], (1742, 882, 1888, 917), 0.8)
        self.reduce_count = Template(assets["calyx"]["reduce_count"], (1206, 881, 1279, 917), 0.9)

        self._get_support = True

    def get_support(self):
        """
            start: team selection interface

            end: team selection interface
        """
        if self._get_support:
            Matcher(self.get_support_button).click_center_when_exist()
            Matcher(self.add_to_team).click_center_when_exist()

    def start_farm(self, max_count):
        """
            start: team selection interface

            end: open world
        """
        self.get_support()
        Matcher(self.start_challenge_2).click_center_when_exist()

        auto_battle = Matcher(self.auto_battle_off).wait_and_get_location()
        mouse.relative_click(auto_battle, (179, 24))

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
            self.start_farm(max_count)

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
            self.start_farm(float('inf'))
            self.navigator.navigate_to_domain(category, domain)
            mouse.relative_click(Matcher(self.add_count).wait_and_get_location(), (9, 17))
        else:
            Matcher(self.not_enough_stamina).while_exist_do(
                keyboard.press_and_release, ["esc"]
            )

        for i in range(6):
            Matcher(self.start_challenge).click_center_when_exist()
            status = status_matcher.wait_and_match()
            if status.template is self.not_enough_stamina:
                Matcher(self.not_enough_stamina).while_exist_do(
                    keyboard.press_and_release, ["esc"]
                )
                mouse.click_center(Matcher(self.reduce_count).wait_and_get_location())
                continue
            else:
                break
        else:
            Matcher(self.start_challenge).while_exist_do(
                keyboard.press_and_release, ["esc"]
            )
        self.start_farm(1)

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
            "shut down when done": 0,
        }

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
        if self.options["launch game"]:
            self.login.launch_game()
        if self.options["log in (default server)"]:
            self.login.log_in_to_game()
        if self.options["navigate to domain"]:
            self.navigate.navigate_to_domain(category, domain)
        if self.options["farm domain (all stamina)"]:
            self.domain_farm.general_domain_farm(category, domain)
        if self.options["shut down when done"]:
            os.system('shutdown /s /t 0')

        return 0


if __name__ == '__main__':
    s = HSRMacro()
    s.session()
