# Made with <3 by Haato :)
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
from Libs.utils.bot_utils import BotUtils
load_dotenv(".env")

class Bot(commands.Bot):
    def __init__(self, prefix: str, status_message: str):
        super().__init__(command_prefix=prefix)
        self.remove_command("help")
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
        user: discord.User = self.get_user(member.id)
        if not user.bot:
            # Inserts the user into Heeto's database
            # Since ID is a primary key it will just raise an error when trying to insert it if it's already in the db
            self.AddUserToDatabase(user, member.guild)

    async def on_member_remove(self, member: discord.Member):
        user: discord.User = self.get_user(member.id)
        if not user.bot:
            query = f"UPDATE Users SET Servers = array_remove(Servers, {member.guild.id}) WHERE ID = {user.id};"
            if self.Database.CommitCommand(query):
                Logger.Log(f"Updated user: {user.name}")

    def AddUserToDatabase(self, user, guild):
        addUserToDatabase = self.Database.AddToTable(
                    "Users",
                    ID = int(user.id),
                    Name = user.name,
                    Servers = [guild.id],
                    Credits = 500,
                    Level = 1,
                    Experience = 0,
                    last_day_streak = datetime(1990, 1, 1).strftime("%m/%d/%Y"),
                    streak = 0,
                    last_message_epoch = int(time.time()),
                    description = "You can change your user card [here](http://heeto.herokuapp.com)",
                    cardColor = "#FFFFFF",
                    discriminator = user.discriminator,
                    avatar = str(user.avatar_url).replace("webp?size=1024", "png"),
                    married_to = None,
                    Badges = []
                )
        if not addUserToDatabase:
            # This happens if Heeto fails to add user to database (Usually because user is already in the db).
            # If that happens then just add the Server ID to the user entry
            query = f'''
                UPDATE Users SET Servers = array_append(Servers, {guild.id}) WHERE (ID = {user.id} AND NOT {guild.id} = any(Servers));
            '''
            self.Database.CommitCommand(query)
    
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
                self.AddUserToDatabase(user, guild)

    async def on_ready(self):
        Logger.Log(f"{self.user.name} is now connected to Discord!")
        #Sets bot activity
        Activity = discord.Game(name=self.statusMessage, start=datetime.now())
        await self.change_presence(status=discord.Status.online, activity=Activity)

    async def on_message(self, message: discord.Message):
        # Ignore other bot messages
        if (message.author.bot):
            return

        # If server isnt in the database, then create it
        if BotUtils.isPublicChannel(type(message.channel)) and not self.Database.GetFromTable("Guilds", f"ID = {message.guild.id}"):
            newGuild = self.Database.AddToTable(
                "Guilds",
                ID = message.guild.id,
                OwnerId = message.guild.owner_id,
                EnabledCommands = (True, True)
            )
            if newGuild:
                Logger.Log("Created new guild entry into the database.")

        if BotUtils.isPublicChannel(type(message.channel)) and not self.Database.GetFromTable("Users", f"ID = {message.author.id}"):
            self.AddUserToDatabase(message.author, message.guild)
            Logger.Log("Added user to database")
        
        # On user message, handle exp and level
        if BotUtils.isPublicChannel(type(message.channel)):
            if Level.CheckIfExpOnCooldown(self.Database, message.author.id, message):
                newLevel = self.Database.GetFromTable("Users", f"ID = {message.author.id}")[0][4]
                await message.channel.send(f"Congratulations {message.author.mention}! you are now **level {newLevel}**! <:peepoHappy:617113235828637721>")


        # Process command
        await self.process_commands(message)
    
