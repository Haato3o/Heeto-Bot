class BotUtils():

    @staticmethod
    def formatCommandsDict(bot_prefix: str, commands_dict: dict):
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
    def isEmoji(char: str):
        '''
            Checks if character is an emoji based on it's unicode.
            :param emote:
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