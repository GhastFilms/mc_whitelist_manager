import os
import logging

class BotConfig:
    prefix = ''
    
    whitelist_channel = 0
    whitelist_log_channel = 0

    RCON_HOST = ''
    RCON_PORT = 0
    RCON_PASSWORD = ''
    
    def __init__(self):   

        # RCON config
        self.RCON_HOST = os.getenv("RCON_HOST")
        self.RCON_PORT = os.getenv("RCON_PORT")
        self.RCON_PASSWORD = os.getenv("RCON_PASSWORD")
        
        # General Discord Config
        self.whitelist_channel     = os.getenv("WHITELIST_CHANNEL_ID")
        self.whitelist_log_channel = os.getenv("WHITELIST_LOG_CHANNEL_ID")
        self.prefix                = os.getenv("COMMAND_PREFIX")

        if self.RCON_HOST is None:
            logging.error("Unspecified rcon host, exiting")
            exit(0)

        if self.RCON_PORT is None:
            logging.info("Unspecified rcon port, using 25575")
            self.RCON_PORT = 25575

        if self.RCON_PASSWORD is None:
            logging.info("Unspecified rcon password, using \'\'")
            self.RCON_PASSWORD = ''

        try:
            self.RCON_PORT = int(self.RCON_PORT)
        except ValueError:
            logging.warn("rcon port could not be coverted to int, using 25575")
        
        if self.prefix is None:
            logging.warn("Unspecified prefix, using $")
            self.prefix = '$'

        if self.whitelist_channel is None:
            logging.warn("whitelist channel unspecified and is now disabled disabling")
        else:
            try:
                self.whitelist_channel = int(self.whitelist_channel)
            except ValueError:
                logging.warn("whitelist channel could not be converted to int")
                self.whitelist_channel = 0
            
        if self.whitelist_log_channel is None:
            logging.info("whitelist log channel unspecified and is now disabled disabling")
        else:
            try:
                self.whitelist_log_channel = int(self.whitelist_log_channel)
            except ValueError:
                logging.warn("whitelist channel could not be converted to int")
                self.whitelist_log_channel = 0

class dbConfig:
    host = None
    user = None
    password = None
    port = None
    db = None

    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT")

        if self.host is None:
            logging.error("DB_HOST env var missing, exiting")
            exit(0)
        
        if self.user is None:
            logging.error("DB_USERNAME env var missing, exiting")
            exit(0)

        if self.password is None:
            logging.error("DB_PASSWORD env var missing, exiting")
            exit(0)
        
        if self.port is None:
            logging.error("DB_PORT env var missing, exiting")
            exit(0)