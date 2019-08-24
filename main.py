# Import and load .env
from dotenv import load_dotenv as loadEnv
import os

loadEnv('.env')
TOKEN = os.getenv('BOT_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')
STATUS_MESSAGE = os.getenv('STATUS_MESSAGE')

# Import core libs
from Core.Bot import Bot

__version__ = "v1.3.2"


Heeto = Bot(PREFIX, STATUS_MESSAGE)
Heeto.run(TOKEN)