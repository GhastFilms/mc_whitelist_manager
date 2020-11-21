import os
import sys
import logging

from bot import BotClient
from botConfig import BotConfig

if __name__ == "__main__":

    if os.path.isfile("./.env") is True:
        from dotenv import load_dotenv
        load_dotenv()
    
    loglevel = logging.INFO
    
    llenv = os.getenv('LOG_LEVEL').lower()
    
    if llenv == 'debug':
        loglevel = logging.DEBUG
        logging.debug("logging at debug level")
    elif llenv == 'warn'
    

    logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

    if token is None:
        logging.error("discord token env var is missing")
        exit(0)

    client = BotClient()
    
    client.config = BotConfig()
    
    client.register_commands()

    token = os.getenv("TOKEN")
    
    client.run(token)