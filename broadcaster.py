##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


from typing import Optional

import requests

from config import config
from constants import USER_AGENT
from utils import raise_on_error


class Broadcaster:
    def __init__(self, channel: str, token: Optional[str] = None):
        self.channel = channel.lower()
        self.ready = False
        if token is not None:
            self.get_infos(token)
        self.mods = []
        print(f"Loaded broadcaster {self.channel}")

    def get_infos(self, token):
        if not self.ready:
            print(f"Get infos for {self.channel}...")
            r = requests.get(
                f"https://api.twitch.tv/helix/users?login={self.channel}",
                headers={
                    "User-Agent": USER_AGENT,
                    "Authorization": token,
                    "Client-Id": config.twitch.client_id
                }
            )
            j = raise_on_error(r)
            self.id = j['data'][0]['id']
            self.display_name = j['data'][0]['display_name']
            self.image = j['data'][0]['profile_image_url']
            self.ready = True
            print(f"Loaded infos for {self.channel} ({self.id})")
