import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime

from Core.Logger import Logger
from Libs.Database import Database

# Load .env
load_dotenv(".env")

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        Logger.Log("Economy mechanics loaded!")
        self.Database = Database(
            username = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            host = os.getenv("DATABASE_HOST"),
            port = os.getenv("DATABASE_PORT"),
            db_name = os.getenv("DATABASE_NAME")
        )
        self.Database.connect()

    @commands.command(pass_context=True)
    async def daily(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        if (datetime.date(datetime.now()) - dbQuery[0][6]) > 0:
            # TODO finish this
            return

def setup(bot):
    bot.add_cog(Economy(bot))