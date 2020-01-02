from discord.ext import commands
import discord
from Core.Logger import Logger

class Server(commands.Cog):
    def __init__(self, bot):
        self.Bot: commands.Bot = bot
        self.Database = Database(
            username = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            host = os.getenv("DATABASE_HOST"),
            port = os.getenv("DATABASE_PORT"),
            db_name = os.getenv("DATABASE_NAME")
        )
        self.Database.connect()

    @commands.group(pass_context=True)
    async def server(self, ctx: commands.Context):
        if not (ctx.author.id == ctx.guild.owner_id):
            return
        
    @server.command(pass_context=True)
    async def prefix(self, ctx: commands.Context, prefix: str):
        # TODO: Stop lazy and finish this
        pass
    