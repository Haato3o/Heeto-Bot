import discord
from discord.ext import commands
import asyncio
import os
import random
from dotenv import load_dotenv

from Libs.Database import Database
from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils


load_dotenv('.env')

class Family(commands.Cog):
    name = "family"
    description = '''
        This group has all commands related to the family and marriage systems.
    '''
    color = "#9B26F0"

    MarriageCost = 1000

    def __init__(self, bot):
        self.Bot: commands.Bot = bot
        Logger.Log("Loaded Family mechanics!")
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
            await message.clear_reactions()
            return None
        else:
            if str(emote.emoji) == "✅" and usr.id == user.id:
                return True
            else:
                return False

    def divorceUsers(self, user_req, user_target):
        query1 = f'''UPDATE Users SET married_to = null WHERE id = {user_req};'''
        query2 = f'''UPDATE Users SET married_to = null WHERE id = {user_target};'''
        return self.Database.CommitCommand(query1) and self.Database.CommitCommand(query2)
        

    def marryUsers(self, user_req, user_target):
        query1 = f'''UPDATE Users SET married_to = {user_target} WHERE id = {user_req};'''
        query2 = f'''UPDATE Users SET married_to = {user_req} WHERE id = {user_target};'''
        return self.Database.CommitCommand(query1) and self.Database.CommitCommand(query2)
        

    @commands.command(pass_context=True, help="<@user>", usage="marry @YourLove#0001", description="You can marry <@user> in exchange for some amount of credits.\n > NOTE: Both users must accept the marriage.")
    async def marry(self, ctx: commands.Context, target = None):
        try:
            target = int(target.strip("<!@>"))
            target = self.Bot.get_user(target)
        except:
            await ctx.send(f"{ctx.author.mention} That's not a valid user!")
            return
        if target == None:
            await ctx.send("You can't marry to no one :(")
            return
        elif target.id == ctx.author.id:
            await ctx.send("You can't marry yourself. :(")
            return
        elif target.id == self.Bot.user.id:
            quotes = [
                "UWU U WANNAN MAWWY MIII? UHUH UWU OWO",
                "I'm {random_age} years old btw",
                f"🎉 {ctx.author.mention} is now married to {self.Bot.user.mention}! ❤"
            ]
            await ctx.send(random.choice(quotes).replace("{random_age}", f"{random.randint(2, 14)}"))
            return

        userQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        married_to = userQuery[0][13]
        Credits = userQuery[0][3]
        
        targetQuery = self.Database.GetFromTable("Users", f"ID = {target.id}")
        target_Married_to = targetQuery[0][13]

        if married_to == None:
            if target_Married_to != None:
                await ctx.send(f"{ctx.author.mention} That person is married already!")
                return
            if BotUtils.parseMoney(Credits) >= Family.MarriageCost:
                # Creates the confirmation message
                confirmation:discord.Message = await ctx.send(f"{ctx.author.mention} Marrying costs ${Family.MarriageCost}. Do you want to continue?")
                confirmationRequest = await self.createConfirmation(confirmation, ["✅", "❌"], ctx.author)
                if confirmationRequest == False:
                    await confirmation.edit(content="Marriage cancelled!")
                    return
                elif confirmationRequest:      
                    receiveMarriageRequest = await ctx.send(f"{target.mention} Do you want to marry {ctx.author.mention}?")
                    confirmationReceive = await self.createConfirmation(receiveMarriageRequest, ["✅", "❌"], target)
                    if confirmationReceive == False:
                        await confirmationReceive.edit(content=f"{target.mention} denied {ctx.author.mention}'s proposal!")
                        return
                    elif confirmationReceive:
                        if self.marryUsers(ctx.author.id, target.id):
                            query = f"UPDATE Users SET credits = {BotUtils.parseMoney(Credits) - Family.MarriageCost} where ID = {ctx.author.id};"
                            self.Database.CommitCommand(query)
                            await ctx.send(f"🎉 {ctx.author.mention} is now married to {target.mention}! ❤")
                            return
            else:
                await ctx.send(f"Marrying costs ${Family.MarriageCost}, you have only {Credits}")
        else:
            await ctx.send("You're married already! Use `~divorce` if you want to marry someone else.")

    @commands.command(pass_context=True, help="None", usage="divorce", description="Divorces you from the person you're engaged with.")
    async def divorce(self, ctx: commands.Context):
        userQuery = self.Database.GetFromTable("Users", f"id = {ctx.author.id}")
        if userQuery[0][13] != None:
            married_to = self.Bot.get_user(userQuery[0][13])
            confirmation = await ctx.send(f"Are you sure you want to divorce **{married_to}**?")
            confirm = await self.createConfirmation(confirmation, ["✅", "❌"], ctx.author)
            if confirm == False:
                await confirmation.edit(content="Divorce cancelled!")
            elif confirm:
                self.divorceUsers(ctx.author.id, married_to.id)
                await ctx.send(f"You and {married_to.name} are not married anymore!")
        else:
            await ctx.send("Uhhh... You can't divorce if you're not even married!")


def setup(bot):
    bot.add_cog(Family(bot))