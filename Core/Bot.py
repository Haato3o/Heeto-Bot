from discord import *
from discord.ext import commands
import asyncio
from Core.Logger import Logger

class Bot(Client):
    async def on_ready(self):
        Logger.Log(f"{self.user.name} is now connected to Discord!")