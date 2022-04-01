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

# ! oudated
# IGNORE_CHANNELS = [
#     "twitch"
# ]

# ! oudated
# IGNORE_ACTIONS = [
#     "MOD_USER",
#     "UNMOD_USER",
#     "VIP_USER",
#     "UNVIP_USER",
#     "RAID",
#     "HOST"
# ]

ACTIONS = [
    "clear",
    "delete",
    "timeout",
    "untimeout",
    "ban",
    "unban",
    "slow",
    "slowoff",
    "emoteonly",
    "emoteonlyoff",
    "followers",
    "followersoff",
    "subscribers",
    "subscribersoff",
    "r9kbeta",
    "r9kbetaoff"
]
