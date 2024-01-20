import Paths
import json

with open(Paths.settings_json, 'r') as f:
    settings = json.load(f)

hsr = settings["hsr"]
genshin = settings["genshin"]