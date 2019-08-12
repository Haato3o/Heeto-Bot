from discord.ext import commands
import discord
from datetime import datetime

from Core.Logger import Logger
from Core.Libs.utils.bot_utils import BotUtils
import Libs.TeraStatus as TeraStatus

class Tera(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Tera loaded!")
        self.bot: commands.Bot = bot
        self.teraCommands = {
            "terastatus** *<region>*" : "Returns information about server in <region>"
        }

    @commands.command(pass_context=True)
    async def terastatus(self, ctx: commands.Context, region: str = 'na'):
        Status = TeraStatus.Servers.GetTeraStatus(region)
        if len(Status) == 0:
            await ctx.send(f"{ctx.author.mention} Region `{region}` doesn't exist or isn't supported yet!")
            return
        StatusEmbed = discord.Embed(
            title = "Tera status",
            description = "\n".join([f">> {s} is **{Status[s]}**" for s in Status]),
            timestamp = datetime.now(),
            color = 0x9430FF
        )
        await ctx.send(embed=StatusEmbed)

    @commands.group(pass_context=True)
    async def tera(self, ctx: commands.Context):
        if ctx.invoked_subcommand == None:
            teraHelpEmbed = discord.Embed(
                title = "Tera subcommands",
                description = BotUtils.formatCommandsDict(self.teraCommands),
                color = 0x9430FF
            )
            await ctx.send(embed = teraHelpEmbed)

def setup(bot):
    bot.add_cog(Tera(bot))