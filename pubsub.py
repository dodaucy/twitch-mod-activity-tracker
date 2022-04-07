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

import websockets

from constants import LANGUAGE_STRUCTURE, PUBSUB, USER_AGENT
from cursor import Cursor


log = logging.getLogger(__name__)


class PubSub:
    def run(self, broadcaster) -> None:
        "Start pubsub"
        self.broadcaster = broadcaster
        while True:
            self.loop = asyncio.new_event_loop()
            self.stop = False
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
            log.debug("Loop closed")

    async def connect(self) -> None:
        "Connect to pubsub"
        log.debug("Get acress...")
        token, mod_id, channel_id = await self.broadcaster.get_acress()
        log.debug(f"mod: {mod_id}, channel: {channel_id}")
        log.debug("Connect to websocket...")
        self.ws = await websockets.connect(
            PUBSUB,
            extra_headers={
                "User-Agent": USER_AGENT
            }
        )
        log.debug("Send LISTEN command...")
        await self.ws.send(json.dumps({
            "type": "LISTEN",
            "data": {
                "auth_token": token,
                "topics": [
                    f"chat_moderator_actions.{mod_id}.{channel_id}"
                ]
            }
        }))

    def reconnect(self) -> None:
        "Reconnect to pubsub"
        log.info("Reconnect...")
        self.stop = True

    async def recv(self) -> None:
        "Receive packets"
        while not self.stop:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), 10)  # TODO: maybe configurable
                log.debug(f"New package: {msg.strip()}")
                response = json.loads(msg)
                if response['type'] == "PONG":
                    if self.last_pong is None:
                        log.info("PubSub connected")
                    self.last_pong = time.time()
                    log.debug(f"Twitch pong: {self.last_pong - self.last_ping} seconds")
                elif response['type'] == "RESPONSE":
                    if response['error'] != "":
                        log.error(response['error'])
                        self.reconnect()
                elif response['type'] == "MESSAGE":
                    message = json.loads(response['data']['message'])
                    if message['type'] == "moderation_action":
                        action = message['data']['moderation_action']
                        if action in LANGUAGE_STRUCTURE['actions']:
                            with Cursor() as c:
                                c.execute(
                                    f"""
                                    INSERT INTO actions
                                    (
                                        mod_id,
                                        login,
                                        `{action}`
                                    )
                                    VALUES
                                    (
                                        %s, %s, 1
                                    )
                                    ON DUPLICATE KEY
                                    UPDATE
                                        login = %s,
                                        `{action}` = `{action}` + 1
                                    """,
                                    (
                                        message['data']['created_by_user_id'],
                                        message['data']['created_by'],
                                        message['data']['created_by']
                                    )
                                )
                        else:
                            log.debug(f"Ignore {action} event")
                        log.debug(f"from automod: {message['data']['from_automod']}")  # TODO: evaluate or remove
                elif response['type'] == "RECONNECT":
                    log.info("Twitch sended reconnet signal")
                    self.reconnect()
                else:
                    log.error(response)
                    self.reconnect()
            except websockets.exceptions.ConnectionClosed:
                log.error('Recv disconnected')
                self.reconnect()
            except asyncio.exceptions.TimeoutError:
                pass
        log.debug("Recv closed")

    async def heartbeat(self):
        "Maintain connection"
        try:
            while not self.stop:
                await self.ws.send(json.dumps({"type": "PING"}))
                self.last_ping = time.time()
                await asyncio.sleep(30)  # TODO: configurable
        except websockets.exceptions.ConnectionClosed:
            log.error("Heartbeat disconnected")
            self.reconnect()
        log.debug("Heartbeat closed")

    async def check_pong(self):
        "Check if connection is alive"
        while not self.stop:
            await asyncio.sleep(1)
            if self.last_ping is not None:
                if time.time() - self.last_ping > 10:  # TODO: configurable
                    if self.last_pong is None:
                        log.error("No first pong")
                        self.reconnect()
                    elif self.last_ping > self.last_pong:
                        log.error("No pong")
                        self.reconnect()
        log.debug("Check pong closed")
