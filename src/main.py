import os
import sys
import logging
import redis
from redisgraph import Graph

import time

from bot import BotClient
from botConfig import BotConfig, dbConfig

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
            conn = redis.Redis(host=dbcfg.host, port=dbcfg.port)
            if conn:
                conn.close()
                break
        except:
            logging.warning("failed to connect to db, watiting 5 seconds and retrying")
            time.sleep(5)
    
    client.db.pool = redis.ConnectionPool(host=dbcfg.host, port=dbcfg.port, db=0)

    r = redis.Redis(client.db.pool)
    graph = Graph('Users', r)

    if not client.db.pool:
        logging.warning("failed to create db pool, exiting")
        exit(0)

    client.run(token)