import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

from Libs.Database import Database
from Core.Logger import Logger
from Libs.utils.bot_utils import BotUtils

load_dotenv('.env')

class Family(commands.Cog):
    MarriageCost = 0

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
    
    def divorceUsers(self, user_req, user_target):
        query1 = f'''UPDATE Users SET married_to = null WHERE id = {user_req};'''
        query2 = f'''UPDATE Users SET married_to = null WHERE id = {user_target};'''
        self.Database.CommitCommand(query1)
        self.Database.CommitCommand(query2)

    def marryUsers(self, user_req, user_target):
        query1 = f'''UPDATE Users SET married_to = {user_target} WHERE id = {user_req};'''
        query2 = f'''UPDATE Users SET married_to = {user_req} WHERE id = {user_target};'''
        self.Database.CommitCommand(query1)
        self.Database.CommitCommand(query2)

    @commands.command(pass_context=True)
    async def marry(self, ctx: commands.Context, target = None):
        if target == None:
            await ctx.send("You can't marry to no one :(")
            return
        elif target == ctx.author.id:
            await ctx.send("You can't marry youself. :(")
            return

        userQuery = self.Database.GetFromTable("Users", f"ID = {ctx.author.id}")
        married_to = userQuery[0][13]
        Credits = userQuery[0][3]
        try:
            target = int(target.strip("<!@>"))
            target = self.Bot.get_user(target)
        except:
            await ctx.send(f"{ctx.author.mention} That's not a valid user!")
        targetQuery = self.Database.GetFromTable("Users", f"ID = {target.id}")
        target_Married_to = targetQuery[0][13]

        def confirmMarriageRequest(reaction, user):
            if str(reaction.emoji) == "✅" and user == ctx.author:
                return True
            elif str(reaction.emoji) == "❌" and user == ctx.author:
                return False
            else:
                return
        
        def confirmMarriageReceive(reaction, user):
            if str(reaction.emoji) == "✅" and user == target:
                return True
            elif str(reaction.emoji) == "❌" and user == target:
                return False
            else:
                return

        if married_to == None:
            if target_Married_to != None:
                await ctx.send(f"{ctx.author.mention} That person is married already!")
                return
            if BotUtils.parseMoney(Credits) >= Family.MarriageCost:
                # Creates the confirmation message
                confirmation:discord.Message = await ctx.send(f"{ctx.author.mention} Marrying costs ${Family.MarriageCost}. Do you want to continue?")
                await confirmation.add_reaction("✅")
                await confirmation.add_reaction("❌")
                # Wait for user reaction
                try:
                    reaction, user = await self.Bot.wait_for("reaction_add", timeout=20.0, check=confirmMarriageRequest)
                except asyncio.TimeoutError:
                    await confirmation.edit("Time's up!")
                else:
                    if (user.id == ctx.author.id):
                        # Creates the confirmation message
                        confirmationReceive:discord.Message = await ctx.send(f"{target.mention} Do you want to marry {ctx.author.mention}?")
                        await confirmationReceive.add_reaction("✅")
                        await confirmationReceive.add_reaction("❌")
                        try:
                            reaction, user = await self.Bot.wait_for("reaction_add", timeout=20.0, check=confirmMarriageReceive)
                        except asyncio.TimeoutError:
                            await confirmationReceive.edit("Time's up!")
                        else:
                            if (user.id == target.id):
                                self.marryUsers(ctx.author.id, target.id)
                                await ctx.send(f"🎉 {ctx.author.mention} is now married to {target.mention}! ❤")
                                return
            else:
                await ctx.send(f"Marrying costs ${Family.MarriageCost}, you have only {Credits}")
        else:
            await ctx.send("You're married already! Use `~divorce` if you want to marry someone else.")

    @commands.command(pass_context=True)
    async def divorce(self, ctx: commands.Context):
        userQuery = self.Database.GetFromTable("Users", f"id = {ctx.author.id}")
        if userQuery[0][13] != None:
            married_to = self.Bot.get_user(userQuery[0][13])
            self.divorceUsers(ctx.author.id, married_to.id)
            await ctx.send(f"You and {married_to.name} are not married anymore!")
        else:
            await ctx.send("Uhhh... You can't divorce if you're not even married!")


def setup(bot):
    bot.add_cog(Family(bot))