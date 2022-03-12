##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import os
import shelve

import requests
from disnake.ext.tasks import loop

from config import config, data_path
from constants import GQL, REQUEST_BODY, IGNORE_CHANNELS, IGNORE_ACTIONS
from utils import get_actions, put_actions


@loop(seconds=config.twitch.pause_between_requests)
async def get_mod_actions():
    # Download the latest 200 mod actions from Twitch
    body = REQUEST_BODY.copy()
    body['variables']['channelID'] = config.twitch.channel_id
    r = requests.post(
        GQL,
        headers={
            "User-Agent": config.twitch.user_agent,
            "Authorization": config.twitch.token
        },
        json=body
    )
    try:
        j = r.json()
    except requests.exceptions.JSONDecodeError:
        print(r.text)
        return
    if "error" in j:
        print(f"Twitch [{j['error']}]: {j['message']}")
        return
    # * twitch duraction: j['extensions']['durationMilliseconds']
    if j['data']['channel'] is None:
        print("Channel not found")
        return
    if j['data']['channel']['moderationLogs']['actions'] is None:
        print("No mod rights on this channel")
        return
    edges = j['data']['channel']['moderationLogs']['actions']['edges']
    with shelve.open(os.path.join(data_path, "last_ids")) as db:
        if config.twitch.channel_id in db:
            last_id = db[config.twitch.channel_id]
        else:
            last_id = ""
        db[config.twitch.channel_id] = edges[0]['node']['id']
    actions = get_actions()
    for edge in edges:
        if edge['node']['id'] == last_id:
            break
        if edge['node']['moderator']['login'] in IGNORE_CHANNELS or edge['node']['action'] in IGNORE_ACTIONS:
            continue
        if config.twitch.ignore_broadcaster:
            if edge['node']['moderator']['id'] == config.twitch.channel_id:
                continue
        if not edge['node']['action'] in actions:
            actions[edge['node']['action']] = {}
        if not edge['node']['moderator']['login'] in actions[edge['node']['action']]:
            actions[edge['node']['action']][edge['node']['moderator']['login']] = 0
        actions[edge['node']['action']][edge['node']['moderator']['login']] += 1
    put_actions(actions)
