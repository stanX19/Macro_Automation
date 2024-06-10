import os
import cv2
import mouse
import keyboard
import time
import pyautogui
import traceback
import utils
import Paths
import macro_settings
from template import Template
from matcher import TemplateData, Matcher
import UI
from logger import logger
import hsr_helper


class LogIn:
    def __init__(self):
        assets = Paths.assets_path_dict["genshin"]["templates"]["login"]
        self.templates = assets
        self.launcher_exe = macro_settings.genshin["launcher_exe"]
        self.launcher_play = Template(assets["launcher_play"], (1290, 780, 1592, 865))
        self.choose_server = Template(assets["start_game"], (831, 468, 1087, 549))
        self.click_to_start = Template(assets["click_to_start"], (0, 0, 1920, 1080))

    def launch_game(self):
        os.startfile(self.launcher_exe)
        logger.info("ok")

    def log_in_to_game(self):
        logger.debug("started")
        Matcher(self.launcher_play).click_center_when_exist()
        Matcher(self.choose_server).click_center_when_exist()
        Matcher(self.click_to_start).click_center_when_exist()
        time.sleep(300)
        logger.info("completed")

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


