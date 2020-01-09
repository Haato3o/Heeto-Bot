from discord.ext import commands
from discord.ext.commands import core
import discord
import os

from Libs.Steppin import Steppin
from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils

class Images(commands.Cog):
    name = "images"
    description = '''This group has all images manipulation related commands.'''
    color = 0x42BFF5

    def __init__(self, Bot):
        Logger.Log("Images loaded!")
        self.Bot: commands.Bot = Bot

    @commands.command(pass_context=True)
    async def steppin(self, ctx: commands.Context, user: str = None):
        # TODO: Support default discord profile pic
        if (user == None):
            # Uses the profile picture of the user who called the command
            user: discord.User = ctx.author
        else:
            try:
                user: discord.User = await commands.MemberConverter().convert(ctx, user)
            except:
                await ctx.send(f"{user} not found!")
                return
        ImageUrl = BotUtils.parseUserProfileToPNG(user.id, user.avatar)
        DownloadedImagePath = BotUtils.DownloadImage(ImageUrl, os.path.join(os.path.abspath("temp"), f"{user.avatar}.png"))
        if (DownloadedImagePath != None):
            SteppinImage = Steppin(DownloadedImagePath)
            outputPath = SteppinImage.ManipulateImage()
            await ctx.send(file=discord.File(outputPath, filename=f"steppin.png"))

def setup(bot):
    bot.add_cog(Images(bot))