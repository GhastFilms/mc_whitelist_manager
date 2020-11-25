import os
import sys
import logging
import psycopg2

from psycopg2 import pool

import time

from bot import BotClient
from botConfig import BotConfig
from botConfig import dbConfig

if __name__ == "__main__":

    if os.path.isfile("./.env") is True:
        from dotenv import load_dotenv
        load_dotenv()
    
    loglevel = logging.INFO
    
    llenv = os.getenv('LOG_LEVEL')

    if llenv is None:
        loglevel = logging.INFO

    elif llenv.lower() == 'debug':
        loglevel = logging.DEBUG

    elif llenv.lower() == 'info':
        loglevel = logging.INFO

    elif llenv.lower() == 'warn':
        loglevel = logging.WARN
        
    

    logging.basicConfig(level=loglevel)

    token = os.getenv("TOKEN")

    if token is None:
        logging.error("discord token env var is missing")
        exit(0)

    client = BotClient()

    client.config = BotConfig()
    client.db = dbConfig()

    dbcfg = client.db
    
    while True:
        try:
            logging.info("attemting to connect to database")
            conn = psycopg2.connect(user=dbcfg.user, password=dbcfg.password, host=dbcfg.host, port=dbcfg.port, dbname="mc")
            conn.close()
            break
        except:
            logging.warning("failed to connect to db, watiting 5 seconds and retrying")
            time.sleep(5)
    
    client.db.pool = psycopg2.pool.ThreadedConnectionPool(3, 12, user = dbcfg.user, password = dbcfg.password, host = dbcfg.host, port = dbcfg.port, dbname="mc")

    if not client.db.pool:
        logging.warning("failed to create db pool, exiting")
        exit(0)

    client.regiester_commands()
    
    client.run(token)