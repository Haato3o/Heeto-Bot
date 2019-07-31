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
