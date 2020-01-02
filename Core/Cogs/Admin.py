from discord.ext import commands
import discord
from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils
import datetime

class Admin(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Admin loaded!")
        self.bot: commands.Bot = bot
        self.Owners: list = [
            183067754784358400
        ]
        self.AdminCommands = {
            "shutdown**": "Shuts the bot down.",
            "playgame** *<game name>*": "Changes the bot message status.",
            "servers**" : "Returns the name of every server the bot is in.",
            "say** *<channel_id>* *<message>*" : "Sends a message to the target *channel_id*"
        }
    
    def isOwner(self, user_id:int):
        return user_id in self.Owners
        
    @commands.group(pass_context=True, hidden=True)
    async def admin(self, ctx:commands.Context):
        if ctx.invoked_subcommand == None:
            if self.isOwner(ctx.message.author.id):
                helpAdmin = discord.Embed(
                    title = None,
                    description = None,
                    timestamp = datetime.datetime.now(),
                    color = 0x9430ff
                )
                helpAdmin.add_field(
                    name = "**Admin**",
                    value = BotUtils.formatCommandsDict(self.bot.command_prefix, self.AdminCommands)
                )
                await ctx.send(embed=helpAdmin)
            else:
                await ctx.send("Nope.")
        return

    @admin.command(pass_context=True, hidden=True)
    async def shutdown(self, ctx:commands.Context):
        if self.isOwner(ctx.message.author.id):
            await ctx.send("Shutting down...")
            await self.bot.close()

    @admin.command(pass_context=True, hidden=True)
    async def playgame(self, ctx:commands.Context, *, gameName: str):
        if self.isOwner(ctx.message.author.id):
            newGameName = discord.Game(gameName)
            await self.bot.change_presence(
                activity = newGameName
            )
            await ctx.send(f"Changed game to `{gameName}`")
            Logger.Log(f"{ctx.message.author.name} changed bot status message to \"{gameName}\"")

    @admin.command(pass_context=True, hidden=True)
    async def servers(self, ctx:commands.Context):
        if self.isOwner(ctx.message.author.id):
            serversList = []
            for server in self.bot.guilds:
                serversList.append(server.name)
            await ctx.send("```Servers:\n{}```".format("\n".join(serversList)))
    
    @admin.command(pass_context=True, hidden=True)
    async def say(self, ctx:commands.Context, channel_id:str, *, message: str):
        if self.isOwner(ctx.message.author.id):
            try:
                channel_id = int(channel_id)
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                await ctx.send(f"`{channel_id}` is not a valid channel!")
            targetChannel = self.bot.get_channel(channel_id)
            try:
                await targetChannel.send(message)
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                await ctx.send(f"Failed to send a message to `{channel_id}`")


def setup(bot):
    bot.add_cog(Admin(bot))