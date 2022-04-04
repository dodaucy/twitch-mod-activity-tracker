##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


SCOPE = "channel:moderate"  # https://dev.twitch.tv/docs/pubsub#available-topics

PUBSUB = "wss://pubsub-edge.twitch.tv"

USER_AGENT = "Twitch Mod Activity Tracker"

# TODO: Check length
# All stored functions or classes are executed
LANGUAGE_STRUCTURE = {
    "no_data": str,
    "required_optional_footer": str,
    "commands": {
        "help": {
            "display_name": (str, str.lower),
            "description": str,
            "arguments": {
                "command": {
                    "display_name": (str, str.lower),
                    "description": str
                }
            },
            "embed": {
                "title": str
            }
        },
        "top": {
            "display_name": (str, str.lower),
            "description": str,
            "embed": {
                "title": str
            }
        },
        "list": {
            "display_name": (str, str.lower),
            "description": str,
            "arguments": {
                "action": {
                    "display_name": (str, str.lower),
                    "description": str
                }
            },
            "embed": {
                "title": str,
                "total": str,
                "specialized": {
                    "title": str,
                    "total": str,
                    "no_action": str
                }
            }
        },
        "stats": {
            "display_name": (str, str.lower),
            "description": str,
            "arguments": {
                "moderator": {
                    "display_name": (str, str.lower),
                    "description": str
                }
            },
            "embed": {
                "title": str,
                "total": str,
                "mod_not_found": {
                    "title": str,
                    "description": str
                }
            }
        },
        "about": {
            "display_name": str,
            "description": str
        }
    },
    "actions": {
        "clear": str,
        "delete": str,
        "timeout": str,
        "untimeout": str,
        "ban": str,
        "slow": str,
        "unban": str,
        "slowoff": str,
        "emoteonly": str,
        "emoteonlyoff": str,
        "followers": str,
        "followersoff": str,
        "subscribers": str,
        "subscribersoff": str,
        "r9kbeta": str,
        "r9kbetaoff": str
    }
}

# Arguments which are shown as required
ARGUMENTS_REQUIRED = {
    "help": {
        "command": False
    },
    "list": {
        "action": False
    },
    "stats": {
        "moderator": True
    }
}
