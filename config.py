##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import os

import yaml
from jsonc_parser.parser import JsoncParser
from munch import munchify


if os.getenv("RUN_IN_DOCKER"):
    config_path = "/config"
    data_path = "/data"
else:
    config_path = "."
    data_path = "data"


with open(os.path.join(config_path, "config.yml"), "r") as f:
    config = munchify(yaml.safe_load(f))

language = munchify(JsoncParser.parse_file(os.path.join(config_path, "languages", f"{config.language}.jsonc")))
