# Import and load .env
from dotenv import load_dotenv as loadEnv
import os

loadEnv('.env')
TOKEN = os.getenv('BOT_TOKEN')

# Import core libs
from Core.Bot import Bot

__version__ = "v1.0.0"


Heeto = Bot()
Heeto.run(TOKEN)