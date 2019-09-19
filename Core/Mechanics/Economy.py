import discord
from discord.ext import commands
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from random import randint, choice
import asyncio

from Core.Logger import Logger
from Libs.Database import Database
from Libs.utils.bot_utils import BotUtils
from Libs.utils.gamble import Gamble

# Load .env
load_dotenv(".env")

class Economy(commands.Cog):
    name = "economy"
    description = '''This group has all commands related to the economy. Including daily credits commands and money management commands and gambling.'''
    color = "#CD56FF"

    Coins = {
        "tails" : "https://cdn.discordapp.com/attachments/619705602519728138/619705640796946461/coin_tails.gif",
        "heads" : "https://cdn.discordapp.com/attachments/619705602519728138/619705624430641152/badge_heetocoin.gif"
    }

    MaxBet = 800

    # Hardcoded values for daily credits because I want to have control for the credits for each day. 
    # That's why I don't use a formula to calculate it automatically
    DailyStreak = {
        0 : 250,
        1 : 300,
        2 : 350,
        3 : 400,
        4 : 450,
        5 : 500,
        6 : 550
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
        '''
            Creates a confirmation message with a check mark and a X emote;
            :params message: Discord message that will be listened and edited;
            :params emojis: list with emotes that will be added to the message;
            :params user: Discord user that needs to confirm
            :return: True if user clicked on check mark, False if user clicked on X and None if time's up
        '''
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


    @commands.group(pass_context=True, help="<subcommand params>", usage="money", description="A group of commands.")
    async def money(self, ctx: commands.Context):
        if ctx.invoked_subcommand == None:
            dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
            currencyEmbed = discord.Embed(
                title=f"{ctx.author.name}'s balance",
                description=f"**Balance:** {dbQuery[0][3]}",
                color=BotUtils.parseColorFromString(dbQuery[0][10])
                )
            await ctx.send(embed=currencyEmbed)

    @money.command(pass_context=True, help="<@user> <amount>", usage="money send @Haato#0704 $1000", description="Sends <@user> <amount> from your balance.")
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
                self.Database.GiveUserMoney(ctx.author.id, userMoney)
                self.Database.GiveUserMoney(to_user.id, targetQueryMoney)
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
            await ctx.send(f"{ctx.author.mention} You don't have that much money!")

    @commands.command(pass_context=True, help="None", usage="balance", description="Shows your credits balance.", aliases=["bank"])
    async def balance(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        currencyEmbed = discord.Embed(
            title=f"{ctx.author.name}'s balance",
            description=f"**Balance:** {dbQuery[0][3]}",
            color=BotUtils.parseColorFromString(dbQuery[0][10])
            )
        await ctx.send(embed=currencyEmbed)
    
    @commands.command(pass_context=True, help="None", usage="daily", description="Claims your daily amount of credits. The higher your streak the more you get! (Up to 7 days in a row)")
    async def daily(self, ctx: commands.Context):
        dbQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        lastClaim = (datetime.date(datetime.now()) - dbQuery[0][6])
        streak = dbQuery[0][7]
        userCredits = BotUtils.parseMoney(dbQuery[0][3])
        if lastClaim.days > 0:
            streak = streak if lastClaim.days == 1 else 0
            if streak < len(Economy.DailyStreak):
                dailyCredit = Economy.DailyStreak.get(streak)
                newStreak = streak + 1 if streak < (len(Economy.DailyStreak) - 1) else 0
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
            now = datetime.utcnow()
            resetTime = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            timeUntilReset = time.strftime("%H hours, %M minutes, %S seconds", time.gmtime(((resetTime - now).seconds)))
            await ctx.send(f"{ctx.author.mention} You already claimed your daily credits <:peepoMad:617113238328442958>! Dailies reset everyday at 00:00 AM UTC! You can claim it again in **{timeUntilReset}**! ")

    # Gamble commands
    @commands.group(pass_context=True, help="<subcommand> <subcommand params>", usage="gamble", description="Shows available gambling games!", aliases=["gambling"])
    async def gamble(self, ctx: commands.Context):
        if ctx.invoked_subcommand == None:
            await ctx.send(f'''{ctx.author.mention} You need to specify which gamble game you want to play and how much money you want to bet! <:peepoCry:617113235459407894>\nAvailable games:
            ```\n~gamble slots\n~gamble coin```
            ''')
    
    @gamble.group(pass_context=True, help="<heads or tails> <bet>", usage="gamble coin $1000", description="Coin toss!", aliases=["coins"])
    @commands.cooldown(rate=2, per=2.0, type=commands.BucketType.channel)
    async def coin(self, ctx: commands.Context, side: str = "None", bet: str = None):
        if not side.endswith("s"):
            side = f"{side}s"
        if side.lower() not in ["heads", "tails"]:
            await ctx.send(f"Command usage:\n~gamble coin <heads or tails> <bet>")
            return
        userInfo = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        if bet.lower() == "all":
            bet = Economy.MaxBet
        try:
            bet = BotUtils.parseMoney(str(bet))
        except:
            await ctx.send(f"{ctx.author.mention} That's not a valid amount of money!")
            return
        if bet < 1:
            await ctx.send(f"{ctx.author.mention} You can't bet ${bet:,.2f}! The minimum bet is **$1**")
            return
        if bet > Economy.MaxBet:
            await ctx.send(f"{ctx.author.mention} The max you can bet is **${Economy.MaxBet:,.2f}**! <:peepoCry:617113235459407894>")
            return
        userMoney = BotUtils.parseMoney(userInfo[0][3])
        if bet > userMoney:
            await ctx.send(f"{ctx.author.mention} You don't have enough money for that! <:peepoCry:617113235459407894>")
            return
        else:
            faces = ["heads", "tails"]
            toss = choice(faces)
            if toss == side.lower():
                multiplier = 1
                newBet = bet * multiplier
                description = f"You won **${bet + newBet:,.2f}** <:peepoJackpot:618839207418396682>"
            else:
                multiplier = -1
                newBet = bet * multiplier
                description = f"You lost **${bet:,.2f}** <:peepoCry:617113235459407894>"
            newAmount = userMoney + newBet
            if self.Database.GiveUserMoney(ctx.author.id, newAmount):
                coinEmbed = discord.Embed(
                    title = "Coin toss!",
                    description = f"You chose **{side.lower()}** and got **{toss}**\n{description}",
                    color = 0x9430FF
                )
                coinEmbed.set_thumbnail(url=Economy.Coins.get(toss))
                await ctx.send(embed=coinEmbed)
            else:
                await ctx.send("Something went wrong and I couldn't update your credits! Try again later... <:peepoCry:617113235459407894>")

    @gamble.group(pass_context=True, help="<bet>", usage="gamble slots $800", description="Gambling slot machine!\nJackpot = 10x bet\n3 symbols = 2x bet\n2 symbols = 1.2x bet")
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.channel)
    async def slots(self, ctx: commands.Context, bet: str):
        userInfo = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        if bet.lower() == "all":
            bet = Economy.MaxBet
        try:
            bet = BotUtils.parseMoney(str(bet))
        except:
            await ctx.send(f"{ctx.author.mention} That's not a valid amount of money!")
            return
        if bet < 1:
            await ctx.send(f"{ctx.author.mention} You can't bet ${bet:,.2f}! The minimum bet is **$1**")
            return
        if bet > Economy.MaxBet:
            await ctx.send(f"{ctx.author.mention} The max you can bet is **${Economy.MaxBet:,.2f}**! <:peepoCry:617113235459407894>")
            return
        userMoney = BotUtils.parseMoney(userInfo[0][3])
        if bet > userMoney:
            await ctx.send(f"{ctx.author.mention} You don't have enough money for that! <:peepoCry:617113235459407894>")
            return
        else:
            slots = ["<:peepoCrying:617447775147261952>", "<:peepoSweat:617447775537201164>", "<:peepoLove:618828609569816597>", "<:peepoHappy:617113235828637721>", "<:peepoBlush:617113235489030144>"]
            slotsMachine = discord.Embed(
                title = "SLOTS MACHINE",
                description = "**- Starting slots machine -**",
                color = 0x9430FF
                )
            slotsMachine.set_thumbnail(url="https://cdn.discordapp.com/attachments/619705602519728138/620446195818561546/HeetoSlots.gif")
            slotsMachine.add_field(
                name = "**Results**",
                value = "- - -"
            )
            slotsMachineMessage = await ctx.send(embed=slotsMachine)
            for simSlots in range(3):
                simulated = Gamble.SimulateSlots(slots, 3)
                if simSlots == 2:
                    jackpot_rng = randint(1, 1000)
                    if jackpot_rng <= 5:
                        simulated = ["<:peepoJackpot:618839207418396682>", "<:peepoJackpot:618839207418396682>", "<:peepoJackpot:618839207418396682>"]
                    slotsMachine.description = f"{'  |  '.join(simulated)}"
                    break
                else:
                    slotsMachine.description = f"{'  |  '.join(simulated)}"
                    await slotsMachineMessage.edit(embed=slotsMachine)
                    await asyncio.sleep(0.5)

            slotsMachineField = slotsMachine.fields[0]
            if Gamble.slotsOutput(simulated) == 1:
                if simulated[0] == "<:peepoJackpot:618839207418396682>":
                    newBet = bet * 12
                    slotsMachineField.value = f"DING DING DING! Jackpot! You just won 12x your bet! Added **${bet + newBet:,.2f}** to your balance! <:peepoJackpot:618839207418396682>"
                else:
                    # If all slots are equal, @user gets 2x the bet
                    newBet = bet * 1.5
                    slotsMachineField.value = f"YOU WON **${bet + newBet:,.2f}!** <:peepoHappy:617113235828637721>"
            # If 2 slots are equal and 1 is different, 1.2x the bet
            elif Gamble.slotsOutput(simulated) == 2:
                newBet = bet * 1.1
                slotsMachineField.value = f"YOU WON **${bet + newBet:,.2f}!** <:peepoHappy:617113235828637721>"
            # If all slots are different, @user loses money pepeHands
            else:
                slotsMachineField.value = f"YOU LOST **${bet:,.2f}!** <:peepoCrying:617447775147261952>"
                newBet = bet * (-1)
            newAmount = userMoney + newBet
            slotsMachine.clear_fields()
            slotsMachine.add_field(
                name = slotsMachineField.name,
                value = slotsMachineField.value
            )
            if self.Database.GiveUserMoney(ctx.author.id, newAmount):
                await slotsMachineMessage.edit(embed=slotsMachine)
            else:
                slotsMachine.add_field(name="**Whoops**", value=f"Whoops, something went wrong! You didn't lose credits, so don't worry. Try gambling again later <:peepoCrying:617447775147261952>")
                await slotsMachineMessage.edit(embed=slotsMachine)
def setup(bot):
    bot.add_cog(Economy(bot))