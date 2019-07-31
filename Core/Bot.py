import discord
from discord.ext import commands
import asyncio
from Core.Logger import Logger
from Core.Commands import Commands
from datetime import datetime

class Bot(commands.Bot):
    def __init__(self, prefix: str, status_message: str):
        super().__init__(command_prefix=prefix)
        self.add_cog(Commands(self))
        self.statusMessage = status_message

    async def on_ready(self):
        Logger.Log(f"{self.user.name} is now connected to Discord!")
        #Sets bot activity
        Activity = discord.Game(name=self.statusMessage, start=datetime.now())
        await self.change_presence(status=Status.online, activity=Activity)

    async def on_message(self, message: discord.Message):
        # Ignore other bot messages
        if (message.author.bot):
            return
