##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import time
import logging
import uuid

from fastapi import status


log = logging.getLogger(__name__)


class AuthError(Exception):
    def __init__(self, title: str, details: str, status_code: int):
        self.title = title
        self.details = details
        self.status_code = status_code


class Auth:
    def __init__(self):
        self.states = []

    def add(self) -> str:
        state = uuid.uuid4().hex
        log.debug(f"Create state ({state})")
        self.states.append({
            "expire": time.time() + 3600,
            "state": state
        })
        return state

    def validade(self, state) -> None:
        for index, entry in enumerate(self.states):
            if entry['state'] == state:
                if entry['expire'] > time.time():
                    self.states.pop(index)
                    log.debug(f"State {state} is valid")
                    return
        raise AuthError(
            "Invalid state",
            "Please repeat the authentication",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def remove_expired_states(self) -> None:
        for index, entry in enumerate(self.states):
            if entry['expire'] < time.time():
                self.states.pop(index)
                log.debug(f"Expired state ({entry['state']}) removed")
