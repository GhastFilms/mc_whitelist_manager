import os
import discord
import socket
from mcipc.rcon import Client
import sys

if os.path.isfile("./.env") is True:
    from dotenv import load_dotenv
    load_dotenv()

from config import BotConfig

client = discord.Client()

async def whitelist_from_channel(dclient, message):
    
    conf = dclient.config

    if len(message.content.split(" ")) > 1:
        return()

    player = message.content
    
    try:
        with Client(conf.RCON_HOST, conf.RCON_PORT) as c:
            if not c.login(conf.RCON_PASSWORD):
                print("Failed to login to the minecraft server")
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
        print("Connection to the minecraft server timed out after")
        await message.channel.send("Connection to the minecraft server timed out")



# the value pair contains if the command requires admin and the function to run the command

# main functions

async def command_handler(client, command, is_admin, message):
    cmd_pair = client.command_map.get(command)
    if cmd_pair is None:
        return 0
    req_admin = cmd_pair[0]

    if (((req_admin is True) and (is_admin is True)) or (req_admin is False)):
        await cmd_pair[1].run(cmd_pair[1], client, message)

def is_user_admin(message):
    user_perms = message.author.guild_permissions
    if user_perms.administrator:
        return True
    return False

class Bot(discord.Client):

    config = BotConfig
    command_map = {}

    def regiester_commands(self):
        f = os.listdir("./commands")
        print(f)
        for i in f:
            print(i)
            if i[-3:] == ".py":
                w = __import__(('commands.'+ i[:-3]), fromlist=['command'])
                try:
                    w.command.run
                    w.command.command_name
                except NameError:
                    print("Not in scope!")
                else:
                    print("In scope: " + w.command.command_name)
                    self.command_map[w.command.command_name] = (False, w.command)


    async def on_ready(self):

        self.config = BotConfig()

        self.regiester_commands()
        
        print(f'{client.user} has connected')

        print("command map:")
        print(self.command_map)

    async def on_message(self, message):
        command = self.get_command(message)

        # if the message is in the whitelist channel then do this
        
        # for some stupid reason i have to convert both values to string to get them to compare right. without converting them even when they were the same python was saying that it was unequal
        
        if (str(message.channel.id) == str(self.config.whitelist_channel)) and not (message.author.id == self.user.id):
            await whitelist_from_channel(self, message)
            
        if command is not None:
            await command_handler(self, command, is_user_admin(message), message)

    def get_command(self, message):
        if message.content.startswith(self.config.prefix):
            return message.content.split(" ")[0][1:]
        else:
            return None



if __name__ == "__main__":
    client = Bot()
    token = os.getenv("TOKEN")

    if token is None:
        print("discord token env var is missing")
        exit(0)
    
    client.run(token)