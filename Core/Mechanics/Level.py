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
    name = "level"
    description = '''
        The level group contains all commands related to the levelling and experience systems.
    '''
    color = "#6DF96D"
    Experience_Cooldown = 30
    ExpMultiplier = 2
    CalculateLevelFormula = lambda level: int((100 + (100 * level) * (level / 100)))

    def __init__(self, bot):
        self.Bot:commands.Bot = bot
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
            "level <user>**" : "Shows <user> level and experience.",
            "level ranking <global or server>**" : "Shows the people with highest level in server or globally. (Default is server)"
        }
    
    @commands.group(pass_context=True, help="<@user>*", usage="level @Haato#0704", description="Shows <user> user card. It'll show your own card if user is not specified.", aliases=["profile"])
    async def level(self, ctx: commands.Context):
        if ctx.invoked_subcommand == None:
            user: discord.User = ctx.message.mentions[0] if len(ctx.message.mentions) > 0 else ctx.author
            userQuery = self.Database.GetFromTable(
                "Users",
                f"ID = {user.id}"
            )
            
            userDescription = userQuery[0][9]
            userColor = BotUtils.parseColorFromString(userQuery[0][10])
            userLevelEmbed = discord.Embed(
                title = f"{user.name}",
                description = userDescription,
                color = userColor
            )
            userLevelEmbed.add_field(
                name = "**BADGES**",
                value = ' '.join(userQuery[0][14]) if userQuery[0][14] else "This user has no badges.",
                inline = False
            )
            userLevelEmbed.add_field(
                name = "**LEVEL**",
                value = userQuery[0][4],
                inline = True
            )
            userLevelEmbed.add_field(
                name = "**EXPERIENCE**",
                value = f"{userQuery[0][5]}/{Level.CalculateLevelFormula(userQuery[0][4])}",
                inline = True
            )
            userLevelEmbed.add_field(
                name = "**MARRIED TO**",
                value = "No one." if userQuery[0][13] == None else self.Bot.get_user(userQuery[0][13])
            )
            userLevelEmbed.set_thumbnail(
                url = BotUtils.parseUserProfilePicture(user.is_avatar_animated(), user.id, user.avatar)
            )
            await ctx.send(embed=userLevelEmbed)

    @level.command(pass_context=True, help="<description>", usage="profile description Hello world!", description="Changes your user card description")
    async def description(self, ctx: commands.Context, *, description: str):
        if (description == "" or description == None):
            await ctx.send("User description cannot be empty <:peepoMad:617113238328442958>")
            return
        if (self.Database.UpdateUserDescription(ctx.author.id, description)):
            await ctx.send("User description updated! <:peepoHappy:617113235828637721>")
        else:
            await ctx.send("Whoops! Something went wrong and I couldn't update your description <:peepoCrying:617447775147261952>")

    @level.command(pass_context=True, help="<color>", usage="profile level #FFFFFF", description="Changes user card color (supports HEX and RGB)")
    async def color(self, ctx: commands.Context, *, color: str):
        if (color == "" or color == None):
            await ctx.send("Color can't be empty <:peepoMad:617113238328442958>")
            return
        if (color.startswith("(") or color.lower().startswith("rgb(")):
            try:
                color = BotUtils.parseColorFromRGB(color)
            except Exception as err:
                Logger.Log(err)
                await ctx.send("Failed to parse RGB to hex, are you sure that's a valid color?")
        if (color.startswith("#") and len(color) >= 7):
            color = color[0:7]
            Logger.Log(color)
            if (self.Database.UpdateUserColor(ctx.author.id, color)):
                colorEmbed = discord.Embed(
                    title = f"Updated {ctx.author.name} color",
                    description = f"New color: {color}",
                    color = BotUtils.parseColorFromString(color)
                )
                await ctx.send(embed=colorEmbed)
            else:
                await ctx.send("Failed to update your profile color <:peepoCrying:617447775147261952>")

    @level.command(pass_context=True, help="<global or server>*", usage="level ranking global", description="Shows the people with highest level in server or globally.")
    async def ranking(self, ctx: commands.Context, rankingType: str = "server"):
        if rankingType not in ["server", "global"]:
            rankingType = "server"
        if rankingType == "server":
            ranking = self.Database.GetFromTable("Users", f"({ctx.guild.id} = ANY(Servers)) order by Level")
        elif rankingType == "global":
            ranking = self.Database.GetFromTable("Users", "(TRUE) order by Level")
        ranking: list = ranking[::-1] # Reverse array
        ranking_title = f"Ranking for {ctx.guild.name}" if rankingType == "server" else "Global ranking"
        rankingEmbed = discord.Embed(
            title = ranking_title,
            description = "\n".join([f"{ranking.index(user) + 1}° - **{user[1]}**: Level {user[4]}" for user in ranking[0: 20]]),
            color = 0x9430FF
        )
        await ctx.send(embed=rankingEmbed)

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
        exp = randint(3, 9) * Level.ExpMultiplier
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