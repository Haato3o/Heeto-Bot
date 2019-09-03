from discord.ext import commands
import discord
from datetime import datetime

# Bot stuff
from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils
import Libs.SkWiki as SkWiki

class SKWiki(commands.Cog):
    name = "spiralknights"
    description = '''
        This group has all commands related to the game Spiral Knights.
    '''
    color = "#FF8914"

    def __init__(self, bot):
        Logger.Log("SKWiki loaded!")
        self.bot:commands.Bot = bot
        self.SKHelp = {
            "sk gear** *<name>*" : "Returns info about weapon, armor, helm and shield"
        }

    @commands.group(pass_context=True, help="<subcommand> <params>", usage="sk", description="A group of commands.")
    async def sk(self, ctx: commands.Context):
        if ctx.invoked_subcommand == None:
            helpText = BotUtils.formatCommandsDict(self.bot.command_prefix, self.SKHelp)
            SkHelpEmbed = discord.Embed(
                title = None,
                description = None,
                timestamp = datetime.now(),
                color = 0x9430FF
            )
            SkHelpEmbed.add_field(
                name = "**Spiral Knights subcommands**",
                value = helpText
            )
            await ctx.send(embed=SkHelpEmbed)
    
    @sk.command(pass_context=True, help="<gear_name>", usage="sk gear Chaos Cloak", description="Returns info about gear from Spiral Knights")
    async def gear(self, ctx, *, gearName: str):
        gearQuery = SkWiki.Gear(gearName)
        if gearQuery.Exists():
            GearEmbed = discord.Embed(
                title = f"{gearName.upper()}",
                description = f"{gearQuery.Description()}",
                color = 0x9430FF
            )
            GearEmbed.set_footer(
                text = "Spiral Knights Wiki",
                icon_url = "https://i.imgur.com/ahfOUk6.png"
            )
            GearEmbed.add_field(
                name = "**STARS**",
                value = gearQuery.Tier()
            )
            GearEmbed.add_field(
                name = "**STATS**",
                value = None
            )
            GearEmbed.set_thumbnail(
                url = gearQuery.Image()
            )
            GearEmbed.set_image(
                url = gearQuery.Status()
            )
            await ctx.send(embed = GearEmbed)
        else:
            await ctx.send("I couldn't find that item!\nAre you sure you typed it correctly? :(")

def setup(bot):
    bot.add_cog(SKWiki(bot))