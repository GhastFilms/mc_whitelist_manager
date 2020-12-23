
import discord
import socket
from mcipc.rcon import Client
import sys
import os
import logging
import discordhealthcheck
from redisgraph import Graph, Node
import redis

from command import CommandHandlerBuilder
from modules import get_modules

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


class BotClient(discord.Client):

    config = BotConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.healthcheck_server = discordhealthcheck.start(self)
        cmd_handler_builder = CommandHandlerBuilder(self)
        mods = get_modules()
        for mod in mods:
            cmd_handler_builder.add_module(mod)
        self.command_handler = cmd_handler_builder.build()

                    
    async def on_ready(self):
        logging.info(f'{self.user} has connected')
        

    async def on_message(self, message):
        (cmd, args, command_module_id) = self.command_handler.get_command(message.content)
            
        if cmd is not None:

            module_enabled = False

            if command_module_id == 0:
                module_enabled = True
        
            module_set_name = (str(message.guild.id) +  "_modules")

            db_conn = redis.Redis(connection_pool=self.db.pool)
        
            pipe = db_conn.pipeline().get("owner_id").exists(module_set_name)

            if command_module_id != 0:
                pipe.sismember(module_set_name, str(command_module_id))

            p = pipe.execute()
            if p[1] == 0:
                default_module_ids = [1,2]
                pipe = db_conn.pipeline()
                for x in default_module_ids:
                    pipe.sadd(module_set_name, x)
                pipe.execute()

            owner_id = p[0]

            if command_module_id != 0:
                module_enabled = p[2]


            is_owner = False
            if owner_id is not None:
                if int(owner_id.decode()) == message.author.id:
                    is_owner = True
        

            if is_owner == True:
                await cmd(self, args, message)
                return

            if module_enabled == False:
                await message.channel.send("module is disabled")
                return
        
            if (message.author.guild_permissions.administrator is True):
                await message.channel.send("you dont have perms lol")
                return

            await cmd(self, args, message)
                #await self.command_handler.run_command(command, message)

    def get_command(self, message):
        if message.content.startswith(self.config.prefix):
            return message.content.split(" ")[0][1:]
        else:
            return None

