import os
import discord
import socket
from mcipc.rcon import Client

if os.path.isfile("./.env") is True:
    from dotenv import load_dotenv
    load_dotenv()

client = discord.Client()

#commands
async def whitelist(dclient, message):
    x = message.content.split(" ")
    if len(x) < 2:
        await message.channel.send("provide a username to whitelist")
        return

    player = message.content.split(" ")[1]
    try:
        with Client(dclient.RCON_HOST, dclient.RCON_PORT) as c:
            if not c.login(dclient.RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("whitelist add " + player)
                # print(r)
                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out after")
        await message.channel.send("Connection to the minecraft server timed out")

async def blacklist(dclient, message):
    x = message.content.split(" ")
    if len(x) < 2:
        await message.channel.send("provide a username to whitelist")
        return
    player = x[1]
    try:
        with Client(dclient.RCON_HOST, dclient.RCON_PORT) as c:
            if not c.login(dclient.RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("whitelist remove " + player)
                # print(r)
                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out ")
        await message.channel.send("Connection to the minecraft server timed out")

async def players(dclient, message):
    try:
        with Client(dclient.RCON_HOST, dclient.RCON_PORT) as c:
            if not c.login(dclient.RCON_PASSWORD):
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

                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out ")
        await message.channel.send("Connection to the minecraft server timed out")

async def player_count(dclient, message):
    try:
        with Client(dclient.RCON_HOST, dclient.RCON_PORT) as c:
            if not c.login(dclient.RCON_PASSWORD):
                print("Failed to login to the minecraft server")
                await message.channel.send("Failed to login to the minecraft , try again later")
            else:
                r = c.run("list").split(" ")
                r = str(r[2]) + "/" + str(r[7])

                await message.channel.send(r)
    except socket.timeout:
        print("Connection to the minecraft server timed out ")
        await message.channel.send("Connection to the minecraft server timed out")

async def whitelist_from_channel(dclient, message):

    if len(message.content.split(" ")) > 1:
        return()

    player = message.content
    
    try:
        with Client(dclient.RCON_HOST, dclient.RCON_PORT) as c:
            if not c.login(dclient.RCON_PASSWORD):
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
command_map = {
    "whitelist":   (True,  whitelist   ),
    "blacklist":   (True,  blacklist   ),
    "players":     (False, players     ),
    "playercount": (False, player_count)
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
    async def on_ready(self):
        #setup config
        #TODO move config into a new class

        # RCON config
        self.RCON_HOST = os.getenv("RCON_HOST")
        self.RCON_PORT = os.getenv("RCON_PORT")
        self.RCON_PASSWORD = os.getenv("RCON_PASSWORD")
        
        # General Discord Config
        self.prefix                = os.getenv("DISCORD_TOKEN")
        self.whitelist_channel     = os.getenv("WHITELIST_CHANNEL_ID")
        self.whitelist_log_channel = os.getenv("WHITELIST_LOG_CHANNEL_ID")
        self.prefix                = os.getenv("COMMAND_PREFIX")

        if self.RCON_HOST is None:
            print("Unspecified rcon host, exiting")
            exit(0)

        if self.RCON_PORT is None:
            print("Unspecified rcon port, using 25575")
            self.RCON_PORT = 25575

        if self.RCON_PASSWORD is None:
            print("Unspecified rcon password, using \'\'")
            self.RCON_PASSWORD = ''

        try:
            self.RCON_PORT = int(self.RCON_PORT)
        except ValueError:
            print("rcon port could not be coverted to int, using 25575")
        
        if self.prefix is None:
            print("Unspecified prefix, using $")
            self.prefix = '$'

        if self.whitelist_channel is None:
            print("whitelist channel unspecified and is now disabled disabling")
        else:
            try:
                self.whitelist_channel = int(self.whitelist_channel)
            except ValueError:
                print("whitelist channel could not be converted to int")
                self.whitelist_channel = 0
            
        if self.whitelist_log_channel is None:
            print("whitelist log channel unspecified and is now disabled disabling")
        else:
            try:
                self.whitelist_log_channel = int(self.whitelist_log_channel)
            except ValueError:
                print("whitelist channel could not be converted to int")
                self.whitelist_log_channel = 0
        
        print(f'{client.user} has connected')

    async def on_message(self, message):
        command = self.get_command(message)

        # if the message is in the whitelist channel then do this
        
        # for some stupid reason i have to convert both values to string to get them to compare right. without converting them even when they were the same python was saying that it was unequal
        
        if (str(message.channel.id) == str(self.whitelist_channel)) and not (message.author.id == self.user.id):
            await whitelist_from_channel(self, message)
            
        if command is not None:
            await command_handler(self, command, is_user_admin(message), message)

    def get_command(self, message):
        if message.content.startswith(self.prefix):
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