import os
import time
import traceback

import Paths
import UI
import macro_settings
import mouse
from logger import logger
import logging
from status_matcher import StatusMatcher
from template import Template


class LogIn:
    def __init__(self):
        assets = Paths.assets_path_dict["genshin"]["templates"]["login"]
        self.templates = assets
        self.launcher_exe = macro_settings.genshin["launcher_exe"]
        self.launcher_play_old = Template(assets["launcher_play_old"], (1290, 780, 1592, 865))
        self.launcher_play = Template(assets["launcher_play"], threshold=0.9)
        self.genshin_logo = Template(assets["genshin_logo"], threshold=0.75, binary=True, variable_size=True)
        self.genshin_icon = Template(assets["genshin_icon"], threshold=0.9)
        self.choose_server = Template(assets["start_game"], (831, 468, 1087, 549))
        self.click_to_start = Template(assets["click_to_start"], (0, 0, 1920, 1080))
        self.menu_bar = Template(assets["menu_bar"], (1300, 0, 1920, 100), 0.75, binary=True)

    def launch_game(self):
        os.startfile(self.launcher_exe)
        logger.info("ok")

    def log_in_to_game(self):
        status_matcher = StatusMatcher(
            self.genshin_logo, self.genshin_icon, self.launcher_play,
            self.choose_server, self.click_to_start, self.menu_bar
        )
        start_time = time.time()
        logger.info("started")
        while start_time + 1800 >= time.time():
            for template, loc, exist_time in status_matcher.get_all_template_status_list():
                if exist_time < 1:
                    continue
                logger.debug(f"{template.file_name} matched {status_matcher[template]}")
                if template is self.genshin_logo:
                    continue
                if template is self.launcher_play and status_matcher[self.genshin_logo].time < 1.0:
                    continue
                if template is self.menu_bar:
                    return
                mouse.click_and_move_away(loc)

        raise TimeoutError("failed to log in")

    def start_and_log_in(self):
        self.launch_game()
        self.log_in_to_game()


class GenshinMacro:
    def __init__(self):
        self.login = LogIn()
        self.options = {
            "launch game": 1,
            "log in (default server)": 1,
            "sleep when done": 0,
        }

        self.sleep_command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"

    def sleep(self):
        logger.info("execute sleep command")
        os.system(self.sleep_command)

    def option_menu(self):
        result = UI.OptionSelector(
            self.options,
            font_color=(200, 200, 200),
            outline_color=(200, 200, 200)
        ).select_option()
        if result is None:
            logger.info("Closed")
            return -1

        self.options = {text: result[text] for text in self.options}
        logger.debug(f"checklist: {self.options}")
        return 0

    def execute_session(self):
        LOGIN = self.options["launch game"] or self.options["log in (default server)"]
        # FARM = self.options["farm domain (all stamina)"]
        CLOSE = self.options["sleep when done"]  # or self.options["shut down when done"]

        if self.options["launch game"]:
            self.login.launch_game()
        if self.options["log in (default server)"]:
            self.login.log_in_to_game()
        if self.options["sleep when done"]:
            self.sleep()
        if CLOSE:
            return -1
        return 0

    def session(self):
        logger.set_name_and_path("Genshin Macro", macro_settings.genshin["log"])
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
        if self.options["sleep when done"]:
            self.sleep()
        return -1


def main():
    s = GenshinMacro()
    logger.edit_stream_logger(log_level=logging.DEBUG)
    s.session_catch()


if __name__ == '__main__':
    main()
