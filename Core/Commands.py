from discord.ext import commands
from discord import *
from Core.Logger import Logger

class Commands(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Basic commands loaded!")
        self.bot:commands.Bot = bot
        self.LoadAllCogs()

    def LoadAllCogs(self):
        Cogs = [
            "Core.Cogs.SKWiki"
        ]
        for cog in Cogs:
            try:
                self.bot.load_extension(cog)
            except Exception as err:
                Logger.Log(err, Logger.WARNING)

    @commands.command(pass_context=True)
    async def test(self, ctx):
        await ctx.send("hi")