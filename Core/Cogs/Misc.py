from discord.ext import commands
from Core.Logger import Logger
import random
from Libs.utils.bot_utils import BotUtils

class Misc(commands.Cog):
    name = "misc"
    description = '''
        Misc contains all commands that doesn't have an specific group.
    '''
    color = "#FBFB43"

    def __init__(self, bot):
        Logger.Log("Miscellaneous loaded!")
        self.bot:commands.Bot = bot
        
    @commands.command(pass_context=True, help="<@users>", usage="spam @user#0001 @user#0002", description="Mentions <@users> 3 times (up to 10 people at once)")
    @commands.cooldown(rate=1, per=4.0, type=commands.BucketType.channel)
    async def spam(self, ctx: commands.Context):
        message: commands.Context.message = ctx.message
        if ctx.message.mention_everyone:
            await ctx.send("You can't spam everyone")
            return
        if len(message.mentions) > 0:
            if len(message.mentions) > 10:
                await ctx.send(f"{ctx.author.mentions} you can only spam up to 10 people at once!")
                return
            for spam in range(3):
                await ctx.send(f"{', '.join([mentioned_user.mention for mentioned_user in message.mentions])} Wake up!")
        else:
            await ctx.send(f"{ctx.author.mention} You need to mention someone!")

    @commands.command(pass_context=True, help="<message>", usage="echo Hello World!", description="Bot repeats the <message>")
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.channel)
    async def echo(self, ctx: commands.Context, *, message: str):
        await ctx.send(message)
    
    @commands.command(pass_context=True, help="<message>", usage="emojos This is a copypasta peepoHappy", description="Turns the <message> into an emoji copypasta")
    @commands.cooldown(rate=2, per=5.0, type=commands.BucketType.guild)
    async def emojos(self, ctx: commands.Context, *, message: str):
        listEmojos = ["😂", "🤔", "😐", "😍", "😴", "😡", "👌", "👊", "👀", "👅", "🍆", "💦"]
        finalResult = [random.choice(listEmojos)]
        messageWords = message.split(" ")
        for message in messageWords:
            finalResult.append(f"{message}{random.choice(listEmojos)}")
        await ctx.send("".join(finalResult[0:1999]))

    @commands.command(pass_context=True, help="<max>*", usage="roll 1000", description="Rolls a dice. Numbers can be from 0 to <max>.")
    async def roll(self, ctx: commands.Context, *, max_number: str = '20'):
        try:
            max_number = int(max_number)
            if max_number < 1:
                await ctx.send("Max number cannot be under 1!")
                return
            rolledNumber = random.randint(0, max_number)
            await ctx.send(f"🎲 {ctx.author.mention} you rolled {rolledNumber}")
        except ValueError:
            await ctx.send("Max number must be a number!")
            return
    
    @commands.command(pass_context=True, help="<background>* <foreground>*", usage="heart 🍑 🍆", description="Creates a heart using default emojis.")
    async def heart(self, ctx:commands.Context, background:str='0', foreground:str='1'):
        heartTemplate = "000000000\n001101100\n011111110\n011111110\n011111110\n001111100\n000111000\n000010000\n000000000"
        heartBackground = ["🖤", "💚", "💜"]
        heartForeground = ["❤", "💛", "💙"]
        choosenBackground = random.choice(heartBackground) if background == '0' else background
        choosenForeground = random.choice(heartForeground) if foreground == '1' else foreground
        if BotUtils.isEmoji(choosenBackground) and BotUtils.isEmoji(choosenForeground):
            await ctx.send(heartTemplate.replace('0', choosenBackground).replace('1', choosenForeground))
        else:
            await ctx.send("This command only works with default emoticons :(")
        
def setup(bot):
    bot.add_cog(Misc(bot))
