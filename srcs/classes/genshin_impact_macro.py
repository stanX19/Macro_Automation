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
import UI
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

    def log_in_to_game(self):
        Matcher(self.launcher_play).click_center_when_exist()
        Matcher(self.choose_server).click_center_when_exist()
        Matcher(self.click_to_start).click_center_when_exist()

    def start_and_log_in(self):
        self.launch_game()
        self.log_in_to_game()
