'''
    This will handle all level and experience stuff
'''
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import discord
from discord.ext import commands
from random import randint
import asyncio

from Libs.Database import Database
from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils

# Load .env
load_dotenv(".env")

class Level(commands.Cog):
    Experience_Cooldown = 60
    CalculateLevelFormula = lambda level: int((100 + (100 * level) * (level / 100)))

    def __init__(self, bot):
        self.Bot = bot
        Logger.Log("Loaded Level mechanics!")
        self.Database = Database(
            username = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            host = os.getenv("DATABASE_HOST"),
            port = os.getenv("DATABASE_PORT"),
            db_name = os.getenv("DATABASE_NAME")
        )
        self.Database.connect()
        self.LevelCommands = {
            "level**" : "Shows user level and experience.",
            "level ranking**" : "Shows the people with highest level globally."
        }
    
    @commands.group(pass_context=True)
    async def level(self, ctx: commands.Context):
        # TODO: Change this command so you can query for other people's level too
        if ctx.invoked_subcommand == None:
            userQuery = self.Database.GetFromTable(
                "Users",
                f"ID = {ctx.author.id}"
            )
            userDescription = userQuery[9]
            userColor = userQuery[10].strip('#')
            userLevelEmbed = discord.Embed(
                title = f"{ctx.author.name}",
                description = userDescription,
                color = int(userColor, 16)
            )
            userLevelEmbed.add_field(
                name = "**LEVEL**",
                value = userQuery[0][4]
            )
            userLevelEmbed.add_field(
                name = "**EXPERIENCE**",
                value = f"{userQuery[0][5]}/{Level.CalculateLevelFormula(userQuery[0][4])}"
            )
            userLevelEmbed.set_thumbnail(
                url = ctx.author.avatar_url
            )
            await ctx.send(embed=userLevelEmbed)

    @level.command(pass_context=True)
    async def ranking(self, ctx: commands.Context, rankingType: str = "server"):
        if rankingType not in ["server", "global"]:
            rankingType = "server"
        if rankingType == "server":
            ranking = self.Database.GetFromTable("Users", f"({ctx.guild.id} = ANY(Servers)) order by Credits")
        elif rankingType == "global":
            ranking = self.Database.GetFromTable("Users", "(TRUE) order by Credits")
        ranking: list = ranking[::-1] # Reverse array
        ranking_title = f"Ranking for {ctx.guild.name}" if rankingType == "server" else "Global ranking"
        rankingEmbed = discord.Embed(
            title = ranking_title,
            description = "\n".join([f"{ranking.index(user) + 1}° - **{user[1]}**: Level {user[4]}" for user in ranking]),
            color = 0x9430FF
        )
        await ctx.send(embed=rankingEmbed)

    @level.command(pass_context=True)
    async def help(self, ctx: commands.Context):
        helpText = BotUtils.formatCommandsDict(self.Bot.command_prefix, self.LevelCommands)
        levelHelp = discord.Embed(
            title = None,
            description = None,
            timestamp = datetime.now(),
            color = 0x9430FF
        )
        levelHelp.add_field(
            name = "**Level subcommands**",
            value = helpText
        )
        await ctx.send(embed=levelHelp)

    @staticmethod
    def IncreaseUserLevel(Database: Database, user: tuple, context: discord.Message):
        currentLevel = user[4]
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
        newExp = user[5] + exp
        query = f'''
            UPDATE Users SET experience = {newExp}, 
                             last_message_epoch = {int(time.time())} 
                         WHERE (ID = {user[0]});
        '''
        if Database.CommitCommand(query):
            Logger.Log(f"{context.author.name} got {exp} EXP")
            # Checks if user leveled up
            if (newExp) >= Level.CalculateLevelFormula(user[4]):
                return Level.IncreaseUserLevel(Database, user, context)
            else:
                return False

    @staticmethod
    def CheckIfExpOnCooldown(Database: Database, user_id: int, context: discord.Message):
        user = Database.GetFromTable("Users", f"(ID = {user_id})")[0]
        userEpoch = user[8]
        if ((int(time.time()) - userEpoch) >= Level.Experience_Cooldown):
            return Level.IncreaseUserExp(Database, user, context)


def setup(bot):
    bot.add_cog(Level(bot))