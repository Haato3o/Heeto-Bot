from discord.ext import commands
import discord
from Core.Logger import Logger

class Admin(commands.Cog):
    def __init__(self, bot):
        Logger.Log("Admin loaded!")
        self.bot: commands.Bot = bot
        self.Owners: list = [
            183067754784358400,
            204361296114614272
        ]
    
    def isOwner(self, user_id):
        return user_id in self.Owners
    
    @commands.group(pass_context=True, hidden=True)
    async def admin(self, ctx):
        if ctx.invoked_subcommand == None:
            if self.isOwner(ctx.message.author.id):
                await ctx.send("```Admin subcommands:\nshutdown\nplaygame <game name>\nversion\nsay <channel> <msg>\ninfo\ncuv <day> <month>```")
            else:
                await ctx.send("Nope.")
        return

    @admin.command(pass_context=True, hidden=True)
    async def shutdown(self, ctx):
        if self.isOwner(ctx.message.author.id):
            await ctx.send("Shutting down...")
            await self.bot.close()

    @admin.command(pass_context=True, hidden=True)
    async def playgame(self, ctx, *, gameName: str):
        if self.isOwner(ctx.message.author.id):
            newGameName = discord.Game(gameName)
            await self.bot.change_presence(
                activity = newGameName
            )
            await ctx.send(f"Changed game to `{gameName}`")
            Logger.Log(f"{ctx.message.author.name} changed bot status message to \"{gameName}\"")

def setup(bot):
    bot.add_cog(Admin(bot))