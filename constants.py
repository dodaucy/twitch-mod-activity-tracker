##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


GQL = "https://gql.twitch.tv/gql"

REQUEST_BODY = {
    "extensions": {
        "persistedQuery": {
            "sha256Hash": "ce67ed3b519c6452da82a42f27d9874a22d9c60d140209fc14698778fd6b1769",
            "version": 1
        },
        "operationName": "ModActionsCtx_GetModerationActions"
    },
    "variables": {
        "first": 200,
        "order": "DESC"
    }
}

IGNORE_CHANNELS = [
    "twitch"
]

IGNORE_ACTIONS = [
    "MOD_USER",
    "UNMOD_USER",
    "VIP_USER",
    "UNVIP_USER",
    "RAID",
    "HOST"
]
