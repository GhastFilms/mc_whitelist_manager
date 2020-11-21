import discord
import socket
from mcipc.rcon import Client

class command:

    name = 'players'

    required_permissions = 0

    dclient = None

    def __init__(self, dclient):
        self.dclient = dclient
    
    async def run(self, message):
        
        conf = self.dclient.config
        
        try:
            with Client(conf.RCON_HOST, conf.RCON_PORT) as c:
                if not c.login(conf.RCON_PASSWORD):
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
                        # takes the usernames of all connected players makes a string seperating each name with a comma
                        r = i[10]
                        for x in i[11:]:
                            r = r + " " + x

                    await message.channel.send(r)

        except socket.timeout:
            print("Connection to the minecraft server timed out ")
            await message.channel.send("Connection to the minecraft server timed out")