import os
import time
import shelve

from config import data_path


class Supervisor:
    def __init__(self):
        mods_path = os.listdir(os.path.join(
            data_path,
            "mods"
        ))
        for mod_path in mods_path:
            with shelve.open(os.path.join(
                data_path,
                "mods",
                mod_path
            )) as db:
                token = db['token']
                refresh_token = db['refresh_token']
                expires = db['expires']
            self.refresh(token, refresh_token, expires, mod_path)

    def refresh(self, token, refresh_token, expires, mod_id) -> None:
        print(f"Refresh token from {mod_id}...")
        if expires > time.time():
            print("Token invalid")
            os.remove(os.path.join(
                data_path,
                "mods",
                mod_id
            ))
            return
        if time.time() - expires < 1800:
            print(f"Token expires in {time.time() - expires} seconds. Refresh...")
            ...
        else:
            print("Token valid")
