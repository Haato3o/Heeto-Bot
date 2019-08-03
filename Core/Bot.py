import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os

from Core.Logger import Logger
from Core.Commands import Commands
from Libs.Database import Database
load_dotenv(".env")

class Bot(commands.Bot):
    def __init__(self, prefix: str, status_message: str):
        super().__init__(command_prefix=prefix)
        self.add_cog(Commands(self))
        self.statusMessage = status_message
        self.Database = Database(
            username = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            host = os.getenv("DATABASE_HOST"),
            port = os.getenv("DATABASE_PORT"),
            db_name = os.getenv("DATABASE_NAME")
        )
        self.Database.connect()

    async def on_ready(self):
        Logger.Log(f"{self.user.name} is now connected to Discord!")
        #Sets bot activity
        Activity = discord.Game(name=self.statusMessage, start=datetime.now())
        await self.change_presence(status=discord.Status.online, activity=Activity)

    async def on_message(self, message: discord.Message):
        # Ignore other bot messages
        if (message.author.bot):
            return

        # Process command
        await self.process_commands(message)
    
