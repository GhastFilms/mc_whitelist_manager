import discord
import socket
from mcipc.rcon import Client

class Command:

    name = 'help'

    required_permissions = 0

    dclient = None

    def __init__(self, dclient):
        self.dclient = dclient

    async def run(self, message):
        
        # conf = self.dclient.config
        keys = list(self.dclient.command_map)
        r = "commands: " + keys[0]
        for i in keys[1:]:
            r = r + ", " + i
       
        await message.channel.send(r)