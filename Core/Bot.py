import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os
import time

from Core.Logger import Logger
from Core.Commands import Commands
from Core.Mechanics.Level import Level
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

    async def on_member_join(self, member: discord.Member):
        '''
            Creates an user entry in the database whenever a member joins the server
        '''
        user: discord.User = await self.get_user(member.id)
        if not user.bot:
            # Inserts the user into Heeto's database
            # Since ID is a primary key it will just raise an error when trying to insert it if it's already in the db
            self.Database.AddToTable(
                    "Users",
                    ID = int(user.id),
                    Credits = 500,
                    Level = 1,
                    Experience = 0,
                    last_day_streak = datetime.now().strftime("%d/%m/%Y"),
                    streak = 0,
                    last_message_epoch = int(time.time())
                )

    async def on_guild_join(self, guild: discord.Guild):
        '''
            Creates a guild config to the database whenever Heeto joins a server
        '''
        Logger.Log(f"Joined new server: {guild.name} [{guild.id}]\nCreating Database entry...")
        self.Database.AddToTable(
            "Guilds",
            ID = int(guild.id),
            OwnerID = int(guild.owner_id),
            EnabledCommands = (True, True)
        )
        for user in guild.members:
            # For each member in the server, creates an entry in Heeto's database
            if not user.bot:
                self.Database.AddToTable(
                    "Users",
                    ID = int(user.id),
                    Credits = 500,
                    Level = 1,
                    Experience = 0,
                    last_day_streak = datetime.now().strftime("%d/%m/%Y"),
                    streak = 0,
                    last_message_epoch = int(time.time())
                )

    async def on_ready(self):
        Logger.Log(f"{self.user.name} is now connected to Discord!")
        #Sets bot activity
        Activity = discord.Game(name=self.statusMessage, start=datetime.now())
        await self.change_presence(status=discord.Status.online, activity=Activity)

    async def on_message(self, message: discord.Message):
        # Ignore other bot messages
        if (message.author.bot):
            return

        if (type(message.channel) not in [discord.ChannelType.private, discord.ChannelType.group]):
            if Level.CheckIfExpOnCooldown(self.Database, message.author.id, message):
                newLevel = self.Database.GetFromTable("Users", f"ID = {message.author.id}")[0][2]
                await message.channel.send(f"Congratulations {message.author.mention}! you are now **level {newLevel}**!")


        # Process command
        await self.process_commands(message)
    
