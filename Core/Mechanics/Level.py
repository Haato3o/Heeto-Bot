'''
    This will handle all level and experience stuff
'''
from dotenv import load_dotenv
import os
import time
import discord
from discord.ext import commands
from random import randint
import asyncio

from Libs.Database import Database
from Core.Logger import Logger

# Load .env
load_dotenv(".env")

class Level(commands.Cog):
    Experience_Cooldown = 60
    CalculateLevelFormula = lambda level: 100 + 100 * level / 5 + (100 * (level / 100))

    def __init__(self, bot):
        self.Bot = bot
        self.Database = Database(
            username = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            host = os.getenv("DATABASE_HOST"),
            port = os.getenv("DATABASE_PORT"),
            db_name = os.getenv("DATABASE_NAME")
        )
        self.Database.connect()
        Logger.Log("Loaded Level mechanics!")
    
    @staticmethod
    def IncreaseUserLevel(Database: Database, user: tuple, context: discord.Message):
        currentLevel = user[2]
        newLevel = int(currentLevel) + 1
        query = f'''
            UPDATE Users SET Level = {newLevel},
                             Experience = 0 
                         WHERE (ID = {user[0]});
        '''
        return Database.CommitCommand(query)
            

    @staticmethod
    def IncreaseUserExp(Database: Database, user: tuple, context: discord.Message):
        exp = randint(3, 9)
        newExp = user[3] + exp
        query = f'''
            UPDATE Users SET experience = {newExp}, 
                             last_message_epoch = {int(time.time())} 
                         WHERE (ID = {user[0]});
        '''
        if Database.CommitCommand(query):
            Logger.Log(f"{context.author.name} got {exp} EXP")
            # Checks if user leveled up
            if (newExp) >= Level.CalculateLevelFormula(user[2]):
                return Level.IncreaseUserLevel(Database, user, context)
            else:
                return False

    @staticmethod
    def CheckIfExpOnCooldown(Database: Database, user_id: int, context: discord.Message):
        user = Database.GetFromTable("Users", f"(ID = {user_id})")[0]
        userEpoch = user[6]
        if ((int(time.time()) - userEpoch) >= Level.Experience_Cooldown):
            return Level.IncreaseUserExp(Database, user, context)


def setup(bot):
    bot.add_cog(Level(bot))