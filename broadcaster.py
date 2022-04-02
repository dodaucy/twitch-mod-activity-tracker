##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import logging
import asyncio

import requests

from config import config
from constants import USER_AGENT
from utils import raise_on_error
from cursor import Cursor


log = logging.getLogger(__name__)


class Broadcaster:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {"User-Agent": USER_AGENT}
        self.ready = False
        log.info(f"Loaded broadcaster {config.twitch.channel.lower()}")

    async def get_acress(self):
        while True:
            with Cursor() as c:
                c.execute(
                    "SELECT * FROM mods"
                )
                mods = c.fetchall()
            for mod in mods:
                r = self.session.get(
                    "https://api.twitch.tv/helix/users",  # TODO: in constants.py
                    headers={
                        "Authorization": f"Bearer {mod['token']}",
                        "Client-Id": config.twitch.client_id
                    }
                )
                log.debug(f"HTTP response: {r.text.strip()}")
                j = raise_on_error(r, "Invalid OAuth token")
                if "message" in j:
                    log.info(f"Token from {mod['id']} expired")
                    with Cursor() as c:
                        c.execute(
                            "DELETE FROM mods WHERE id = %s",
                            (
                                mod['id'],
                            )
                        )
                    continue
                if not self.ready:
                    # get infos about the broadcaster
                    log.debug(f"Get infos for {config.twitch.channel.lower()}...")
                    r = self.session.get(
                        f"https://api.twitch.tv/helix/users?login={config.twitch.channel.lower()}",  # TODO: in constants.py
                        headers={
                            "Authorization": f"Bearer {mod['token']}",
                            "Client-Id": config.twitch.client_id
                        }
                    )
                    log.debug(f"HTTP response: {r.text.strip()}")
                    j = raise_on_error(r)
                    self.id = j['data'][0]['id']
                    self.display_name = j['data'][0]['display_name']
                    self.image = j['data'][0]['profile_image_url']
                    log.info(f"Loaded infos for {self.display_name} ({self.id})")
                    self.ready = True
                return mod['token'], j['data'][0]['id'], self.id
            log.warning(f"No valid tokens found for {config.twitch.channel}. Try again soon...")
            await asyncio.sleep(60)  # TODO: configurable
