from discord.ext import commands
from discord.ext.commands import core
import discord
from Core.Logger import Logger

class Commands(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Basic commands loaded!")
        self.bot:commands.Bot = bot
        self.LoadAllCogs()
        

    @commands.command(pass_context=True)
    async def help(self, ctx: commands.Context, *cogs):
        # cog:core.Group = self.bot.cogs['Level'].get_commands()[0]
        availableGroups = list(self.bot.cogs.keys())
        availableGroups.remove("Admin")
        if len(cogs) == 0:
            help_embed = discord.Embed(
                title = "Help",
                description = '''
                    You can check all commands available [here](http://heetobot.com/commands).
                    Type help <group> to read more about an specific command group.
                    ''',
                color = 0x9430FF
            )
            help_embed.add_field(
                name = "**Available command groups:**",
                value = ", ".join(availableGroups)
            )
            help_embed.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=help_embed)

    def LoadAllCogs(self):
        Cogs = [
            "Core.Mechanics.Level",
            "Core.Mechanics.Economy",
            "Core.Mechanics.Family",
            "Core.Cogs.Admin",
            "Core.Cogs.SKWiki",
            "Core.Cogs.Misc",
            "Core.Cogs.Tera"
        ]
        for cog in Cogs:
            try:
                self.bot.load_extension(cog)
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
