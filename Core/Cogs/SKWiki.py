from discord.ext import commands
import discord
from Core.Logger import Logger

class SKWiki(commands.Cog):
    def __init__(self, bot):
        Logger.Log("SKWiki loaded!")
        self.bot:commands.Bot = bot

    @commands.command(pass_context=True)
    async def check(self, ctx):
        await ctx.send("hello!")

def setup(bot):
    bot.add_cog(SKWiki(bot))