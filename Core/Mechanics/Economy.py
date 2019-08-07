import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
from random import randint

from Core.Logger import Logger
from Libs.Database import Database
from Libs.utils.bot_utils import BotUtils

# Load .env
load_dotenv(".env")

class Economy(commands.Cog):
    DailyStreak = {
        0 : 250,
        1 : 300,
        2 : 400,
        3 : 500,
        4 : 600,
        5 : 700,
        6 : 1000
    }
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
    async def balance(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        currencyEmbed = discord.Embed(
            title=f"{ctx.author.name}'s balance",
            description=f"**Balance:** {dbQuery[0][3]}",
            color=0x9430FF
            )
        await ctx.send(embed=currencyEmbed)
    
    @commands.command(pass_context=True)
    async def daily(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        lastClaim = (datetime.date(datetime.now()) - dbQuery[0][6])
        streak = dbQuery[0][7]
        userCredits = BotUtils.parseMoney(dbQuery[0][3])
        if lastClaim.days > 0:
            streak = streak if lastClaim == 1 else 0
            if streak < 7:
                dailyCredit = Economy.DailyStreak.get(streak)
                newStreak = streak + 1 if streak <= 5 else 0
                query = f'''
                    UPDATE Users SET Credits = {userCredits + dailyCredit},
                                        last_day_streak = '{BotUtils.GetDate()}',
                                        Streak = {newStreak}
                                WHERE (ID = {ctx.author.id});
                '''
                if self.Database.CommitCommand(query):
                    claimEmbed = discord.Embed(title=ctx.author.name, description=f"You claimed ${dailyCredit}.")
                    claimEmbed.add_field(name="**New balance**", value=f"${dailyCredit + userCredits}")
                    await ctx.send(embed=claimEmbed)
        else:
            await ctx.send("🚫 You already claimed your daily credits!")

def setup(bot):
    bot.add_cog(Economy(bot))