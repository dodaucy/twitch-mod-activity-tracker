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
        "Create a random string and store it in a list"

        state = uuid.uuid4().hex
        log.debug(f"Create state: {state}")
        self.states.append({
            "expire": time.time() + 3600,  # TODO: configurable
            "state": state
        })
        return state

    def validade(self, state: str) -> None:
        "Checks whether the specified string is valid"

        for entry in list(self.states):
            if entry['state'] == state:
                if entry['expire'] > time.time():
                    self.states.remove(entry)
                    log.debug(f"State is valid: {state}")
                    return
        log.debug(f"State {state} invalid")
        raise AuthError(
            "Invalid state",
            "Please repeat the authentication",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def remove_expired_states(self) -> None:
        "Removes all invalid data"

        for entry in list(self.states):
            if entry['expire'] < time.time():
                self.states.remove(entry)
                log.debug(f"Expired state removed: {entry['state']}")
