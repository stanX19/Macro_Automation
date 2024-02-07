import Paths
import json

with open(Paths.settings_json, 'r') as f:
    settings = json.load(f)

# hsr
hsr = settings["hsr"]
hsr["log"] = Paths.exc_log_dir + "/" + hsr["log"]

# genshin
genshin = settings["genshin"]
genshin["log"] = Paths.exc_log_dir + "/" + genshin["log"]
