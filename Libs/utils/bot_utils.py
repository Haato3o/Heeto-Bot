from datetime import datetime
import discord
import random

class BotUtils():
    @staticmethod
    def formatCommandsDict(bot_prefix: str, commands_dict: dict) -> str:
        '''
            Formats dict into a readable block of text for the help embed command
            :param bot_prefix: The bot prefix
            :param commands_dict: Dict with all commands
            :return: string
        '''
        helpDescription = []
        for key in commands_dict:
            formattedLine = f"__**{bot_prefix}{key}__ -> {commands_dict.get(key)}"
            helpDescription.append(formattedLine)
        return "\n".join(helpDescription)

    @staticmethod
    def parseColorFromString(color: str) -> int:
        color = color.strip("#")
        return int(color, 16)

    @staticmethod
    def parseMoney(money: str) -> int:
        '''
            Parses money from string format to int
            :param money: Money (ex: $500.0)
            :return: Int (ex: 500)
        '''
        return int(float(money.strip("$").replace(",", "")))

    @staticmethod
    def isPublicChannel(channel_type) -> bool:
        '''
            Checks if channel is public public or not
            :param channel_type: Type of channel
            :return: True if it's a public channel, false if not
        '''
        return channel_type not in [discord.ChannelType.private, discord.ChannelType.group]

    @staticmethod
    def GetDate() -> str:
        return datetime.now().strftime("%m/%d/%Y")

    @staticmethod
    def isEmoji(char: str) -> bool:
        '''
            Checks if character is an emoji based on it's unicode.
            :param char: Char to check if it's an emoji
            :return: True if char is an emoji, false if not
        '''
        char = char[0]
        # Normal emoticons
        if 0x1F600 < ord(char) > 0x1F64F:
            return True
        # Misc Symbols
        elif 0x1F300 < ord(char) > 0x1F5FF:
            return True
        elif 0x1F680 < ord(char) > 0x1F6FF:
            return True
        elif 0x2600 < ord(char) > 0x26FF:
            return True
        elif 0x2700 < ord(char) > 0x27BF:
            return True
        elif 0xFE00 < ord(char) > 0xFE0F:
            return True
        elif 0x1F900 < ord(char) > 0x1F9FF:
            return True
        elif 0x1F1E6 < ord(char) > 0x1F1FF:
            return True
        else:
            return False