##################################################################
#                                                                #
#                   twitch mod activity tracker                  #
#                                                                #
#                Copyright (C) 2022 X Gamer Guide                #
#  https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker  #
#                                                                #
##################################################################


import logging
from typing import Optional

import disnake
from disnake.ext import commands

from config import config, language
from constants import ARGUMENTS_REQUIRED, LANGUAGE_STRUCTURE
from cursor import Cursor


log = logging.getLogger(__name__)

bot = commands.Bot(sync_commands=True)


@bot.event
async def on_ready():
    log.info("Discord bot online")


@bot.slash_command(
    name=language.commands.help.display_name,
    description=language.commands.help.description
)
async def help(
    inter: disnake.ApplicationCommandInteraction,
    command: Optional[str] = commands.Param(
        None,
        name=language.commands.help.arguments.command.display_name,
        description=language.commands.help.arguments.command.description,
        choices=[language.commands[command].display_name for command in LANGUAGE_STRUCTURE['commands']]
    )
):
    if command is None:
        # Generate help text for all commands
        description = ""
        for command in LANGUAGE_STRUCTURE['commands']:
            if not config.discord.enable_about_command:
                if command == "about":
                    continue
            description += f"\n**/{language.commands[command].display_name}**"
            if "arguments" in LANGUAGE_STRUCTURE['commands'][command]:
                for argument in LANGUAGE_STRUCTURE['commands'][command]['arguments']:
                    if ARGUMENTS_REQUIRED[command][argument]:
                        description += f" **<** `{language.commands[command].arguments[argument].display_name}` **>**"
                    else:
                        description += f" **[** `{language.commands[command].arguments[argument].display_name}` **]**"
            description += f"\n{language.commands[command].description}"
        # Create embed
        embed = disnake.Embed(
            title=language.commands.help.embed.title,
            description=description,
            color=config.discord.embed.color.normal
        )
    else:
        # Get original command name
        for cmd in LANGUAGE_STRUCTURE['commands']:
            if language.commands[cmd].display_name == command:
                break
        # Generate help text for a specific commands
        title = f"**/{language.commands[cmd].display_name}**"
        if "arguments" in LANGUAGE_STRUCTURE['commands'][cmd]:
            for argument in LANGUAGE_STRUCTURE['commands'][cmd]['arguments']:
                if ARGUMENTS_REQUIRED[cmd][argument]:
                    title += f" **<** `{language.commands[cmd].arguments[argument].display_name}` **>**"
                else:
                    title += f" **[** `{language.commands[cmd].arguments[argument].display_name}` **]**"
        # Create embed
        embed = disnake.Embed(
            title=title,
            description=language.commands[cmd].description,
            color=config.discord.embed.color.normal
        )
    embed.set_footer(text=language.required_optional_footer)
    # Send message
    await inter.response.send_message(
        embed=embed,
        ephemeral=config.discord.embed.ephemeral
    )


@bot.slash_command(
    name=language.commands.top.display_name,
    description=language.commands.top.description
)
async def top(
    inter: disnake.ApplicationCommandInteraction
):
    # Get mods
    with Cursor() as c:
        c.execute(
            f"SELECT * FROM actions ORDER BY {' + '.join([f'`{action}`' for action in LANGUAGE_STRUCTURE['actions']])} DESC LIMIT 5"
        )
        mods = c.fetchall()
    if mods == []:
        # No mods found
        embed = disnake.Embed(
            title=language.commands.top.embed.title,
            description=language.no_data,
            color=config.discord.embed.color.error
        )
    else:
        # Create embed
        embed = disnake.Embed(
            title=language.commands.top.embed.title,
            color=config.discord.embed.color.normal
        )
        # Add fields
        for place, mod in enumerate(mods):
            action_list = []
            actions = 0
            # Sort actions
            for action in sorted(LANGUAGE_STRUCTURE['actions'], key=lambda x: mod[x], reverse=True):
                if mod[action] > 0:
                    actions += mod[action]
                    action_list.append(f"{language.actions[action]}: **{mod[action]}**")
            embed.add_field(
                name=f"{place + 1}. {mod['login']} | `{actions}`",
                value="\n".join(action_list),
                inline=False
            )
    # Send message
    await inter.response.send_message(
        embed=embed,
        ephemeral=config.discord.embed.ephemeral
    )


@bot.slash_command(
    name=language.commands.list.display_name,
    description=language.commands.list.description
)
async def list(
    inter: disnake.ApplicationCommandInteraction,
    action: Optional[str] = commands.Param(
        None,
        name=language.commands.list.arguments.action.display_name,
        description=language.commands.list.arguments.action.description,
        choices=[language.actions[action] for action in LANGUAGE_STRUCTURE['actions']]
    )
):
    if action is None:
        # Get mods
        with Cursor() as c:
            c.execute(
                f"SELECT * FROM actions ORDER BY {' + '.join([f'`{action}`' for action in LANGUAGE_STRUCTURE['actions']])} DESC"
            )
            mods = c.fetchall()
        if mods == []:
            # No mods found
            embed = disnake.Embed(
                title=language.commands.top.embed.title,
                description=language.no_data,
                color=config.discord.embed.color.error
            )
        else:
            # List all actions
            mod_list = []
            total_actions = 0
            for place, mod in enumerate(mods):
                actions = 0
                for action in LANGUAGE_STRUCTURE['actions']:
                    total_actions += mod[action]
                    actions += mod[action]
                if place <= 50:
                    mod_list.append(f"**{place + 1}.** `{mod['login']}`: {actions}")
            description = "\n".join(mod_list)
            # Create embed
            embed = disnake.Embed(
                title=language.commands.list.embed.title,
                description=f"{language.commands.list.embed.total.format(total=total_actions)}\n\n{description}",
                color=config.discord.embed.color.normal
            )
    else:
        # Get original action name
        for original_action in LANGUAGE_STRUCTURE['actions']:
            if language.actions[original_action] == action:
                break
        # Get mods
        with Cursor() as c:
            c.execute(
                f"SELECT * FROM actions ORDER BY `{original_action}` DESC"
            )
            mods = c.fetchall()
        # Generate top list
        mod_list = []
        total_count = 0
        for place, mod in enumerate(mods):
            if mod[original_action] == 0:
                break
            total_count += mod[original_action]
            if place <= 50:
                mod_list.append(f"**{place + 1}.** `{mod['login']}`: {mod[original_action]}")
        if mod_list == []:
            # No mods found
            embed = disnake.Embed(
                title=language.commands.list.embed.specialized.title.format(action=action),
                description=language.commands.list.embed.specialized.no_action,
                color=config.discord.embed.color.error
            )
        else:
            description = "\n".join(mod_list)
            embed = disnake.Embed(
                title=language.commands.list.embed.specialized.title.format(total=total_count, action=action),
                description=f"{language.commands.list.embed.specialized.total.format(total=total_count, action=action)}\n\n{description}",
                color=config.discord.embed.color.normal
            )
    # Send message
    await inter.response.send_message(
        embed=embed,
        ephemeral=config.discord.embed.ephemeral
    )


@bot.slash_command(
    name=language.commands.stats.display_name.lower(),
    description=language.commands.stats.description
)
async def stats(
    inter: disnake.ApplicationCommandInteraction,
    moderator: str = commands.Param(
        name=language.commands.stats.arguments.moderator.display_name.lower(),
        description=language.commands.stats.arguments.moderator.description
    )
):
    # Get mod
    with Cursor() as c:
        c.execute(
            "SELECT * FROM actions WHERE mod_id = %s OR login = %s",
            (
                moderator,
                moderator.lower()
            )
        )
        mod = c.fetchone()
    if mod is None:
        # No mod found
        embed = disnake.Embed(
            title=language.commands.stats.embed.mod_not_found.title,
            description=language.commands.stats.embed.mod_not_found.description.format(mod=moderator),
            color=config.discord.embed.color.error
        )
    else:
        action_list = []
        total_actions = 0
        for action in sorted(LANGUAGE_STRUCTURE['actions'], key=lambda x: mod[x], reverse=True):
            if mod[action] == 0:
                break
            total_actions += mod[action]
            action_list.append(f"{language.actions.get(action, action)}: **{mod[action]}**")
        description = "\n".join(action_list)
        embed = disnake.Embed(
            title=language.commands.stats.embed.title.format(total=total_actions, mod=mod['login']),
            description=f"{language.commands.stats.embed.total.format(total=total_actions, mod=mod['login'])}\n\n{description}",
            color=config.discord.embed.color.normal
        )
    await inter.response.send_message(
        embed=embed,
        ephemeral=config.discord.embed.ephemeral
    )


if config.discord.enable_about_command:

    @bot.slash_command(
        name=language.commands.about.display_name.lower(),
        description=language.commands.about.description
    )
    async def about(
        inter: disnake.ApplicationCommandInteraction,
    ):
        embed = disnake.Embed(
            description="Visit on GitHub: https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker",
            color=config.discord.embed.color.normal
        )
        embed.set_author(
            name="Copyright (C) 2022 X Gamer Guide",
            url="https://github.com/X-Gamer-Guide/twitch-mod-activity-tracker"
        )
        await inter.response.send_message(
            embed=embed,
            ephemeral=config.discord.embed.ephemeral
        )
