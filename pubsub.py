##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import asyncio
import json
import logging
import time
from broadcaster import Broadcaster
from typing import Any, Iterable, Optional, Union

import websockets

from constants import PUBSUB, USER_AGENT, ACTIONS
from config import config
from cursor import Cursor


log = logging.getLogger(__name__)

broadcaster = Broadcaster()


class PubSub:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.stop = False

    async def on_connect(self) -> None:
        log.info("PubSub connected")

    def run(self) -> None:
        self.last_ping = None
        self.last_pong = None
        self.loop.run_until_complete(self.connect())
        log.debug("Start tasks...")
        self.loop.run_until_complete(asyncio.gather(
            self.loop.create_task(self.heartbeat()),
            self.loop.create_task(self.recv()),
            self.loop.create_task(self.check_pong())
        ))
        log.debug("Close websocket...")
        self.loop.run_until_complete(self.ws.close())
        log.debug("Close loop...")
        self.loop.close()
        log.debug("All tasks completed")

    async def connect(self) -> None:
        log.debug("Get a token...")
        token, mod_id, channel_id = await broadcaster.get_acress()
        log.debug("Connect to WebSocket...")
        self.ws = await websockets.connect(
            PUBSUB,
            extra_headers={
                "User-Agent": USER_AGENT
            }
        )
        log.debug("Connected. Send LISTEN command...")
        await self.ws.send(json.dumps({
            "type": "LISTEN",
            "data": {
                "auth_token": token,
                "topics": [
                    f"chat_moderator_actions.{mod_id}.{channel_id}"
                ]
            }
        }))

    async def reconnect(self) -> None:
        log.info("Reconnect...")
        self.stop = True

    async def recv(self):
        while not self.stop:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), 10)
                log.debug(f"New package: {msg.strip()}")
                response = json.loads(msg)
                if response['type'] == "PONG":
                    if self.last_pong is None:
                        self.loop.create_task(self.on_connect())
                    self.last_pong = time.time()
                    log.debug(f"Twitch pong: {self.last_pong - self.last_ping} seconds")
                elif response['type'] == "RESPONSE":
                    if response['error'] != "":
                        log.error(response['error'])
                elif response['type'] == "MESSAGE":
                    message = json.loads(response['data']['message'])
                    if message['type'] == "moderation_action":
                        if message['data']['moderation_action'] in ACTIONS:
                            with Cursor() as c:
                                c.execute(
                                    f"""
                                    INSERT INTO actions
                                    (
                                        mod_id,
                                        display_name,
                                        {message['data']['moderation_action']}
                                    )
                                    VALUES
                                    (
                                        %s, %s, 1
                                    )
                                    ON DUPLICATE KEY UPDATE display_name = %s,{message['data']['moderation_action']} = {message['data']['moderation_action']} + 1;
                                    """,
                                    (
                                        message['data']['created_by_user_id'],
                                        message['data']['created_by'],
                                        message['data']['created_by']
                                    )
                                )
                        else:
                            log.debug(f"Ignore {message['data']['moderation_action']} event")
                        # ! message['data']['args']
                        # ! message['data']['from_automod']
                elif response['type'] == "RECONNECT":
                    log.info("Twitch sended reconnet signal")
                    await self.reconnect()
                else:
                    log.error(response)
            except websockets.exceptions.ConnectionClosed:
                log.error('Recv disconnected')
                await self.reconnect()
            except asyncio.exceptions.TimeoutError:
                pass
        log.debug("Recv closed")

    async def heartbeat(self):
        try:
            while not self.stop:
                await self.ws.send(json.dumps({"type": "PING"}))
                self.last_ping = time.time()
                await asyncio.sleep(30)
        except websockets.exceptions.ConnectionClosed:
            log.error("Heartbeat disconnected")
            await self.reconnect()
        log.debug("Heartbeat closed")

    async def check_pong(self):
        while not self.stop:
            await asyncio.sleep(1)
            if self.last_ping is not None:
                if time.time() - self.last_ping > 10:
                    if self.last_pong is None:
                        log.error("No first pong")
                        await self.reconnect()
                    elif self.last_ping > self.last_pong:
                        log.error("No pong")
                        await self.reconnect()
        log.debug("Check pong closed")


def run():
    while True:
        pubsub = PubSub()
        pubsub.run()
