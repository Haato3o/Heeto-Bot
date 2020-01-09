from discord.ext import commands
from discord.ext.commands import core
import discord

from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils

class Commands(commands.Cog):
    name = "core"
    description = "Contains all core commands."
    color = "#E685E0"

    def __init__(self, bot):
        Logger.Log("Basic commands loaded!")
        self.bot:commands.Bot = bot
        self.LoadAllCogs()

    @commands.command(pass_context=True, help="<command group>", usage="help Level level ranking", description="Shows information about commands and command groups and how to use them.")
    async def help(self, ctx: commands.Context, *cogs):
        prefix = self.bot.command_prefix(self.bot, ctx.message)
        availableGroups = list(self.bot.cogs.keys())
        availableGroups.remove("Admin")
        if len(cogs) == 0:
            help_embed = discord.Embed(
                title = "Help",
                description = f'''You can check all commands available [here](http://heetobot.com/commands).\nType {prefix}help <group> to read more about an specific command group.\n> **Note:** Groups and commands are case-sensitive.''',
                color = 0x9430FF
            )
            for group in availableGroups:
                help_embed.add_field(
                    name = f"**{group}**",
                    value = ", ".join([command.name for command in self.bot.cogs.get(group).get_commands()]),
                    inline = False
                )
            help_embed.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=help_embed)
        else:
            if cogs[0] in availableGroups:
                groupChosen: commands.Cog = self.bot.cogs[cogs[0]]
                availableCommands = groupChosen.get_commands()
                if len(cogs) < 2:
                    groupEmbed = discord.Embed(
                        title = f"{cogs[0]}",
                        description = f"**Description: ** {groupChosen.description}\nType {prefix}help {cogs[0]} <command> to read more about an specific command.",
                        color = BotUtils.parseColorFromString(groupChosen.color)
                    )
                    groupEmbed.set_footer(
                        text = f"http://heetobot.com/commands/{groupChosen.name}",
                        icon_url = self.bot.user.avatar_url
                    )
                    groupEmbed.add_field(
                        name = "**AVAILABLE COMMANDS**",
                        value = ", ".join([commands.name for commands in availableCommands])
                    )
                    await ctx.send(embed=groupEmbed)
                else:
                    if cogs[1] in [commands.name for commands in availableCommands]:
                        commandIndex = [commands.name for commands in availableCommands].index(cogs[1])
                        commandChosen: core.Group = availableCommands[commandIndex]
                        try:
                            hasSubcommands = True
                            subcommands = commandChosen.all_commands
                            if len(cogs) > 2:
                                commandChosen = subcommands.get(cogs[2])
                                hasSubcommands = len(subcommands) == 0
                                if cogs[2] not in subcommands:
                                    await ctx.send("No subcommand has that name <:peepoCrying:617447775147261952>")
                                    return
                        except:
                            hasSubcommands = False
                            commandIndex = [commands.name for commands in availableCommands].index(cogs[1])
                            commandChosen: core.Group = availableCommands[commandIndex]
                        commandEmbed = discord.Embed(
                            title = f"{' > '.join(cogs[0: 3])}",
                            description = f"**Description:** {commandChosen.description}",
                            color = BotUtils.parseColorFromString(groupChosen.color)
                        )
                        commandEmbed.add_field(
                            name = "**Parameters**",
                            value = commandChosen.help
                        )
                        commandEmbed.add_field(
                            name = "**Usage**",
                            value = f"{prefix}{commandChosen.usage}",
                            inline = False
                        )
                        commandEmbed.add_field(
                            name = "**Aliases**",
                            value = ", ".join(commandChosen.aliases) if len(commandChosen.aliases) > 0 else "None"
                        )
                        if hasSubcommands:
                            commandEmbed.add_field(
                                name = "**Subcommands**",
                                value = ", ".join(commandChosen.all_commands),
                                inline = False
                            )
                        await ctx.send(embed=commandEmbed)
                    else:
                        await ctx.send(f"No command called **{cogs[1]}** in {cogs[0]}")
            else:
                await ctx.send(f"No command group called {cogs[0]}")
                return

    def LoadAllCogs(self):
        Cogs = [
            "Core.Mechanics.Level",
            "Core.Mechanics.Economy",
            "Core.Mechanics.Family",
            "Core.Cogs.Admin",
            "Core.Cogs.SKWiki",
            "Core.Cogs.Misc",
            "Core.Cogs.Tera",
            "Core.Cogs.Images"
        ]
        for cog in Cogs:
            self.bot.load_extension(cog)
            try:
                self.bot.load_extension(cog)
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
