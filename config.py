##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import logging
import os

import yaml
from jsonc_parser.parser import JsoncParser
from munch import munchify

from constants import LANGUAGE_STRUCTURE


log = logging.getLogger(__name__)


def validate_languages(struct: dict, languages: dict) -> dict:
    "Converts all data into the right format and checks if everything is there"
    end = {}
    for i in struct:
        if isinstance(struct[i], dict):
            end[i] = validate_languages(struct[i], languages[i])
        else:
            try:
                end[i] = languages[i]
                for j in struct[i]:
                    end[i] = j(end[i])
            except TypeError:
                end[i] = struct[i](languages[i])
    return end


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
    validate_languages(
        LANGUAGE_STRUCTURE,
        JsoncParser.parse_file(
            os.path.join(
                config_path, "languages",
                f"{config.language}.jsonc"
            )
        )
    )
)
log.debug("Languages loaded")
