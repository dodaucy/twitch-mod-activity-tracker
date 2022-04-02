##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import logging
import time

import requests
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from auth import Auth, AuthError
from cursor import Cursor
from config import config
from constants import SCOPE, USER_AGENT
from utils import join_args, raise_on_error


log = logging.getLogger(__name__)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

session = requests.Session()
session.headers = {"User-Agent": USER_AGENT}

authentication = Auth()

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    log.info("API online")


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
    return RedirectResponse(join_args(
        "https://id.twitch.tv/oauth2/authorize",  # TODO: in constants.py
        client_id=config.twitch.client_id,
        redirect_uri=config.twitch.redirect_uri,
        response_type="code",
        scope=SCOPE,
        state=authentication.add()
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
    log.debug(f"Verify a mod ({state})...")
    r = session.post(
        "https://id.twitch.tv/oauth2/token",  # TODO: in constants.py
        params={
            "client_id": config.twitch.client_id,
            "client_secret": config.twitch.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.twitch.redirect_uri
        }
    )
    j = raise_on_error(r)
    token = j['access_token']
    refresh_token = j['refresh_token']
    r = session.get(
        "https://id.twitch.tv/oauth2/validate",  # TODO: in constants.py
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    log.debug(f"HTTP response: '{r.request.url}': {r.text.strip()}")
    j = raise_on_error(r)
    with Cursor() as c:
        c.execute(
            """
            INSERT INTO mods
            (
                id,
                token,
                refresh_token,
                expires
            )
            VALUES
            (
                %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE token = %s, refresh_token = %s, expires = %s;
            """,
            (
                j['user_id'],
                token,
                refresh_token,
                time.time() + j['expires_in'],
                token,
                refresh_token,
                time.time() + j['expires_in']
            )
        )
    log.info(f"Verified {j['login']} ({j['user_id']} / {state})")
    return templates.TemplateResponse(
        "successful.html",
        {
            "request": request,
            "login": j['login']
        }
    )
