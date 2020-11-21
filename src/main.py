import os
import sys

from bot import BotClient

if __name__ == "__main__":

    if os.path.isfile("./.env") is True:
        from dotenv import load_dotenv
        load_dotenv()

    client = BotClient()
    token = os.getenv("TOKEN")

    if token is None:
        print("discord token env var is missing")
        exit(0)
    
    client.run(token)