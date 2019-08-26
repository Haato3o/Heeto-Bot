import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
from random import randint
import asyncio

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
        self.Bot: commands.Bot = bot
        Logger.Log("Economy mechanics loaded!")
        self.Database = Database(
            username = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            host = os.getenv("DATABASE_HOST"),
            port = os.getenv("DATABASE_PORT"),
            db_name = os.getenv("DATABASE_NAME")
        )
        self.Database.connect()

    async def createConfirmation(self, message: discord.Message, emojis: list, user: discord.User) -> bool:
        def check(emote, usr):
            if (str(emote.emoji) == "✅" and usr == user):
                return True
            elif (str(emote.emoji) == "❌" and usr == user):
                return True
            else:
                return
        
        for reaction in emojis:
            await message.add_reaction(reaction)
        try:
            emote, usr = await self.Bot.wait_for("reaction_add", timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await message.edit(content = "Time's up!")
            return None
        else:
            if str(emote.emoji) == "✅" and usr.id == user.id:
                return True
            else:
                return False


    @commands.group(pass_context=True)
    async def money(self, ctx: commands.Context):
        if ctx.invoked_subcommand == None:
            await ctx.send("This is a placeholder btw, gonna change this later")

    @money.command(pass_context=True)
    async def send(self, ctx: commands.Context, to_user = None, amount = None):
        try:
            amount = BotUtils.parseMoney(amount)
        except:
            await ctx.send(f"{ctx.author.mention} That's not a valid amount! 🤔")
            return
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} Amount must be over $1")
            return
        if to_user == None:
            ctx.send("You can't send money to no one.")
        to_user = to_user.strip("<!@>")
        try:
            to_user = self.Bot.get_user(int(to_user))
        except:
            await ctx.send(f"{ctx.author.mention} Not a valid user!")
            return
        if to_user.id == ctx.author.id:
            # Blocks people sending themselves money
            await ctx.send(f"{ctx.author.mention} You can't send yourself money!")
            return
        # Get users in the database
        targetQuery = self.Database.GetFromTable("Users", f"id = {to_user.id}")[0]
        userQuery = self.Database.GetFromTable("Users", f"id = {ctx.author.id}")[0]
        targetQueryMoney = BotUtils.parseMoney(targetQuery[3])
        userMoney = BotUtils.parseMoney(userQuery[3])
        if userMoney >= amount:
            confirmation = await ctx.send(f"Do you want to give **{to_user}** **${amount:,.2f}**?")
            conf = await self.createConfirmation(confirmation, ["✅", "❌"], ctx.author)
            if conf:
                userMoney -= amount
                targetQueryMoney += amount
                # Gives target $amount
                queries = [
                    f"UPDATE Users SET credits = {userMoney} WHERE id = {ctx.author.id};",
                    f"UPDATE Users SET credits = {targetQueryMoney} WHERE id = {to_user.id};"
                ]
                for query in queries:
                    self.Database.CommitCommand(query)
                transactionEmbed = discord.Embed(
                    title = f"Transaction {ctx.author} => {to_user}",
                    timestamp = datetime.now(),
                    color = 0xF3BF0C
                )
                # Sender
                transactionEmbed.add_field(
                    name = "**SENDER**",
                    value = f"{ctx.author}",
                    inline = True
                )
                transactionEmbed.add_field(
                    name = "**NEW BALANCE**",
                    value = f"||${userMoney:,.2f}||",
                    inline = True
                )
                transactionEmbed.add_field(
                    name = "**ID**",
                    value = f"{ctx.author.id}",
                    inline = True
                )
                # Receiver
                transactionEmbed.add_field(
                    name = "**RECEIVER**",
                    value = f"{to_user}",
                    inline = True
                )
                transactionEmbed.add_field(
                    name = "**NEW BALANCE**",
                    value = f"||${targetQueryMoney:,.2f}||",
                    inline = True
                )
                transactionEmbed.add_field(
                    name = "**ID**",
                    value = f"{to_user.id}",
                    inline = True
                )
                await ctx.send(embed=transactionEmbed)
            elif conf == False:
                await confirmation.edit(content="Transaction cancelled!")
                return
        else:
            await ctx.send(f"{ctx.author.id} You don't have that much money!")

    @commands.command(pass_context=True)
    async def balance(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        currencyEmbed = discord.Embed(
            title=f"{ctx.author.name}'s balance",
            description=f"**Balance:** {dbQuery[0][3]}",
            color=BotUtils.parseColorFromString(dbQuery[0][10])
            )
        await ctx.send(embed=currencyEmbed)
    
    @commands.command(pass_context=True)
    async def daily(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        lastClaim = (datetime.date(datetime.now()) - dbQuery[0][6])
        streak = dbQuery[0][7]
        userCredits = BotUtils.parseMoney(dbQuery[0][3])
        if lastClaim.days > 0:
            streak = streak if lastClaim.days == 1 else 0
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
                    claimEmbed = discord.Embed(title=ctx.author.name, description=f"You claimed ${dailyCredit}.", color = 0x9430FF)
                    claimEmbed.add_field(name="**New balance**", value=f"${dailyCredit + userCredits}")
                    await ctx.send(embed=claimEmbed)
        else:
            await ctx.send("🚫 You already claimed your daily credits!")

def setup(bot):
    bot.add_cog(Economy(bot))