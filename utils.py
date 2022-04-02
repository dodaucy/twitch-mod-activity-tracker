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
import time
import shelve
from urllib.parse import quote_plus
from typing import Optional

import requests

from config import config, language
from constants import USER_AGENT
from cursor import Cursor


log = logging.getLogger(__name__)


# ! oudated
def get_actions(mod_format: bool = False) -> dict:
    "Load all mod actions from a file"
    actions = {}
    with shelve.open(os.path.join(data_path, "actions")) as db:
        for action in db.keys():
            if mod_format:
                for mod in db[action]:
                    if mod not in actions:
                        actions[mod] = {}
                    actions[mod][action] = db[action][mod]
            else:
                actions[action] = db[action]
    return actions


def refresh_all_tokens() -> None:
    with Cursor() as c:
        c.execute(
            "SELECT * FROM mods;"
        )
        mods = c.fetchall()
    for mod in mods:
        log.debug("Refresh token...")
        t = time.time()
        if mod['expires'] < t:
            log.info(f"Token from {mod['id']} expired")
            with Cursor() as c:
                c.execute(
                    "DELETE FROM mods WHERE token = %s;",
                    (
                        mod['token'],
                    )
                )
        elif mod['expires'] - t < 1800:
            log.debug(f"Token from {mod['id']} expires in {mod['expires'] - t} seconds. Refresh...")
            ...  # ! if not authorized delete the token / mod['refresh_token']
            log.debug(f"Token from {mod['id']} refreshed")
        else:
            log.debug(f"Token from {mod['id']} valid. Expires in {mod['expires'] - t} seconds")


def get_command(command_display_name: str) -> str:
    "Returns the original name of a command"
    for command in language.commands:
        if language.commands[command].display_name == command_display_name:
            return command


def get_action(action_display_name: str) -> str:
    "Returns the original name of a command action"
    for action in language.actions:
        if language.actions[action] == action_display_name:
            return action


def command_help(command: str) -> str:
    "Returns how a command should be used"
    description = f"**/{language.commands[command].display_name}**"
    if "arguments" in language.commands[command]:
        description += " "
        for argument in language.commands[command].arguments:
            if language.commands[command].arguments[argument].marked_as_optional:
                description += f"**[** `{language.commands[command].arguments[argument].display_name}` **]**"
            else:
                description += f"**<** `{language.commands[command].arguments[argument].display_name}` **>**"
    return description


def raise_on_error(
    response: requests.Response,
    ignore_message: Optional[str] = None
) -> dict:
    j = response.json()
    if "message" in j:
        if ignore_message is not None:
            if j['message'] == ignore_message:
                return j
        raise Exception(f"{j['error'] if 'error' in j else 'UNKNOW'} / {j['message']}")
    elif response.status_code != 200:
        raise Exception(f"{response.status_code} / {j}")
    return j


def join_args(url: str, *args, **kwargs) -> str:
    if not args and not kwargs:
        return url
    args = [quote_plus(arg) for arg in args]
    for kwarg in kwargs:
        args.append(f"{kwarg}={quote_plus(kwargs[kwarg])}")
    return f'{url}?{"&".join(args)}'
