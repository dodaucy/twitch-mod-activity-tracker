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
from constants import ACTIONS
from cursor import Cursor
from utils import command_help, get_action, get_command


log = logging.getLogger(__name__)

bot = commands.Bot(sync_commands=True)


@bot.event
async def on_ready():
    log.info("Discord bot online")


@bot.slash_command(
    name=language.commands.help.display_name.lower(),
    description=language.commands.help.description
)
async def help(
    inter: disnake.ApplicationCommandInteraction,
    command: Optional[str] = commands.Param(
        None,
        name=language.commands.help.arguments.command.display_name.lower(),
        description=language.commands.help.arguments.command.description,
        choices=[language.commands[command].display_name for command in language.commands]
    )
):
    if command is None:
        embed = disnake.Embed(
            title=language.commands.help.embed.title,
            description="\n".join([f"{command_help(command)}\n{language.commands[command].description}" for command in language.commands]),
            color=config.discord.embed.color.normal
        )
    else:
        command = get_command(command)
        embed = disnake.Embed(
            title=command_help(command),
            description=language.commands[command].description,
            color=config.discord.embed.color.normal
        )
    embed.set_footer(text=language.required_optional_footer)
    await inter.response.send_message(
        embed=embed,
        ephemeral=config.discord.embed.ephemeral
    )


@bot.slash_command(
    name=language.commands.top.display_name.lower(),
    description=language.commands.top.description
)
async def top(
    inter: disnake.ApplicationCommandInteraction
):
    with Cursor() as c:
        c.execute(
            f"SELECT * FROM actions ORDER BY {' + '.join([f'`{action}`' for action in ACTIONS])} DESC LIMIT 5"
        )
        mods = c.fetchall()
    if mods == []:
        embed = disnake.Embed(
            title=language.commands.top.embed.title,
            description=language.no_data,
            color=config.discord.embed.color.error
        )
    else:
        embed = disnake.Embed(
            title=language.commands.top.embed.title,
            color=config.discord.embed.color.normal
        )
        for place, mod in enumerate(mods):
            action_list = []
            for action in sorted(ACTIONS, key=lambda x: mod[x], reverse=True):
                if mod[action] > 0:
                    action_list.append(f"{language.actions.get(action, action)}: **{mod[action]}**")
            embed.add_field(
                name=f"{place + 1}. {mod['display_name']} | `{sum([mod[action] for action in ACTIONS])}`",
                value="\n".join(action_list),
                inline=False
            )
    await inter.response.send_message(
        embed=embed,
        ephemeral=config.discord.embed.ephemeral
    )


@bot.slash_command(
    name=language.commands.list.display_name.lower(),
    description=language.commands.list.description
)
async def list(
    inter: disnake.ApplicationCommandInteraction,
    action: Optional[str] = commands.Param(
        None,
        name=language.commands.list.arguments.action.display_name.lower(),
        description=language.commands.list.arguments.action.description,
        choices=[language.actions[action] for action in language.actions]
    )
):
    mod_list = []
    if action is None:
        total_actions = 0
        mods = get_actions(True)
        if mods == {}:
            embed = disnake.Embed(
                title=language.commands.top.embed.title,
                description=language.no_data,
                color=config.discord.embed.color.error
            )
        else:
            # Sorts all moderators by most actions
            for place, (mod, actions) in enumerate(sorted(mods.items(), key=lambda x: sum(x[1].values()), reverse=True)):
                for action in actions:
                    total_actions += actions[action]
                if place >= 50:
                    continue
                mod_list.append(f"**{place + 1}.** `{mod}`: {sum(actions.values())}")
            description = "\n".join(mod_list)
            embed = disnake.Embed(
                title=language.commands.list.embed.title,
                description=f"{language.commands.list.embed.total.format(total=total_actions)}\n\n{description}",
                color=config.discord.embed.color.normal
            )
    else:
        total_count = 0
        original_action = get_action(action)
        actions = get_actions()
        if original_action in actions:
            # Sorts all moderators by most actions
            for place, (mod, count) in enumerate(sorted(actions[original_action].items(), key=lambda x: x[1], reverse=True)):
                total_count += count
                if place >= 50:
                    continue
                mod_list.append(f"**{place + 1}.** `{mod}`: {count}")
            description = "\n".join(mod_list)
            embed = disnake.Embed(
                title=language.commands.list.embed.specialized.title.format(total=total_count, action=action),
                description=f"{language.commands.list.embed.specialized.total.format(total=total_count, action=action)}\n\n{description}",
                color=config.discord.embed.color.normal
            )
        else:
            embed = disnake.Embed(
                title=language.commands.list.embed.specialized.title.format(action=action),
                description=language.commands.list.embed.specialized.no_action,
                color=config.discord.embed.color.error
            )
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
    moderator = moderator.lower()
    mods = get_actions(True)
    if moderator in mods:
        action_list = []
        total_actions = 0
        for action in sorted(mods[moderator], key=lambda x: mods[moderator][x], reverse=True):
            total_actions += mods[moderator][action]
            action_list.append(f"{language.actions.get(action, action)}: **{mods[moderator][action]}**")
        description = "\n".join(action_list)
        embed = disnake.Embed(
            title=language.commands.stats.embed.title.format(total=total_actions, mod=moderator),
            description=f"{language.commands.stats.embed.total.format(total=total_actions, mod=moderator)}\n\n{description}",
            color=config.discord.embed.color.normal
        )
        await inter.response.send_message(
            embed=embed,
            ephemeral=config.discord.embed.ephemeral
        )
    else:
        embed = disnake.Embed(
            title=language.commands.stats.embed.mod_not_found.title,
            description=language.commands.stats.embed.mod_not_found.description.format(mod=moderator),
            color=config.discord.embed.color.error
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
