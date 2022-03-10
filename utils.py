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

from config import data_path, language


def get_actions(mod_format: bool = False) -> dict:
    actions = {}
    with shelve.open(os.path.join(data_path, "actions")) as db:
        for action in db.keys():
            if mod_format:
                for mod in db[action]:
                    if mod not in actions:
                        actions[mod] = {}
                    actions[mod][action] = db[action][mod]
            else:
                actions[action] = db[action]
    return actions


def put_actions(actions: dict) -> None:
    with shelve.open(os.path.join(data_path, "actions")) as db:
        for key in actions:
            db[key] = actions[key]


def get_command(command_display_name) -> str:
    for command in language.commands:
        if language.commands[command].display_name == command_display_name:
            return command


def get_action(action_display_name) -> str:
    for action in language.actions:
        if language.actions[action] == action_display_name:
            return action


def command_help(command) -> str:
    description = f"**/{language.commands[command].display_name}**"
    if "arguments" in language.commands[command]:
        description += " "
        for argument in language.commands[command].arguments:
            if language.commands[command].arguments[argument].marked_as_optional:
                description += f"**[** `{language.commands[command].arguments[argument].display_name}` **]**"
            else:
                description += f"**<** `{language.commands[command].arguments[argument].display_name}` **>**"
    return description
