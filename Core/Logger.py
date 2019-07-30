from datetime import datetime
class Logger:
    ERROR = 2
    WARNING = 1
    LOG = 0

    @staticmethod
    def GetCurrentTime():
        '''
            Gets and formats the current time in the following format:
                        dd/mm/yyyy  HH:MM:SS
                E.g:   '30/07/2019  12:12:14'
        '''
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def Log(message: str, level: int = LOG):
        '''
            Prints messages on the console
            :param message: A string to be printed on the console
            :param level: Type of log, 0 = normal, 1 = warning, 2 = error (optional)
        '''
        if (level == Logger.ERROR):
            log_prefix = "[ERROR]"
        elif (level == Logger.WARNING):
            log_prefix = "[WARNING]"
        else:
            log_prefix = "[LOG]"
        print(f"{Logger.GetCurrentTime()} {log_prefix} {message}")