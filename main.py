import os
import discord
from dotenv import load_dotenv
import socket
#import grpc

#import WhitelistManager_pb2
#import WhitelistManager_pb2_grpc

from mcipc.rcon import Client

load_dotenv()

client = discord.Client()

RCON_HOST = os.getenv("RCON_HOST")
RCON_PORT = os.getenv("RCON_PORT")
RCON_PASSWORD = os.getenv("RCON_PASSWORD")

if RCON_HOST is None:
    print("Unspecified rcon host, exiting")
    exit(0)

if RCON_PORT is None:
    print("Unspecified rcon port, using 25575")
    RCON_PORT = 25575

try:
    RCON_PORT = int(RCON_PORT)
except ValueError:
    print("rcon port could not be coverted to int, using 25575")

if RCON_PASSWORD is None:
    print("Unspecified rcon password, using \'\'")
    RCON_PASSWORD = ''

#commands
async def whitelist(client, message):
    x = message.content.split(" ")
    if len(x) < 2:
        await message.channel.send("provide a username to whitelist")
        return

    player = message.content.split(" ")[1]
    
    try:
        with Client(RCON_HOST, RCON_PORT) as c:
            if not c.login(RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("whitelist add " + player)
                # print(r)
                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out after")
        await message.channel.send("Connection to the minecraft server timed out")

async def blacklist(client, message):
    x = message.content.split(" ")
    if len(x) < 2:
        await message.channel.send("provide a username to whitelist")
        return

    player = x[1]
    
    try:
        with Client(RCON_HOST, RCON_PORT) as c:
            if not c.login(RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("whitelist remove " + player)
                # print(r)
                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out ")
        await message.channel.send("Connection to the minecraft server timed out")

async def get_players(client, message):
    try:
        with Client(RCON_HOST, RCON_PORT) as c:
            if not c.login(RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                i = c.run("list").split(" ")
                r = ''
                if len(i) == 9:
                    r = 'No players Connected'
                elif len(i) == 11:
                    r = i[10]
                else:
                    r = i[10]
                    for x in i[11:]:
                        r = r + " " + x
                # print(r)
                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out ")
        await message.channel.send("Connection to the minecraft server timed out")


async def get_player_count(client, message):
    try:
        with Client(RCON_HOST, RCON_PORT) as c:
            if not c.login(RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("list").split(" ")
                r = str(r[2]) + "/" + str(r[7])
                # print(r)
                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out ")
        await message.channel.send("Connection to the minecraft server timed out")


command_map = {
    "whitelist": (True, whitelist),
    "blacklist": (True, blacklist),
    "getplayers": (False, get_players),
    "getplayercount": (False, get_player_count)
}

# main functions

async def command_handler(client, command, is_admin, message):
    cmd_pair = command_map.get(command)
    if cmd_pair is None:
        return 0
    req_admin = cmd_pair[0]

    if (((req_admin is True) and (is_admin is True)) or (req_admin is False)):
        await cmd_pair[1](client, message)

def is_user_admin(message):
    user_perms = message.author.guild_permissions
    if user_perms.administrator:
        return True
    return False

class Bot(discord.Client):
    prefix = os.getenv("DISCORD_TOKEN")

    whitelist_channel = 0

    async def on_ready(self):
        self.prefix = os.getenv("COMMAND_PREFIX")
        
        if self.prefix is None:
            print("Unspecified prefix, using $")
            self.prefix = '$'
        
       # self.whitelist_channel = os.getenv("WHITELIST_CHANNEL")
        
        print(f'{client.user} has connected')

    async def on_message(self, message):
        command = self.get_command(message)
        
        if command is not None:
            await command_handler(self, command, is_user_admin(message), message)
        # if the message is in the whitelist channel then do this
        if (message.channel.id is self.whitelist_channel) and not (message.author.id == self.user.id):
            print(message.content)

    def get_command(self, message):
        if message.content.startswith(self.prefix):
            return message.content.split(" ")[0][1:]
        else:
            return None

client = Bot()

token = os.getenv("TOKEN")
if token is None:
    print("discord token env var is missing")
    exit(1)

client.run(token)
