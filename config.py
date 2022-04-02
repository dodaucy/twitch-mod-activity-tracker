##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import os
import logging

import yaml
from jsonc_parser.parser import JsoncParser
from munch import munchify


log = logging.getLogger(__name__)


if os.getenv("RUN_IN_DOCKER"):
    log.info("Docker detected")
    config_path = "/config"
else:
    log.info("Docker not detected")
    config_path = "."


# Read config from file and concert to better object
log.debug("Load config")
with open(os.path.join(config_path, "config.yml"), "r") as f:
    config = munchify(yaml.safe_load(f))
log.debug("Loaded config")


# Load languages
log.debug("Load languages")
language = munchify(
    JsoncParser.parse_file(
        os.path.join(
            config_path, "languages",
            f"{config.language}.jsonc"
        )
    )
)
log.debug("Languages loaded")
