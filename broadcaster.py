##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


from typing import Optional
import logging
import asyncio

import requests

from config import config
from constants import USER_AGENT
from utils import raise_on_error
from cursor import Cursor


log = logging.getLogger(__name__)


class Broadcaster:
    def __init__(self) -> None:
        self.channel = config.twitch.channel.lower()
        self.ready = False
        self.session = requests.Session()
        log.info(f"Loaded broadcaster {self.channel}")

    def get_infos(self, token) -> None:
        if not self.ready:
            log.debug(f"Get infos for {self.channel}...")
            r = self.session.get(
                f"https://api.twitch.tv/helix/users?login={self.channel}",
                headers={
                    "User-Agent": USER_AGENT,
                    "Authorization": token,
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

    async def get_acress(self):
        while True:
            with Cursor() as c:
                c.execute(
                    "SELECT * FROM mods"
                )
                mods = c.fetchall()
            for mod in mods:
                r = self.session.get(
                    "https://api.twitch.tv/helix/users",
                    headers={
                        "User-Agent": USER_AGENT,
                        "Authorization": f"Bearer {mod['token']}",
                        "Client-Id": config.twitch.client_id
                    }
                )
                log.debug(f"HTTP response: {r.text.strip()}")
                j = raise_on_error(r, "Invalid OAuth token")
                if "message" in j:
                    log.debug("Token expired. Delete...")
                    with Cursor() as c:
                        c.execute(
                            "DELETE FROM mods WHERE id = %s",
                            (
                                mod['id'],
                            )
                        )
                    continue
                if not self.ready:
                    self.get_infos(f"Bearer {mod['token']}")
                return mod['token'], j['data'][0]['id'], self.id
            log.warning(f"No valid tokens found for {'channek_id'}. Try again soon...")
            await asyncio.sleep(60)
