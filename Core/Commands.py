from discord.ext import commands
import discord
from Core.Logger import Logger

class Commands(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Basic commands loaded!")
        self.bot:commands.Bot = bot
        self.LoadAllCogs()

    def LoadAllCogs(self):
        Cogs = [
            "Core.Cogs.SKWiki",
            "Core.Cogs.Misc",
            "Core.Cogs.Admin"
        ]
        for cog in Cogs:
            try:
                self.bot.load_extension(cog)
            except Exception as err:
                Logger.Log(err, Logger.ERROR)

    @commands.command(pass_context=True)
    async def test(self, ctx):
        await ctx.send("hi")