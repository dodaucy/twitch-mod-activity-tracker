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
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from auth import Auth, AuthError
from broadcaster import Broadcaster
from config import config, data_path
from constants import SCOPE, USER_AGENT
from utils import join_args, raise_on_error


app = FastAPI()

authentication = Auth()

broadcaster = Broadcaster(config.twitch.channel)

templates = Jinja2Templates(directory="templates")


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exception: AuthError):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "title": exception.title,
            "details": exception.details
        },
        exception.status_code
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        }
    )


@app.get("/auth")
async def auth():
    state = authentication.add()
    return RedirectResponse(join_args(
        "https://id.twitch.tv/oauth2/authorize",
        client_id=config.twitch.client_id,
        redirect_uri=config.twitch.redirect_uri,
        response_type="code",
        scope=SCOPE,
        state=state
    ))


@app.get("/verify")
async def verify(
    request: Request,
    code: str,
    scope: str,
    state: str
):
    authentication.validade(state)
    if scope != SCOPE:
        raise AuthError(
            "Invalid scope",
            "Please repeat the authentication",
            status.HTTP_400_BAD_REQUEST
        )
    print("Verify a mod...")
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        headers={
            "USer-Agent": USER_AGENT
        },
        params={
            "client_id": config.twitch.client_id,
            "client_secret": config.twitch.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.twitch.redirect_uri
        }
    )
    j = raise_on_error(r)
    token = f"Bearer {j['access_token']}"
    refresh_token = j['refresh_token']
    r = requests.get(
        "https://id.twitch.tv/oauth2/validate",
        headers={
            "Authorization": token
        }
    )
    j = raise_on_error(r)
    with shelve.open(os.path.join(
        data_path,
        "mods",
        j['user_id']
    )) as db:
        db['token'] = token
        db['refresh_token'] = refresh_token
        db['expires'] = j['expires_in']
    broadcaster.mods.append(j['user_id'])
    print(f"Verified {j['login']} ({j['user_id']})")
    return templates.TemplateResponse(
        "successful.html",
        {
            "request": request,
            "login": j['login']
        }
    )
