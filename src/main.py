import os
import sys

from bot import BotClient
from botConfig import BotConfig

if __name__ == "__main__":

    if os.path.isfile("./.env") is True:
        from dotenv import load_dotenv
        load_dotenv()
    
    if token is None:
        print("discord token env var is missing")
        exit(0)

    client = BotClient()
    
    client.config = BotConfig()
    
    client.register_commands()

    token = os.getenv("TOKEN")
    
    client.run(token)