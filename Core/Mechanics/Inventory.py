import discord
from discord.ext import commands

from Libs.Database import Database
from Core.Logger import Logger

class Inventory(commands.Cog):
    name = "inventory"
    description = '''This group has all inventory related commands.'''
    color = 0xBDECD3

    def __init__(self, Bot):
        self.Bot: commands.Bot = Bot

    @commands.command(pass_context=True)
    async def inventory(self, ctx: commands.Context):
        return


def setup(bot):
    bot.add_cog(Inventory(bot))