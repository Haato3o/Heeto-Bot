from discord.ext import commands
from discord import Client
from Core.Logger import Logger

class SKWiki(commands.Cog):
    def __init__(self, bot):
        Logger.Log("SKWiki loaded!")
        self.bot = bot

    @commands.command(pass_context=True)
    async def check(self, ctx):
        await ctx.send("hello!")

def setup(bot):
    bot.add_cog(SKWiki(bot))