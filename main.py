##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import logging
import sys
import threading

import coloredlogs
import uvicorn
from disnake.ext import tasks

from api import app, authentication
from bot import bot
from config import config
from utils import refresh_all_tokens
import pubsub


# Enable logging
coloredlogs.install(
    level=logging.DEBUG,
    fmt="[%(asctime)s] [%(threadName)s/%(levelname)s] [%(name)s.%(funcName)s:%(lineno)s]: %(message)s",
    isatty=sys.stderr.isatty()
)


log = logging.getLogger(__name__)


# Disable DEBUG and INFO log for discord
log.debug("Disable DEBUG and INFO log for discord...")
discord_log = logging.getLogger("disnake")
discord_log.setLevel(logging.WARNING)

# Disable DEBUG and INFO log for urllib3
log.debug("Disable DEBUG and INFO log for urllib3...")
urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.WARNING)

# Disable DEBUG and INFO log for websockets
log.debug("Disable DEBUG and INFO log for websockets...")
websockets_log = logging.getLogger("websockets")
websockets_log.setLevel(logging.WARNING)

# Disable DEBUG and INFO log for asyncio
log.debug("Disable DEBUG and INFO log for asyncio...")
asyncio_log = logging.getLogger("asyncio")
asyncio_log.setLevel(logging.WARNING)


# Repeat every 10 minutes
@tasks.loop(minutes=10)
async def routine():
    log.debug("Run routine...")
    log.debug("Refresh old tokens...")
    refresh_all_tokens()
    log.debug("Remove expired states...")
    authentication.remove_expired_states()
    log.debug("Routine finished")


# Start routine
log.debug("Start routine...")
routine.start()


# Start website
log.debug("Start fastapi...")
threading.Thread(
    target=uvicorn.run,
    args=(
        app,
    ),
    kwargs={
        "host": config.website.host,
        "port": config.website.port,
        "log_level": "error"
    },
    daemon=True
).start()


# Start pubsub
log.debug("Start pubsub...")
threading.Thread(
    target=pubsub.run,
    daemon=True
).start()


# Start discord bot
bot.run(config.discord.token)
