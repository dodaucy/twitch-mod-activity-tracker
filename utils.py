##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import logging
import time
from typing import Optional
from urllib.parse import quote_plus

import requests

from config import config, language
from cursor import Cursor


log = logging.getLogger(__name__)

session = requests.session()


def refresh_all_tokens() -> None:
    with Cursor() as c:
        c.execute(
            "SELECT * FROM mods"
        )
        mods = c.fetchall()
    for mod in mods:
        log.debug("Refresh token...")
        t = time.time()
        if mod['expires'] < t:
            log.info(f"Token from {mod['id']} expired")
            with Cursor() as c:
                c.execute(
                    "DELETE FROM mods WHERE token = %s",
                    (
                        mod['token'],
                    )
                )
        elif mod['expires'] - t < 1800:
            log.debug(f"Token from {mod['id']} expires in {mod['expires'] - t} seconds. Refresh...")
            r = session.post(
                "https://id.twitch.tv/oauth2/token",  # TODO: in constants.py
                params={
                    "grant_type": "refresh_token",
                    "refresh_token": mod['refresh_token'],
                    "client_id": config.twitch.client_id,
                    "client_secret": config.twitch.client_secret
                }
            )
            j = raise_on_error(r, "Invalid refresh token")
            with Cursor() as c:
                if "message" in j:
                    c.execute(
                        "DELETE FROM mods WHERE id = %s",
                        (
                            mod['id'],
                        )
                    )
                    log.debug(f"Token from {mod['id']} is invalid")
                else:
                    c.execute(
                        "UPDATE mods SET token = %s, refresh_token = %s, expires = %s WHERE id = %s",
                        (
                            j['access_token'],
                            j['refresh_token'],
                            time.time() + j['expires_in'],
                            mod['id']
                        )
                    )
                    log.debug(f"Token from {mod['id']} refreshed")
        else:
            log.debug(f"Token from {mod['id']} valid. Expires in {mod['expires'] - t} seconds")


def get_command(command_display_name: str) -> str:
    "Returns the original name of a command"
    for command in language.commands:
        if language.commands[command].display_name == command_display_name:
            return command


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
