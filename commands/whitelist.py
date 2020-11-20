import discord
import socket
from mcipc.rcon import Client

class command:
    command_name = 'whitelist'

    async def run(self, dclient, message):
        conf = dclient.config
        x = message.content.split(" ")
        if len(x) < 2:
            await message.channel.send("provide a username to whitelist")
            return

        player = message.content.split(" ")[1]
        try:
            with Client(conf.RCON_HOST, conf.RCON_PORT) as c:
                if not c.login(conf.RCON_PASSWORD):
                    print("Failed to login to the minecraft server")
                    await message.channel.send("Failed to login to the minecraft , try again later")
                else:
                    r = c.run("whitelist add " + player)
                    # print(r)
                    await message.channel.send(r)
        except socket.timeout:
            print("Connection to the minecraft server timed out after")
            await message.channel.send("Connection to the minecraft server timed out")