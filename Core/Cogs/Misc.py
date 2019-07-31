from discord.ext import commands
from Core.Logger import Logger

class Misc(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Miscellaneous loaded!")
        self.bot:commands.Bot = bot
    
    @commands.command(pass_context=True)
    async def echo(self, ctx, *, message: str):
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Misc(bot))
