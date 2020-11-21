
import discord
import socket
from mcipc.rcon import Client
import sys
import os
import logging

from botConfig import BotConfig

async def whitelist_from_channel(dclient, message):
    
    conf = dclient.config

    if len(message.content.split(" ")) > 1:
        return()

    player = message.content
    
    try:
        with Client(conf.RCON_HOST, conf.RCON_PORT) as c:
            if not c.login(conf.RCON_PASSWORD):
                logging.warn("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("whitelist add " + player)

                if r.lower() == ("added " + player + " to the whitelist").lower():
                    emoji = '\N{THUMBS UP SIGN}'
                    await message.add_reaction(emoji)
                    await dclient.get_channel(dclient.whitelist_log_channel).send("whitelisted " + "<@" + str(message.author.id) + "> as " + player)
                else:
                    emoji = '\N{THUMBS DOWN SIGN}'
                    await message.add_reaction(emoji)
                    await dclient.get_channel(dclient.whitelist_log_channel).send("fail to whitelisted " + "<@" + str(message.author.id) + ">. message: \"" + r + "\"")                

    except socket.timeout:
        logging.warn("Connection to the minecraft server timed out after")
        await message.channel.send("Connection to the minecraft server timed out")


# the value pair contains if the command requires admin and the function to run the command

# main functions

async def command_handler(client, command, message):
    cmd_class = client.command_map.get(command)
    if cmd_class is None:
        return 0
    
    req_perms = cmd_class.required_permissions

    if (((req_perms == 1) and (message.author.guild_permissions.administrator is True)) or (req_perms == 0)):
        await cmd_class.run(message)

def is_command(cmd):
    has_run = hasattr(cmd, "run")
    has_name = hasattr(cmd, "name")
    has_permissions  = hasattr(cmd, "required_permissions")

    if has_run and has_name and has_permissions:
        return True
    else: 
        return False


class BotClient(discord.Client):

    config = BotConfig
    command_map = {}

    def regiester_commands(self):
        logging.debug("Registering commands...")
        f = os.listdir("./src/commands")
        for i in f:
            if i[-3:] == ".py":
                
                w = __import__(('commands.'+ i[:-3]), fromlist=['Command'])
                if is_command(w.Command):
                    c = w.Command(self)
                    self.command_map[c.name] = c
                    logging.debug("Registered command located in " + w.name)
                else:
                    logging.warning("failed to register command located in file: " + i)
                    
    async def on_ready(self):
        logging.info(f'{self.user} has connected')
        

    async def on_message(self, message):
        logging.debug("processing message: " + message)
        command = self.get_command(message)

        # if the message is in the whitelist channel then do this
        
        # for some stupid reason i have to convert both values to string to get them to compare right. without converting them even when they were the same python was saying that it was unequal
        
        if (str(message.channel.id) == str(self.config.whitelist_channel)) and not (message.author.id == self.user.id):
            await whitelist_from_channel(self, message)
            return 0
            
        if command is not None:
            await command_handler(self, command, message)

    def get_command(self, message):
        if message.content.startswith(self.config.prefix):
            return message.content.split(" ")[0][1:]
        else:
            return None

