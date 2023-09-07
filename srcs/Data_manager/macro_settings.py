import Paths
import json

with open(Paths.settings_json, 'r') as f:
    settings = json.load(f)
hsr_launcher_exe = settings["hsr"]["launcher_exe"]