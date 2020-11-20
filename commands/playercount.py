import discord
import socket
from mcipc.rcon import Client

class command:
    command_name = 'playercount'

    async def run(self, dclient, message):
    
        conf = dclient.config
    
        try:
            with Client(conf.RCON_HOST, conf.RCON_PORT) as c:
                if not c.login(conf.RCON_PASSWORD):
                    print("Failed to login to the minecraft server")
                    await message.channel.send("Failed to login to the minecraft , try again later")
                else:
                    r = c.run("list").split(" ")
                    r = str(r[2]) + "/" + str(r[7])

                    await message.channel.send(r)
        except socket.timeout:
            print("Connection to the minecraft server timed out ")
            await message.channel.send("Connection to the minecraft server timed out")